
const POSITIVE_START_ROBOT_EMOTIONS = ['cheerful1','amazed1','success1','yes1'];
const POSITIVE_END_ROBOT_EMOTIONS = ['success1','cheerful1','yes1','amazed1'];
const POSITIVE_DANCE_ROBOT_EMOTIONS = ['dance1','dance2','dance3'];

function positiveActivityEmotion(phase='end', itemOrContext=null){
  const title = String(itemOrContext?.title || '').toLowerCase();
  const principal = String(itemOrContext?.emotion || '');
  const danceIds = Array.isArray(robotMotionPolicy.dance_positive) ? robotMotionPolicy.dance_positive : ['dance1','dance2','dance3'];

  let pool = phase === 'start'
    ? (robotMotionPolicy.start_positive || ['dance1','dance2','dance3','cheerful1'])
    : (robotMotionPolicy.end_positive || ['dance1','dance2','dance3','cheerful1','success1']);

  const emotionPool = Array.isArray(robotMotionPolicy.emotion_positive) ? robotMotionPolicy.emotion_positive : [];
  if(emotionPool.length){
    pool = [...pool, ...emotionPool];
  }

  if(title.includes('baile') || title.includes('bailar') || String(itemOrContext?.id||'').includes('dance')){
    pool = [...danceIds, ...pool];
  }

  let finalPool = pool.filter(Boolean);
  if(robotMotionPolicy.avoid_for_principal_emotion){
    finalPool = finalPool.filter(x => x !== principal);
  }
  if(!finalPool.length) finalPool = [phase === 'start' ? (robotMotionPolicy.fallback_start || 'dance1') : (robotMotionPolicy.fallback_end || 'dance2')];

  // Para visibilidad, priorizar bailes al inicio/final si están configurados.
  const visibleDance = finalPool.filter(x => danceIds.includes(x));
  if(visibleDance.length && (phase === 'start' || title.includes('baile') || title.includes('bailar'))){
    return visibleDance[Math.floor(Math.random() * visibleDance.length)];
  }
  return finalPool[Math.floor(Math.random() * finalPool.length)];
}

const APP_VERSION='5.9.95';
/*
v5.9.61 · Comentarios de programación

Este archivo es el controlador principal de la interfaz web de Ritxi.

Responsabilidades principales:
- controlar el chat y la caja de texto;
- activar, pausar y parar el micrófono;
- enviar audio a STT local y texto a FastAPI/Ollama;
- reproducir voz con TTS del navegador;
- ejecutar tarjetas de emociones, juegos, actividades y tutor;
- mantener contexto de actividades largas;
- pintar estado de modo, estado actual, actividad y latencias;
- evitar bloqueos de interfaz cuando micro, TTS u Ollama tardan.

Flujo simplificado:
usuario escribe/habla → app.js → /api/chat o /api/audio/... → FastAPI → Ollama/STT/Robot → app.js actualiza UI.
*/


// Cancela cualquier captura de micrófono o STT pendiente. Se usa cuando el texto debe tener prioridad.
async function hardStopMicCapture(reason='hard-stop'){
  try{ clearMicSilenceTimer(); }catch(_){}
  try{
    if(serverSttStopper){
      const stopper = serverSttStopper;
      serverSttStopper = null;
      await Promise.resolve(stopper(`hard-stop-${reason}`)).catch(()=>{});
    }
  }catch(_){}
  try{ if(recognition) recognition.abort(); }catch(_){}
  try{ if(recognition) recognition.stop(); }catch(_){}
  recognizing=false;
  serverSttActive=false;
  manualStopRequested=true;
  logClient('warn','mic',`Captura de micro cancelada: ${reason}`);
  await sleep(180);
}

function setTextIfPresent(id, value){
  const el = $(id);
  if(el) el.textContent = value;
  return el;
}

function setValueIfPresent(id, value){
  const el = $(id);
  if(el) el.value = value;
  return el;
}


const $ = (id) => document.getElementById(id);
let lastStatus = null;
let realtimeEnabled = false;
let realtimeSending = false;
let realtimeLoopTimer = null;
let recognition = null;
let recognizing = false;
let browserSpeaking = false;
let manualStopRequested = false;
let currentCharacter = null;
let idleEnabled = false;
let serverSttActive = false;
let serverSttStopper = null;
let serverSttSession = 0;
let micSilenceTimer = null;
let lastMicError = null;
let micErrorStreak = 0;
let pendingMicText = '';
let pendingMicInterim = '';
let logEvents = [];
let lastLatencies = [];
let actionSequenceId = 0;
let uiActionBusy = false;
let pendingActionItem = null;
let pendingActionBtn = null;
let lastUserTurnTs = 0;
let micPermissionGranted = false;
let micPermissionAskedThisSession = false;
let autoListenAfterBot = false;
let activityAutoListenAfterBot = false;
let lastBotTurnDoneTs = 0;
let micRetryTimer = null;
let activityAwaitingUser = false;
let selectedConfigFilePath = '';
let selectedConfigFileLabel = '';
let inlineConfigSelectedPath = 'system_prompt';
let inlineConfigSelectedLabel = 'Prompt del sistema';

// Actualiza el texto y estilo del botón principal de micro según el estado real.
function updateMicToggleUi(){
  const btn=$('realtimeToggle');
  if(!btn) return;
  if(micAlwaysOn && !persistentMicPaused){
    btn.textContent='■ Parar micro';
    btn.classList.add('active-mic');
  }else{
    btn.textContent='▶ Activar micro';
    btn.classList.remove('active-mic');
  }
}

async function stopMicByUser(reason='manual-stop'){
  manualMicStopLock = true;
  realtimeEnabled = false;
  autoListenAfterBot = false;
  activityAutoListenAfterBot = false;
  activityAwaitingUser = false;
  if(micRetryTimer){ clearTimeout(micRetryTimer); micRetryTimer=null; }
  await stopAlwaysOnMic(reason);
  setMicStatus('Micro parado por el usuario. No se reactivará solo hasta que pulses Activar micro o abras una actividad con respuesta por voz.');
  logClient('info','mic',`Micro detenido manualmente y bloqueado: ${reason}`);
  updateMicToggleUi();
}

function unlockMicForActivity(reason='activity'){
  if(!manualMicStopLock) return;
  manualMicStopLock = false;
  logClient('info','mic',`Bloqueo manual del micro levantado por ${reason}`);
}

// v5.9.19: gestor de micro continuo controlado.
// Mantiene el stream abierto y solo pausa mientras Ritxi habla.
let micAlwaysOn = false;
let persistentStream = null;
let persistentAudioContext = null;
let persistentSource = null;
let persistentProcessor = null;
let persistentRecording = false;
let persistentVoiceStarted = false;
let persistentChunks = [];
let persistentFirstVoiceAt = 0;
let persistentLastVoiceAt = 0;
let persistentRecordingStartMs = 0;
let persistentMaxRms = 0;
let persistentTranscribing = false;
let persistentMicPaused = false;
let persistentMicPauseReason = '';
let persistentNoiseFloor = 0.008;
let persistentLastIdleStatusAt = 0;

let currentVocabularyHint = '';

const REVIEWED_TURN_ACTIVITY_IDS = new Set(['adivina_sonido','animal_corto','animal_gato','animal_perro','animal_vaca','ayuda_corta','baile_divertido','baile_suave','buscar_palabra','cantar_saludo','completar_frase','cuento_corto','cuento_interactivo','despedida_corta','despedida_guiada','eco_ritxi','elegir_emocion','emocion_nombre','emociones_caras','ensayo_decidir','ensayo_pedir_ayuda','escucha_activa','escucha_y_repite','escuchar','explicar_imagen','final_historia','frase_corta','frase_segura','historia_turnos','imitame','instrumento_tambor','no_corto','opuestos','palabra_corta','palmas_lentas','palmas_rapidas','pausa_sensorial','pedir_ayuda','pedir_descanso','pedir_turno','personajes','preguntar_nombre','presentacion','recordar_historia','respetar_turno_dinamico','ritmo_palmas','rutina_primero_despues','saludo_corto','si_corto','sinonimos','turno_corto','validar_emocion','vamos_hablar']);
const REVIEWED_ANIMAL_ACTIVITY_IDS = new Set(['animal_corto','animal_perro','animal_gato','animal_vaca','adivina_sonido']);
const REVIEWED_YESNO_ACTIVITY_IDS = new Set(['si_corto','no_corto']);
const REVIEWED_SHORT_ACTIVITY_IDS = new Set(['palabra_corta','buscar_palabra','sinonimos','opuestos']);
const activityReplyCounters = {};
function nextActivityVariant(id, count){
  const key = id || 'generic';
  activityReplyCounters[key] = (activityReplyCounters[key] || 0) + 1;
  return activityReplyCounters[key] % Math.max(1,count);
}
function chooseActivityReply(id, variants){
  if(!variants || !variants.length) return '';
  return variants[nextActivityVariant(id, variants.length)];
}
let currentActivityContext = null;
let lastActivityContext = null;
let activityTurnIndex = 0;
let robotMotionBusyUntilMs = 0;
let lastOfficialAudioEndedAt = 0;
let manualMicStopLock = false;


let lastSafeBotTextFallback = false;


let robotMotionPolicy = {
  activity_start_end_enabled:true,
  only_text_chat_without_animations:true,
  visible_start_wait_ms:850,
  visible_end_wait_ms:450,
  play_audio_on_positive_start:true,
  play_audio_on_positive_end:true,
  positive_audio_force:true,
  positive_audio_wait_until_end:false,
  positive_action_wait_start:false,
  positive_action_wait_end:false,
  validated_visible_emotions:['dance1','dance2','dance3','cheerful1','enthusiastic1','amazed1','electric1','success1','yes1','no1','attentive1','thoughtful1'],
  start_positive:['cheerful1','enthusiastic1','amazed1','success1','yes1'],
  end_positive:['cheerful1','enthusiastic1','success1','yes1','amazed1'],
  dance_positive:['dance1','dance2','dance3'],
  emotion_positive:['cheerful1','enthusiastic1','amazed1','electric1','success1','yes1','no1','attentive1','thoughtful1'],
  fallback_start:'cheerful1',
  fallback_end:'success1',
  avoid_for_principal_emotion:true,
  prefer_visible_dances:false
};

let conversationPolicy = {
  repetition_guard:{enabled:true, replace_exact_repetition:true, replace_when_user_topic_changes:true, min_repeated_chars:25},
  current_topic_guard:{enabled:true, instruction:'Responde al último mensaje exacto del usuario.'},
  topic_fallbacks:{},
  default_fallbacks:{
    precise:'Te escucho. Dime el tema con una palabra.',
    balanced:'Entendido. Dime el tema y te respondo con una frase corta.',
    creative:'Vamos a hacerlo fácil: dame una palabra y la convertimos en una idea sencilla.'
  }
};
let lastAssistantVisibleText = '';
let lastAssistantUserText = '';

let interactionPolicy = {
  localActivityIds: new Set(['saludo_corto','si_corto','no_corto','turno_corto','ayuda_corta','despedida_corta','animal_corto','palabra_corta','calma_corta','ritmo_palmas','palmas_lentas','palmas_rapidas','eco_ritxi','instrumento_campana','chiste','success1']),
  ollamaActivityIds: new Set(['escucha_activa','escuchar','vamos_hablar','presentacion','validar_emocion','emocion_nombre','emociones_caras','elegir_emocion','historia_turnos','cuento_interactivo','final_historia','explicar_imagen','frase_corta','completar_frase','buscar_palabra','sinonimos','opuestos','pedir_ayuda','pedir_turno','cuento_corto','personajes','recordar_historia','ensayo_decidir']),
  defaults:{model:'qwen3:0.6b', temperature:0.25, chat_timeout_ms:60000},
};

let activeInteractionMode = 'text';
let currentActionButton = null;
let shortCycleActive = false;
let shortCycleTimer = null;
let shortCycleIndex = 0;
let shortCycleMode = 'turn';
let shortCycleWaitingForNext = false;
const SHORT_ACTION_IDS = [
  'saludo_corto','animal_corto','cantar_saludo','ritmo_palmas','eco_ritxi','instrumento_campana',
  'palmas_lentas','palmas_rapidas','baile_suave','baile_divertido','imitame','chiste','success1'
];


const EMOTIONS = [
  'saludo','alegre','celebracion','animo','paciencia','escucha_activa','pensando','thoughtful1','curioso','sorprendido','calma','empatia','triste','preocupado','asustado','miedo','timido','enfadado_suave','pedir_turno','repetir','asentir','negar','baile','juego','aplauso','esconderse','neutral'
];

const ACTION_GROUPS = [
  { title: 'Emociones oficiales Pollen Robotics', target: 'emotionActionGrid', items: [
    { id:'wake_up', title:'Despertar', icon:'☀️', emotion:'wake_up', text:'', subtitle:'Reset postura + audio oficial', recordedAudio:true },
    { id:'cheerful1', title:'Alegría / cariño', icon:'🥰', emotion:'cheerful1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'enthusiastic1', title:'Entusiasmo', icon:'🤩', emotion:'enthusiastic1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'gasp1', title:'Sorpresa', icon:'😲', emotion:'gasp1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'amazed1', title:'Asombro', icon:'🌟', emotion:'amazed1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'curious1', title:'Curiosidad', icon:'🔎', emotion:'curious1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'attentive1', title:'Atento', icon:'👂', emotion:'attentive1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'calming1', title:'Calma', icon:'🍃', emotion:'calming1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'boredom1', title:'Aburrido / pensar', icon:'🤔', emotion:'boredom1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'confused1', title:'Confundido', icon:'😕', emotion:'confused1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'yes1', title:'Sí / OK', icon:'👍', emotion:'yes1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'no1', title:'No / rechazo', icon:'👎', emotion:'no1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'sad1', title:'Triste', icon:'😭', emotion:'sad1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'anxiety1', title:'Ansiedad / asco', icon:'🤢', emotion:'anxiety1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'angry1', title:'Enojo', icon:'😡', emotion:'angry1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'sleep1', title:'Sueño', icon:'😴', emotion:'sleep1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
  ]},
  { title: 'Bailes y expresividad', target: 'emotionActionGrid', items: [
    { id:'dance1', title:'Baile oficial 1', icon:'🕺', emotion:'dance1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'dance2', title:'Baile oficial 2', icon:'💃', emotion:'dance2', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'dance3', title:'Baile oficial 3', icon:'🤖', emotion:'dance3', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'baile_divertido', title:'Baile divertido', icon:'🎶', emotion:'baile', text:'¡Vamos con un baile divertido para animarnos!', subtitle:'Movimiento dinámico + voz', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'success1', title:'Fiesta', icon:'🪩', emotion:'celebracion', text:'¡Fiesta! Celebramos el esfuerzo y las ganas de participar.', subtitle:'Celebración + voz' },
    { id:'electric1', title:'Energía eléctrica', icon:'⚡', emotion:'electric1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'baile_suave', title:'Baile suave', icon:'🌊', emotion:'calma', text:'Nos movemos suave y tranquilos. Muy bien.', subtitle:'Movimiento suave + voz', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'ritmo_palmas', title:'Ritmo con palmas', icon:'👏', emotion:'aplauso', text:'Escucha el ritmo: una, dos, una, dos. Ahora te toca a ti.', subtitle:'Juego rítmico', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
  ]},
  { title: 'Gestos sociales y comunicación', target: 'emotionActionGrid', items: [
    { id:'hello1', title:'Saludo / hola', icon:'🙋', emotion:'hello1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'saludo_alegre', title:'Saludo alegre', icon:'🖐️', emotion:'hello1', text:'Hola. Me alegra verte. ¿Quieres practicar una conversación?', subtitle:'Gesto social + voz' },
    { id:'come1', title:'Ven conmigo', icon:'🤝', emotion:'come1', text:'Ven conmigo. Vamos paso a paso.', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'pulgar_arriba', title:'Pulgar arriba', icon:'👍', emotion:'yes1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'no_suave', title:'No suave', icon:'👎', emotion:'no1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'corazon', title:'Corazón', icon:'❤️', emotion:'cheerful1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'despedida', title:'Despedida', icon:'👋', emotion:'hello1', text:'Hasta luego. Ha sido un gusto practicar contigo.', subtitle:'Gesto + voz' },
    { id:'pedir_turno', title:'Pedir turno', icon:'✋', emotion:'pedir_turno', text:'Ahora pedimos turno. Puedes decir: por favor, ¿puedo hablar?', subtitle:'Habilidad social', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'escucha_activa', title:'Escucha activa', icon:'👂', emotion:'escucha_activa', text:'Te escucho. Puedes contarme una cosa con una frase corta.', subtitle:'Gesto de escucha', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'gracias', title:'Dar las gracias', icon:'🙏', emotion:'cheerful1', text:'Muchas gracias. Has hablado muy bien y te he entendido.', subtitle:'Cortesía + refuerzo' },
  ]},
  { title: 'Tutor / Terapia y apoyo emocional', target: 'emotionActionGrid', items: [
    { id:'respira', title:'Respira conmigo', icon:'🫁', emotion:'calma', text:'Respira conmigo. Inspiramos despacio… y soltamos el aire. Muy bien.', subtitle:'Relajación guiada' },
    { id:'buen_trabajo', title:'Buen trabajo', icon:'⭐', emotion:'cheerful1', text:'¡Buen trabajo! Lo importante es intentarlo, y tú lo has intentado.', subtitle:'Refuerzo + movimiento' },
    { id:'vamos_hablar', title:'Vamos a hablar', icon:'💬', emotion:'escucha_activa', text:'Vamos a hablar. Te haré una pregunta sencilla y tú puedes responder con calma.', subtitle:'Conversación guiada', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'relajate', title:'Relájate', icon:'🍃', emotion:'calming1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true },
    { id:'repetir_despacio', title:'Repetir despacio', icon:'🔁', emotion:'repetir', text:'Lo repito más despacio. Primero escucho. Después pienso. Luego respondo.', subtitle:'Apoyo comprensión' },
    { id:'no_hay_prisa', title:'No hay prisa', icon:'🧘', emotion:'paciencia', text:'No hay prisa. Podemos hacerlo paso a paso y con calma.', subtitle:'Paciencia + voz' },
    { id:'emocion_nombre', title:'Nombrar emoción', icon:'😊', emotion:'thoughtful1', text:'Vamos a nombrar una emoción. Puedes decir: estoy contento, estoy triste o estoy tranquilo.', subtitle:'Actividad tutor', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'pedir_ayuda', title:'Pedir ayuda', icon:'🆘', emotion:'escucha_activa', text:'Vamos a practicar pedir ayuda. Puedes decir: ¿me ayudas, por favor?', subtitle:'Habilidad comunicativa', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
  ]},
];


const SHORT_ACTIVITY_GROUPS = [
  { title: 'Actividades cortas con turno', target: 'directActionGrid', items: [
    { id:'saludo_corto', title:'Saludo corto', icon:'👋', emotion:'saludo', text:'Hola. Ahora te toca saludar a ti.', subtitle:'Breve + turno', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'si_corto', title:'Decir sí', icon:'👍', emotion:'asentir', text:'Yo digo sí. Ahora tú puedes decir sí.', subtitle:'Respuesta breve', awaitUser:true, requiresInput:true, vocabularyHint:'yes_no' },
    { id:'no_corto', title:'Decir no', icon:'👎', emotion:'negar', text:'Yo digo no. Ahora tú puedes decir no.', subtitle:'Respuesta breve', awaitUser:true, requiresInput:true, vocabularyHint:'yes_no' },
    { id:'turno_corto', title:'Pedir turno', icon:'✋', emotion:'pedir_turno', text:'Por favor, ¿puedo hablar? Ahora inténtalo tú.', subtitle:'Habilidad social', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'ayuda_corta', title:'Pedir ayuda', icon:'🆘', emotion:'escucha_activa', text:'¿Me ayudas, por favor? Ahora dilo tú.', subtitle:'Comunicación', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'despedida_corta', title:'Despedida', icon:'👋', emotion:'saludo', text:'Hasta luego, gracias. Ahora te toca a ti.', subtitle:'Cortesía', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'animal_corto', title:'Animal rápido', icon:'🐶', emotion:'juego', text:'Guau guau. ¿Qué animal es?', subtitle:'Sonido + pregunta', sound:'dog', awaitUser:true, requiresInput:true, vocabularyHint:'animal' },
    { id:'palabra_corta', title:'Palabra rápida', icon:'🔤', emotion:'curioso', text:'Dime una palabra que empiece por ma.', subtitle:'Lenguaje', awaitUser:true, requiresInput:true, vocabularyHint:'short' },
    { id:'calma_corta', title:'Respira corto', icon:'🧘', emotion:'calma', text:'Respiramos una vez. Inspira. Suelta el aire.', subtitle:'Regulación' },
  ]},
];

const DIRECT_ACTION_GROUPS = [
  { title: 'Conversación y habilidades sociales', target: 'directActionGrid', items: [
    { id:'presentacion', title:'Presentación', icon:'🙋', emotion:'saludo', text:'Hola, soy Ritxi. Estoy aquí para conversar, acompañarte y ayudarte a practicar comunicación.', subtitle:'Voz + gesto', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'preguntar_nombre', title:'Preguntar nombre', icon:'👤', emotion:'escucha_activa', text:'¿Cómo te llamas? Di solo tu nombre, despacio y claro. Yo te escucho.', subtitle:'Pregunta social', vocabularyHint:'open_name', minVoiceMs:180, awaitUser:true, requiresInput:true, vocabularyHint:'open_name' },
    { id:'pedir_turno', title:'Pedir turno', icon:'✋', emotion:'pedir_turno', text:'Ahora pedimos turno. Puedes decir: por favor, ¿puedo hablar?', subtitle:'Habilidad social', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'pedir_ayuda', title:'Pedir ayuda', icon:'🆘', emotion:'escucha_activa', text:'Vamos a practicar pedir ayuda. Puedes decir: ¿me ayudas, por favor?', subtitle:'Comunicación funcional', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'escuchar', title:'Escucha activa', icon:'👂', emotion:'escucha_activa', text:'Te escucho. Puedes contarme una cosa con una frase corta.', subtitle:'Acompañamiento', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'despedida_guiada', title:'Despedida guiada', icon:'👋', emotion:'saludo', text:'Ahora practicamos despedirnos. Puedes decir: hasta luego, gracias.', subtitle:'Cortesía social', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
  ]},
  { title: 'Lenguaje: palabras, sinónimos y frases', target: 'directActionGrid', items: [
    { id:'buscar_palabra', title:'Buscar palabra', icon:'🔤', emotion:'curioso', text:'Juego de palabras. Pista: sirve para beber agua. Ahora dime una palabra.', subtitle:'Vocabulario + turno', awaitUser:true, requiresInput:true, vocabularyHint:'short' },
    { id:'sinonimos', title:'Sinónimos', icon:'↔️', emotion:'thoughtful1', text:'Vamos a buscar sinónimos. Si yo digo contento, tú puedes decir alegre o feliz. Ahora dime otro sinónimo de contento.', subtitle:'Lenguaje + turno', awaitUser:true, requiresInput:true, vocabularyHint:'short' },
    { id:'opuestos', title:'Opuestos', icon:'🔁', emotion:'thoughtful1', text:'Jugamos a los opuestos. Si yo digo grande, tú puedes decir pequeño. Ahora dime el opuesto de grande.', subtitle:'Comprensión + turno', awaitUser:true, requiresInput:true, vocabularyHint:'short' },
    { id:'completar_frase', title:'Completar frase', icon:'🧩', emotion:'juego', text:'Completa la frase: Por favor, ¿me puedes...? Ahora complétala tú.', subtitle:'Frase + turno', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'explicar_imagen', title:'Describir imagen', icon:'🖼️', emotion:'curioso', text:'Vamos a describir. Puedes decir una cosa que ves, una acción y una emoción. Ahora te toca.', subtitle:'Narración + turno', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'frase_corta', title:'Frase corta', icon:'💬', emotion:'paciencia', text:'Responde con una frase corta. Por ejemplo: quiero agua, por favor. Ahora di tú una frase corta.', subtitle:'Comunicación + turno', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
  ]},
  { title: 'Cuentos, historias y narración', target: 'directActionGrid', items: [
    { id:'cuento_corto', title:'Cuento corto', icon:'📖', emotion:'curioso', text:'Érase una vez un pequeño robot que aprendió a escuchar con paciencia. Cada día hacía una pregunta amable y esperaba la respuesta.', subtitle:'Narración breve', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'historia_turnos', title:'Historia por turnos', icon:'🧵', emotion:'juego', text:'Hacemos una historia por turnos. Yo empiezo: un robot encontró una llave dorada. Ahora tú dices qué pasó después.', subtitle:'Creatividad y turnos', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'final_historia', title:'Inventar final', icon:'🏁', emotion:'thoughtful1', text:'Voy a contar una historia y tú inventas el final. Un gato perdió su pelota en el parque...', subtitle:'Imaginación', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'personajes', title:'Personajes', icon:'🎭', emotion:'curioso', text:'Elige un personaje: robot, dragón o exploradora. Después hacemos una pequeña historia.', subtitle:'Elección guiada', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'recordar_historia', title:'Recordar historia', icon:'🧠', emotion:'thoughtful1', text:'Te cuento tres datos y luego recordamos uno. El robot era pequeño, azul y muy curioso.', subtitle:'Memoria auditiva', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
  ]},
  { title: 'Juegos de sonido y animales', target: 'directActionGrid', items: [
    { id:'animal_perro', title:'Adivina animal: perro', icon:'🐶', emotion:'juego', text:'Escucha: guau, guau. ¿Qué animal es?', subtitle:'Sonido + pregunta', awaitUser:true, requiresInput:true, vocabularyHint:'animal' },
    { id:'animal_gato', title:'Adivina animal: gato', icon:'🐱', emotion:'juego', text:'Escucha: miau, miau. ¿Qué animal es?', subtitle:'Sonido + pregunta', awaitUser:true, requiresInput:true, vocabularyHint:'animal' },
    { id:'animal_vaca', title:'Adivina animal: vaca', icon:'🐮', emotion:'juego', text:'Escucha: muuu. ¿Qué animal es?', subtitle:'Sonido + pregunta', awaitUser:true, requiresInput:true, vocabularyHint:'animal' },
    { id:'sonido_lluvia', title:'Sonido lluvia', icon:'🌧️', emotion:'calma', text:'Imagina que escuchas lluvia suave. ¿La lluvia te relaja?', subtitle:'Relajación sonora' },
    { id:'instrumento_tambor', title:'Tambor', icon:'🥁', emotion:'juego', text:'Suena un tambor: pum, pum, pum. ¿Puedes repetir el ritmo?', subtitle:'Ritmo y atención', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'instrumento_campana', title:'Campana', icon:'🔔', emotion:'curioso', text:'Suena una campana: din, don. ¿Es un sonido fuerte o suave?', subtitle:'Discriminación auditiva' },
  ]},
  { title: 'Canciones, ritmo y dinámica corporal', target: 'directActionGrid', items: [
    { id:'cantar_saludo', title:'Cantar saludo', icon:'🎤', emotion:'alegre', text:'Cantamos un saludo: hola, hola, qué tal estás. Me alegra verte y contigo hablar.', subtitle:'Canto corto', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'palmas_lentas', title:'Palmas lentas', icon:'👏', emotion:'aplauso', text:'Damos palmas lentas: una… dos… una… dos. Ahora lo intentas tú.', subtitle:'Ritmo lento', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'palmas_rapidas', title:'Palmas rápidas', icon:'⚡', emotion:'celebracion', text:'Ahora palmas rápidas: una, dos, tres. ¡Muy bien!', subtitle:'Ritmo rápido', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'imitame', title:'Imítame', icon:'🪞', emotion:'juego', text:'Juego de imitación. Yo hago un gesto y tú intentas hacerlo también.', subtitle:'Atención e imitación', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'estirar', title:'Estirar suave', icon:'🙆', emotion:'calma', text:'Estiramos suave. Subimos, bajamos y respiramos. Muy bien.', subtitle:'Movimiento guiado' },
  ]},
  { title: 'Refuerzo y regulación emocional', target: 'directActionGrid', items: [
    { id:'reforzar', title:'Reforzar', icon:'⭐', emotion:'animo', text:'¡Muy bien! Has participado, y eso ya es un avance importante.', subtitle:'Refuerzo positivo' },
    { id:'calmar', title:'Calmar', icon:'🍃', emotion:'calma', text:'Si estás nervioso, podemos parar un momento. Respiramos y seguimos despacio.', subtitle:'Regulación' },
    { id:'validar_emocion', title:'Validar emoción', icon:'💛', emotion:'empatia', text:'Está bien sentirse así. Podemos decirlo con palabras y pedir ayuda si la necesitamos.', subtitle:'Apoyo emocional', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'celebrar_intento', title:'Celebrar intento', icon:'🎉', emotion:'celebracion', text:'¡Lo has intentado! Eso es muy importante. Celebramos el esfuerzo.', subtitle:'Motivación' },
    { id:'chiste', title:'Contar chiste', icon:'😄', emotion:'alegre', text:'¿Por qué los robots no cuentan chistes malos? Porque ya bastante tienen con sus errores de programación.', subtitle:'Humor breve' },
  ]},
,
  { title: 'Juegos dinámicos guiados', target: 'directActionGrid', items: [
    { id:'juego_animales', title:'Adivina el animal', icon:'🐾', emotion:'juego', subtitle:'Sonido + pregunta + refuerzo', intro:'escucha el sonido y adivina el animal.', steps:[
      {label:'Preparar', emotion:'curioso', text:'Vamos a jugar a adivinar animales. Escucha con atención.', chat:'Juego: adivina el animal.'},
      {label:'Sonido perro', emotion:'juego', sound:'dog', durationMs:850, text:'¿Qué animal hace guau guau?', chat:'Ritxi reproduce un sonido de animal.'},
      {label:'Refuerzo', emotion:'animo', text:'Muy bien. Puedes responder: es un perro. Ahora probamos otro.', sound:'success', durationMs:650},
      {label:'Sonido gato', emotion:'curioso', sound:'cat', durationMs:850, text:'¿Qué animal hace miau?', chat:'Segundo sonido.'},
      {label:'Cierre', emotion:'celebracion', text:'¡Buen trabajo escuchando y respondiendo!'}
    ]},
    { id:'sinonimos_dinamico', title:'Juego de sinónimos', icon:'↔️', emotion:'thoughtful1', subtitle:'Palabras + turnos', intro:'buscaremos palabras parecidas.', steps:[
      {label:'Inicio', emotion:'saludo', text:'Jugamos a sinónimos. Yo digo una palabra y tú dices otra parecida.', chat:'Actividad de vocabulario: sinónimos.'},
      {label:'Palabra 1', emotion:'thoughtful1', text:'Primera palabra: contento. Una palabra parecida puede ser alegre. ¿Puedes decir otra?'},
      {label:'Espera', emotion:'escucha_activa', text:'Te escucho. Puedes responder despacio.', pauseAfter:1200},
      {label:'Refuerzo', emotion:'animo', text:'Muy bien. Lo importante es intentarlo y usar palabras nuevas.'}
    ]},
    { id:'cuento_interactivo', title:'Cuento por turnos', icon:'📚', emotion:'curioso', subtitle:'Narración + emociones', intro:'crearemos una historia juntos.', steps:[
      {label:'Inicio', emotion:'curioso', text:'Vamos a crear un cuento por turnos. Yo empiezo y tú continúas.', chat:'Actividad: cuento por turnos.'},
      {label:'Escena', emotion:'thoughtful1', text:'Un robot pequeño encontró una estrella brillante en el suelo. La estrella decía: necesito ayuda para volver al cielo.'},
      {label:'Tu turno', emotion:'pedir_turno', text:'Ahora es tu turno. ¿Qué crees que hizo el robot?', pauseAfter:1300},
      {label:'Refuerzo', emotion:'celebracion', text:'¡Qué buena idea! Me gusta cómo has continuado la historia.'}
    ]},
    { id:'respiracion_guiada', title:'Respira conmigo', icon:'🫁', emotion:'calma', subtitle:'Regulación + movimiento suave', intro:'haremos respiración guiada.', steps:[
      {label:'Inicio', emotion:'calma', text:'Vamos a respirar juntos. Lo haremos despacio.'},
      {label:'Inspirar', emotion:'calma', text:'Cogemos aire por la nariz... uno... dos... tres.', pauseAfter:500},
      {label:'Soltar', emotion:'empatia', text:'Soltamos el aire despacio... uno... dos... tres.', pauseAfter:500},
      {label:'Cierre', emotion:'animo', text:'Muy bien. Tu cuerpo puede estar un poco más tranquilo ahora.'}
    ]},
    { id:'ritmo_palmas', title:'Ritmo y palmas', icon:'🥁', emotion:'juego', subtitle:'Sonido + imitación', intro:'repetiremos un ritmo.', steps:[
      {label:'Inicio', emotion:'alegre', text:'Juego de ritmo. Escucha y luego intenta repetir.'},
      {label:'Ritmo', emotion:'juego', sound:'drum', durationMs:1200, text:'Pum, pum, pum. Ahora tú.'},
      {label:'Refuerzo', emotion:'aplauso', text:'¡Muy bien! Has seguido el ritmo.', sound:'success', durationMs:700}
    ]},
    { id:'emociones_caras', title:'Nombrar emociones', icon:'😊', emotion:'empatia', subtitle:'Emoción + comunicación', intro:'practicaremos cómo nombrar emociones.', steps:[
      {label:'Alegría', emotion:'alegre', text:'Esta emoción es alegría. Puedes decir: estoy contento.'},
      {label:'Tristeza', emotion:'triste', text:'Esta emoción es tristeza. Puedes decir: estoy triste y necesito ayuda.'},
      {label:'Calma', emotion:'calma', text:'Esta emoción es calma. Respiramos y seguimos despacio.'},
      {label:'Cierre', emotion:'animo', text:'Nombrar emociones ayuda a comunicarnos mejor. ¡Buen trabajo!'}
    ]}
  ]},
  { title: 'Actividades de comunicación funcional', target: 'directActionGrid', items: [
    { id:'pedir_ayuda_dinamico', title:'Pedir ayuda', icon:'🆘', emotion:'escucha_activa', subtitle:'Modelo + práctica', intro:'practicaremos pedir ayuda.', steps:[
      {label:'Modelo', emotion:'saludo', text:'Primero lo digo yo: ¿me ayudas, por favor?'},
      {label:'Práctica', emotion:'escucha_activa', text:'Ahora prueba tú. Puedes decirlo despacio: ¿me ayudas, por favor?', pauseAfter:1200},
      {label:'Refuerzo', emotion:'animo', text:'Muy bien. Pedir ayuda con respeto es una habilidad muy importante.'}
    ]},
    { id:'respetar_turno_dinamico', title:'Respetar turnos', icon:'✋', emotion:'pedir_turno', subtitle:'Turno + espera', intro:'practicaremos esperar y pedir turno.', steps:[
      {label:'Inicio', emotion:'pedir_turno', text:'Cuando queremos hablar, podemos pedir turno.'},
      {label:'Modelo', emotion:'escucha_activa', text:'Puedes decir: por favor, ¿puedo hablar ahora?'},
      {label:'Espera', emotion:'paciencia', text:'Esperamos un momento. Esperar también comunica respeto.', pauseAfter:1000},
      {label:'Refuerzo', emotion:'celebracion', text:'¡Muy bien esperando tu turno!'}
    ]},
    { id:'elegir_opcion', title:'Elegir opción', icon:'✅', emotion:'curioso', subtitle:'Elección guiada', intro:'practicaremos elegir entre dos opciones.', steps:[
      {label:'Inicio', emotion:'curioso', text:'Vamos a elegir. ¿Prefieres jugar con palabras o escuchar un cuento?'},
      {label:'Escucha', emotion:'escucha_activa', text:'Puedes responder con una frase corta: prefiero el cuento. O: prefiero palabras.', pauseAfter:1400},
      {label:'Refuerzo', emotion:'animo', text:'Perfecto. Elegir y decirlo con palabras es comunicar.'}
    ]}
  ]}
];

function flags() {
  return {
    input_microphone: $('inputMicrophone').checked,
    output_text: $('outputText').checked,
    output_audio: $('outputAudio').checked,
    stt: $('sttEnabled').checked,
    llm: $('llmEnabled').checked,
    tts: $('ttsEnabled').checked,
    robot_motion: $('robotMotion').checked,
    camera_vision: $('cameraVision').checked,
    process_emotions: $('processEmotions').checked,
    streaming: $('streaming').checked,
    synchronize_turn: $('synchronizeTurn').checked,
    debug: $('debug').checked,
    speech_motion: $('speechMotion').checked,
    active_wait: $('activeWait').checked,
    move_talk_generate_text: $('moveTalkGenerateText').checked,
    auto_voice_response: $('autoVoiceResponse').checked,
    auto_send_after_stt: $('autoSendAfterStt').checked,
    echo_guard: $('echoGuard').checked,
    mode_tutor_di: $('modeTutorDi').checked,
    detailed_logs: $('debug').checked,
    save_session: $('saveSession').checked,
    simulation_mode: $('simulationMode').checked,
  };
}


function safeBotText(data, userText=''){
  // Garantiza texto visible y marca si se ha usado fallback local.
  // Si Ollama devuelve solo etiqueta de emoción o texto vacío, se genera una respuesta de seguridad.
  lastSafeBotTextFallback = false;

  let txt = String(data?.text || '').trim();
  txt = txt.replace(/<think>[\s\S]*?<\/think>/gi,'').trim();
  txt = txt.replace(/^\[[A-ZÁÉÍÓÚÑ_]+\]\s*/,'').trim();

  if(txt) return txt;

  lastSafeBotTextFallback = true;
  const t = creativityValue();
  const p = creativityProfile(t);
  const u = String(userText||'').trim().toLowerCase();

  const pick = (precise, balanced, creative) => {
    if(t <= 0.20) return precise;
    if(t <= 0.65) return balanced;
    return creative;
  };

  if(u.includes('naturaleza')){
    return pick(
      'La naturaleza incluye plantas, animales, agua, aire y paisajes.',
      'La naturaleza es el conjunto de seres vivos y paisajes: plantas, animales, ríos, montañas, aire y agua.',
      'La naturaleza es como una casa grande compartida: árboles, animales, ríos, montañas y personas vivimos dentro de ella.'
    );
  }
  if(u.includes('hola')){
    return pick(
      'Hola. Te escucho.',
      'Hola. ¿De qué quieres hablar hoy?',
      'Hola. Me alegra verte. Dime un tema y lo exploramos juntos.'
    );
  }
  if(u.includes('amor')){
    return pick(
      'El amor es cariño y cuidado hacia alguien.',
      'El amor es sentir cariño, cuidar a alguien y querer que esté bien.',
      'El amor es como una luz suave: ayuda a cuidar, acompañar y sentirse cerca de otra persona.'
    );
  }
  if(u.includes('chiste')){
    return pick(
      'Un chiste es una frase corta para hacer reír.',
      'Un chiste es una pequeña broma para hacer reír. Puede ser de animales, robots o situaciones divertidas.',
      'Un chiste es como una sorpresa pequeña: empieza normal y termina con algo que hace reír.'
    );
  }
  if(u.includes('jugar') || u.includes('juego')){
    return pick(
      'Jugar sirve para divertirse y aprender.',
      'Jugar sirve para divertirse, aprender reglas y compartir tiempo con otras personas.',
      'Jugar es como abrir una puerta a la imaginación: pruebas, ríes y aprendes sin darte cuenta.'
    );
  }
  if(u.includes('vida')){
    return pick(
      'La vida incluye aprender, cuidar, descansar y disfrutar.',
      'La vida tiene muchas cosas importantes: aprender, cuidar a otros, descansar, jugar y disfrutar poco a poco.',
      'La vida es como un camino con muchas paradas: aprender, equivocarse, reír, cuidar a otros y descubrir cosas nuevas poco a poco.'
    );
  }
  if(u.includes('perro') && u.includes('gato')){
    return pick(
      'Un perro suele ser sociable y un gato suele ser más independiente.',
      'Un perro suele buscar juego y compañía. Un gato suele ser más tranquilo y curioso.',
      'Un perro se parece a un compañero que te invita a jugar. Un gato se parece a un pequeño explorador tranquilo.'
    );
  }
  if(u.includes('perro')){
    return pick(
      'Un perro es un animal sociable.',
      'Un perro es un animal sociable. Le gusta jugar, aprender órdenes sencillas y acompañar a las personas.',
      'Un perro puede ser como un amigo con mucha energía: corre, juega y se alegra cuando estás cerca.'
    );
  }
  if(u.includes('gato')){
    return pick(
      'Un gato es un animal tranquilo y curioso.',
      'Un gato es un animal tranquilo y curioso. Suele moverse con cuidado y le gusta explorar.',
      'Un gato es como un pequeño explorador silencioso: mira, investiga y busca un sitio cómodo para descansar.'
    );
  }
  if(u.includes('ayuda')){
    return pick(
      'Puedes decir: “Por favor, ¿me puedes ayudar?”',
      'Claro. Podemos practicar cómo pedir ayuda. Puedes decir: “Por favor, ¿me puedes ayudar?”',
      'Imagina que levantas la mano con calma y dices: “Por favor, ¿me puedes ayudar?” Es una frase clara y amable.'
    );
  }
  if(u.includes('contento') || u.includes('feliz')){
    return pick(
      'Sí, estoy contento de practicar contigo.',
      'Sí, estoy contento de practicar contigo. Lo estás haciendo muy bien.',
      'Sí, estoy contento. Es como cuando una luz se enciende porque estamos aprendiendo juntos.'
    );
  }
  if(u.includes('hola')){
    return pick(
      'Hola. Te escucho.',
      'Hola. Estoy contigo y te escucho.',
      'Hola. Me alegra verte. Cuéntame el tema y lo vemos paso a paso.'
    );
  }
  if(u.includes('dime')){
    return pick(
      'Dime el tema y respondo corto.',
      'Claro. Dime el tema y te doy una respuesta corta.',
      'Claro. Dame una palabra y la convertimos en una pequeña idea fácil de entender.'
    );
  }

  const fallbacks = t <= 0.20
    ? ['Entendido. Dime una palabra clave.', 'Vale. Respondo corto si me das un tema.']
    : t <= 0.65
      ? ['Entendido. ¿Quieres que lo practiquemos con un ejemplo?', 'Puedo ayudarte paso a paso. Dime una palabra clave.']
      : ['Podemos convertir esa idea en un ejemplo sencillo. Dime una palabra y empezamos.', 'Vamos a hacerlo como un pequeño juego: dame una palabra y yo la explico.'];
  return fallbackFromConversationPolicy(userText);
}

function chatFlagsForBackend(){
  const f = flags();

  // Los modos superiores controlan SOLO el chat conversacional.
  // Las fichas/actividades de clic directo usan su propio runtime y no dependen de esto.
  if(activeInteractionMode === 'textRobot' || activeInteractionMode === 'full'){
    return {
      ...f,
      robot_motion:false,
      speech_motion:false,
      move_talk_generate_text:false,
      synchronize_turn:false,
    };
  }

  return f;
}

async function api(path, options = {}) {
  const isForm = options.body instanceof FormData;
  let res;
  try{
    res = await fetch(path, {
      headers: isForm ? {} : { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options
    });
  }catch(err){
    throw new Error(`No se pudo contactar con FastAPI al abrir ${path}: ${String(err)}`);
  }

  const text = await res.text();
  let payload = null;
  try{ payload = text ? JSON.parse(text) : null; }catch(_){ payload = text; }

  if(!res.ok){
    const detail = payload && payload.detail ? payload.detail : (typeof payload === 'string' ? payload : res.statusText);
    throw new Error(`HTTP ${res.status} ${detail}`);
  }
  return payload;
}

function nowTime() { return new Date().toLocaleTimeString('es-ES', { hour12:false }) + '.' + String(new Date().getMilliseconds()).padStart(3,'0'); }
function logClient(level, origin, message, data = {}) {
  const evt = { level, origin, message, data, time: nowTime(), ts: Date.now() };
  logEvents.unshift(evt);
  if (logEvents.length > 600) logEvents = logEvents.slice(0, 600);
  api('/api/log/client', { method:'POST', body: JSON.stringify({ level: level === 'warn' ? 'warning' : level, message: `[${origin}] ${message}`, data }) }).catch(()=>{});
}
function appendLog(message, data=null, level='info') { logClient(level, data?.origin || 'ui', message, data || {}); }
function renderLogs(){ /* v5.9.86: registros en pantalla eliminados; logs siguen enviándose a backend. */ }
function escapeHtml(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function setChip(id, title, sub, mode='') { const el=$(id); if(!el)return; el.className=`chip ${mode}`; el.innerHTML=`<b>${title}</b><small>${sub}</small>`; }
function setMicStatus(text){ const el=$('micStatus'); if(el) el.textContent=text; }
function selectedMicMode(){ return $('micMode')?.value || 'server_whisper'; }


function ensureRecommendedModelSelected(){
  const sel = $('modelSelect');
  if(!sel) return;
  // qwen3:0.6b no debe quedar como selección inicial en chat libre.
  if(!sel.dataset.userTouched && (!sel.value || sel.value === 'qwen3:0.6b')){
    sel.value = 'gemma3:1b';
    logClient?.('info','ollama','Modelo inicial corregido a gemma3:1b para conversación estable');
  }
}

function effectiveModelForChat(model, activeContextForTurn=null){
  const m = String(model || selectedModelName());
  // qwen se mantiene disponible como prueba experimental, pero para chat libre
  // se enruta a gemma3:1b para que responda con IA real y no con fallback genérico.
  if(m.includes('qwen3:0.6b') && !activeContextForTurn){
    logClient?.('warn','ollama','qwen3:0.6b redirigido a gemma3:1b en chat libre',{selected:m,effective:'gemma3:1b'});
    setMicStatus?.('qwen3:0.6b es experimental. Para chat libre se usa gemma3:1b.');
    return 'gemma3:1b';
  }
  return m;
}

function selectedModelName(){
  return $('modelSelect')?.value || 'gemma3:1b';
}

function modelSpeedInfo(model){
  const m = String(model || '');
  if(m.includes('qwen3:0.6b')) return {label:'Experimental', level:'warn', note:'muy rápido pero inestable para conversación'};
  if(m.includes('gemma3:1b')) return {label:'Rápido recomendado', level:'fast', note:'equilibrado para conversación'};
  if(m.includes('llama3.2:1b')) return {label:'Rápido', level:'medium', note:'llama 1B'};
  if(m.includes('llama3.2:3b')) return {label:'Lento / calidad', level:'slow', note:'3B puede tardar 25-40 s en CPU'};
  return {label:'Velocidad desconocida', level:'unknown', note:'modelo personalizado'};
}

function updateModelPills(model=null){
  const m = model || selectedModelName();
  const speed = modelSpeedInfo(m);
  if($('modelLoadedPill')) $('modelLoadedPill').textContent = `Modelo: ${m}`;
  if($('modelLoadedPillBottom')) $('modelLoadedPillBottom').textContent = `Modelo: ${m}`;
  if($('modelSpeedPill')){
    setTextIfPresent('modelSpeedPill', speed.label);
    $('modelSpeedPill').className = `model-speed-pill ${speed.level}`;
    $('modelSpeedPill').title = speed.note;
  }
  const hint=$('interactionModeHint');
  if(hint && m.includes('llama3.2:3b')){
    hint.textContent='Modelo seleccionado lento: llama3.2:3b. El modo no cambia el modelo automáticamente.';
  }
}

// Desbloqueo ligero del estado de turno para que un envío de texto no quede bloqueado.
function forceUnlockTurnState(reason='turn-unlock'){
  // Desbloqueo ligero usado por el envío de texto.
  // No debe fallar nunca: si falla aquí, el botón ➤ parece no hacer nada.
  try{
    realtimeSending=false;
    persistentTranscribing=false;
    recognizing=false;
    serverSttActive=false;
    activityAwaitingUser=false;
    activityAutoListenAfterBot=false;
    autoListenAfterBot=false;
    shortCycleWaitingForNext=false;
    if(micRetryTimer){ clearTimeout(micRetryTimer); micRetryTimer=null; }
    try{ clearMicSilenceTimer(); }catch(_){}
    try{ if(recognition) recognition.abort(); }catch(_){}
    enableTextInputAlways(`forceUnlockTurnState-${reason}`);
    updateMicToggleUi();
    logClient?.('debug','ui',`Turno desbloqueado: ${reason}`);
  }catch(err){
    console.error('[Ritxi] forceUnlockTurnState falló', err);
  }
}

function forceUiUnblock(reason='manual'){
  realtimeSending=false;
  persistentTranscribing=false;
  recognizing=false;
  serverSttActive=false;
  activityAwaitingUser=false;
  activityAutoListenAfterBot=false;
  autoListenAfterBot=false;
  if(micRetryTimer){ clearTimeout(micRetryTimer); micRetryTimer=null; }
  try{ stopBrowserTts(); }catch(_){}
  try{ stopEffectAudio(); }catch(_){}
  $('currentState').textContent='Listo para conversar';
  $('currentSubState').textContent='Desbloqueado manualmente';
  setMicStatus('Interfaz desbloqueada. Puedes escribir, activar micro o lanzar otra actividad.');
  setExecuting('—','Desbloqueado');
  logClient('warn','ui',`Desbloqueo manual/automático: ${reason}`);
  updateMicToggleUi();
}

function micSilenceMs(){ return Math.max(700, Math.min(5000, Number($('silenceSendMs')?.value || 1400))); }
function serverMaxRecordMs(){ return Math.max(1500, Math.min(20000, Number($('serverRecordMaxMs')?.value || 3500))); }
function serverVadThreshold(){ return Math.max(0.003, Math.min(0.12, Number($('serverVadThreshold')?.value || 0.024))); }
function normalizeTranscript(text){ return (text || '').replace(/\s+/g,' ').trim(); }

function addChat(role, text, meta='') {
  const box=$('chatHistory');
  const node=document.createElement('div');
  node.className=`msg ${role==='user'?'user':'bot'}`;
  node.innerHTML=`<div class="meta"><b>${role==='user'?'Tú':'Ritxi'}</b><span>${new Date().toLocaleTimeString('es-ES',{hour:'2-digit',minute:'2-digit'})}</span>${meta?`<span>${meta}</span>`:''}</div><div>${escapeHtml(text).replace(/\n/g,'<br>')}</div>`;
  box.appendChild(node); box.scrollTop=box.scrollHeight;
}

function ensureFreshSessionId(){
  const el=$('sessionId');
  if(!el) return;
  const current=(el.value||'').trim();
  if(!current || current==='demo'){
    el.value = `web-${Date.now()}-${Math.floor(Math.random()*10000)}`;
    logClient?.('info','session',`Nueva sesión conversacional: ${el.value}`);
  }
}

function initChat(){
  const box=$('chatHistory');
  if(box && !box.dataset.initialized){
    addChat('bot','¡Hola! Soy Ritxi 🤖 Escribe el tema del que quieres hablar.');
    box.dataset.initialized='1';
  }
}

function updateMicDiag(extra={}){
  const el=$('micDiag'); if(!el)return;
  el.textContent=JSON.stringify({realtimeEnabled,recognizing,serverSttActive,browserSpeaking,lastMicError,micErrorStreak,mode:selectedMicMode(),pending_final:pendingMicText,pending_interim:pendingMicInterim,can_listen:canListenNow(),backend_turn_state:lastStatus?.turn_state,backend_micro_enabled:lastStatus?.echo_guard?.microphone_enabled,backend_tts_speaking:lastStatus?.tts?.speaking,...extra},null,2);
}
function canListenNow(status=lastStatus){ if(!status)return false; const f=flags(); if(!f.input_microphone||!f.stt)return false; if(browserSpeaking)return false; if(f.echo_guard && !status.echo_guard.microphone_enabled)return false; if(status.tts.speaking)return false; if(status.turn_state!=='idle')return false; return true; }
async function refreshStatus(){
  try{
    const status=await api('/api/architecture/status'); lastStatus=status;
    const robot=status.robot.connected?'En línea':'Sin daemon';
    setChip('chipRobot','Robot',robot,status.robot.connected?'':'');
    setChip('chipMic','Micrófono',flags().input_microphone?'Activo':'OFF');
    setChip('chipStt','STT',recognizing||serverSttActive?'Escuchando':(status.stt.available?'OK':'No disponible'),'blue');
    setChip('chipOllama','Ollama',status.llm.available?selectedModelName():'Fallback','purple'); updateModelPills(status.llm?.model || selectedModelName());
    setChip('chipTts','TTS',browserSpeaking?'Hablando':status.tts.provider,'purple');
    setChip('chipQueue','Cola',String(status.scheduler.queue_size),'blue');
    setTextIfPresent('currentState', status.turn_state === 'idle' ? 'Listo para conversar' : status.turn_state);
    setTextIfPresent('currentSubState', canListenNow(status) ? 'Esperando tu mensaje' : 'Procesando / protegido');
    setTextIfPresent('latencyPill', status.last_latencies?.llm_total_ms ? `${Math.round(status.last_latencies.llm_total_ms)} ms` : '— ms');
    if($('robotDot')) $('robotDot').textContent = status.robot.connected ? '● En línea' : '● Sin conexión';
    if($('robotSubtitle')) $('robotSubtitle').textContent = status.robot.connected ? `Conectado a ${status.robot.host}` : (status.robot.last_error || 'Daemon no conectado');
    if($('robotTopDot')){
      $('robotTopDot').textContent = status.robot.connected ? '● En línea' : '● Sin conexión';
      $('robotTopDot').style.color = status.robot.connected ? '#30d158' : '#ff453a';
    }
    if($('batteryTop')) $('batteryTop').textContent = status.robot.connected ? '78%' : 'Sim';
    if($('tempTop')) $('tempTop').textContent = status.robot.connected ? '34 °C' : '—';
    if($('wifiTop')) $('wifiTop').textContent = status.robot.connected ? 'Excelente' : 'Sin daemon';
    setTextIfPresent('statusCompact', JSON.stringify({robot:status.robot,llm:status.llm,stt:status.stt,tts:status.tts,cola:status.scheduler,echo_guard:status.echo_guard,warnings:status.warnings},null,2));
    setTextIfPresent('logStatus', `Log: ${status.logs?.session_log_file || ''}`);
    idleEnabled=status.scheduler.idle_enabled;
    updateMicDiag();
  }catch(err){ logClient('error','status',`No se pudo refrescar estado: ${String(err)}`); }
}



function renderDaemonStatus(data){
  const dot=$('daemonDot');
  const consoleEl=$('daemonConsole');
  if(dot){
    dot.textContent = data.running ? '● Puerto 8000 OK' : '● Sin daemon';
    dot.classList.toggle('on', !!data.running);
    dot.classList.toggle('off', !data.running);
  }
  if(consoleEl){
    const lines = data.last_lines || [];
    consoleEl.textContent = lines.length ? lines.join('\n') : (data.message || 'Sin salida todavía.');
    consoleEl.scrollTop = consoleEl.scrollHeight;
  }
}
async function refreshDaemon(){
  try{ const data=await api('/api/daemon/status?limit=80'); renderDaemonStatus(data); return data; }
  catch(err){ logClient('warn','daemon',`No se pudo leer estado del daemon: ${String(err)}`); }
}
async function startDaemonFromPanel(){
  try{ const data=await api('/api/daemon/start',{method:'POST',body:'{}'}); renderDaemonStatus(data); logClient(data.running?'info':'warn','daemon',data.running?'Daemon disponible en puerto 8000':'Daemon lanzado, esperando puerto 8000',data); setTimeout(refreshDaemon,2500); }
  catch(err){ logClient('error','daemon',`No se pudo iniciar daemon: ${String(err)}`); }
}
async function stopDaemonFromPanel(){
  try{ const data=await api('/api/daemon/stop',{method:'POST',body:'{}'}); renderDaemonStatus(data); logClient('warn','daemon','Solicitud de parada del daemon lanzado por Ritxi',data); setTimeout(refreshDaemon,1500); }
  catch(err){ logClient('error','daemon',`No se pudo parar daemon: ${String(err)}`); }
}


async function ensureMicrophoneReady({ask=true, reason='micro'}={}){
  if(micPermissionGranted && flags().input_microphone && flags().stt && $('inputMicrophone')?.checked && $('sttEnabled')?.checked){
    return true;
  }
  if(!flags().input_microphone || !$('inputMicrophone').checked){
    if(!ask || !confirm('Esta actividad necesita micrófono. ¿Quieres activar el micrófono?')) {
      setMicStatus('Micro no activado. Puedes escribir la respuesta y pulsar ➤.');
      return false;
    }
    $('inputMicrophone').checked = true;
  }
  if(!flags().stt || !$('sttEnabled').checked){
    if(!ask || !confirm('Para hablar también hace falta STT. ¿Quieres activar STT?')) {
      setMicStatus('STT no activado. Puedes escribir la respuesta y pulsar ➤.');
      return false;
    }
    $('sttEnabled').checked = true;
  }
  if(!navigator.mediaDevices?.getUserMedia){
    setMicStatus('El navegador no permite abrir el micro. Escribe en el chat y pulsa ➤.');
    logClient('error','mic','getUserMedia no disponible',{reason});
    return false;
  }
  try{
    setMicStatus('Pidiendo permiso de micrófono…');
    const stream = await navigator.mediaDevices.getUserMedia({
      audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true,channelCount:1}
    });
    stream.getTracks().forEach(t=>t.stop());
    micPermissionGranted = true;
    micPermissionAskedThisSession = true;
    logClient('info','mic','Permiso de micrófono concedido',{reason});
    setMicStatus('Micro autorizado. Puedes hablar cuando Ritxi te dé turno.');
    return true;
  }catch(err){
    micPermissionGranted = false;
    micPermissionAskedThisSession = true;
    setMicStatus('No se pudo activar el micro. Revisa permisos del navegador o escribe y pulsa ➤.');
    logClient('error','mic',`Permiso de micro denegado/error: ${String(err)}`,{reason});
    return false;
  }
}


function persistentMicStatus(extra=''){
  const suffix = extra ? ` ${extra}` : '';
  if(micAlwaysOn && persistentStream && !persistentMicPaused && !browserSpeaking && !realtimeSending){
    setMicStatus(`Micro siempre activo: habla cuando quieras.${suffix}`);
  } else if(micAlwaysOn && persistentMicPaused){
    setMicStatus(`Micro preparado, pausado: ${persistentMicPauseReason || 'Ritxi habla'}.${suffix}`);
  }
}

function pauseAlwaysOnMic(reason='pausa'){
  persistentMicPaused = true;
  persistentMicPauseReason = reason;
  persistentRecording = false;
  persistentVoiceStarted = false;
  persistentChunks = [];
  persistentMicStatus();
}

function resumeAlwaysOnMic(reason='reanudar'){
  if(!micAlwaysOn) return;
  persistentMicPaused = false;
  persistentMicPauseReason = '';
  persistentMicStatus(`(${reason})`);
}

async function stopAlwaysOnMic(reason='manual'){
  micAlwaysOn = false;
  persistentMicPaused = false;
  persistentMicPauseReason = '';
  persistentRecording = false;
  persistentVoiceStarted = false;
  persistentTranscribing = false;
  persistentChunks = [];
  try{ if(persistentProcessor) persistentProcessor.disconnect(); }catch(_){}
  try{ if(persistentSource) persistentSource.disconnect(); }catch(_){}
  try{ if(persistentAudioContext) await persistentAudioContext.close(); }catch(_){}
  try{ if(persistentStream) persistentStream.getTracks().forEach(t=>t.stop()); }catch(_){}
  persistentProcessor = null;
  persistentSource = null;
  persistentAudioContext = null;
  persistentStream = null;
  updateMicToggleUi();
  setMicStatus(manualMicStopLock ? 'Micro desconectado por el usuario.' : 'Micro desconectado. Pulsa Activar micro para activarlo.');
  logClient('info','mic',`Micro continuo desconectado: ${reason}`);
}

function resetPersistentRecording(){
  persistentRecording = false;
  persistentVoiceStarted = false;
  persistentChunks = [];
  persistentFirstVoiceAt = 0;
  persistentLastVoiceAt = 0;
  persistentRecordingStartMs = 0;
  persistentMaxRms = 0;
}

// Cierra una frase detectada por VAD, genera WAV y lo manda al STT local.
// Cierra una frase detectada por VAD, crea WAV y lo manda a transcripción.
async function finishPersistentUtterance(reason='silence'){
  if(persistentTranscribing) return;
  persistentTranscribing = true;
  const chunks = persistentChunks.slice();
  const inputRate = persistentAudioContext?.sampleRate || 48000;
  const maxRms = persistentMaxRms;
  resetPersistentRecording();

  if(!chunks.length){
    persistentTranscribing = false;
    resumeAlwaysOnMic('sin audio');
    return;
  }

  const samples = flattenFloat32(chunks);
  if(!samples.length){
    persistentTranscribing = false;
    resumeAlwaysOnMic('sin muestras');
    return;
  }

  const configuredThreshold = serverVadThreshold();
  const minRmsFactor = isOpenVocabularyHint(currentVocabularyHint) ? 0.80 : 1.15;
  const minSamples = isOpenVocabularyHint(currentVocabularyHint) ? 900 : 1600;
  if(maxRms < configuredThreshold * minRmsFactor || samples.length < minSamples){
    logClient('warn','stt','Audio descartado antes de Whisper por señal baja',{reason,maxRms:Number(maxRms.toFixed(5)),threshold:configuredThreshold,samples:samples.length,vocabulary_hint:currentVocabularyHint,minRmsFactor,minSamples});
    setMicStatus(currentVocabularyHint === 'open_name' ? 'He oído algo, pero no he captado el nombre. Repítelo despacio o escríbelo.' : (isOpenVocabularyHint(currentVocabularyHint) ? 'He oído algo, pero no he captado la frase. Repítelo despacio o escríbelo.' : 'He oído ruido, pero no voz clara. Repite cerca del micro o escribe y pulsa ➤.'));
    persistentTranscribing = false;
    resumeAlwaysOnMic('señal baja');
    return;
  }

  setMicStatus('Transcribiendo lo que has dicho…');
  logClient('info','stt','Micro continuo finaliza frase',{reason,samples:samples.length,maxRms:Number(maxRms.toFixed(5)),hint:currentVocabularyHint});

  try{
    const language = ($('micLang').value || 'es-ES').split('-')[0] || 'es';
    const wav = encodeWavFromFloat32(downsampleFloat32(samples,inputRate,16000),16000);
    const data = await transcribeBlobWithServer(wav, language);
    const text = normalizeTranscript(data.text || '');
    if(rejectIfRepeatedTranscript(text,'always-on-mic')){
      persistentTranscribing = false;
      resumeAlwaysOnMic('repetición descartada');
      return;
    }
    pendingMicText = text;
    $('message').value = text;
    logClient('info','stt',`Transcripción continua: “${text || '(vacía)'}”`,{latency_ms:data.latency_ms,metadata:data.metadata,vocabulary_hint:currentVocabularyHint});

    if(!text){
      setMicStatus(currentVocabularyHint === 'open_name' ? 'No he captado el nombre. Dilo de nuevo despacio o escríbelo y pulsa ➤.' : (isOpenVocabularyHint(currentVocabularyHint) ? 'No he captado la frase. Repítela despacio o escríbela y pulsa ➤.' : 'No he entendido. Vuelve a hablar o escribe y pulsa ➤.'));
      persistentTranscribing = false;
      resumeAlwaysOnMic('no entendido');
      return;
    }

    setMicStatus(`He entendido: “${text}”. Enviando…`);
    persistentTranscribing = false;
    await sendTurn({source:'always-on-mic'});
  }catch(err){
    persistentTranscribing = false;
    setMicStatus(`Error de micro/STT: ${String(err)}. Puedes escribir y pulsar ➤.`);
    logClient('error','stt',`Error en micro continuo: ${String(err)}`);
    resumeAlwaysOnMic('error stt');
  }
}

function handlePersistentAudioProcess(ev){
  if(!micAlwaysOn || persistentMicPaused || browserSpeaking || realtimeSending || persistentTranscribing || manualMicStopLock) return;
  const input = ev.inputBuffer.getChannelData(0);
  const copy = new Float32Array(input.length);
  copy.set(input);

  let sum=0;
  for(let i=0;i<copy.length;i++) sum += copy[i]*copy[i];
  const rms = Math.sqrt(sum / copy.length);
  const configuredThreshold = serverVadThreshold();
  const effectiveThreshold = Math.max(configuredThreshold, persistentNoiseFloor * 2.6);
  const now = performance.now();

  if(!persistentRecording){
    // Actualizar ruido de fondo lentamente si no hay voz.
    if(rms < configuredThreshold * 0.80){
      persistentNoiseFloor = Math.max(0.004, Math.min(0.04, persistentNoiseFloor * 0.96 + rms * 0.04));
      if(now - persistentLastIdleStatusAt > 2500){
        persistentLastIdleStatusAt = now;
        updateMicDiag({mode:'always_on_idle', rms:Number(rms.toFixed(5)), noise_floor:Number(persistentNoiseFloor.toFixed(5)), threshold:Number(effectiveThreshold.toFixed(5))});
      }
      return;
    }

    if(rms >= effectiveThreshold){
      persistentRecording = true;
      persistentVoiceStarted = true;
      persistentChunks = [copy];
      persistentFirstVoiceAt = now;
      persistentLastVoiceAt = now;
      persistentRecordingStartMs = now;
      persistentMaxRms = rms;
      setMicStatus(`Micro activo: voz detectada nivel=${rms.toFixed(3)}`);
      logClient('info','stt','Voz detectada por micro continuo',{rms:Number(rms.toFixed(5)),threshold:Number(effectiveThreshold.toFixed(5)),configuredThreshold,currentVocabularyHint,noiseFloor:Number(persistentNoiseFloor.toFixed(5))});
    }
    return;
  }

  persistentChunks.push(copy);
  persistentMaxRms = Math.max(persistentMaxRms, rms);
  if(rms >= effectiveThreshold) persistentLastVoiceAt = now;

  const voiceMs = now - persistentFirstVoiceAt;
  const silence = now - persistentLastVoiceAt;
  const elapsed = now - persistentRecordingStartMs;
  const minVoiceMs = 260;
  const silenceMs = micSilenceMs();
  const maxMs = serverMaxRecordMs();

  if(voiceMs >= minVoiceMs && silence >= silenceMs){
    void finishPersistentUtterance('silence');
  } else if(elapsed >= maxMs){
    void finishPersistentUtterance('max-duration');
  } else {
    setMicStatus(`Micro escuchando… nivel=${rms.toFixed(3)} silencio=${Math.round(silence)}ms`);
  }
}

// Abre el micrófono persistente del navegador y mantiene escucha continua controlada.
// Abre escucha continua del navegador para capturar voz y enviar al STT local.
async function startAlwaysOnMic({reason='manual', autoSend=true, force=false}={}){
  if(manualMicStopLock && !force){
    updateMicToggleUi();
    setMicStatus('Micro detenido manualmente. Pulsa Activar micro o inicia una actividad con respuesta por voz para reactivarlo.');
    logClient('debug','mic',`Apertura de micro ignorada por bloqueo manual: ${reason}`);
    return false;
  }
  const ok = await ensureMicrophoneReady({ask:true, reason});
  if(!ok) return false;

  micAlwaysOn = true;
  realtimeEnabled = true;
  autoListenAfterBot = true;
  updateMicToggleUi();

  if(persistentStream && persistentAudioContext && persistentProcessor){
    try{ await persistentAudioContext.resume(); }catch(_){}
    resumeAlwaysOnMic(reason);
    setMicStatus('Micro continuo activo: habla cuando quieras.');
    return true;
  }

  if(!navigator.mediaDevices?.getUserMedia){
    setMicStatus('El navegador no permite abrir el micro. Puedes escribir y pulsar ➤.');
    return false;
  }

  try{
    setMicStatus('Solicitando micro al navegador…');
    persistentStream = await navigator.mediaDevices.getUserMedia({
      audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true,channelCount:1}
    });

    const AC = window.AudioContext || window.webkitAudioContext;
    persistentAudioContext = new AC();
    try{ await persistentAudioContext.resume(); }catch(_){}

    persistentSource = persistentAudioContext.createMediaStreamSource(persistentStream);
    persistentProcessor = persistentAudioContext.createScriptProcessor(2048,1,1);
    persistentProcessor.onaudioprocess = handlePersistentAudioProcess;
    persistentSource.connect(persistentProcessor);
    persistentProcessor.connect(persistentAudioContext.destination);

    resetPersistentRecording();
    persistentMicPaused = false;
    persistentMicPauseReason = '';
    setMicStatus('Micro continuo activo: habla cuando quieras.');
    logClient('info','mic','Micro continuo iniciado',{
      reason,
      threshold:serverVadThreshold(),
      silenceMs:micSilenceMs(),
      maxMs:serverMaxRecordMs(),
      audioContextState:persistentAudioContext.state
    });
    return true;
  }catch(err){
    await stopAlwaysOnMic('error apertura');
    setMicStatus(`No se pudo abrir micro: ${String(err)}. Revisa permisos del navegador o escribe y pulsa ➤.`);
    logClient('error','mic',`No se pudo abrir micro continuo: ${String(err)}`);
    return false;
  }
}

function stopBrowserMic(){ 
  manualStopRequested=true; 
  clearMicSilenceTimer(); 
  stopServerSttMic(); 
  try{ if(recognition&&recognizing) recognition.abort(); }catch(_){} 
  recognizing=false; 
  // Parada real del micro continuo.
  if(micAlwaysOn || persistentStream) void stopAlwaysOnMic('stopBrowserMic');
  setMicStatus('Micro PC parado.'); 
  updateMicDiag({stopped:true}); 
}
function clearMicSilenceTimer(){ if(micSilenceTimer) clearTimeout(micSilenceTimer); micSilenceTimer=null; }
function scheduleRealtimeLoop(delay=700){ if(realtimeLoopTimer) clearTimeout(realtimeLoopTimer); if(!realtimeEnabled)return; realtimeLoopTimer=setTimeout(realtimeLoop,delay); }
async function realtimeLoop(){ if(!realtimeEnabled||recognizing||serverSttActive||realtimeSending)return; await refreshStatus(); if(!canListenNow()){ setMicStatus(`Tiempo real esperando: Ritxi termina de hablar o echo guard está activo. estado=${lastStatus?.turn_state}, speaking=${browserSpeaking}, micro=${lastStatus?.echo_guard?.microphone_enabled}`); scheduleRealtimeLoop(500); return; } await startMic({autoSend:flags().auto_send_after_stt, askPermission:false, reason:'realtime-loop'}); }
async function setRealtime(enabled){ 
  if(enabled){
    await startConversationMicNow({autoSend:flags().auto_send_after_stt, reason:'boton-conversacion-micro'});
    logClient('info','mic','Conversación/micro activada de forma directa',{flags:flags(), activity_runtime:activityRuntimeMode(item),mic_mode:selectedMicMode()});
    return;
  }
  await stopMicByUser('setRealtime-off');
}

async function startMic({autoSend=true, askPermission=true, reason='manual'}={}){ 
  return await startAlwaysOnMic({reason, autoSend});
}
function speechRecognitionFactory({continuous=false}={}){ const C=window.SpeechRecognition||window.webkitSpeechRecognition; if(!C)return null; const rec=new C(); rec.lang=$('micLang')?.value||'es-ES'; rec.interimResults=true; rec.continuous=continuous; rec.maxAlternatives=3; return rec; }
function startBrowserMic({autoSend=false,continuous=false}={}){
  if(!flags().input_microphone||!flags().stt){ setMicStatus('Micro o STT desactivado por checkbox.'); return; }
  if(recognizing)return; recognition=speechRecognitionFactory({continuous}); if(!recognition){ setMicStatus('Web Speech API no disponible. Usa STT local Whisper.'); logClient('error','stt','Web Speech API no disponible'); return; }
  let finalText='', sent=false; manualStopRequested=false; pendingMicText=''; pendingMicInterim='';
  const submit=async(reason='final')=>{ const text=normalizeTranscript(finalText||pendingMicText); if(sent||!text)return; sent=true; manualStopRequested=true; try{recognition.abort()}catch(_){} recognizing=false; $('message').value=text; logClient('info','stt',`Texto reconocido: “${text}”`,{reason}); if(autoSend) await sendTurn({source:'web-speech'}); };
  recognition.onstart=()=>{ recognizing=true; lastMicError=null; setMicStatus('Web Speech escuchando…'); logClient('info','mic','Escucha Web Speech activada'); };
  recognition.onresult=(ev)=>{ let interim='', finalAdded=''; for(let i=ev.resultIndex;i<ev.results.length;i++){ const t=ev.results[i][0].transcript||''; if(ev.results[i].isFinal) finalAdded+=' '+t; else interim+=' '+t; } if(finalAdded.trim()) finalText=normalizeTranscript(`${finalText} ${finalAdded}`); pendingMicText=finalText; pendingMicInterim=normalizeTranscript(interim); $('message').value=normalizeTranscript(`${pendingMicText} ${pendingMicInterim}`); setMicStatus(pendingMicInterim?`Escuchando… ${pendingMicInterim}`:`Texto detectado: ${pendingMicText}`); if(finalAdded.trim()&&selectedMicMode()==='short') submit('short-final'); else if(finalAdded.trim()&&autoSend){ clearMicSilenceTimer(); micSilenceTimer=setTimeout(()=>submit('silence'),micSilenceMs()); } };
  recognition.onerror=(ev)=>{ lastMicError=ev.error; if(ev.error==='aborted'&&manualStopRequested){ logClient('debug','mic','Reconocimiento abortado de forma controlada'); return; } micErrorStreak++; logClient(ev.error==='not-allowed'?'error':'warn','mic',`Error micro PC: ${ev.error}`); setMicStatus(`Error micro PC: ${ev.error}`); };
  recognition.onend=async()=>{ recognizing=false; clearMicSilenceTimer(); const text=normalizeTranscript(finalText||pendingMicText); if(autoSend&&text&&!sent) await submit('onend'); else if(realtimeEnabled&&!manualStopRequested) scheduleRealtimeLoop(1200); };
  try{ recognition.start(); }catch(err){ recognizing=false; setMicStatus(`No se pudo iniciar micro: ${String(err)}`); logClient('error','mic',`No se pudo iniciar Web Speech: ${String(err)}`); }
}

function flattenFloat32(chunks){ const total=chunks.reduce((a,b)=>a+b.length,0); const out=new Float32Array(total); let off=0; chunks.forEach(c=>{out.set(c,off);off+=c.length}); return out; }
function downsampleFloat32(buffer,inputRate,outputRate=16000){ if(inputRate===outputRate)return buffer; const ratio=inputRate/outputRate; const len=Math.round(buffer.length/ratio); const result=new Float32Array(len); let ob=0; for(let or=0;or<len;or++){ const next=Math.round((or+1)*ratio); let acc=0,cnt=0; for(let i=ob;i<next&&i<buffer.length;i++){acc+=buffer[i];cnt++;} result[or]=cnt?acc/cnt:0; ob=next;} return result; }
function encodeWavFromFloat32(samples,sampleRate=16000){ const buffer=new ArrayBuffer(44+samples.length*2); const view=new DataView(buffer); const ws=(o,t)=>{for(let i=0;i<t.length;i++)view.setUint8(o+i,t.charCodeAt(i));}; ws(0,'RIFF'); view.setUint32(4,36+samples.length*2,true); ws(8,'WAVE'); ws(12,'fmt '); view.setUint32(16,16,true); view.setUint16(20,1,true); view.setUint16(22,1,true); view.setUint32(24,sampleRate,true); view.setUint32(28,sampleRate*2,true); view.setUint16(32,2,true); view.setUint16(34,16,true); ws(36,'data'); view.setUint32(40,samples.length*2,true); let off=44; for(let i=0;i<samples.length;i++,off+=2){ const s=Math.max(-1,Math.min(1,samples[i])); view.setInt16(off,s<0?s*0x8000:s*0x7fff,true);} return new Blob([view],{type:'audio/wav'}); }

function transcriptTokens(text){
  return normalizeTranscript(text || '')
    .toLowerCase()
    .replace(/[¿?¡!.,;:()[\]"']/g,' ')
    .replace(/\s+/g,' ')
    .trim()
    .split(' ')
    .filter(Boolean);
}
function isLikelyRepeatedTranscript(text){
  const tokens = transcriptTokens(text);
  if(tokens.length < 12) return false;
  const unique = new Set(tokens);
  const uniqueRatio = unique.size / tokens.length;
  const countNgrams = (n)=>{
    const m = new Map();
    for(let i=0;i<=tokens.length-n;i++){
      const gram = tokens.slice(i,i+n).join(' ');
      m.set(gram,(m.get(gram)||0)+1);
    }
    let maxCount = 0, maxGram = '';
    for(const [g,c] of m.entries()){
      if(c>maxCount){ maxCount=c; maxGram=g; }
    }
    return {maxCount,maxGram};
  };
  const big = countNgrams(2);
  const tri = countNgrams(3);
  const four = countNgrams(4);
  return (
    (tokens.length >= 18 && (big.maxCount >= 6 || tri.maxCount >= 4 || four.maxCount >= 3)) ||
    (tokens.length >= 12 && uniqueRatio < 0.26) ||
    (tokens.length >= 18 && uniqueRatio < 0.40 && tri.maxCount >= 3)
  );
}
function rejectIfRepeatedTranscript(text, source='stt'){
  if(!isLikelyRepeatedTranscript(text)) return false;
  logClient('warn','stt',`Transcripción descartada por repetición automática`,{source,text_preview:text.slice(0,260)});
  $('message').value='';
  pendingMicText='';
  pendingMicInterim='';
  setMicStatus('He detectado una repetición automática del micro. No la envío. Repite la palabra o escribe y pulsa ➤.');
  return true;
}

// Envía un WAV al backend STT y recibe la transcripción.
async function transcribeBlobWithServer(blob,language){ const form=new FormData(); form.append('file',blob,`ritxi_mic_${Date.now()}.wav`); const start=performance.now(); const effectiveHint = (currentVocabularyHint && !isOpenVocabularyHint(currentVocabularyHint)) ? currentVocabularyHint : ''; const hint = effectiveHint ? `&vocabulary_hint=${encodeURIComponent(effectiveHint)}` : ''; const res=await fetch(`/api/audio/transcribe_file?language=${encodeURIComponent(language||'es')}${hint}`,{method:'POST',body:form}); if(!res.ok)throw new Error(`${res.status} ${await res.text()}`); const data=await res.json(); data.client_upload_total_ms=Math.round(performance.now()-start); data.effective_vocabulary_hint=effectiveHint; return data; }
async function startServerWhisperMic({autoSend=false}={}){
  if(!flags().input_microphone||!flags().stt){ setMicStatus('Micro o STT desactivado por checkbox.'); return; }
  if(serverSttActive||recognizing)return; if(!navigator.mediaDevices?.getUserMedia){ setMicStatus('getUserMedia no disponible.'); logClient('error','stt','getUserMedia no disponible'); return; }
  const session=++serverSttSession, threshold=serverVadThreshold(), maxMs=serverMaxRecordMs(), silenceMs=micSilenceMs(), minVoiceMs=250, language=($('micLang').value||'es-ES').split('-')[0]||'es';
  serverSttActive=true; recognizing=true; manualStopRequested=false; setMicStatus(`STT rápido: habla ahora. Nivel mínimo=${threshold}`); logClient('info','stt','Captura STT local iniciada',{autoSend,session,threshold,maxMs,silenceMs}); updateMicDiag({server_stt:'recording'});
  let stream=null, audioContext=null, source=null, processor=null, chunks=[], voiceStarted=false, firstVoiceAt=0,lastVoiceAt=0,stopped=false,maxRms=0; const startMs=performance.now();
  const cleanup=async()=>{ try{processor&&processor.disconnect()}catch(_){} try{source&&source.disconnect()}catch(_){} try{audioContext&&await audioContext.close()}catch(_){} try{stream&&stream.getTracks().forEach(t=>t.stop())}catch(_){} serverSttActive=false; recognizing=false; serverSttStopper=null; };
  const finish=async(reason='manual')=>{ if(stopped)return; stopped=true; const inputRate=audioContext?.sampleRate||48000; await cleanup(); clearMicSilenceTimer(); const samples=flattenFloat32(chunks); const elapsed=Math.round(performance.now()-startMs); logClient('info','stt','Captura STT local finalizada',{reason,elapsed_ms:elapsed,samples:samples.length,maxRms:Number(maxRms.toFixed(5)),threshold}); if(reason==='manual-stop'&&!autoSend){setMicStatus('STT local parado manualmente.'); return;} if(!samples.length||(!voiceStarted&&maxRms<threshold*0.60)){setMicStatus('No he entendido la voz. Pulsa Hablar ahora y vuelve a hablar, o escribe y pulsa ➤.'); updateMicToggleUi(); logClient('warn','stt','Audio descartado por falta de voz',{voiceStarted,reason,maxRms:Number(maxRms.toFixed(5)),threshold}); if(activityAutoListenAfterBot){activityAwaitingUser=true;} return;} const wav=encodeWavFromFloat32(downsampleFloat32(samples,inputRate,16000),16000); setMicStatus('Transcribiendo voz…'); try{ const data=await transcribeBlobWithServer(wav,language); const text=normalizeTranscript(data.text||''); if(rejectIfRepeatedTranscript(text,'server-whisper')){ if(realtimeEnabled||activityAutoListenAfterBot){autoListenAfterBot=true; activityAwaitingUser=true;} return;} pendingMicText=text; $('message').value=text; logClient('info','stt',`Transcripción completada: “${text || '(vacía)'}”`,{latency_ms:data.latency_ms,metadata:data.metadata,vocabulary_hint:currentVocabularyHint}); if(!text){setMicStatus('No he entendido la voz. Pulsa Hablar ahora y vuelve a hablar, o escribe y pulsa ➤.'); updateMicToggleUi(); if(realtimeEnabled||activityAutoListenAfterBot){autoListenAfterBot=true; activityAwaitingUser=true;} return;} setMicStatus(`STT local detectó: “${text}”`); if(autoSend){ await sendTurn({source:'server-whisper'}); if(realtimeEnabled)scheduleRealtimeLoop(Number($('relistenDelayMs').value||1000)); } } catch(err){ setMicStatus(`Error STT local: ${String(err)}`); logClient('error','stt',`Error STT local: ${String(err)}`); if(realtimeEnabled)scheduleRealtimeLoop(2000); } };
  serverSttStopper=finish;
  try{ stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true,channelCount:1,sampleRate:16000}}); const AC=window.AudioContext||window.webkitAudioContext; audioContext=new AC(); source=audioContext.createMediaStreamSource(stream); processor=audioContext.createScriptProcessor(4096,1,1); processor.onaudioprocess=(ev)=>{ if(stopped)return; const input=ev.inputBuffer.getChannelData(0); const copy=new Float32Array(input.length); copy.set(input); chunks.push(copy); let sum=0; for(let i=0;i<copy.length;i++)sum+=copy[i]*copy[i]; const rms=Math.sqrt(sum/copy.length); maxRms=Math.max(maxRms,rms); const now=performance.now(); if(rms>=threshold){ if(!voiceStarted){voiceStarted=true; firstVoiceAt=now; logClient('info','stt','Voz detectada',{rms:Number(rms.toFixed(5)),threshold});} lastVoiceAt=now;} const elapsed=now-startMs; if(voiceStarted){ const voiceMs=now-firstVoiceAt, silence=now-lastVoiceAt; setMicStatus(`STT local escuchando… nivel=${rms.toFixed(3)} silencio=${Math.round(silence)}ms`); if(voiceMs>=minVoiceMs&&silence>=silenceMs)finish('vad-silence'); } else setMicStatus(`STT local esperando voz… nivel=${rms.toFixed(3)} umbral=${threshold}`); if(elapsed>=maxMs)finish('max-duration');}; source.connect(processor); processor.connect(audioContext.destination); setTimeout(()=>finish('max-duration-timeout'),maxMs+600); } catch(err){ await cleanup(); setMicStatus(`No se pudo abrir micro: ${String(err)}`); logClient('error','mic',`No se pudo abrir micro: ${String(err)}`); if(realtimeEnabled)scheduleRealtimeLoop(2000); }
}
function stopServerSttMic(){ if(serverSttStopper)serverSttStopper('manual-stop'); }

let currentEffectAudio=null;
function stopEffectAudio(){ try{ if(currentEffectAudio){ currentEffectAudio.pause(); currentEffectAudio.currentTime=0; } }catch(_){} currentEffectAudio=null; }
// Reproduce desde navegador los audios oficiales HF/Pollen asociados a movimientos.

function recordedEmotionIdForBotEmotion(emotion){
  // Mapea emociones internas del tutor a emociones oficiales con audio Pollen.
  const e=(emotion||'').toLowerCase();
  const map={
    alegre:'cheerful1',
    celebracion:'enthusiastic1',
    animo:'cheerful1',
    saludo:'cheerful1',
    curioso:'curious1',
    escucha_activa:'attentive1',
    pensando:'boredom1',
    thoughtful1:'boredom1',
    calma:'calming1',
    empatia:'calming1',
    triste:'sad1',
    preocupado:'anxiety1',
    asustado:'anxiety1',
    miedo:'anxiety1',
    enfadado_suave:'angry1',
    sorprendido:'gasp1',
    asentir:'yes1',
    negar:'no1',
    baile:'enthusiastic1',
    juego:'curious1',
    aplauso:'enthusiastic1',
    neutral:'attentive1'
  };
  if(map[e]) return map[e];
  // Si ya viene un id oficial, se respeta.
  if(/^(cheerful|enthusiastic|gasp|amazed|curious|attentive|calming|boredom|confused|yes|no|sad|anxiety|angry|wake_up)/.test(e)) return emotion;
  return 'attentive1';
}

function shouldPlayEmotionSound(){
  // Importante: sonido emocional no equivale a leer la respuesta con TTS.
  // En Texto + IA, output_audio/tts pueden estar OFF, pero las emociones oficiales siguen sonando.
  return true;
}

async function playOfficialRecordedAudio(emotionId, title='emoción', options={}){
  const force = !!options.force;
  const waitUntilEnd = options.wait !== false;
  if(!force && !flags().output_audio){
    logClient('debug','audio',`Audio oficial omitido por Audio salida desactivado: ${emotionId}`);
    return {started:false, skipped:'output_audio_disabled'};
  }
  try{
    stopEffectAudio();
    // Solo pausamos micro si hay micro escuchando. El modo texto no debe bloquearse.
    if(micAlwaysOn) pauseAlwaysOnMic('Audio oficial HF');
    const url=`/api/audio/recorded/${encodeURIComponent(emotionId)}?t=${Date.now()}`;
    const audio=new Audio(url);
    currentEffectAudio=audio;
    audio.preload='auto';
    audio.volume=Number($('effectVolumeUi')?.value||1.0);
    await setClientSpeaking(true,'official-audio-start').catch(()=>{});
    setMicStatus(`Emoción oficial: reproduciendo audio de ${title}`);
    logClient('info','audio',`Reproduciendo audio oficial por navegador: ${emotionId}`,{url,force,waitUntilEnd});
    const ended = new Promise(resolve=>{
      audio.onended=()=>{ resolve({kind:'ended'}); };
      audio.onerror=()=>{ resolve({kind:'error'}); };
      setTimeout(()=>resolve({kind:'timeout'}),6500);
    });
    await audio.play();

    if(!waitUntilEnd){
      // Sonido emocional no bloqueante: se libera la interfaz y se limpia al acabar en segundo plano.
      ended.then(result=>{
        lastOfficialAudioEndedAt=performance.now();
        setClientSpeaking(false,`official-audio-${result.kind}`).catch(()=>{});
        if(currentEffectAudio===audio) currentEffectAudio=null;
        if(micAlwaysOn && !manualMicStopLock) resumeAlwaysOnMic('audio oficial finalizado');
        logClient('info','audio',`audio oficial finalizado en segundo plano: ${emotionId}`,result);
      });
      return {started:true,url,ended:'background'};
    }

    const result = await ended;
    lastOfficialAudioEndedAt=performance.now();
    await setClientSpeaking(false,`official-audio-${result.kind}`).catch(()=>{});
    if(currentEffectAudio===audio) currentEffectAudio=null;
    if(result.kind==='error'){
      logClient('error','audio',`No se pudo reproducir audio oficial: ${emotionId}. No se usará TTS de sustitución.`);
      if(micAlwaysOn && !manualMicStopLock) resumeAlwaysOnMic('audio oficial error');
      return {started:false,error:'browser_audio_error',url};
    }
    logClient('info','audio',`audio oficial finalizado: ${emotionId}`,result);
    if(micAlwaysOn && !manualMicStopLock) resumeAlwaysOnMic('audio oficial finalizado');
    return {started:true,url,ended:result.kind};
  }catch(err){
    await setClientSpeaking(false,'official-audio-exception').catch(()=>{});
    if(micAlwaysOn && !manualMicStopLock) resumeAlwaysOnMic('audio oficial excepción');
    logClient('warn','audio',`Fallo reproduciendo audio oficial ${emotionId}: ${String(err)}. No se usará TTS de sustitución.`);
    return {started:false,error:String(err)};
  }
}

function stopBrowserTts(){ if('speechSynthesis'in window) window.speechSynthesis.cancel(); browserSpeaking=false; }
function estimateSpeechMs(text){ const words=(text||'').trim().split(/\s+/).filter(Boolean).length; return Math.min(20000,Math.max(1700,words*430)); }
async function setClientSpeaking(speaking,reason='browser-tts'){ browserSpeaking=speaking; try{ await api('/api/microphone/client_speaking',{method:'POST',body:JSON.stringify({speaking,reason})}); }catch(err){ logClient('warn','tts',`No se pudo notificar speaking: ${String(err)}`); } }


async function talkNowButton(){
  // Botón principal: si está escuchando, para. Si está parado, siempre intenta abrir.
  if(micAlwaysOn && !persistentMicPaused){
    await stopMicByUser('boton-parar-micro');
    return;
  }

  // Desbloqueo duro: después de una actividad puede quedar actividadAwaitingUser/realtimeSending
  // en un estado viejo. El botón manual debe obedecer siempre.
  manualMicStopLock = false;
  realtimeSending = false;
  persistentTranscribing = false;
  activityAwaitingUser = true;
  activityAutoListenAfterBot = true;
  realtimeEnabled = true;
  autoListenAfterBot = true;

  if(micRetryTimer){ clearTimeout(micRetryTimer); micRetryTimer=null; }
  updateMicToggleUi();
  setMicStatus('Activando micro manualmente… habla cuando aparezca Micro activo.');
  await startAlwaysOnMic({reason:'boton-micro-manual', autoSend:true, force:true});
}
function scheduleMicOpenAfterSpeech({autoSend=true, reason='after-speech'}={}){
  if(micRetryTimer) clearTimeout(micRetryTimer);
  let attempts = 0;

  const tryOpen = async()=>{
    attempts += 1;

    // Si ya no estamos en una actividad/conversación, no abrimos micro.
    if(manualMicStopLock){
      setMicStatus('Micro parado manualmente. No se reabre automáticamente.');
      return;
    }
    if(!realtimeEnabled && !activityAwaitingUser && !autoListenAfterBot && !activityAutoListenAfterBot && !micAlwaysOn){
      return;
    }

    // Esperar solo a condiciones LOCALES del navegador: Ritxi hablando, transcripción o envío.
    // No bloqueamos por echo_guard/canListenNow del backend, porque era la causa del bloqueo "Abriendo micro...".
    if(browserSpeaking || realtimeSending || persistentTranscribing){
      if(attempts < 20){
        setMicStatus(`Micro preparado, esperando a que Ritxi termine… ${attempts}/20`);
        micRetryTimer = setTimeout(tryOpen, 250);
      } else {
        setMicStatus('Micro preparado. Pulsa Activar micro o escribe y pulsa ➤.');
        logClient('warn','mic','No se abrió micro por espera local agotada',{reason,browserSpeaking,realtimeSending,persistentTranscribing});
      }
      return;
    }

    setMicStatus('Abriendo micro continuo desde el navegador…');
    const ok = await startAlwaysOnMic({autoSend, reason});
    if(!ok){
      setMicStatus('No se pudo abrir el micro. Revisa permisos del navegador o escribe y pulsa ➤.');
      logClient('error','mic','startAlwaysOnMic devolvió false',{reason});
    }
  };

  micRetryTimer = setTimeout(tryOpen, 150);
}

async function startConversationMicNow({autoSend=true, reason='manual-conversation'}={}){
  manualMicStopLock = false;
  realtimeEnabled = true;
  autoListenAfterBot = true;
  activityAwaitingUser = true;
  activityAutoListenAfterBot = true;
  updateMicToggleUi();
  setMicStatus('Activando micro continuo…');
  return await startAlwaysOnMic({autoSend, reason, force:true});
}

async function speakWithBrowser(text, options={}){ 
  const clean=(text||'').trim();
  const force = !!options.force;
  const afterListen = options.afterListen !== false;
  const shouldListenAfter = afterListen && (realtimeEnabled || activityAwaitingUser || autoListenAfterBot || activityAutoListenAfterBot || micAlwaysOn);

  if(!clean || (!force && (!flags().output_audio || !flags().tts || !flags().auto_voice_response))){
    if(shouldListenAfter){
      if(micAlwaysOn) resumeAlwaysOnMic('sin TTS');
      else await startAlwaysOnMic({reason:'no-tts-after-bot', autoSend:true});
    }
    return; 
  } 

  if(!('speechSynthesis' in window)){
    logClient('warn','tts','speechSynthesis no disponible'); 
    if(shouldListenAfter){
      if(micAlwaysOn) resumeAlwaysOnMic('sin speechSynthesis');
      else await startAlwaysOnMic({reason:'no-speechSynthesis', autoSend:true});
    }
    return;
  } 

  if(micAlwaysOn) pauseAlwaysOnMic(force ? 'Ficha hablando' : 'Ritxi hablando');
  stopBrowserTts(); 
  await setClientSpeaking(true,force ? 'card-tts-start' : 'browser-tts-start'); 
  setMicStatus(force ? 'Ritxi reproduce audio de actividad…' : 'Ritxi está hablando. Micro pausado para evitar eco…'); 
  logClient('info','tts',force ? 'Reproduciendo voz de ficha/actividad' : 'Reproduciendo audio con voz del navegador',{len:clean.length}); 

  await new Promise(resolve=>{ 
    const u=new SpeechSynthesisUtterance(clean); 
    u.lang=$('micLang')?.value||'es-ES'; 
    u.rate=Number($('speechRateUi')?.value||0.95); 
    u.pitch=1.05; 
    u.volume=1.0; 
    let done=false; 
    const finish=(kind)=>{ 
      if(done)return; 
      done=true; 
      logClient('info','tts',`TTS navegador finalizado: ${kind}`); 
      resolve();
    }; 
    u.onend=()=>finish('onend'); 
    u.onerror=e=>finish(`error:${e.error||'unknown'}`); 
    window.speechSynthesis.cancel(); 
    window.speechSynthesis.speak(u); 
    setTimeout(()=>finish('timeout-seguridad'),estimateSpeechMs(clean)+1500); 
  }); 

  await setClientSpeaking(false,force ? 'card-tts-end' : 'browser-tts-end'); 

  if(shouldListenAfter && !manualMicStopLock){
    setMicStatus('Ritxi terminó de hablar. Reactivando micro…');
    if(micAlwaysOn) {
      resumeAlwaysOnMic('Ritxi terminó de hablar');
      updateMicToggleUi();
    } else {
      await startAlwaysOnMic({reason:'after-tts-direct', autoSend:true});
    }
  } else {
    setMicStatus(force ? 'Audio de actividad finalizado.' : 'Ritxi terminó de hablar. Micro parado.');
  }
}

// Envía un turno completo a FastAPI/Ollama y gestiona estados de bloqueo/desbloqueo.

// Fuerza que la caja de texto y el botón de envío estén operativos.
function enableTextInputAlways(reason=''){
  const msg=$('message');
  const btn=$('sendBtn');
  if(msg){
    msg.disabled=false;
    msg.readOnly=false;
    msg.removeAttribute('disabled');
    msg.removeAttribute('readonly');
    msg.classList.remove('disabled');
    msg.style.pointerEvents='auto';
    msg.style.userSelect='text';
  }
  if(btn){
    btn.disabled=false;
    btn.removeAttribute('disabled');
    btn.classList.remove('disabled');
    btn.style.pointerEvents='auto';
    btn.style.opacity='1';
  }
  if(reason) logClient?.('debug','ui',`Entrada de texto habilitada: ${reason}`);
}

// Da prioridad al texto: pausa micro/STT sin cambiar el modelo ni el modo por sí solo.
function enterTextPriorityMode(reason='text-priority', {deepStop=false}={}){
  // La caja de texto manda sobre el micro. Esta función NO debe bloquear el envío.
  // Solo cambia estado de forma síncrona y detiene capturas en segundo plano.
  manualMicStopLock = true;
  realtimeEnabled = false;
  autoListenAfterBot = false;
  activityAutoListenAfterBot = false;
  persistentTranscribing = false;
  serverSttActive = false;
  recognizing = false;
  if(micRetryTimer){ clearTimeout(micRetryTimer); micRetryTimer=null; }

  try{ clearMicSilenceTimer(); }catch(_){}
  try{ if(serverSttStopper){ const stopper=serverSttStopper; serverSttStopper=null; Promise.resolve(stopper(`text-${reason}`)).catch(()=>{}); } }catch(_){}
  try{ if(recognition) recognition.abort(); }catch(_){}
  try{ if(recognition) recognition.stop(); }catch(_){}
  recognizing=false;
  serverSttActive=false;

  if(deepStop){
    stopAlwaysOnMic(reason).catch(()=>{});
  }else if(micAlwaysOn){
    pauseAlwaysOnMic('Modo texto');
  }

  enableTextInputAlways(reason);
  updateMicToggleUi();
  setMicStatus('Modo texto activo: micro parado/pausado. Escribe y pulsa ➤.');
  logClient('info','ui',`Modo texto prioritario activado: ${reason}`,{deepStop});
}



function chatRobotInteractionContext(){
  return {id:'chat_conversacional', title:'Chat conversacional', source:'chat', emotion:'escucha_activa'};
}

async function maybeRobotPositiveStartForChat(activeContextForTurn=null){
  if(activeContextForTurn) return {skipped:'activity_context'};
  if(isPureTextChatMode()) return {skipped:'text_only_chat'};
  if(activeInteractionMode === 'textRobot' || activeInteractionMode === 'voiceRobot' || activeInteractionMode === 'full'){
    return launchPositiveRobotAnimation(chatRobotInteractionContext(), 'start', 'chat conversacional inicio');
  }
  return {skipped:'chat_mode_without_robot'};
}

async function maybeRobotPositiveEndForChat(activeContextForTurn=null){
  if(activeContextForTurn) return {skipped:'activity_context'};
  if(isPureTextChatMode()) return {skipped:'text_only_chat'};
  if(activeInteractionMode === 'textRobot' || activeInteractionMode === 'voiceRobot' || activeInteractionMode === 'full'){
    return launchPositiveRobotAnimation(chatRobotInteractionContext(), 'end', 'chat conversacional final');
  }
  return {skipped:'chat_mode_without_robot'};
}

function isActivityTurnSource(sourceText=''){
  const s = String(sourceText || '');
  return s.startsWith('activity') || s.includes('activity-text') || s.includes('turno-actividad') || activityAwaitingUser || activityAutoListenAfterBot || shortCycleWaitingForNext;
}


function isExperimentalConversationModel(model=null){
  return String(model || selectedModelName()).includes('qwen3:0.6b');
}

function shouldUseSafeLocalForExperimentalModel(sentText='', activeContextForTurn=null){
  // v5.9.89: ya no se bloquea el chat con respuesta segura genérica.
  // Si el usuario elige qwen3:0.6b, effectiveModelForChat() redirige a gemma3:1b en chat libre.
  return false;
}

async function respondExperimentalModelSafely(sentText){
  const botText = fallbackFromConversationPolicy(sentText);
  lastSafeBotTextFallback = true;
  addChat('bot', botText, `modelo: ${selectedModelName()} · respuesta segura local · creatividad: ${creativityValue().toFixed(2)}`);
  lastAssistantVisibleText = botText;
  lastAssistantUserText = sentText;
  logClient('warn','ollama','Modelo experimental evitado en chat libre; respuesta segura local aplicada',{sentText, botText, model:selectedModelName()});
  setExecuting('Respuesta segura local','qwen3:0.6b no se usa para chat libre');
  await refreshStatus().catch(()=>{});
}

// Envía un turno de texto a actividad local u Ollama, conservando contexto y desbloqueando la UI.
async function sendTurn({source='manual'}={}){
  enableTextInputAlways(`sendTurn-${source}`);
  const text=($('message').value||'').trim(); 
  if(!text){ setMicStatus('Escribe un texto y pulsa ➤.'); enableTextInputAlways('texto-vacio'); return null; }
  const sourceText = String(source || '');
  const manualTyped = sourceText === 'manual' || sourceText.includes('manual') || sourceText.includes('activity-text') || sourceText.includes('enter') || sourceText.includes('button') || sourceText.includes('text');
  if(!manualTyped && rejectIfRepeatedTranscript(text,'sendTurn')){
    return null;
  }

  const activitySource = isActivityTurnSource(sourceText);
  const manualLike = sourceText === 'manual' || sourceText.includes('manual') || sourceText.includes('activity-text') || sourceText.includes('enter') || sourceText.includes('button') || sourceText.includes('text');

  // Evita que una actividad anterior contamine el chat normal.
  // Solo usamos contexto de actividad si el turno viene realmente de una actividad.
  const activeContextForTurn = activitySource ? (currentActivityContext || lastActivityContext) : null;
  if(!activitySource && currentActivityContext){
    clearActivityContext('mensaje conversacional normal: se ignora contexto de actividad anterior');
    lastActivityContext = null;
  }

  if(manualLike){
    // Enviar texto debe funcionar SIEMPRE, incluso si el micro está esperando.
    // Si es un turno de actividad, se conserva activeContextForTurn; si no, se responde como chat normal.
    enterTextPriorityMode(`send-text-${sourceText}`, {deepStop:false});
    forceUnlockTurnState(`send-text-${sourceText}`);
    manualMicStopLock = false;
    activityAwaitingUser = false;
    activityAutoListenAfterBot = false;
    shortCycleWaitingForNext = false;
    realtimeSending = false;
    enableTextInputAlways(`send-text-${sourceText}`);
  } else if(realtimeSending){
    logClient('warn','chat',`Turno ignorado porque había otro envío en curso: ${sourceText}`);
    return null;
  }

  realtimeSending=true; 
  const selectedModel = selectedModelName();
  const effectiveModel = effectiveModelForChat(selectedModel, activeContextForTurn);
  updateModelPills(effectiveModel);
  if(micAlwaysOn) pauseAlwaysOnMic('Procesando respuesta');
  const wasActivityTurn = activityAwaitingUser || activityAutoListenAfterBot || sourceText.startsWith('activity') || shortCycleWaitingForNext || shortCycleActive;

  lastUserTurnTs=Date.now(); 
  activityAwaitingUser=false; 
  const start=performance.now(); 
  $('currentState').textContent=activeContextForTurn ? 'Procesando actividad con IA local' : 'Pensando con IA local'; 
  $('currentSubState').textContent=activeContextForTurn ? 'Actividad o IA local según corresponda' : `Modelo: ${selectedModel}`;
  addChat('user',text); 
  const sentText = text;
  $('message').value='';
  const payloadFlags = (typeof chatFlagsForBackend === 'function') ? chatFlagsForBackend() : flags();
  logClient('info','chat',`Usuario: ${sentText}`,{source,wasActivityTurn,flags:flags(),backend_flags:payloadFlags,model:selectedModel,effective_model:effectiveModel,temperature:creativityValue(),activity_context:activeContextForTurn});
  logClient('debug','chat','Preparando envío de texto a actividad/IA',{source,activitySource,hasContext:!!activeContextForTurn});
  logClient('info','ollama',`Modelo real usado en turno: ${effectiveModel}`,{selected:selectedModel, ...modelSpeedInfo(effectiveModel)});

  if(await respondFastActivityLocally(sentText, activeContextForTurn)){
    realtimeSending=false;
    $('currentState').textContent='Listo para conversar';
    $('currentSubState').textContent='Respuesta rápida de actividad';
    return {text:'respuesta rápida local', provider:'local-activity'};
  }

  if(shouldUseSafeLocalForExperimentalModel(sentText, activeContextForTurn)){
    await respondExperimentalModelSafely(sentText);
    realtimeSending=false;
    $('currentState').textContent='Listo para conversar';
    $('currentSubState').textContent='Respuesta segura local para modelo experimental';
    enableTextInputAlways('experimental-model-safe-response');
    return {text:'respuesta segura local', provider:'local-experimental-model'};
  }

  let watchdog=null;
  const controller = new AbortController();
  const timeoutMs = Math.max(20000, Math.min(90000, Number(window.RITXI_CHAT_TIMEOUT_MS || 60000)));
  try{ 
    watchdog = setTimeout(()=>{
      try{ controller.abort(); }catch(_){}
      setMicStatus('La IA local sigue pensando. No cambio de modo ni de modelo automáticamente…');
      logClient('warn','ollama',`Timeout cliente tras ${timeoutMs} ms`,{model:selectedModel});
    }, timeoutMs);

    await maybeRobotPositiveStartForChat(activeContextForTurn);
    const textForLLM = applyCreativityInstruction(enrichUserTextWithActivityContext(sentText, activeContextForTurn));
    const payload={session_id:$('sessionId').value||'demo',text:textForLLM,flags:payloadFlags,llm_model:effectiveModel,temperature:creativityValue()}; 
    const data=await api('/api/chat',{method:'POST',body:JSON.stringify(payload),signal:controller.signal}); 
    if(watchdog){ clearTimeout(watchdog); watchdog=null; }
    updateModelPills(data.model || effectiveModel);
    let botText = (typeof safeBotText === 'function') ? safeBotText(data, sentText) : (String(data?.text||'').trim() || fallbackFromConversationPolicy(sentText));
    const repeatCheck = maybeReplaceRepetitiveReply(botText, sentText);
    botText = repeatCheck.text;
    if(repeatCheck.replaced) lastSafeBotTextFallback = true;
    data.text = botText;
    if(flags().output_text) addChat('bot',botText,`emoción: ${data.emotion} · modelo: ${data.model || effectiveModel} · creatividad: ${creativityValue().toFixed(2)} ${lastSafeBotTextFallback ? '· fallback/anti-repetición' : ''}`);
    lastAssistantVisibleText = botText;
    lastAssistantUserText = sentText;
    rememberLatency(data.latencies);
    logClient('info','ollama',`Respuesta recibida (${Math.round(data.latencies?.llm_total_ms || 0)} ms)`,{provider:data.provider,model:data.model || effectiveModel,warnings:data.warnings,text_len:botText.length});
    // Orden correcto: 1) texto visible, 2) emoción sonora, 3) movimiento si el modo lo permite.
    playAutomaticEmotionAfterReply(data);
    playAutomaticRobotEmotionAfterReply(data);
    if(activeInteractionMode==='textRobot' || activeInteractionMode==='full') setExecuting(`Emoción: ${data.emotion}`,'Texto mostrado; emoción/robot en segundo plano');
    await refreshStatus();
    if(flags().tts){ speakWithBrowser(botText).catch(err=>logClient('warn','tts',`TTS no bloqueante con aviso: ${String(err)}`)); }
    refreshStatus().catch(()=>{}); 
    lastBotTurnDoneTs = Date.now();
    if(activeContextForTurn && !shortCycleActive){
      if((isMaxCreativeActivityContext(activeContextForTurn) || isLongInteractionActivityContext(activeContextForTurn)) && !userAskedToEndActivity(sentText)){
        currentActivityContext = activeContextForTurn;
        lastActivityContext = activeContextForTurn;
        activityAwaitingUser = true;
        activityAutoListenAfterBot = true;
        $('message').placeholder = isMaxCreativeActivityContext(activeContextForTurn)
          ? 'Seguimos la actividad creativa: habla o escribe aquí...'
          : 'Seguimos la interacción larga: habla o escribe aquí...';
        setMicStatus('Seguimos en la actividad. Puedes continuar hablando o escribiendo. Di “terminar” para cerrar.');
        setTimeout(()=>scheduleMicOpenAfterSpeech({autoSend:true, reason:isMaxCreativeActivityContext(activeContextForTurn) ? 'maxima-interaccion-continua' : 'interaccion-larga-continua'}), 350);
      }else{
        clearActivityContext('turno respondido por Ollama');
      }
    }
    return data; 
  }
  catch(err){ 
    if(watchdog){ clearTimeout(watchdog); watchdog=null; }
    const msg = String(err);
    logClient('error','chat',`Error en turno: ${msg}`,{model:selectedModel}); 
    if(msg.includes('AbortError') || msg.includes('aborted')){
      addChat('bot',`La IA local no ha respondido dentro del tiempo esperado. El modo y el modelo no han cambiado. Revisa Ollama o usa manualmente un modelo más rápido.`,'sistema');
    }else{
      addChat('bot',`He tenido un problema técnico: ${msg}`,'sistema'); 
    }
    return null; 
  }
  finally{ 
    if(watchdog){ clearTimeout(watchdog); watchdog=null; }
    realtimeSending=false; 
    $('currentState').textContent='Listo para conversar'; 
    $('currentSubState').textContent='Esperando tu mensaje';
    updateModelPills();
    logClient('debug','chat',`Turno cliente completado en ${Math.round(performance.now()-start)} ms`); 

    if(!manualMicStopLock && activeContextForTurn && (wasActivityTurn || activityAutoListenAfterBot)){
      activityAwaitingUser=true;
      activityAutoListenAfterBot=true;
      setMicStatus('Tu turno: Ritxi ha terminado. Reabriendo micro…');
      resumeAlwaysOnMic('activity-turn-relisten'); if(!micAlwaysOn) scheduleMicOpenAfterSpeech({autoSend:true,reason:'activity-turn-relisten'});
    } else if(!manualMicStopLock && (realtimeEnabled||autoListenAfterBot)){
      resumeAlwaysOnMic('sendTurn-finally'); if(!micAlwaysOn) scheduleMicOpenAfterSpeech({autoSend:true,reason:'sendTurn-finally'});
    } else if(manualMicStopLock){
      setMicStatus('Micro parado por el usuario. Puedes escribir o activar micro.');
    }
  }
}
// Guarda y muestra latencias para diagnosticar lentitud de Ollama/modelos.


function playAutomaticRobotEmotionAfterReply(data){
  if(!data || !(activeInteractionMode==='textRobot' || activeInteractionMode==='full')) return;
  const emotionId = recordedEmotionIdForBotEmotion(data.emotion);
  // Movimiento emocional breve automático, separado del TTS y del micro.
  api('/api/robot/action',{method:'POST',body:JSON.stringify({
    emotion: emotionId,
    text:null,
    motion_enabled:true,
    audio_enabled:false,
    return_to_neutral:true,
    layer:'manual',
    wait:false,
    speech_motion:false
  })}).then(r=>logClient('info','robot',`Movimiento emocional automático: ${emotionId}`,r))
    .catch(err=>logClient('warn','robot',`Movimiento emocional automático no ejecutado: ${String(err)}`));
}

function playAutomaticEmotionAfterReply(data){
  if(!data || !shouldPlayEmotionSound()) return;
  const emotionId = recordedEmotionIdForBotEmotion(data.emotion);
  // No bloquea el chat. No es lectura TTS de la respuesta, es sonido/emoción breve de Ritxi.
  playOfficialRecordedAudio(emotionId, `emoción ${data.emotion || emotionId}`, {force:true, wait:false})
    .catch(err=>logClient('warn','audio',`Emoción automática no reproducida: ${String(err)}`));
}

function rememberLatency(latencies){ if(!latencies)return; lastLatencies.push(latencies); if(lastLatencies.length>40)lastLatencies.shift(); $('latencyPill').textContent=`${Math.round(latencies.llm_total_ms||0)} ms`; }
// Actualiza el bloque superior de actividad/ejecución y el botón Detener.
function setExecuting(title,subtitle){
  const card=$('executingCard');
  const rawTitle = String(title||'—');
  const cleanTitle = rawTitle
    .replace(/^Respuesta de actividad:\s*/,'')
    .replace(/^Resp\. actividad:\s*/,'')
    .replace(/^Acción seleccionada:\s*/,'')
    .trim() || '—';
  const cleanSubtitle = subtitle||'Movimiento + audio';
  if(card){
    card.querySelector('b').textContent = cleanTitle==='—' ? 'Sin ejecución activa' : `Ejecutando: ${cleanTitle}`;
    card.querySelector('small').textContent=cleanSubtitle;
  }
  const d=$('actionDetailPanel');
  if(d){
    $('detailTitle').textContent = cleanTitle==='—' ? 'Actividad actual: —' : `Actividad actual: ${cleanTitle}`;
    $('detailSubtitle').textContent = cleanSubtitle;
    d.classList.toggle('active', cleanTitle!=='—');
  }
}

// Cambia visualmente una píldora ON/OFF del modo de interacción.
function setPillState(id,on,labelOn,labelOff){
  const el=$(id);
  if(!el) return;
  el.classList.toggle('on',!!on);
  el.classList.toggle('off',!on);
  el.textContent = on ? labelOn : labelOff;
}
// Sincroniza la zona superior: Texto, Micro, IA y Robot ON/OFF.
function updateInteractionModeState(name='full'){
  const f=flags();
  setPillState('modeTextState',true,'Texto ON','Texto OFF');
  setPillState('modeMicState',!!(f.input_microphone && f.stt),'Micro ON','Micro OFF');
  setPillState('modeAiState',!!f.llm,'IA ON','IA OFF');
  setPillState('modeRobotState',!!f.robot_motion,'Robot ON','Robot OFF');
  const topMode=$('activeChatModeTop');
  if(topMode){
    const labels={text:'Chat: Texto + IA',textRobot:'Chat: Texto + IA + Robot',voiceRobot:'Chat: Micro + IA + sonidos',full:'Chat: Completo'};
    topMode.textContent=labels[name]||labels.text;
  }
  const chatHint=$('chatModeHint');
  if(chatHint){
    if(name==='text') chatHint.textContent='Chat escrito con IA. La respuesta se muestra por texto y no se reproduce en voz alta.';
    else if(name==='textRobot') chatHint.textContent='Chat escrito con IA y animación de robot después de la respuesta.';
    else if(name==='voiceRobot') chatHint.textContent='Chat por micro con voz/sonidos, sin robot conversacional.';
    else chatHint.textContent='Chat completo: texto, micro, voz/sonidos y robot conversacional.';
  }
  const hint=$('interactionModeHint');
  if(hint){
    if(name==='text') hint.textContent='Texto + IA: micro apagado, respuesta escrita en pantalla; emociones sonoras activas.';
    else if(name==='textRobot') hint.textContent='Texto + IA + Robot: micro apagado, respuesta escrita, emociones sonoras y movimiento del robot.';
    else if(name==='voiceRobot') hint.textContent='Micro + IA + sonidos: micro activo, voz/sonidos activos, robot parado.';
    else hint.textContent='Completo: texto + micro + IA + voz + robot.';
  }
}

// Marca visualmente el modo activo: Texto + IA, Micro + IA o Completo.
function markPresetButton(name){
  const map={text:'presetTextOnlyBtn',textRobot:'presetTextRobotBtn',voiceRobot:'presetVoiceRobotBtn',full:'presetFullTutorBtn'};
  ['presetTextOnlyBtn','presetTextRobotBtn','presetVoiceRobotBtn','presetFullTutorBtn','textModeBtn'].forEach(id=>$(id)?.classList.remove('active-preset'));
  $(map[name]||map.full)?.classList.add('active-preset');
  if(name==='text') $('textModeBtn')?.classList.add('active-preset');
  updateInteractionModeState(name);
}

const QUICK_CHARACTER_PRESETS = {
  ritxi_tutor_comunicacion_di: {
    label:'Tutor amable',
    tone:'Tutor amable, claro, paciente y motivador.',
    extra:'Usa frases cortas, una pregunta por turno y refuerzo positivo.'
  },
  ritxi_apoyo_emocional: {
    label:'Apoyo emocional',
    tone:'Acompañante tranquilo, empático y regulador.',
    extra:'Prioriza calma, validación emocional, respiración y seguridad. No presiones.'
  },
  ritxi_lenguaje_claro: {
    label:'Lenguaje claro',
    tone:'Tutor de lenguaje claro y muy estructurado.',
    extra:'Usa vocabulario sencillo, ejemplos, sinónimos, opuestos y frases funcionales.'
  },
  ritxi_juegos_canciones: {
    label:'Juegos y canciones',
    tone:'Animador lúdico, musical y positivo.',
    extra:'Propón juegos breves, canciones cortas, turnos y movimiento suave.'
  },
  ritxi_modo_calma: {
    label:'Modo calma',
    tone:'Muy tranquilo, lento y predecible.',
    extra:'Reduce estímulos. Usa pausas, respiración, frases de seguridad y no hay prisa.'
  }
};
function applyQuickCharacterPreset(id){
  const preset=QUICK_CHARACTER_PRESETS[id] || QUICK_CHARACTER_PRESETS.ritxi_tutor_comunicacion_di;
  if($('characterChip')) $('characterChip').textContent=preset.label;
  if($('quickCharacterSelect')) $('quickCharacterSelect').value=id;
  if(currentCharacter){
    currentCharacter = {
      ...currentCharacter,
      name: preset.label,
      tone: preset.tone,
      prompt_extra: preset.extra,
    };
    renderCharacterForm(currentCharacter);
  }
  logClient('info','character',`Carácter rápido seleccionado: ${preset.label}`,preset);
}

// Aplica los tres modos generales: solo texto, voz+robot o tutor completo.
// Aplica el modo de trabajo seleccionado sin cambiarlo automáticamente después.
function setModulePreset(name){
  // Conceptos separados:
  // - Texto: entrada escrita. Siempre queda disponible.
  // - Micro/STT: entrada por voz. Se enciende o apaga por modo/botón.
  // - TTS: leer en voz alta el texto de la respuesta. En modo texto se apaga.
  // - Sonidos emocionales: audios breves oficiales de Ritxi. Siguen activos en modo texto.
  // - Robot: movimiento físico/simulado. Solo activo en Texto+IA+Robot y Completo.
  const sets={
    text:{
      inputMicrophone:false,sttEnabled:false,llmEnabled:true,ttsEnabled:false,outputAudio:true,outputText:true,
      robotMotion:false,speechMotion:false,cameraVision:false,debug:true,saveSession:true,simulationMode:true,
      activeWait:false,moveTalkGenerateText:false,autoVoiceResponse:false,autoSendAfterStt:false,echoGuard:false,modeTutorDi:true
    },
    textRobot:{
      inputMicrophone:false,sttEnabled:false,llmEnabled:true,ttsEnabled:false,outputAudio:true,outputText:true,
      robotMotion:true,speechMotion:false,cameraVision:false,debug:true,saveSession:true,simulationMode:true,
      activeWait:false,moveTalkGenerateText:true,autoVoiceResponse:false,autoSendAfterStt:false,echoGuard:false,modeTutorDi:true
    },
    voiceRobot:{
      inputMicrophone:true,sttEnabled:true,llmEnabled:true,ttsEnabled:true,outputAudio:true,outputText:true,
      robotMotion:false,speechMotion:false,cameraVision:false,debug:true,saveSession:true,simulationMode:true,
      activeWait:true,moveTalkGenerateText:false,autoVoiceResponse:true,autoSendAfterStt:true,echoGuard:true,modeTutorDi:true
    },
    full:{
      inputMicrophone:true,sttEnabled:true,llmEnabled:true,ttsEnabled:true,outputAudio:true,outputText:true,
      robotMotion:true,speechMotion:true,cameraVision:false,debug:true,saveSession:true,simulationMode:true,
      activeWait:true,moveTalkGenerateText:true,autoVoiceResponse:true,autoSendAfterStt:true,echoGuard:true,modeTutorDi:true
    }
  };
  activeInteractionMode = (sets[name] ? name : 'text');
  const cfg=sets[activeInteractionMode]||sets.text;
  Object.entries(cfg).forEach(([id,val])=>{ if($(id)) $(id).checked=!!val; });
  markPresetButton(activeInteractionMode);
  enableTextInputAlways(`preset-${activeInteractionMode}`);
  logClient('info','config',`Modo de interacción aplicado: ${activeInteractionMode}`,cfg);
  if($('activeWait')) toggleIdleFromCheckbox().catch(()=>{});

  if(name==='text'){
    enterTextPriorityMode('preset-texto-ia',{deepStop:true});
    setMicStatus('Texto + IA: micro apagado. La respuesta no se lee, pero las emociones de Ritxi pueden sonar.');
  }else if(name==='textRobot'){
    enterTextPriorityMode('preset-texto-ia-robot',{deepStop:true});
    setMicStatus('Texto + IA + Robot: micro apagado. Ritxi puede sonar y moverse con emociones.');
  }else if(name==='voiceRobot'){
    manualMicStopLock=false;
    realtimeEnabled=true;
    autoListenAfterBot=true;
    activityAutoListenAfterBot=false;
    setMicStatus('Micro + IA + sonidos: habla cuando quieras. El texto sigue disponible. Robot parado.');
    updateMicToggleUi();
    scheduleMicOpenAfterSpeech({autoSend:true, reason:'preset-micro'});
  }else{
    manualMicStopLock=false;
    realtimeEnabled=true;
    autoListenAfterBot=true;
    setMicStatus('Completo: texto, micro, IA, voz, sonidos y robot activos.');
    updateMicToggleUi();
    scheduleMicOpenAfterSpeech({autoSend:true, reason:'preset-tutor-completo'});
  }
}

function sleep(ms){ return new Promise(resolve=>setTimeout(resolve,ms)); }
function ensureAudioContext(){ const AC=window.AudioContext||window.webkitAudioContext; if(!AC)return null; if(!window.ritxiAudioContext) window.ritxiAudioContext=new AC(); return window.ritxiAudioContext; }
const GAME_TAB_ACTION_IDS = new Set([
  'dance1','dance2','dance3','baile_divertido','success1','electric1','baile_suave','ritmo_palmas',
  'animal_corto','animal_perro','animal_gato','animal_vaca','juego_animales','adivina_sonido','eco_ritxi',
  'sonido_lluvia','instrumento_tambor','instrumento_campana',
  'cantar_saludo','palmas_lentas','palmas_rapidas','imitame','estirar',
  'cuento_corto','historia_turnos','final_historia','personajes','recordar_historia','cuento_interactivo',
  'chiste','celebrar_intento'
]);

const GAME_ACTION_GROUPS = [
  { title:'Bailes y movimiento divertido', target:'gamesActionGrid', items:[
    { id:'dance1', title:'Baile oficial 1', icon:'🕺', emotion:'dance1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true, fallbackText:'Ritxi baila.' },
    { id:'dance2', title:'Baile oficial 2', icon:'💃', emotion:'dance2', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true, fallbackText:'Ritxi baila.' },
    { id:'dance3', title:'Baile oficial 3', icon:'🤖', emotion:'dance3', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true, fallbackText:'Ritxi baila.' },
    { id:'baile_divertido', title:'Baile divertido', icon:'🎶', emotion:'baile', text:'Vamos a movernos un poco. Yo bailo suave y tú puedes seguir el ritmo.', subtitle:'Baile + voz', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'baile_suave', title:'Baile suave', icon:'🌊', emotion:'calma', text:'Nos movemos suave y tranquilos. Muy bien.', subtitle:'Movimiento suave', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'success1', title:'Fiesta', icon:'🎉', emotion:'celebracion', text:'¡Fiesta! Celebramos que estamos practicando juntos.', subtitle:'Celebración + voz' },
    { id:'electric1', title:'Energía eléctrica', icon:'⚡', emotion:'electric1', text:'', subtitle:'Movimiento oficial + audio', recordedAudio:true, fallbackText:'Ritxi hace un movimiento con energía.' },
    { id:'estirar', title:'Estirar suave', icon:'🙆', emotion:'calma', text:'Estiramos suave. Subimos, bajamos y respiramos. Muy bien.', subtitle:'Movimiento guiado' },
    { id:'imitame', title:'Imítame', icon:'🪞', emotion:'juego', text:'Juego de imitación. Yo hago un gesto y tú intentas hacerlo también.', subtitle:'Atención e imitación', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
  ]},
  { title:'Canciones y ritmo', target:'gamesActionGrid', items:[
    { id:'cantar_saludo', title:'Cantar saludo', icon:'🎤', emotion:'alegre', text:'Cantamos un saludo: hola, hola, qué tal estás. Me alegra verte y contigo hablar.', subtitle:'Canto corto', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'ritmo_palmas', title:'Ritmo con palmas', icon:'👏', emotion:'aplauso', text:'Escucha el ritmo: una, dos, una, dos. Ahora te toca a ti.', subtitle:'Juego rítmico', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'palmas_lentas', title:'Palmas lentas', icon:'👏', emotion:'aplauso', text:'Damos palmas lentas: una… dos… una… dos. Ahora lo intentas tú.', subtitle:'Ritmo lento', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'palmas_rapidas', title:'Palmas rápidas', icon:'⚡', emotion:'celebracion', text:'Ahora palmas rápidas: una, dos, tres. ¡Muy bien!', subtitle:'Ritmo rápido', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'instrumento_tambor', title:'Tambor', icon:'🥁', emotion:'juego', text:'Suena un tambor: pum, pum, pum. ¿Puedes repetir el ritmo?', subtitle:'Ritmo y atención', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'instrumento_campana', title:'Campana', icon:'🔔', emotion:'curioso', text:'Suena una campana: din, don. ¿Es un sonido fuerte o suave?', subtitle:'Discriminación auditiva' },
    { id:'sonido_lluvia', title:'Sonido lluvia', icon:'🌧️', emotion:'calma', text:'Imagina que escuchas lluvia suave. ¿La lluvia te relaja?', subtitle:'Relajación sonora' },
  ]},
  { title:'Juegos de animales y sonidos', target:'gamesActionGrid', items:[
    { id:'animal_corto', title:'Animal rápido', icon:'🐶', emotion:'juego', text:'Guau guau. ¿Qué animal es?', subtitle:'Sonido + pregunta', sound:'dog', awaitUser:true, requiresInput:true, vocabularyHint:'animal' },
    { id:'animal_perro', title:'Adivina animal: perro', icon:'🐶', emotion:'juego', text:'Escucha: guau, guau. ¿Qué animal es?', subtitle:'Sonido + pregunta', awaitUser:true, requiresInput:true, vocabularyHint:'animal' },
    { id:'animal_gato', title:'Adivina animal: gato', icon:'🐱', emotion:'juego', text:'Escucha: miau, miau. ¿Qué animal es?', subtitle:'Sonido + pregunta', awaitUser:true, requiresInput:true, vocabularyHint:'animal' },
    { id:'animal_vaca', title:'Adivina animal: vaca', icon:'🐮', emotion:'juego', text:'Escucha: muuu. ¿Qué animal es?', subtitle:'Sonido + pregunta', awaitUser:true, requiresInput:true, vocabularyHint:'animal' },
    { id:'juego_animales', title:'Adivina el animal', icon:'🐾', emotion:'juego', subtitle:'Sonido + pregunta + refuerzo', intro:'escucha el sonido y adivina el animal.', steps:[
      {label:'Preparar', emotion:'curioso', text:'Vamos a jugar a adivinar animales. Escucha con atención.', chat:'Juego: adivina el animal.'},
      {label:'Sonido perro', emotion:'juego', sound:'dog', durationMs:850, text:'¿Qué animal hace guau guau?', chat:'Ritxi reproduce un sonido de animal.'},
      {label:'Refuerzo', emotion:'animo', text:'Muy bien. Puedes responder: es un perro. Ahora probamos otro.', sound:'success', durationMs:650},
      {label:'Sonido gato', emotion:'curioso', sound:'cat', durationMs:850, text:'¿Qué animal hace miau?', chat:'Segundo sonido.'}
    ]},
    { id:'adivina_sonido', title:'Adivina sonido', icon:'👂', emotion:'curioso', text:'Escucha con atención. Si suena din don, puede ser una campana. Ahora jugamos a adivinar sonidos.', subtitle:'Juego auditivo', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'eco_ritxi', title:'Eco de Ritxi', icon:'🔁', emotion:'juego', text:'Juego del eco. Yo digo una palabra corta y tú la repites: hola.', subtitle:'Repetición lúdica', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
  ]},
  { title:'Cuentos y juego imaginativo', target:'gamesActionGrid', items:[
    { id:'cuento_corto', title:'Cuento corto', icon:'📖', emotion:'curioso', text:'Érase una vez un pequeño robot que aprendió a escuchar con paciencia. Cada día hacía una pregunta amable y esperaba la respuesta.', subtitle:'Narración breve', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'historia_turnos', title:'Historia por turnos', icon:'🧵', emotion:'juego', text:'Hacemos una historia por turnos. Yo empiezo: un robot encontró una llave dorada. Ahora tú dices qué pasó después.', subtitle:'Creatividad y turnos', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'final_historia', title:'Inventar final', icon:'🏁', emotion:'thoughtful1', text:'Voy a contar una historia y tú inventas el final. Un gato perdió su pelota en el parque...', subtitle:'Imaginación', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'personajes', title:'Personajes', icon:'🎭', emotion:'curioso', text:'Elige un personaje: robot, dragón o exploradora. Después hacemos una pequeña historia.', subtitle:'Elección guiada', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'recordar_historia', title:'Recordar historia', icon:'🧠', emotion:'thoughtful1', text:'Te cuento tres datos y luego recordamos uno. El robot era pequeño, azul y muy curioso.', subtitle:'Memoria auditiva', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'cuento_interactivo', title:'Cuento por turnos', icon:'📚', emotion:'curioso', text:'Vamos a crear un cuento por turnos. Yo digo una frase y tú dices la siguiente.', subtitle:'Narración + juego', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'chiste', title:'Contar chiste', icon:'😄', emotion:'alegre', text:'¿Por qué los robots no cuentan chistes malos? Porque ya bastante tienen con sus errores de programación.', subtitle:'Humor breve' },
  ]},
];



const TUTOR_ACTION_IDS = new Set([
  'respira','buen_trabajo','vamos_hablar','relajate','repetir_despacio','no_hay_prisa','emocion_nombre','pedir_ayuda',
  'calma_corta','calmar','validar_emocion','reforzar','celebrar_intento','respiracion_guiada','emociones_caras',
  'pausa_sensorial','semáforo_emocional','frase_segura','elegir_emocion','pedir_descanso','rutina_primero_despues',
  'ensayo_pedir_ayuda','ensayo_decidir','escucha_y_repite','refuerzo_especifico','cierre_calma'
]);

const TUTOR_ACTION_GROUPS = [
  { title:'Regulación y calma', target:'tutorActionGrid', items:[
    { id:'respira', title:'Respira conmigo', icon:'🫁', emotion:'calma', text:'Respira conmigo. Inspiramos despacio… y soltamos el aire. Muy bien.', subtitle:'Relajación guiada' },
    { id:'respiracion_guiada', title:'Respiración 3 pasos', icon:'🌬️', emotion:'calma', text:'Hacemos tres pasos: miro, respiro y respondo. Primero respiramos despacio.', subtitle:'Regulación' },
    { id:'pausa_sensorial', title:'Pausa sensorial', icon:'🧘', emotion:'calma', text:'Hacemos una pausa. Bajamos el ritmo. Puedes mirar un punto y respirar conmigo.', subtitle:'Bajar activación', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'semáforo_emocional', title:'Semáforo emocional', icon:'🚦', emotion:'thoughtful1', text:'Semáforo emocional: rojo paro, amarillo respiro, verde pido ayuda o sigo.', subtitle:'Estrategia visual' },
    { id:'frase_segura', title:'Frase segura', icon:'🛟', emotion:'paciencia', text:'Puedes decir: necesito un momento. Está bien pedir una pausa.', subtitle:'Autoprotección', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'pedir_descanso', title:'Pedir descanso', icon:'☕', emotion:'calma', text:'Practicamos pedir descanso. Puedes decir: necesito descansar un poco.', subtitle:'Comunicación funcional', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
  ]},
  { title:'Comunicación funcional y lenguaje', target:'tutorActionGrid', items:[
    { id:'vamos_hablar', title:'Vamos a hablar', icon:'💬', emotion:'escucha_activa', text:'Vamos a hablar. Te haré una pregunta sencilla y tú puedes responder con calma.', subtitle:'Conversación guiada', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'pedir_ayuda', title:'Pedir ayuda', icon:'🆘', emotion:'escucha_activa', text:'Vamos a practicar pedir ayuda. Puedes decir: ¿me ayudas, por favor?', subtitle:'Pedir ayuda', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'ensayo_pedir_ayuda', title:'Ensayo pedir ayuda', icon:'🙋', emotion:'escucha_activa', text:'Ensayamos. Primero digo: necesito ayuda. Ahora repítelo tú si quieres.', subtitle:'Ensayo guiado', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'escucha_y_repite', title:'Escucha y repite', icon:'🔁', emotion:'repetir', text:'Escucha y repite: por favor, ¿puedes repetirlo?', subtitle:'Repetición funcional', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'rutina_primero_despues', title:'Primero / después', icon:'1️⃣', emotion:'thoughtful1', text:'Primero escuchamos. Después respondemos con una frase corta.', subtitle:'Estructura temporal', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'ensayo_decidir', title:'Elegir opción', icon:'🔀', emotion:'curioso', text:'Practicamos elegir. Puedes decir: quiero esta opción, o prefiero la otra.', subtitle:'Toma de decisiones', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
  ]},
  { title:'Emociones y refuerzo', target:'tutorActionGrid', items:[
    { id:'buen_trabajo', title:'Buen trabajo', icon:'⭐', emotion:'cheerful1', text:'¡Buen trabajo! Lo importante es intentarlo, y tú lo has intentado.', subtitle:'Refuerzo + movimiento' },
    { id:'refuerzo_especifico', title:'Refuerzo específico', icon:'🎯', emotion:'animo', text:'Me ha gustado cómo lo has intentado. Has esperado tu turno y has respondido.', subtitle:'Refuerzo concreto' },
    { id:'emocion_nombre', title:'Nombrar emoción', icon:'😊', emotion:'thoughtful1', text:'Vamos a nombrar una emoción. Puedes decir: estoy contento, estoy triste o estoy tranquilo.', subtitle:'Nombrar emoción', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'elegir_emocion', title:'Elegir emoción', icon:'💛', emotion:'empatia', text:'Elige una emoción: alegre, triste, nervioso o tranquilo. Puedes decir una palabra.', subtitle:'Elección emocional', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'validar_emocion', title:'Validar emoción', icon:'🤲', emotion:'empatia', text:'Está bien sentirse así. Podemos decirlo con palabras y pedir ayuda si la necesitamos.', subtitle:'Validación', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'cierre_calma', title:'Cierre tranquilo', icon:'🌙', emotion:'calma', text:'Terminamos con calma. Gracias por practicar. Has hecho un buen trabajo.', subtitle:'Cierre positivo' },
  ]},
];

function withoutTutorItems(groups){
  return (groups||[]).map(group=>({
    ...group,
    items:(group.items||[]).filter(item=>!TUTOR_ACTION_IDS.has(item.id))
  })).filter(group=>(group.items||[]).length>0);
}

const FALLBACK_GAME_ACTION_GROUPS = [
  { title:'Juegos rápidos', target:'gamesActionGrid', items:[
    { id:'animal_corto', title:'Animal rápido', icon:'🐶', emotion:'juego', text:'Guau guau. ¿Qué animal es?', subtitle:'Sonido + pregunta', sound:'dog', awaitUser:true, requiresInput:true, vocabularyHint:'animal' },
    { id:'adivina_sonido', title:'Adivina sonido', icon:'👂', emotion:'curioso', text:'Escucha con atención. Si suena din don, puede ser una campana.', subtitle:'Juego auditivo', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'eco_ritxi', title:'Eco de Ritxi', icon:'🔁', emotion:'juego', text:'Juego del eco. Yo digo una palabra corta y tú la repites: hola.', subtitle:'Repetición lúdica', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'chiste', title:'Chiste', icon:'😄', emotion:'alegre', text:'¿Por qué los robots no cuentan chistes malos? Porque ya bastante tienen con sus errores de programación.', subtitle:'Humor breve' },
  ]},
  { title:'Canciones y bailes', target:'gamesActionGrid', items:[
    { id:'cantar_saludo', title:'Cantar saludo', icon:'🎤', emotion:'alegre', text:'Cantamos un saludo: hola, hola, qué tal estás. Me alegra verte y contigo hablar.', subtitle:'Canto corto', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'ritmo_palmas', title:'Ritmo con palmas', icon:'👏', emotion:'aplauso', text:'Escucha el ritmo: una, dos, una, dos. Ahora te toca a ti.', subtitle:'Juego rítmico', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'palmas_lentas', title:'Palmas lentas', icon:'👏', emotion:'aplauso', text:'Damos palmas lentas: una… dos… una… dos. Ahora lo intentas tú.', subtitle:'Ritmo lento', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'baile_suave', title:'Baile suave', icon:'🌊', emotion:'calma', text:'Nos movemos suave y tranquilos. Muy bien.', subtitle:'Movimiento suave', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'baile_divertido', title:'Baile divertido', icon:'🎶', emotion:'baile', text:'Vamos a movernos un poco. Yo bailo suave y tú puedes seguir el ritmo.', subtitle:'Baile + voz', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
  ]},
];
function effectiveGameGroups(){
  return (typeof GAME_ACTION_GROUPS !== 'undefined' && GAME_ACTION_GROUPS && GAME_ACTION_GROUPS.length) ? GAME_ACTION_GROUPS : FALLBACK_GAME_ACTION_GROUPS;
}

function withoutGameItems(groups){
  return (groups||[]).map(group=>({
    ...group,
    items:(group.items||[]).filter(item=>!GAME_TAB_ACTION_IDS.has(item.id))
  })).filter(group=>(group.items||[]).length>0);
}


async function playSyntheticSound(kind='bell', durationMs=800){
  if(!flags().output_audio){ logClient('debug','audio',`Sonido sintético omitido: ${kind}`); return; }
  const ctx=ensureAudioContext();
  if(!ctx){ logClient('warn','audio','AudioContext no disponible para sonidos de juego'); return; }
  if(ctx.state==='suspended') await ctx.resume().catch(()=>{});
  await setClientSpeaking(true,`synthetic-${kind}-start`).catch(()=>{});
  logClient('info','audio',`Sonido de actividad: ${kind}`,{durationMs});
  const now=ctx.currentTime;
  const master=ctx.createGain(); master.gain.value=0.18; master.connect(ctx.destination);
  const osc=(type,freq,start,dur,gain=1)=>{
    const o=ctx.createOscillator(); const g=ctx.createGain();
    o.type=type; o.frequency.setValueAtTime(freq,now+start); g.gain.setValueAtTime(0,now+start); g.gain.linearRampToValueAtTime(gain,now+start+0.03); g.gain.exponentialRampToValueAtTime(0.001,now+start+dur);
    o.connect(g); g.connect(master); o.start(now+start); o.stop(now+start+dur+0.05);
  };
  const noise=(start,dur,gain=0.25)=>{
    const len=Math.floor(ctx.sampleRate*dur); const buffer=ctx.createBuffer(1,len,ctx.sampleRate); const data=buffer.getChannelData(0); for(let i=0;i<len;i++)data[i]=(Math.random()*2-1)*0.55;
    const src=ctx.createBufferSource(); src.buffer=buffer; const g=ctx.createGain(); g.gain.setValueAtTime(gain,now+start); g.gain.exponentialRampToValueAtTime(0.001,now+start+dur); src.connect(g); g.connect(master); src.start(now+start); src.stop(now+start+dur);
  };
  if(kind==='dog'){ osc('sawtooth',180,0,0.18); osc('sawtooth',135,0.24,0.20); }
  else if(kind==='cat'){ osc('sine',520,0,0.55); osc('triangle',720,0.10,0.38,0.55); }
  else if(kind==='cow'){ osc('sawtooth',105,0,0.75); osc('sine',85,0.2,0.55,0.55); }
  else if(kind==='bird'){ osc('sine',1200,0,0.12); osc('sine',1600,0.16,0.12); osc('sine',1000,0.32,0.14); }
  else if(kind==='rain'){ noise(0,1.2,0.22); }
  else if(kind==='drum'){ osc('sine',115,0,0.16); osc('sine',90,0.32,0.18); osc('sine',130,0.64,0.16); }
  else if(kind==='bell'){ osc('sine',880,0,0.75); osc('sine',1320,0,0.6,0.45); }
  else if(kind==='success'){ osc('sine',523,0,0.15); osc('sine',659,0.16,0.15); osc('sine',784,0.32,0.22); }
  else { osc('sine',440,0,0.4); }
  await sleep(durationMs);
  await setClientSpeaking(false,`synthetic-${kind}-end`).catch(()=>{});
}


function setActionButtonsDisabled(disabled, exceptBtn=null){
  document.querySelectorAll('.action-card').forEach(b=>{
    if(disabled && b!==exceptBtn) b.classList.add('temporarily-disabled');
    else b.classList.remove('temporarily-disabled');
    if(b!==exceptBtn) b.disabled = !!disabled;
  });
}
function clearCurrentActionButton(){
  if(currentActionButton){
    currentActionButton.classList.remove('running','active','finished','queued');
    const badge=currentActionButton.querySelector('.running-badge');
    if(badge) badge.remove();
    currentActionButton=null;
  }
  setActionButtonsDisabled(false);
}
function markActionButton(btn,item){
  clearCurrentActionButton();
  if(!btn) return;
  currentActionButton=btn;
  btn.classList.add('running','active');
  btn.disabled=false;
  setActionButtonsDisabled(true,btn);
  if(!btn.querySelector('.running-badge')){
    const badge=document.createElement('span');
    badge.className='running-badge';
    badge.textContent='En curso';
    btn.appendChild(badge);
  }
  setExecuting(item?.title || 'Acción','Ejecutando acción');
}
function finishActionButton(btn, token=null){
  if(token !== null && token !== actionSequenceId) return;
  if(btn && btn===currentActionButton){
    const badge=btn.querySelector('.running-badge');
    if(badge) badge.textContent='Terminado';
    btn.classList.add('finished');
    setTimeout(()=>{ 
      btn.classList.remove('running','active','finished','queued'); 
      const b=btn.querySelector('.running-badge'); 
      if(b) b.remove(); 
      if(currentActionButton===btn) currentActionButton=null; 
      setActionButtonsDisabled(false);
    },650);
  } else {
    setActionButtonsDisabled(false);
  }
}
function queueNextAction(item,btn){
  pendingActionItem=item;
  pendingActionBtn=btn;
  if(btn){
    btn.classList.add('queued');
    if(!btn.querySelector('.running-badge')){
      const badge=document.createElement('span');
      badge.className='running-badge';
      badge.textContent='En cola';
      btn.appendChild(badge);
    } else {
      btn.querySelector('.running-badge').textContent='En cola';
    }
  }
  logClient('info','ui',`Acción en cola: ${item.title}`);
}
async function runPendingActionIfAny(){
  if(pendingActionItem){
    const item=pendingActionItem;
    const btn=pendingActionBtn;
    pendingActionItem=null;
    pendingActionBtn=null;
    await sleep(120);
    return executeAction(item,btn,{queued:true});
  }
}



const POSITIVE_CLOSING_ROBOT_EMOTIONS = [
  // Lista validada: ids reales o alias que resuelven en la librería Pollen.
  'cheerful1',
  'amazed1',
  'yes1',
  'success1',
  'dance1',
  'dance2',
  'dance3'
];

function activityContainsRobot(itemOrContext){
  if(!itemOrContext) return false;
  // Emociones oficiales ya ejecutan su propia animación principal, pero también pueden
  // participar en la regla general de inicio/final cuando pertenecen a una actividad.
  return cardForcesRobot(itemOrContext) || !!itemOrContext.emotion || Array.isArray(itemOrContext.steps);
}

function isPureTextChatMode(){
  return activeInteractionMode === 'text';
}

function shouldUseRobotAnimationForInteraction(itemOrContext, phase='middle'){
  // Regla v5.9.91:
  // Único caso sin animaciones automáticas: chat conversacional puro Texto + IA.
  // Cualquier ficha/emoción/actividad/juego debe poder animar al inicio y al final,
  // aunque el chat esté en modo Texto + IA.
  if(!itemOrContext) return !isPureTextChatMode();
  if(itemOrContext.noRobot === true || itemOrContext.robotMotion === false) return false;
  if(itemOrContext.source === 'chat') return !isPureTextChatMode();
  return true;
}

function activityRuntimeMode(item){
  // Runtime propio de ficha/actividad: no usa el modo conversacional del chat.
  // Las fichas/actividades/juegos/emociones tienen animación aunque el chat esté en Texto + IA.
  const rt = cardRuntime(item);
  const needsMic = isMicroInputActivity(item);
  const needsRobot = shouldUseRobotAnimationForInteraction(item, 'activity-runtime');
  return {
    ...rt,
    robot_motion:needsRobot,
    speech_motion:needsRobot,
    input_microphone:needsMic,
    complete:!!(needsRobot || rt.output_audio || needsMic),
  };
}

function shouldPositiveCloseShortActivity(itemOrContext, reply=null){
  if(!itemOrContext) return false;
  if(reply?.keepContext) return false;
  // Si es interacción larga/abierta, solo cerrar cuando el usuario pide terminar.
  const id = itemOrContext.id || '';
  if(MAX_CREATIVE_ACTIVITY_IDS?.has?.(id) || LONG_INTERACTION_ACTIVITY_IDS?.has?.(id) || OPEN_CONVERSATION_ACTIVITY_IDS?.has?.(id)) return !!reply?.endContext;
  return shouldUseRobotAnimationForInteraction(itemOrContext, 'end');
}


function shouldPlayPositiveAnimationAudio(phase='end'){
  if(phase === 'start') return robotMotionPolicy.play_audio_on_positive_start !== false;
  if(phase === 'end') return robotMotionPolicy.play_audio_on_positive_end !== false;
  return false;
}

function firePositiveAnimationAudio(emotion, itemOrContext=null, phase='end', reason='positive-audio'){
  if(!emotion || !shouldPlayPositiveAnimationAudio(phase)) return;
  logClient('info','audio',`Audio oficial positivo ${phase} solicitado: ${emotion}`,{
    activity:itemOrContext?.id,
    title:itemOrContext?.title,
    phase,
    reason
  });
  playOfficialRecordedAudio(emotion, `${phase} positivo ${itemOrContext?.title || ''}`, {
    force: robotMotionPolicy.positive_audio_force !== false,
    wait: !!robotMotionPolicy.positive_audio_wait_until_end,
    waitUntilEnd: !!robotMotionPolicy.positive_audio_wait_until_end
  }).catch(err=>{
    logClient('warn','audio',`No se pudo reproducir audio positivo ${phase}: ${String(err)}`,{
      emotion,
      activity:itemOrContext?.id
    });
  });
}

async function launchPositiveRobotAnimation(itemOrContext, phase='end', reason='positive-robot'){
  if(!shouldUseRobotAnimationForInteraction(itemOrContext, phase)) return {skipped:'robot_animation_not_needed'};
  const emotion = positiveActivityEmotion(phase, itemOrContext);
  const title = itemOrContext?.title || itemOrContext?.id || 'actividad';
  const label = phase === 'start' ? 'Inicio positivo' : 'Cierre positivo';

  if(phase !== 'start') setExecuting(label, `Animación positiva: ${emotion}`);

  logClient('info','robot',`${label} aleatorio de actividad con robot: ${emotion}`,{
    reason,
    phase,
    activity:itemOrContext?.id,
    title,
    chat_mode:activeInteractionMode,
    autonomous_activity_mode:true,
    audio_enabled:shouldPlayPositiveAnimationAudio(phase)
  });

  // Audio oficial del movimiento positivo. Se reproduce desde navegador, igual que las emociones oficiales.
  firePositiveAnimationAudio(emotion, itemOrContext, phase, reason);

  if(phase !== 'start') await waitForRobotMotionSlot(`${phase}-positive-${itemOrContext?.id || 'activity'}`);

  return api('/api/robot/action',{
    method:'POST',
    body:JSON.stringify({
      emotion,
      text:null,
      motion_enabled:true,
      // El audio real de los movimientos positivos se reproduce en navegador con firePositiveAnimationAudio().
      // audio_enabled del backend queda en false para evitar doble audio/cola TTS.
      audio_enabled:false,
      return_to_neutral:true,
      layer:'manual',
      wait: phase === 'start'
        ? !!robotMotionPolicy.positive_action_wait_start
        : !!robotMotionPolicy.positive_action_wait_end,
      speech_motion:true
    })
  }).then(res=>{
    noteRobotMotionBusy({...(itemOrContext||{}), title:`${title} ${label}`});
    return res;
  }).catch(err=>{
    logClient('warn','robot',`No se pudo lanzar ${label.toLowerCase()}: ${String(err)}`,{emotion,activity:itemOrContext?.id});
    return {error:String(err)};
  });
}

async function launchPositiveClosingRobotAnimation(itemOrContext, reason='positive-close'){
  if(!shouldPositiveCloseShortActivity(itemOrContext)) return {skipped:'not_short_or_no_robot'};
  return launchPositiveRobotAnimation(itemOrContext, 'end', reason);
}

async function launchPositiveOpeningRobotAnimation(itemOrContext, reason='positive-start'){
  if(!shouldUseRobotAnimationForInteraction(itemOrContext, 'start')) return {skipped:'robot_animation_not_needed'};
  return launchPositiveRobotAnimation(itemOrContext, 'start', reason);
}




async function firePositiveOpeningRobotAnimationVisible(itemOrContext, reason='positive-start'){
  // Inicio visible: movimiento + audio oficial en paralelo, sin bloquear toda la duración.
  logClient('info','robot','Animación positiva INICIO visible solicitada',{activity:itemOrContext?.id,title:itemOrContext?.title,reason});
  launchPositiveOpeningRobotAnimation(itemOrContext, reason)
    .then(res=>logClient('debug','robot','Animación positiva INICIO lanzada',{activity:itemOrContext?.id,result:res}))
    .catch(err=>logClient('warn','robot',`Inicio positivo visible falló: ${String(err)}`,{activity:itemOrContext?.id, reason}));
  await sleep(Number(robotMotionPolicy.visible_start_wait_ms || 850));
  return {queued:true, visible_wait_ms:Number(robotMotionPolicy.visible_start_wait_ms || 850)};
}

function firePositiveOpeningRobotAnimation(itemOrContext, reason='positive-start'){
  // No bloquea el arranque de la actividad. Si el robot/daemon tarda, la actividad continúa.
  logClient('info','robot','Animación positiva INICIO solicitada',{activity:itemOrContext?.id,title:itemOrContext?.title,reason});
  launchPositiveOpeningRobotAnimation(itemOrContext, reason)
    .then(res=>logClient('debug','robot','Animación positiva INICIO lanzada',{activity:itemOrContext?.id,result:res}))
    .catch(err=>logClient('warn','robot',`Inicio positivo no bloqueante falló: ${String(err)}`,{activity:itemOrContext?.id, reason}));
}

function firePositiveClosingRobotAnimation(itemOrContext, reason='positive-close'){
  // Cierre positivo con movimiento + audio oficial. No bloquea el siguiente turno.
  logClient('info','robot','Animación positiva FINAL solicitada',{activity:itemOrContext?.id,title:itemOrContext?.title,reason});
  launchPositiveClosingRobotAnimation(itemOrContext, reason)
    .then(async res=>{
      logClient('debug','robot','Animación positiva FINAL lanzada',{activity:itemOrContext?.id,result:res});
      const ms = Number(robotMotionPolicy.visible_end_wait_ms || 0);
      if(ms > 0) await sleep(ms);
    })
    .catch(err=>logClient('warn','robot',`Cierre positivo no bloqueante falló: ${String(err)}`,{activity:itemOrContext?.id, reason}));
}

function isTurnShortActivity(item){
  if(!item) return false;
  return !!item.awaitUser || ['saludo_corto','si_corto','no_corto','turno_corto','ayuda_corta','despedida_corta','animal_corto','palabra_corta','calma_corta','preguntar_nombre','pedir_turno','pedir_ayuda','buscar_palabra','sinonimos','opuestos','completar_frase','frase_corta'].includes(item.id);
}

function isMicroInputActivity(item){
  return !!(item && (item.awaitUser || item.requiresInput || activityNeedsMicroPrompt(item) || isTurnShortActivity(item)));
}
function noteRobotMotionBusy(item, audioResult=null){
  const now=performance.now();
  const title=(item?.title||'').toLowerCase();
  let estimated=1300;
  if(item?.recordedAudio){
    estimated=2400;
    if(title.includes('baile')) estimated=4200;
    if(title.includes('aburrido') || title.includes('pensar')) estimated=5200;
    if(title.includes('curiosidad') || title.includes('calma')) estimated=3300;
  }
  robotMotionBusyUntilMs=Math.max(robotMotionBusyUntilMs, now+estimated);
  logClient('debug','robot',`Ventana antisolape movimiento hasta ${Math.round(robotMotionBusyUntilMs-now)} ms`,{action:item?.id,estimated});
}
async function waitForRobotMotionSlot(reason='motion-slot'){
  const now=performance.now();
  const waitMs=Math.max(0, robotMotionBusyUntilMs-now);
  if(waitMs>60){
    setExecuting('Esperando movimiento anterior',`Pausa antisolape ${Math.round(waitMs)} ms`);
    logClient('info','robot',`Esperando para evitar solape de movimiento: ${Math.round(waitMs)} ms`,{reason});
    await sleep(Math.min(waitMs, 5200));
  }
}


// Construye el contexto que permite continuar una actividad sin perder coherencia.
function buildActivityContext(item, step=null){
  if(!item) return null;
  return {
    id:item.id || '',
    title:item.title || 'Actividad',
    subtitle:item.subtitle || '',
    prompt:item.text || step?.text || '',
    step_label:step?.label || '',
    step_text:step?.text || '',
    vocabulary_hint:currentVocabularyHint || vocabularyHintForActivity(item),
    turn_index:activityTurnIndex + 1,
  };
}
// Guarda la actividad actual para que la siguiente respuesta del usuario se entienda dentro de ese flujo.
function rememberActivityContext(item, step=null){
  currentActivityContext = buildActivityContext(item, step);
  lastActivityContext = currentActivityContext;
  activityTurnIndex += 1;
  return currentActivityContext;
}
function clearActivityContext(reason='clear'){
  currentActivityContext = null;
  activityTurnIndex = 0;
  logClient?.('debug','activity',`Contexto de actividad limpiado: ${reason}`);
}
// Envuelve la respuesta del usuario con instrucciones para que Ollama continúe la actividad correcta.
function enrichUserTextWithActivityContext(text, context){
  if(!context) return text;
  return [
    '[CONTEXTO_ACTIVIDAD]',
    `Actividad: ${context.title}`,
    context.subtitle ? `Tipo: ${context.subtitle}` : '',
    context.prompt ? `Consigna de Ritxi: ${context.prompt}` : '',
    context.step_label ? `Paso: ${context.step_label}` : '',
    context.step_text ? `Texto del paso: ${context.step_text}` : '',
    `Respuesta del usuario: ${text}`,
    'Instrucción: continúa esta actividad concreta con una frase corta de refuerzo/corrección y una sola pregunta relacionada.',
    '[/CONTEXTO_ACTIVIDAD]'
  ].filter(Boolean).join('\n');
}
// Resuelve localmente actividades cerradas para evitar llamadas lentas a Ollama cuando no son necesarias.
function fastActivityReply(text, context){
  if(!context) return null;
  const id = context.id || '';

  if((isMaxCreativeActivityContext(context) || isLongInteractionActivityContext(context)) && userAskedToEndActivity(text)){
    return {text:'De acuerdo, cerramos esta actividad. Cuando quieras empezamos otra.', emotion:'calma', endContext:true};
  }

  if(isMaxCreativeActivityContext(context)){
    return null;
  }

  if(OPEN_CONVERSATION_ACTIVITY_IDS.has(id)){
    return null; // Conversación abierta: usar IA local/Ollama, no respuesta rápida genérica.
  }
  const t = (text || '').trim();
  const lower = t.toLowerCase();
  const said = t ? `“${t}”` : 'tu respuesta';

  if(REVIEWED_ANIMAL_ACTIVITY_IDS.has(id) || id.includes('animal') || context.vocabulary_hint === 'animal'){
    if(lower.includes('perro')) return {text:chooseActivityReply(id,['Correcto, es un perro. Muy bien escuchado.','Sí, perro. Has reconocido el sonido.','Muy bien, era un perro. Probamos otro cuando quieras.']), emotion:'celebracion'};
    if(lower.includes('gato')) return {text:chooseActivityReply(id,['Correcto, es un gato. Muy bien.','Sí, era un gato. Has escuchado muy bien.','Muy bien, gato. Seguimos con otro sonido.']), emotion:'celebracion'};
    if(lower.includes('vaca')) return {text:chooseActivityReply(id,['Correcto, es una vaca. Muy bien.','Sí, vaca. Has acertado.','Muy bien, era una vaca.']), emotion:'celebracion'};
    return {text:chooseActivityReply(id,[`He oído ${said}. Buen intento. Escuchamos otra vez con calma.`,`Vale, has dicho ${said}. Vamos a probar otro sonido.`,`Gracias. Me quedo con ${said}. Seguimos escuchando.`]), emotion:'animo'};
  }

  if(id === 'completar_frase'){
    const completed = lower.includes('ayudar') ? 'Por favor, ¿me puedes ayudar?' : `Por favor, ¿me puedes ${t}?`;
    return {text:chooseActivityReply(id,[`Muy bien. La frase queda: ${completed}.`,`Perfecto. Has completado: ${completed}.`,`Bien hecho. Podemos decirlo así: ${completed}.`]), emotion:'celebracion'};
  }

  if(id === 'frase_corta'){
    return {text:chooseActivityReply(id,[`Bien. Has dicho ${said}. Es una frase corta.`,`Muy bien, ${said} sirve como frase corta.`,`Te he entendido: ${said}. Buen trabajo con la frase.`]), emotion:'animo'};
  }

  if(id === 'buscar_palabra'){
    return {text:chooseActivityReply(id,[`Muy bien, ${said} puede ser la palabra que buscábamos.`,`Bien pensado: ${said}. Seguimos con otra pista.`,`Has respondido ${said}. Buen intento de vocabulario.`]), emotion:'animo'};
  }
  if(id.includes('sinonimos')){
    return {text:chooseActivityReply(id,[`Bien, ${said} puede funcionar como palabra parecida.`,`Buen intento con ${said}. Buscamos otra palabra parecida después.`,`Te he oído: ${said}. Seguimos practicando sinónimos.`]), emotion:'animo'};
  }
  if(id.includes('opuestos')){
    return {text:chooseActivityReply(id,[`Bien, ${said} puede ser un opuesto.`,`Buen intento. Has dicho ${said}.`,`Seguimos con opuestos. Me quedo con ${said}.`]), emotion:'animo'};
  }

  if(id === 'preguntar_nombre'){
    const name = t.replace(/^me llamo\s+/i,'').replace(/^soy\s+/i,'').trim();
    return {text:chooseActivityReply(id,[`Encantado, ${name || t}. Gracias por decir tu nombre.`,`Hola, ${name || t}. Me alegra conocerte.`,`Muy bien, ${name || t}. Ya sé cómo llamarte en esta actividad.`]), emotion:'saludo'};
  }

  if(['saludo_corto','presentacion'].includes(id)){
    return {text:chooseActivityReply(id,[`Hola, te he escuchado. Buen saludo.`,`Muy bien, has saludado con claridad.`,`Gracias por saludar. Seguimos hablando despacio.`]), emotion:'saludo'};
  }
  if(['despedida_corta','despedida_guiada'].includes(id)){
    return {text:chooseActivityReply(id,[`Muy bien, esa despedida ha sido clara.`,`Gracias. Has practicado muy bien la despedida.`,`Perfecto, así podemos despedirnos con educación.`]), emotion:'saludo'};
  }
  if(['pedir_turno','turno_corto','respetar_turno_dinamico'].includes(id)){
    return {text:chooseActivityReply(id,[`Muy bien, has pedido turno de forma adecuada.`,`Perfecto. Has esperado y pedido turno.`,`Buen trabajo. Pedir turno ayuda a conversar mejor.`]), emotion:'animo'};
  }
  if(['pedir_ayuda','ayuda_corta','ensayo_pedir_ayuda'].includes(id)){
    return {text:chooseActivityReply(id,[`Muy bien, has practicado pedir ayuda.`,`Perfecto. Pedir ayuda está muy bien cuando la necesitamos.`,`Te he entendido. Esa es una buena forma de pedir ayuda.`]), emotion:'animo'};
  }
  if(['si_corto','no_corto'].includes(id)){
    return {text:chooseActivityReply(id,[`Muy bien, has respondido de forma clara.`,`Te he oído. Respuesta clara.`,`Perfecto, has practicado una respuesta breve.`]), emotion:'asentir'};
  }

  if(['ritmo_palmas','palmas_lentas','palmas_rapidas','instrumento_tambor'].includes(id)){
    return {text:chooseActivityReply(id,[`Muy bien, has seguido el ritmo.`,`Buen turno. Has respondido al ritmo.`,`Genial, seguimos con atención y ritmo.`]), emotion:'celebracion'};
  }
  if(['cantar_saludo','baile_suave','baile_divertido','imitame','eco_ritxi'].includes(id)){
    return {text:chooseActivityReply(id,[`Muy bien, has participado en el juego.`,`Genial, has hecho tu turno.`,`Buen trabajo, seguimos con otro juego corto.`]), emotion:'celebracion'};
  }

  if(['emocion_nombre','emociones_caras','elegir_emocion','validar_emocion'].includes(id)){
    return {text:chooseActivityReply(id,[`Gracias por decirlo. Esa emoción es importante.`,`Te he escuchado. Podemos hablar de esa emoción con calma.`,`Muy bien, has puesto palabras a una emoción.`]), emotion:'empatia', keepContext:false};
  }
  if(['pausa_sensorial','frase_segura','pedir_descanso','escucha_y_repite','rutina_primero_despues','ensayo_decidir'].includes(id)){
    return {text:chooseActivityReply(id,[`Muy bien. Has practicado una forma útil de comunicarte.`,`Buen trabajo. Esa frase puede ayudarte.`,`Te he entendido. Lo has hecho paso a paso.`]), emotion:'calma'};
  }

  if(id === 'explicar_imagen'){
    return {text:chooseActivityReply(id,[`Muy bien. Has descrito ${said}. Ahora añade una emoción.`,`Bien. Primero una cosa: ${said}. Ahora dime una acción.`,`Te he escuchado: ${said}. Seguimos describiendo con otra idea.`]), emotion:'escucha_activa', keepContext:true};
  }
  if(['historia_turnos','cuento_interactivo','final_historia','personajes','recordar_historia','cuento_corto'].includes(id) || id.includes('historia') || id.includes('cuento')){
    return {text:chooseActivityReply(id,[`Buena idea: ${said}. Seguimos la historia: el robot dio un paso adelante. ¿Qué pasó después?`,`Me gusta: ${said}. Entonces apareció una nueva pista. ¿Qué hacemos ahora?`,`Perfecto, añadimos ${said} a la historia. Ahora falta el siguiente paso.`]), emotion:'curioso', keepContext:true};
  }

  if(['escucha_activa','escuchar','vamos_hablar'].includes(id)){
    return {text:chooseActivityReply(id,[`Te he escuchado: ${said}. Gracias por contármelo.`,`Entiendo. Has dicho ${said}. Seguimos con calma.`,`Gracias. Me quedo con tu frase: ${said}.`]), emotion:'escucha_activa'};
  }

  return {text:chooseActivityReply(id,[`Te he escuchado: ${said}. Seguimos con esta actividad.`,`Gracias por responder. Has dicho ${said}.`,`Muy bien, continuamos desde tu respuesta: ${said}.`]), emotion:'animo'};
}
// Envía una respuesta local rápida y libera la interfaz sin esperar al TTS.
async function respondFastActivityLocally(text, context){
  const reply = fastActivityReply(text, context);
  if(!reply) return false;
  addChat('bot', reply.text, `actividad: ${context.title}`);
  $('currentState').textContent='Listo para conversar';
  $('currentSubState').textContent='Respuesta rápida de actividad';
  setExecuting(`Respuesta rápida: ${context.title}`,'Actividad resuelta al instante; IA no necesaria');
  logClient('info','activity',`Respuesta rápida local para ${context.id}`,{text,reply});

  // Importante: no esperamos a que termine TTS. Así la respuesta local es realmente rápida
  // y no bloquea el botón de texto ni el siguiente turno.
  if(flags().tts){
    speakWithBrowser(reply.text).catch(err=>logClient('warn','tts',`TTS local rápido con aviso: ${String(err)}`));
  }

  if(reply.endContext){
    clearActivityContext('actividad finalizada por usuario');
    firePositiveClosingRobotAnimation(context, 'respuesta rápida local endContext');
  }else if(reply.keepContext){
    activityAwaitingUser = true;
    activityAutoListenAfterBot = true;
    $('message').placeholder = 'Seguimos la actividad: habla o escribe aquí...';
    setMicStatus('Seguimos la actividad. Puedes responder por micro o texto.');
    // Abrimos micro después, pero no bloqueamos escritura.
    setTimeout(()=>scheduleMicOpenAfterSpeech({autoSend:true, reason:'actividad-local-continua'}), 650);
  }else{
    clearActivityContext('respuesta rápida local');
    firePositiveClosingRobotAnimation(context, 'respuesta rápida local finalizada');
  }
  enableTextInputAlways('respuesta rápida local');
  return true;
}

// Abre un turno de usuario después de una actividad que requiere respuesta.
async function promptUserAfterActivity(item,{autoListen=true,autoSend=true}={}){
  activityAwaitingUser = true;
  activityAutoListenAfterBot = true;
  manualMicStopLock = false;
  realtimeSending = false;
  currentVocabularyHint = vocabularyHintForActivity(item);
  rememberActivityContext(item);

  const hint = item?.title ? `Tu turno después de: ${item.title}` : 'Tu turno';
  setExecuting(hint,'Habla ahora o escribe y pulsa enviar');
  $('message').placeholder = 'Tu turno: habla o escribe aquí...';
  enableTextInputAlways('turno actividad');

  const hintText = currentVocabularyHint && !isOpenVocabularyHint(currentVocabularyHint)
    ? `Tu turno: escuchando vocabulario esperado (${currentVocabularyHint}). También puedes escribir y pulsar ➤.`
    : (currentVocabularyHint === 'open_name'
      ? 'Tu turno: di tu nombre despacio. También puedes escribirlo y pulsar ➤.'
      : (currentVocabularyHint === 'open_text' || currentVocabularyHint === 'open_phrase'
        ? 'Tu turno: respuesta libre. Puedes hablar con una frase corta o escribir y pulsar ➤.'
        : 'Tu turno: puedes hablar ahora. El micro se mantiene activo hasta parar o salir de la actividad.'));
  setMicStatus(hintText);

  logClient('info','activity','Turno de usuario activado tras actividad',{
    item:item?.id,
    autoListen,
    autoSend,
    vocabulary_hint:currentVocabularyHint,
    flags:flags()
  });

  if(autoListen){
    // Las actividades con turno pueden pedir micro aunque el chat esté en modo Texto + IA.
    // Si el usuario no concede/acepta micro, siempre queda la respuesta por texto.
    unlockMicForActivity(`turno-actividad:${item?.id||'actividad'}`);
    const ok = await ensureMicrophoneReady({ask:true, reason:`turno-actividad:${item?.id||'actividad'}`});
    if(!ok){
      setMicStatus('No se pudo activar el micro. Escribe la respuesta y pulsa ➤.');
      return;
    }
    await startAlwaysOnMic({reason:`turno-actividad:${item?.id||'actividad'}`, autoSend, force:true});
  } else {
    setMicStatus('Tu turno: responde escribiendo en el chat y pulsa ➤.');
  }
}


function setShortCycleStatus(text){
  const el = $('shortCycleStatus');
  if(el) el.textContent = text;
}
function updateShortCycleButtons(mode=null){
  const active=!!shortCycleActive;
  $('shortCycleTurnBtn')?.classList.toggle('active-cycle',active);
  if($('shortCycleTurnBtn')) $('shortCycleTurnBtn').textContent=active ? '■ Parar ciclo con turnos' : '▶ Ciclo corto';
  if($('shortCycleNextBtn')) $('shortCycleNextBtn').disabled = !(active && shortCycleWaitingForNext);
}

function getShortCycleItems(){
  const all=[
    ...SHORT_ACTIVITY_GROUPS.flatMap(g=>g.items),
    ...effectiveGameGroups().flatMap(g=>g.items),
    ...DIRECT_ACTION_GROUPS.flatMap(g=>g.items),
    ...ACTION_GROUPS.flatMap(g=>g.items),
  ];
  const byId=new Map(all.map(i=>[i.id,i]));
  const preferred=[
    'saludo_corto','animal_corto','cantar_saludo','ritmo_palmas','palmas_lentas',
    'palmas_rapidas','baile_suave','baile_divertido','imitame','chiste',
    'cuento_corto','despedida_corta'
  ];
  const selected=preferred.map(id=>byId.get(id)).filter(Boolean);
  if(selected.length) return selected;
  return all.filter(item=>item && item.text).slice(0,10);
}

function waitForNextShortCycle(item=null){
  shortCycleWaitingForNext=true;
  const btn=$('shortCycleNextBtn');
  if(btn) btn.disabled=false;
  updateShortCycleButtons('turn');
  updateShortCycleButtons('turn');
  const startedTurn = lastUserTurnTs;
  promptUserAfterActivity(item,{autoListen:true,autoSend:true});
  return new Promise(resolve=>{
    let done=false;
    const finish=(reason='next')=>{ 
      if(done) return;
      done=true;
      shortCycleWaitingForNext=false;
      if(btn) btn.disabled=true;
      updateShortCycleButtons(shortCycleMode);
      updateShortCycleButtons(shortCycleMode);
      if(shortCycleTimer){ clearTimeout(shortCycleTimer); shortCycleTimer=null; }
      logClient('info','cycle',`Ciclo corto continúa por: ${reason}`);
      resolve();
    };
    const handler=()=>{ btn?.removeEventListener('click',handler); finish('boton-siguiente'); };
    btn?.addEventListener('click',handler,{once:true});
    const poll=setInterval(()=>{
      if(!shortCycleActive){ clearInterval(poll); btn?.removeEventListener('click',handler); finish('ciclo-parado'); return; }
      if(lastBotTurnDoneTs > startedTurn){ clearInterval(poll); btn?.removeEventListener('click',handler); setTimeout(()=>finish('respuesta-usuario-y-ritxi'),900); }
    },500);
    shortCycleTimer=setTimeout(()=>{ clearInterval(poll); btn?.removeEventListener('click',handler); finish('timeout-turno'); }, 22000);
  });
}
// Ejecuta el ciclo con turnos: una actividad breve y espera de respuesta/Siguiente.
// Ejecuta un ciclo corto de fichas y espera respuesta/Siguiente cuando corresponde.
async function runShortCycle(mode='turn'){
  if(shortCycleActive){
    stopShortCycle();
    return;
  }

  const items=getShortCycleItems();
  if(!items.length){
    setShortCycleStatus('No hay actividades disponibles para el ciclo.');
    logClient('warn','cycle','No hay actividades disponibles.');
    return;
  }

  shortCycleActive=true;
  shortCycleMode='turn';
  shortCycleIndex=0;
  shortCycleWaitingForNext=false;
  updateShortCycleButtons('turn');

  setShortCycleStatus(`Ciclo corto activo: ${items.length} actividades. Ritxi espera respuesta o Siguiente.`);
  logClient('info','cycle','Ciclo corto iniciado',{items:items.map(i=>i.id)});

  while(shortCycleActive && items.length){
    const item=items[shortCycleIndex % items.length];
    shortCycleIndex += 1;
    setShortCycleStatus(`Turnos activo · ${((shortCycleIndex-1)%items.length)+1}/${items.length}: ${item.title}.`);

    const btn=document.querySelector(`[data-action-id="${item.id}"]`);
    await executeAction(item,btn,{fromCycle:true});
    if(!shortCycleActive) break;

    await waitForNextShortCycle(item);
  }
  stopShortCycle();
}

function stopShortCycle(){
  shortCycleActive=false;
  shortCycleWaitingForNext=false;
  activityAutoListenAfterBot=false;
  if(shortCycleTimer){ clearTimeout(shortCycleTimer); shortCycleTimer=null; }
  updateShortCycleButtons(null);
  setShortCycleStatus('Ciclo corto: usa fichas breves; Siguiente avanza cuando espera respuesta.');
  clearCurrentActionButton();
}



const OPEN_NAME_ACTIVITY_IDS = new Set([
  'preguntar_nombre'
]);

const OPEN_NATURAL_ACTIVITY_IDS = new Set([
  // Conversación natural o respuesta libre
  'presentacion','escuchar','vamos_hablar','explicar_imagen','historia_turnos','cuento_interactivo',
  'cuento_corto','final_historia','personajes','recordar_historia','chiste',

  // Tutor/apoyo emocional: frases abiertas, no vocabulario cerrado
  'validar_emocion','pausa_sensorial','frase_segura','pedir_descanso','ensayo_decidir',
  'rutina_primero_despues','escucha_y_repite','cierre_calma','refuerzo_especifico',
  'ensayo_pedir_ayuda','elegir_emocion','emocion_nombre','semáforo_emocional',
  'respiracion_guiada',

  // Frases funcionales o lenguaje abierto
  'frase_corta','completar_frase','despedida_guiada','pedir_ayuda','pedir_turno',
  'turno_corto','ayuda_corta',

  // Juegos que esperan frase/imitación, no lista cerrada
  'eco_ritxi','imitame'
]);

const CLOSED_ANIMAL_ACTIVITY_IDS = new Set([
  'animal_corto','animal_perro','animal_gato','animal_vaca','juego_animales'
]);

const CLOSED_SHORT_ACTIVITY_IDS = new Set([
  'palabra_corta','buscar_palabra','sinonimos','opuestos'
]);

const CLOSED_YESNO_ACTIVITY_IDS = new Set([
  'si_corto','no_corto','elegir_opcion'
]);

function isOpenVocabularyHint(hint){
  return hint === 'open_name' || hint === 'open_text' || hint === 'open_phrase';
}

// Decide si una actividad usa vocabulario cerrado o respuesta abierta.
// Decide qué tipo de vocabulario usa una actividad: cerrado, abierto o nombre.
function vocabularyHintForActivity(item){
  if(!item) return '';
  const id = item.id || '';
  const title = (item.title || '').toLowerCase();

  if(id === 'preguntar_nombre' || OPEN_NAME_ACTIVITY_IDS.has(id) || id.includes('nombre') || title.includes('cómo te llamas')){
    return 'open_name';
  }
  if(REVIEWED_ANIMAL_ACTIVITY_IDS.has(id) || CLOSED_ANIMAL_ACTIVITY_IDS.has(id)){
    return 'animal';
  }
  if(REVIEWED_YESNO_ACTIVITY_IDS.has(id) || CLOSED_YESNO_ACTIVITY_IDS.has(id)){
    return 'yes_no';
  }
  if(REVIEWED_SHORT_ACTIVITY_IDS.has(id)){
    return 'short';
  }
  if(REVIEWED_TURN_ACTIVITY_IDS.has(id) || OPEN_NATURAL_ACTIVITY_IDS.has(id)){
    return 'open_text';
  }

  if(item.vocabularyHint){
    if(item.vocabularyHint === 'open_name' || item.vocabularyHint === 'open_text') return item.vocabularyHint;
    return item.vocabularyHint;
  }
  if(CLOSED_ANIMAL_ACTIVITY_IDS.has(id) || id.includes('animal') || title.includes('animal')) return 'animal';
  if(CLOSED_SHORT_ACTIVITY_IDS.has(id) || id.includes('_corto') || title.includes('corto') || id.includes('palabra')) return 'short';
  if(id.includes('preguntar') || id.includes('escuchar') || title.includes('?') || title.includes('pregunta')) return 'open_text';
  return '';
}

// Determina si una ficha debe abrir turno de usuario por micro/texto.
function activityNeedsMicroPrompt(item){
  if(!item) return false;
  if(item.askUser || item.requiresInput || item.awaitUser) return true;
  const id = item.id || '';
  const title = (item.title || '').toLowerCase();
  const text = (item.text || '').toLowerCase();
  if(REVIEWED_TURN_ACTIVITY_IDS.has(id)) return true;

  const turnPhrases = [
    'ahora te toca','tu turno','puedes decir','puedes responder','qué crees','qué animal',
    'dime ','di ','inventa','continúa','repite','elige','complétala','inténtalo','¿'
  ];
  if(turnPhrases.some(p => title.includes(p) || text.includes(p))) return true;

  return id.includes('_corto') || id.includes('preguntar') || id.includes('pedir_') ||
    id.includes('sinonimos') || id.includes('opuestos') || id.includes('frase') ||
    id.includes('animal') || id.includes('historia') || id.includes('cuento') ||
    id.includes('emocion') || id.includes('turno');
}
async function confirmMicForActivity(item){
  if(!activityNeedsMicroPrompt(item)) return true;
  if(micPermissionGranted && flags().input_microphone && flags().stt) return true;
  const ok = confirm(`La actividad "${item.title}" necesita que puedas responder. ¿Quieres activar el micrófono?\\n\\nSi eliges Cancelar, podrás responder escribiendo en el chat.`);
  if(!ok){
    setMicStatus('Actividad con respuesta por texto: escribe en el chat y pulsa ➤.');
    return false;
  }
  unlockMicForActivity(`actividad:${item.id}`);
  return await ensureMicrophoneReady({ask:true, reason:`actividad:${item.id}`});
}


function cardForcesRobot(item){
  // Las fichas de clic directo imponen su propio modo:
  // si tienen emoción/movimiento/actividad guiada, no dependen del modo de chat.
  if(!item) return false;
  if(item.robotMotion === false || item.noRobot === true) return false;
  if(item.recordedAudio || item.emotion) return true;
  if(Array.isArray(item.steps) && item.steps.some(s=>s && (s.emotion || s.sound || s.text))) return true;
  return false;
}

function cardForcesSound(item){
  // Audio de ficha: sonidos oficiales, efectos o textos de actividad.
  // Esto no es lo mismo que TTS conversacional del chat.
  if(!item) return false;
  if(item.audio === false || item.noAudio === true) return false;
  if(item.recordedAudio || item.sound || item.text) return true;
  if(Array.isArray(item.steps) && item.steps.some(s=>s && (s.recordedAudio || s.sound || s.text))) return true;
  return false;
}

function cardRuntime(item){
  // Runtime propio de ficha/actividad: no usa el modo conversacional del chat.
  // Si la ficha necesita robot, audio o voz, se fuerza aquí.
  return {
    output_text:true,
    robot_motion:cardForcesRobot(item),
    output_audio:cardForcesSound(item),
    tts:cardForcesSound(item),
    speech_motion:cardForcesRobot(item),
  };
}

async function speakWithBrowserForCard(text,item){
  if(!text) return;
  // Voz de actividad/ficha: se fuerza aunque el chat esté en modo texto.
  await speakWithBrowser(text,{force:true, afterListen:false, reason:`card-${item?.id||'activity'}`});
}

async function runActivity(item,btn=null,options={}){
  const token=actionSequenceId;
  markActionButton(btn,item);
  const runtime = activityRuntimeMode(item);
  const micOkForActivity = await confirmMicForActivity(item);
  try{
    setExecuting(item.title,item.subtitle||'Actividad guiada con voz + movimiento');
    logClient('info','activity',`Actividad iniciada: ${item.title}`,{...item, card_runtime:runtime, chat_mode:activeInteractionMode, autonomous_activity_mode:true});
    if(runtime.robot_motion) await firePositiveOpeningRobotAnimationVisible(item, 'actividad guiada inicio'); else logClient('warn','robot','Actividad sin animación de inicio por runtime',{id:item.id,title:item.title,runtime});
    if(runtime.output_text) addChat('bot',`▶️ ${item.title}: ${item.intro || 'vamos a empezar.'}`,'actividad');
    const steps=item.steps||[];
    for(let i=0;i<steps.length;i++){
      const step=steps[i];
      if(step.wait){ await sleep(step.wait); continue; }
      const label=step.label||`Paso ${i+1}`;
      setExecuting(`${item.title}: ${label}`, step.subtitle || 'Actividad en curso');
      if(step.chat && runtime.output_text) addChat('bot',step.chat,`actividad: ${label}`);
      if(step.sound) await playSyntheticSound(step.sound, step.durationMs || 900);
      const emotion=step.emotion || item.emotion || 'juego';
      if(runtime.robot_motion){
        await api('/api/robot/action',{method:'POST',body:JSON.stringify({emotion,text:null,motion_enabled:true,audio_enabled:false,return_to_neutral:false,layer:'manual',wait:false,speech_motion:runtime.speech_motion})}).catch(err=>logClient('warn','robot',`Movimiento de actividad con aviso: ${String(err)}`));
      }
      if(step.text) await speakWithBrowserForCard(step.text,item);
      const stepText = (step.text || '').toLowerCase();
      const stepNeedsUser = step.askUser || step.requiresInput || step.awaitUser ||
        stepText.includes('tu turno') || stepText.includes('ahora es tu turno') ||
        stepText.includes('qué crees') || stepText.includes('continúa') || stepText.includes('puedes responder');
      if(stepNeedsUser){
        await promptUserAfterActivity({...item, id:item.id, title:item.title, vocabularyHint:vocabularyHintForActivity(item) || 'open_text'}, {autoListen:true, autoSend:true});
      }
      if(step.recordedAudio) await playOfficialRecordedAudio(step.emotion || item.emotion, step.label || item.title, {force:true, wait:false});
      if(step.pauseAfter) await sleep(step.pauseAfter);
    }
    if(runtime.robot_motion && activeInteractionMode !== 'text'){ await api('/api/robot/action',{method:'POST',body:JSON.stringify({emotion:'neutral',text:null,motion_enabled:activeInteractionMode !== 'text',audio_enabled:false,return_to_neutral:false,layer:'manual',wait:false,speech_motion:false})}).catch(()=>{}); }
    setExecuting(item.title,'Actividad finalizada');
    const willAskUserAfterActivity = (isTurnShortActivity(item) || item.awaitUser || item.requiresInput || activityNeedsMicroPrompt(item)) && !options.fromCycle;
    if(willAskUserAfterActivity){
      await promptUserAfterActivity(item,{autoListen:true,autoSend:true});
    }else{
      firePositiveClosingRobotAnimation(item, 'actividad corta guiada finalizada');
    }
    logClient('info','activity',`Actividad finalizada: ${item.title}`);
  } catch(err){
    logClient('error','activity',`Error en actividad ${item?.title || ''}: ${String(err)}`);
  } finally {
    finishActionButton(btn,token);
  }
}
// Ejecuta una tarjeta: movimiento, audio, texto, pasos y posible turno de usuario.
// Ejecuta una tarjeta: emoción, movimiento, audio, texto, pasos y turno si procede.

function recordedEmotionNoTtsFallback(item, audioResult){
  // Las emociones oficiales no deben decir "Ritxi reproduce..." ni frases similares.
  // Regla: si existe WAV, suena el WAV. Si no existe/falla, solo animación del robot.
  if(!item?.recordedAudio) return false;
  if(audioResult?.started) return false;
  const reason = audioResult?.error || audioResult?.skipped || audioResult?.ended || 'wav_not_started';
  logClient('warn','audio',`audio oficial no disponible; solo animación para ${item.emotion}`,{item:item.id,title:item.title,reason,audioResult});
  setMicStatus(`Emoción ${item.title}: audio oficial no disponible. Solo animación del robot.`);
  return true;
}


function isOfficialEmotionCard(item){
  // Tarjetas de emociones oficiales: no son chat, no dependen de modo conversacional.
  return !!(item && item.recordedAudio && item.emotion && !item.steps);
}

async function executeOfficialEmotionCard(item, btn=null, options={}){
  // Regla funcional:
  // - Siempre intentar audio oficial.
  // - Siempre enviar animación al robot/simulador.
  // - No usar TTS de sustitución si el WAV falla.
  // - No depender de Texto+IA, Micro+IA, Texto+IA+Robot o Completo.
  markActionButton(btn,item);
  const token = actionSequenceId;
  const emotionId = item.emotion || item.id || 'neutral';
  setExecuting(item.title || emotionId, 'Emoción oficial: WAV + animación independiente del modo');
  logClient('info','emotion',`Emoción oficial lanzada independiente del modo: ${emotionId}`,{
    id:item.id,
    title:item.title,
    chat_mode:activeInteractionMode,
    recordedAudio:!!item.recordedAudio
  });

  if(!isTurnShortActivity(item) && !item.awaitUser && !item.requiresInput){
    currentVocabularyHint='';
    activityAutoListenAfterBot=false;
    activityAwaitingUser=false;
    if(micAlwaysOn) await stopAlwaysOnMic('emocion-oficial-sin-turno');
    manualMicStopLock=false;
  }

  const audioPromise = playOfficialRecordedAudio(emotionId, item.title || emotionId, {force:true, wait:false, official:true});
  const robotPromise = api('/api/robot/action',{
    method:'POST',
    body:JSON.stringify({
      emotion:emotionId,
      text:null,
      motion_enabled:true,
      audio_enabled:false,
      return_to_neutral:true,
      layer:'manual',
      wait:true,
      speech_motion:true
    })
  }).catch(err=>({error:String(err)}));

  const [audioResult, motionResult] = await Promise.all([audioPromise, robotPromise]);

  noteRobotMotionBusy(item, audioResult);

  if(!audioResult?.started){
    recordedEmotionNoTtsFallback(item, audioResult);
  }

  if(motionResult?.error){
    setMicStatus(`Emoción ${item.title}: error animación robot. Revisa logs.`);
    logClient('error','robot',`Animación oficial no ejecutada: ${emotionId}`,motionResult);
  }else{
    logClient('info','robot',`Animación oficial ejecutada: ${emotionId}`,motionResult);
    if(audioResult?.started){
      setMicStatus(`Emoción ${item.title}: audio oficial y animación enviados.`);
    }else{
      setMicStatus(`Emoción ${item.title}: solo animación enviada; audio oficial no disponible.`);
    }
  }

  await refreshStatus().catch(()=>{});
}

async function executeAction(item,btn=null,options={}){
  if(uiActionBusy && !options.fromCycle && !options.queued){
    queueNextAction(item,btn);
    return;
  }
  const token=++actionSequenceId;
  uiActionBusy=true;
  try{
    if(isOfficialEmotionCard(item)){
      await executeOfficialEmotionCard(item,btn,options);
      return;
    }
    if(item.steps && Array.isArray(item.steps)) return await runActivity(item,btn,options);
    markActionButton(btn,item);
    const runtime = activityRuntimeMode(item);
    const itemHintForTurn = vocabularyHintForActivity(item);
    if(!isTurnShortActivity(item) && !item.awaitUser && !item.requiresInput){ currentVocabularyHint=''; activityAutoListenAfterBot=false; activityAwaitingUser=false; if(micAlwaysOn) await stopAlwaysOnMic('accion-sin-turno'); manualMicStopLock=false; }
    else { currentVocabularyHint = itemHintForTurn; }
    setExecuting(item.title,item.subtitle);
    logClient('info','robot',`Acción/actividad lanzada: ${item.title}`,{...item, card_runtime:runtime, chat_mode:activeInteractionMode, autonomous_activity_mode:true});
    if(runtime.robot_motion) await firePositiveOpeningRobotAnimationVisible(item, 'actividad directa inicio'); else logClient('warn','robot','Acción sin animación de inicio por runtime',{id:item.id,title:item.title,runtime});
    const hasText = !!(item.text && item.text.trim());
    if(runtime.output_text && hasText) addChat('bot',item.text,`acción: ${item.title}`);
    const useRecordedAudio = !!item.recordedAudio;
    let officialAudioPromise = Promise.resolve({started:false, skipped:'not-recorded'});
    if(useRecordedAudio){
      officialAudioPromise = playOfficialRecordedAudio(item.emotion, item.title, {force:true, wait:false});
    }

    await waitForRobotMotionSlot(item?.id || 'executeAction');

    const motionResult = runtime.robot_motion
      ? await api('/api/robot/action',{method:'POST',body:JSON.stringify({
          emotion:item.emotion,
          text: null,
          motion_enabled:true,
          audio_enabled:false,
          return_to_neutral:true,
          layer:'manual',
          wait:false,
          speech_motion:runtime.speech_motion
        })}).catch(err=>({error:String(err)}))
      : {skipped:'card_without_robot'};

    const audioResult = await officialAudioPromise;
    noteRobotMotionBusy(item, audioResult);
    if(motionResult?.error) logClient('warn','robot',`Movimiento con aviso: ${motionResult.error}`,motionResult);
    else logClient('info','robot',`Movimiento procesado: ${item.emotion}`,motionResult);

    if(useRecordedAudio){
      if(!audioResult?.started){
        // No usar TTS de sustitución en emociones oficiales.
        // Si no hay WAV, solo queda la animación del robot.
        recordedEmotionNoTtsFallback(item, audioResult);
      }
    } else if(hasText){
      await speakWithBrowserForCard(item.text,item);
    }
    const willAskUserAfterAction = (isTurnShortActivity(item) || item.awaitUser || item.requiresInput || activityNeedsMicroPrompt(item)) && !options.fromCycle;
    if(willAskUserAfterAction){
      await promptUserAfterActivity(item,{autoListen:true,autoSend:true});
    }else{
      firePositiveClosingRobotAnimation(item, 'actividad directa finalizada');
    }
    await refreshStatus();
  } catch(err){
    logClient('error','action',`Error ejecutando acción ${item?.title || ''}: ${String(err)}`);
  } finally {
    finishActionButton(btn,token);
    uiActionBusy=false;
    if(!shortCycleActive) await runPendingActionIfAny();
  }
}
// Pinta tarjetas de acciones/actividades dentro de una pestaña.

const OPEN_CONVERSATION_ACTIVITY_IDS = new Set(['escucha_activa','escuchar','vamos_hablar','presentacion','validar_emocion','emocion_nombre','emociones_caras','elegir_emocion']);
const MAX_CREATIVE_ACTIVITY_IDS = new Set([
  'historia_turnos',
  'cuento_interactivo',
  'final_historia',
  'explicar_imagen',
  'elegir_emocion'
]);

const LONG_INTERACTION_ACTIVITY_IDS = new Set([
  'escucha_activa',
  'escuchar',
  'vamos_hablar',
  'presentacion',
  'validar_emocion',
  'emocion_nombre',
  'emociones_caras',
  'personajes',
  'recordar_historia',
  'cuento_corto',
  'ensayo_decidir'
]);

function isLongInteractionActivityContext(context){
  return !!(context && (
    LONG_INTERACTION_ACTIVITY_IDS.has(context.id || '') ||
    OPEN_CONVERSATION_ACTIVITY_IDS.has(context.id || '')
  ));
}

function interactionLevelForActivity(item){
  if(!item) return {level:'none', label:'Solo reproduce'};
  const id = item.id || '';

  // Orden intencionado:
  // 1) Máxima interacción: actividades creativas, largas y abiertas.
  // 2) Interacción larga: conversación sostenida, escucha activa, emociones y acompañamiento.
  // 3) Respuesta local simple: actividad cerrada muy fácil sin IA.
  // 4) Interacción corta: una pregunta/respuesta o pocos turnos.
  if(MAX_CREATIVE_ACTIVITY_IDS.has(id)){
    return {level:'max', label:'Máxima interacción'};
  }
  if(LONG_INTERACTION_ACTIVITY_IDS.has(id) || OPEN_CONVERSATION_ACTIVITY_IDS.has(id)){
    return {level:'long', label:'Interacción larga'};
  }
  if(interactionPolicy.localActivityIds?.has?.(id)){
    return {level:'local', label:'Respuesta local simple'};
  }
  if(activityNeedsMicroPrompt(item)){
    return {level:'short', label:'Interacción corta'};
  }
  return {level:'none', label:'Solo reproduce'};
}

function isMaxCreativeActivityContext(context){
  return !!(context && MAX_CREATIVE_ACTIVITY_IDS.has(context.id || ''));
}

function userAskedToEndActivity(text){
  const t=(text||'').toLowerCase().trim();
  return ['terminar','fin','salir','paramos','para','parar','cambiar','otra actividad','hemos terminado','ya está'].some(x=>t.includes(x));
}

// Dibuja las tarjetas de una pestaña y añade la barra inferior de nivel de interacción.
function renderActionGroups(groups,targetId){
  const root=$(targetId);
  if(!root){
    console.warn('[Ritxi] No existe contenedor de acciones:', targetId);
    return;
  }
  root.innerHTML='';
  const safeGroups=(groups||[]).map(group=>({
    title:group?.title || 'Grupo',
    items:(group?.items||[]).filter(Boolean)
  })).filter(group=>group.items.length>0);

  if(!safeGroups.length){
    const empty=document.createElement('div');
    empty.className='activity-top-note empty-actions-note';
    empty.textContent='No se han cargado tarjetas en esta pestaña. Recarga con Ctrl+F5 o revisa app.js.';
    root.appendChild(empty);
    console.warn('[Ritxi] Sin tarjetas para', targetId);
    return;
  }

  safeGroups.forEach(group=>{
    const section=document.createElement('section');
    section.className='action-section';
    section.innerHTML=`<h3>${group.title}</h3><div class="action-grid"></div>`;
    const grid=section.querySelector('.action-grid');
    group.items.forEach(item=>{
      const info=interactionLevelForActivity(item);
      const btn=document.createElement('button');
      btn.className=`action-card interaction-${info.level}`;
      btn.dataset.actionId=item.id || '';
      btn.dataset.interactionLevel=info.level;
      btn.title = `${item.title || item.id || 'Acción'} · ${info.label}`;
      btn.innerHTML=`<span class="icon">${item.icon || '▶'}</span><b>${item.title || item.id || 'Acción'}</b><small>${item.subtitle || 'Actividad'}</small><span class="interaction-strip" aria-hidden="true"></span><span class="interaction-label">${info.label}</span>`;
      btn.addEventListener('click',()=>executeAction(item,btn));
      grid.appendChild(btn);
    });
    root.appendChild(section);
  });
}
function renderTabs(){ document.querySelectorAll('.tab').forEach(btn=>btn.addEventListener('click',()=>{ document.querySelectorAll('.tab').forEach(b=>b.classList.remove('active')); document.querySelectorAll('.tab-page').forEach(p=>p.classList.remove('active')); btn.classList.add('active'); $(`tab-${btn.dataset.tab}`).classList.add('active'); if(btn.dataset.tab==='config' && $('inlineConfigEditor') && !$('inlineConfigEditor').dataset.loaded){ $('inlineConfigEditor').dataset.loaded='1'; loadInlineConfigFile('system_prompt').catch(err=>logClient('error','config',`No se pudo cargar configuración inicial: ${String(err)}`)); } })); }

async function saveSpeechMotionConfig(){ await api('/api/config/speech_motion',{method:'POST',body:JSON.stringify({enabled:$('speechMotion').checked,intensity:Number($('speechMotionIntensity').value||0.72)})}); logClient('info','config','Movimiento de habla guardado',{enabled:$('speechMotion').checked,intensity:$('speechMotionIntensity').value}); await refreshStatus(); }
async function loadSettings(){ try{ const s=await api('/api/runtime/settings'); const f=s.flags_defaults; const map={inputMicrophone:f.input_microphone,outputText:f.output_text,outputAudio:f.output_audio,sttEnabled:f.stt,llmEnabled:f.llm,ttsEnabled:f.tts,robotMotion:f.robot_motion,cameraVision:f.camera_vision,debug:f.debug,speechMotion:f.speech_motion,activeWait:f.active_wait,moveTalkGenerateText:f.move_talk_generate_text,autoVoiceResponse:f.auto_voice_response,autoSendAfterStt:f.auto_send_after_stt,echoGuard:f.echo_guard,modeTutorDi:f.mode_tutor_di,saveSession:f.save_session,simulationMode:f.simulation_mode}; Object.entries(map).forEach(([id,val])=>{ if($(id))$(id).checked=!!val; }); $('speechMotionIntensity').value=s.speech_motion_intensity; idleEnabled=s.idle_enabled; currentCharacter=s.current_character; if($('characterChip')) $('characterChip').textContent=s.current_character?.name||'Tutor amable'; if($('quickCharacterSelect')) $('quickCharacterSelect').value='ritxi_tutor_comunicacion_di'; renderCharacterForm(currentCharacter); }catch(err){logClient('warn','config',`No se pudo cargar configuración: ${String(err)}`);} }
function renderCharacterEmotionSelect(){ const sel=$('characterDefaultEmotion'); sel.innerHTML=''; EMOTIONS.forEach(e=>{ const opt=document.createElement('option'); opt.value=e; opt.textContent=e; sel.appendChild(opt); }); }
function lines(value){ return (value||'').split('\n').map(x=>x.trim()).filter(Boolean); }
function renderCharacterForm(profile){ if(!profile)return; $('characterName').value=profile.name||''; $('characterRole').value=profile.role||''; $('characterMission').value=profile.mission||''; $('characterTone').value=profile.tone||''; $('characterRules').value=(profile.communication_rules||[]).join('\n'); $('characterActivities').value=(profile.activity_style||[]).join('\n'); $('characterSafety').value=(profile.safety_rules||[]).join('\n'); $('characterMovement').value=profile.movement_style||''; $('characterExtra').value=profile.prompt_extra||''; $('characterDefaultEmotion').value=profile.default_emotion||'alegre'; $('characterAllowedEmotions').value=(profile.allowed_emotions||[]).join(', '); $('characterChip').textContent=profile.name||'Tutor amable'; }
async function loadCharacters(){ const data=await api('/api/characters'); const sel=$('characterSelect'); sel.innerHTML=''; data.characters.forEach(p=>{ const opt=document.createElement('option'); opt.value=p.id; opt.textContent=`${p.name} (${p.id})`; sel.appendChild(opt); }); sel.value=data.current_character_id; const current=data.characters.find(p=>p.id===data.current_character_id)||data.characters[0]; currentCharacter=current; renderCharacterForm(current); }
async function openCharacterEditor(){
  try{
    await loadCharacters();
    $('characterDialog').showModal();
    $('characterSaveStatus') && ($('characterSaveStatus').textContent='Carácter cargado. Puedes editar y guardar.');
  }catch(err){
    alert('No se pudo cargar el carácter: '+String(err));
    logClient('error','character',`Error abriendo carácter: ${String(err)}`);
  }
}

async function openCharacterJsonInConfig(){
  await openAdvancedConfig();
  // buscar y abrir el archivo character_profile
  setTimeout(()=>{
    const btn=[...document.querySelectorAll('.config-file-btn')].find(b=>b.dataset.configPath==='character_profile');
    if(btn) btn.click();
  },150);
}

async function saveCharacter(){ 
  const status=$('characterSaveStatus');
  try{
    if(status) status.textContent='Guardando carácter...';
    const base=currentCharacter||{id:'ritxi_tutor_comunicacion_di'}; 
    const profile={
      id:base.id,
      name:$('characterName').value||'Ritxi',
      role:$('characterRole').value||'',
      mission:$('characterMission').value||'',
      tone:$('characterTone').value||'',
      communication_rules:lines($('characterRules').value),
      activity_style:lines($('characterActivities').value),
      safety_rules:lines($('characterSafety').value),
      movement_style:$('characterMovement').value||'',
      prompt_extra:$('characterExtra').value||'',
      default_emotion:$('characterDefaultEmotion').value||'alegre',
      allowed_emotions:$('characterAllowedEmotions').value.split(',').map(x=>x.trim()).filter(Boolean)
    }; 
    const data=await api('/api/character',{method:'PUT',body:JSON.stringify({profile,persist:true})}); 
    currentCharacter=data.current; 
    renderCharacterForm(currentCharacter); 
    logClient('info','character','Carácter guardado en archivo JSON',currentCharacter); 
    await loadCharacters(); 
    await refreshStatus(); 
    if(status) status.textContent='Guardado correctamente en profiles/characters.';
    alert('Carácter guardado correctamente.');
  }catch(err){
    if(status) status.textContent='Error al guardar carácter.';
    alert('No se pudo guardar el carácter: '+String(err));
    logClient('error','character',`Error guardando carácter: ${String(err)}`);
  }
}

async function toggleIdleFromCheckbox(){ 
  const enabled=$('activeWait').checked; 
  idleEnabled=enabled; 
  await api('/api/config/idle',{method:'POST',body:JSON.stringify({enabled})}); 
  logClient('info','robot',`Espera activa ${enabled?'activada':'desactivada'}`); 
  if(enabled && flags().robot_motion){
    setExecuting('Espera activa','Movimiento suave activado');
    await api('/api/robot/action',{method:'POST',body:JSON.stringify({emotion:'escucha_activa',text:null,motion_enabled:true,audio_enabled:false,return_to_neutral:false,layer:'manual',wait:false,speech_motion:false})}).catch(err=>logClient('warn','robot',`No se pudo lanzar movimiento inmediato de espera activa: ${String(err)}`));
  } else if(!enabled){
    if(activeInteractionMode !== 'text') if(activeInteractionMode !== 'text') if(activeInteractionMode !== 'text') api('/api/robot/action',{method:'POST',body:JSON.stringify({emotion:'neutral',text:null,motion_enabled:activeInteractionMode !== 'text',audio_enabled:false,return_to_neutral:false,layer:'manual',wait:false,speech_motion:false})}).catch(()=>{});
  }
  await refreshStatus(); 
}
async function forceMicroOn(){ manualMicStopLock=false; const data=await api('/api/microphone/force_unmute',{method:'POST',body:'{}'}); logClient('info','mic','Micro forzado a ON',data); await startAlwaysOnMic({reason:'force-micro-on', autoSend:true, force:true}); if(realtimeEnabled)scheduleRealtimeLoop(200); await refreshStatus(); }
async function reconnectRobot(){ const data=await api('/api/robot/reconnect',{method:'POST',body:'{}'}); logClient(data.connected?'info':'warn','robot',data.connected?'Robot reconectado':'No se pudo reconectar robot',data); await refreshStatus(); }
function inlineConfigLabelFor(path){
  const btn = document.querySelector(`.config-quick-file[data-config-path="${CSS.escape(path)}"]`);
  if(btn) return btn.textContent.trim();
  const map = {
    system_prompt:'Prompt del sistema',
    settings_py:'Constantes / configuración Python',
    model_presets:'Modelos Ollama',
    interaction_policy:'Política interacción / local_activity_ids / ollama_activity_ids',
    ritxi_constants:'Constantes externas Ritxi',
    character_profile:'Carácter de Ritxi JSON',
    '.env.example':'Variables .env',
    stt_vocab_activity_mapping:'Mapa vocabulario actividades',
    'app/config/stt_vocabularies/activity_mapping.json':'Mapa vocabulario actividades',
    'app/config/interaction_policy.json':'Política interacción / fichas',
    'app/config/conversation_policy.json':'Política conversación / repetición',
    'app/config/ritxi_constants.py':'Constantes externas Ritxi',
    stt_vocab_language:'Vocabulario lenguaje',
    stt_vocab_social:'Vocabulario comunicación',
    stt_vocab_animals:'Vocabulario animales'
  };
  return map[path] || path;
}

async function loadInlineConfigFile(path='system_prompt', anchor=''){
  inlineConfigSelectedPath = path;
  inlineConfigSelectedLabel = inlineConfigLabelFor(path);
  document.querySelectorAll('.config-quick-file').forEach(b=>b.classList.toggle('active', b.dataset.configPath===path));
  const editor=$('inlineConfigEditor');
  const title=$('inlineConfigTitle');
  const real=$('inlineConfigRealPath');
  const status=$('inlineConfigStatus');
  if(!editor){
    logClient('warn','config','No existe inlineConfigEditor en la pestaña Configuración.');
    return;
  }
  if(title) title.textContent = `Archivo: ${inlineConfigSelectedLabel}`;
  if(real) real.textContent = path;
  if(status) status.textContent = 'Cargando archivo...';
  editor.value = 'Cargando...';
  try{
    const detail = await api(`/api/config/file?path=${encodeURIComponent(path)}`);
    editor.value = detail.content || '';
    if(real) real.textContent = detail.real_path || detail.path || path;
    if(status) status.textContent = anchor ? `Cargado: ${inlineConfigSelectedLabel}. Edita la sección ${anchor}.` : `Cargado: ${inlineConfigSelectedLabel}. Puedes editar y guardar.`;
    if(anchor && editor.value.includes(`"${anchor}"`)){
      const idx = editor.value.indexOf(`"${anchor}"`);
      editor.focus();
      editor.setSelectionRange(idx, Math.min(editor.value.length, idx + anchor.length + 2));
    }
    logClient('info','config',`Archivo de configuración cargado: ${path}`);
  }catch(err){
    editor.value = `Error cargando ${path}:\n${String(err)}\n\nComprueba que el servidor FastAPI esté activo y que la ruta sea relativa y permitida.`;
    if(real) real.textContent = path;
    if(status) status.textContent = `Error cargando: ${String(err)}`;
    logClient('error','config',`Error cargando configuración ${path}: ${String(err)}`);
  }
}

async function saveInlineConfigFile(){
  const editor=$('inlineConfigEditor');
  const status=$('inlineConfigStatus');
  if(!editor || !inlineConfigSelectedPath){
    alert('Selecciona un archivo de configuración.');
    return;
  }
  if(status) status.textContent = 'Guardando...';
  try{
    const data = await api(`/api/config/file?path=${encodeURIComponent(inlineConfigSelectedPath)}`,{
      method:'POST',
      body:JSON.stringify({content:editor.value})
    });
    if(status) status.textContent = `Guardado correctamente (${data.bytes} bytes).`;
    logClient('info','config',`Archivo guardado desde pestaña Configuración: ${inlineConfigSelectedPath}`,data);

    if(inlineConfigSelectedPath === 'character_profile'){
      await loadCharacters().catch(()=>{});
      await refreshStatus().catch(()=>{});
    }
    if(inlineConfigSelectedPath === 'model_presets'){
      updateModelPills();
    }
  }catch(err){
    if(status) status.textContent = 'Error al guardar.';
    alert('No se pudo guardar el archivo: '+String(err));
    logClient('error','config',`Error guardando configuración ${inlineConfigSelectedPath}: ${String(err)}`);
  }
}

async function reloadInlineConfigFile(){
  await loadInlineConfigFile(inlineConfigSelectedPath || 'system_prompt');
}

async function renderAllConfigFilesList(){
  const box = $('allConfigFilesList');
  if(!box) return;
  box.textContent = 'Cargando...';
  try{
    const data = await api('/api/config/files');
    const files = data.files || [];
    box.innerHTML = '';
    files.forEach(file=>{
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'config-quick-file compact-config-file';
      btn.dataset.configPath = file.real_path || file.path;
      btn.textContent = file.label || file.path;
      btn.title = file.real_path || file.path;
      btn.addEventListener('click',()=>loadInlineConfigFile(file.real_path || file.path));
      box.appendChild(btn);
    });
    if(!files.length) box.textContent='No hay archivos editables.';
    logClient('info','config',`Lista completa de configuración cargada: ${files.length} archivos`);
  }catch(err){
    box.textContent = 'Error cargando lista.';
    logClient('error','config',`No se pudo cargar lista de configuración: ${String(err)}`);
  }
}

function initInlineConfigEditor(){
  document.querySelectorAll('.config-quick-file').forEach(btn=>{
    btn.addEventListener('click',()=>{
      const path = btn.dataset.configPath || 'system_prompt';
      const anchor = btn.dataset.configAnchor || '';
      loadInlineConfigFile(path, anchor);
    });
  });
  renderAllConfigFilesList().catch(err=>logClient('error','config',`Error renderizando lista completa: ${String(err)}`));
  $('inlineConfigSaveBtn')?.addEventListener('click',saveInlineConfigFile);
  $('inlineConfigReloadBtn')?.addEventListener('click',reloadInlineConfigFile);
}

async function openAdvancedConfig(){
  const modal=$('advancedConfigDialog');
  const list=$('configFileList');
  const content=$('configFileContent');
  const title=$('configFileTitle');
  const status=$('configSaveStatus');
  if(!modal || !list || !content){
    logClient('warn','config','No existe el modal de configuración avanzada en el HTML.');
    return;
  }
  modal.showModal();
  content.value='Cargando archivos de configuración...';
  if(status) status.textContent='Cargando...';

  const loadFile = async(file)=>{
    selectedConfigFilePath = file.path;
    selectedConfigFileLabel = file.label || file.path;
    document.querySelectorAll('.config-file-btn').forEach(x=>x.classList.remove('active'));
    const btn = document.querySelector(`[data-config-path="${CSS.escape(file.path)}"]`);
    if(btn) btn.classList.add('active');
    if(title) title.textContent = `Archivo: ${selectedConfigFileLabel}`;
    if(status) status.textContent = 'Cargando archivo...';
    const detail=await api(`/api/config/file?path=${encodeURIComponent(file.path)}`);
    content.value=detail.content || '';
    if(status) status.textContent = 'Cargado. Puedes editar.';
    content.focus();
  };

  try{
    const data=await api('/api/config/files');
    list.innerHTML='';
    (data.files||[]).forEach(file=>{
      const b=document.createElement('button');
      b.type='button';
      b.textContent=file.label || file.path;
      b.className='config-file-btn';
      b.dataset.configPath=file.path;
      b.addEventListener('click',()=>loadFile(file).catch(err=>{
        content.value='Error cargando archivo: '+String(err);
        if(status) status.textContent='Error';
        logClient('error','config',`Error cargando archivo: ${String(err)}`);
      }));
      list.appendChild(b);
    });
    if((data.files||[])[0]) await loadFile(data.files[0]);
    else {
      content.value='No se han encontrado archivos de configuración.';
      if(status) status.textContent='Sin archivos';
    }
  }catch(err){
    content.value='Error abriendo configuración avanzada: '+String(err);
    if(status) status.textContent='Error';
    logClient('error','config',`Error abriendo configuración avanzada: ${String(err)}`);
  }
}

async function saveSelectedConfigFile(){
  if(!selectedConfigFilePath){
    alert('Selecciona primero un archivo.');
    return;
  }
  const content=$('configFileContent')?.value ?? '';
  const status=$('configSaveStatus');
  if(status) status.textContent='Guardando...';
  try{
    const data=await api(`/api/config/file?path=${encodeURIComponent(selectedConfigFilePath)}`,{
      method:'POST',
      body:JSON.stringify({content})
    });
    if(status) status.textContent=`Guardado (${data.bytes} bytes)`;
    logClient('info','config',`Archivo guardado: ${selectedConfigFilePath}`,data);
    if(selectedConfigFilePath==='character_profile'){
      await loadCharacters();
      await refreshStatus();
    }
  }catch(err){
    if(status) status.textContent='Error al guardar';
    alert('No se pudo guardar: '+String(err));
    logClient('error','config',`Error guardando archivo: ${String(err)}`);
  }
}

async function reloadSelectedConfigFile(){
  if(!selectedConfigFilePath) return openAdvancedConfig();
  const file={path:selectedConfigFilePath,label:selectedConfigFileLabel || selectedConfigFilePath};
  const content=$('configFileContent');
  const status=$('configSaveStatus');
  try{
    if(status) status.textContent='Recargando...';
    const detail=await api(`/api/config/file?path=${encodeURIComponent(file.path)}`);
    content.value=detail.content || '';
    if(status) status.textContent='Recargado';
  }catch(err){
    if(status) status.textContent='Error al recargar';
    alert('No se pudo recargar: '+String(err));
  }
}

async function exitAll(){
  const ok=confirm('¿Cerrar Ritxi y el daemon de Reachy?');
  if(!ok) return;
  try{
    stopShortCycle();
    stopBrowserMic();
    stopBrowserTts();
    stopEffectAudio();
    setExecuting('Saliendo','Cerrando Ritxi y daemon...');
    logClient('warn','system','SALIR pulsado: cerrando servicios');
    await api('/api/exit_all',{method:'POST',body:'{}'});
    addChat('bot','Ritxi se está cerrando. Puedes cerrar esta pestaña.','sistema');
    setTimeout(()=>{ try{ window.close(); }catch(e){} },800);
  }catch(err){
    alert('No se pudo cerrar desde la interfaz. Usa Ctrl+C o cierra las ventanas de daemon/FastAPI.');
    logClient('error','system',`Error al cerrar: ${String(err)}`);
  }
}


let textSendInFlight = false;
// Envío robusto del botón ➤ y Enter, con captura de errores para logs.
async function sendTextNow(source='text-now'){
  enableTextInputAlways(source);
  const msg=$('message');
  const text=(msg?.value||'').trim();
  if(!text){
    setMicStatus('Modo texto activo: escribe algo y pulsa ➤.');
    return null;
  }
  if(textSendInFlight){
    logClient('debug','chat','Envío de texto ignorado: ya había uno en curso',{source});
    return null;
  }
  textSendInFlight=true;
  try{
    enterTextPriorityMode(source,{deepStop:false});
    return await sendTurn({source});
  }catch(err){
    const msgErr = String(err && (err.stack || err.message || err));
    console.error('[Ritxi] Error enviando texto', err);
    logClient('error','chat',`Error enviando texto: ${msgErr}`,{source});
    setMicStatus('Error enviando texto. Revisa registros; la entrada sigue activa.');
    addChat?.('bot',`He tenido un problema al enviar el texto: ${escapeHtml(String(err?.message || err))}`,'sistema');
    return null;
  }finally{
    setTimeout(()=>{ textSendInFlight=false; enableTextInputAlways('sendTextNow-finally'); },250);
  }
}
// Conecta todos los botones, selects y entradas de la interfaz con sus funciones.
function bindEvents(){
  enableTextInputAlways('bindEvents');
  const sendHandler=(ev,source)=>{
    if(ev){ ev.preventDefault(); ev.stopPropagation(); }
    sendTextNow(source);
  };
  $('sendBtn')?.addEventListener('click',(ev)=>sendHandler(ev,activityAwaitingUser?'activity-text-click':'manual-click'),{capture:true});
  $('sendBtn')?.addEventListener('pointerdown',()=>enableTextInputAlways('send pointerdown'),{capture:true});
  $('message')?.addEventListener('keydown',(ev)=>{ if(ev.key==='Enter' && !ev.shiftKey){ ev.preventDefault(); sendTextNow(activityAwaitingUser?'activity-text-enter':'manual-enter'); } });
  $('textModeBtn')?.addEventListener('click',(ev)=>{ ev.preventDefault(); setModulePreset('text'); });
  $('message')?.addEventListener('focus',()=>enterTextPriorityMode('focus-texto',{deepStop:false}),{capture:true});
  $('message')?.addEventListener('pointerdown',()=>enterTextPriorityMode('pointer-texto',{deepStop:false}),{capture:true});
  $('message')?.addEventListener('input',()=>{ enableTextInputAlways('input-texto'); if(micAlwaysOn || persistentTranscribing || serverSttActive) enterTextPriorityMode('input-texto',{deepStop:false}); });

  $('micBtn')?.addEventListener('click',async()=>await startMic({autoSend:false, askPermission:true, reason:'boton-micro'}));
  $('stopMicBtn')?.addEventListener('click',async()=>{ await stopMicByUser('boton-parar-micro'); });
  $('forceMicBtn')?.addEventListener('click',forceMicroOn);
  $('realtimeToggle').addEventListener('click',talkNowButton); $('unlockBtn')?.addEventListener('click',()=>forceUiUnblock('boton-desbloquear'));   $('useFastModelBtn')?.addEventListener('click',()=>{ if($('modelSelect')){$('modelSelect').value='gemma3:1b'; updateModelPills('gemma3:1b'); logClient('info','ollama','Modelo cambiado manualmente a rápido: gemma3:1b');} });
$('modelSelect')?.addEventListener('change',()=>{$('modelSelect').dataset.userTouched='1'; updateModelPills(); logClient('info','ollama',`Modelo seleccionado: ${selectedModelName()}`);});
  $('temperatureUi')?.addEventListener('input',()=>{updateCreativityUi();
  updateSpeechRateUi(); logClient('debug','ollama',`Creatividad ajustada: ${creativityValue()} (${creativityProfile().label})`);}); $('modelSelect')?.addEventListener('change',()=>logClient('info','ollama',`Modelo seleccionado: ${$('modelSelect').value}`,{modelSelectChange:true}));
  $('resetBtn')?.addEventListener('click',async()=>{forceUnlockTurnState('reset'); manualMicStopLock=false; activityAutoListenAfterBot=false; activityAwaitingUser=false; await api(`/api/sessions/${$('sessionId').value||'demo'}/reset`,{method:'POST',body:'{}'}); $('chatHistory').innerHTML=''; ensureFreshSessionId();
  initChat();
  loadInteractionPolicy();
  loadConversationPolicy();
  loadRobotMotionPolicy(); updateMicToggleUi(); logClient('info','chat','Sesión reiniciada');});
  document.querySelectorAll('[data-quick="reconnect"]').forEach(b=>b.addEventListener('click',reconnectRobot));
  $('activeWait')?.addEventListener('change',toggleIdleFromCheckbox);
  $('saveSpeechMotionBtn')?.addEventListener('click',saveSpeechMotionConfig);
  $('presetTextOnlyBtn')?.addEventListener('click',()=>setModulePreset('text'));
  $('presetTextRobotBtn')?.addEventListener('click',()=>setModulePreset('textRobot'));
  $('presetVoiceRobotBtn')?.addEventListener('click',()=>setModulePreset('voiceRobot'));
  $('presetFullTutorBtn')?.addEventListener('click',()=>setModulePreset('full'));
  $('quickCharacterSelect')?.addEventListener('change',()=>applyQuickCharacterPreset($('quickCharacterSelect').value));
  $('detailStopBtn')?.addEventListener('click',()=>{$('stopAllBtn')?.click();});
  $('shortCycleTurnBtn')?.addEventListener('click',()=>runShortCycle('turn'));
  $('exitAllBtn')?.addEventListener('click',exitAll);
  $('stopAllBtn').addEventListener('click',()=>{forceUnlockTurnState('stop-all');stopShortCycle();activityAutoListenAfterBot=false;activityAwaitingUser=false;stopBrowserMic();stopBrowserTts();stopEffectAudio();setExecuting('—','Detenido desde interfaz'); setShortCycleStatus?.('Ciclo corto: usa fichas breves; Siguiente avanza cuando espera respuesta.'); logClient('warn','ui','Acción detenida por usuario');});
  $('openCharacterBtn')?.addEventListener('click',openCharacterEditor); $('openCharacterBtn2')?.addEventListener('click',openCharacterEditor);
  $('openConfigBtn')?.addEventListener('click',()=>{document.querySelector('[data-tab="config"]')?.click();});
  $('openAdvancedBtn')?.addEventListener('click',openAdvancedConfig); $('saveConfigFileBtn')?.addEventListener('click',saveSelectedConfigFile); $('reloadConfigFileBtn')?.addEventListener('click',reloadSelectedConfigFile);
  $('saveCharacterBtn')?.addEventListener('click',saveCharacter); $('openCharacterJsonBtn')?.addEventListener('click',openCharacterJsonInConfig); $('reloadCharacterBtn')?.addEventListener('click',async()=>{await loadCharacters();$('characterSaveStatus') && ($('characterSaveStatus').textContent='Carácter recargado desde archivo.');logClient('info','character','Carácter recargado');});
  $('characterSelect')?.addEventListener('change',async()=>{ const data=await api('/api/character/select',{method:'POST',body:JSON.stringify({character_id:$('characterSelect').value})}); currentCharacter=data.current; renderCharacterForm(currentCharacter); logClient('info','character','Carácter seleccionado',currentCharacter); });
  $('message').addEventListener('keydown',e=>{ if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendTurn({source:'keyboard'});} });
  $('startDaemonBtn')?.addEventListener('click',startDaemonFromPanel);
  $('refreshDaemonBtn')?.addEventListener('click',refreshDaemon);
  $('stopDaemonBtn')?.addEventListener('click',stopDaemonFromPanel);
  $('whisperHelpBtn')?.addEventListener('click',()=>logClient('info','stt','Para STT local ejecuta: scripts\\setup_uv_stt_whisper_windows.bat'));
  window.addEventListener('beforeunload',()=>{realtimeEnabled=false;stopBrowserMic();stopBrowserTts();});
}


async function warmupWhisper(){
  if(selectedMicMode()!=='server_whisper') return;
  try{
    setMicStatus('Preparando micro/Whisper…');
    const data=await api('/api/audio/warmup_whisper',{method:'POST',body:'{}'});
    logClient('info','stt',`Whisper preparado (${Math.round(data.elapsed_ms||0)} ms)`,data);
    setMicStatus('Micro preparado. Pulsa 🎙️ o usa una actividad con turnos.');
  }catch(err){
    logClient('warn','stt',`No se pudo precargar Whisper: ${String(err)}`);
    setMicStatus('Micro preparado parcialmente. Si tarda la primera vez, espera unos segundos.');
  }
}


const EMERGENCY_DIRECT_ACTION_GROUPS = [
  { title:'Actividades de comunicación funcional', items:[
    { id:'pedir_ayuda', title:'Pedir ayuda', icon:'🆘', emotion:'escucha_activa', text:'Vamos a practicar pedir ayuda. Puedes decir: ¿me ayudas, por favor?', subtitle:'Modelo + práctica', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'pedir_turno', title:'Respetar turnos', icon:'✋', emotion:'pedir_turno', text:'Ahora practicamos pedir turno. Puedes decir: por favor, ¿puedo hablar?', subtitle:'Turno + espera', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'preguntar_nombre', title:'Preguntar nombre', icon:'👤', emotion:'escucha_activa', text:'¿Cómo te llamas? Di solo tu nombre, despacio y claro. Yo te escucho.', subtitle:'Pregunta abierta', awaitUser:true, requiresInput:true, vocabularyHint:'open_name' },
    { id:'frase_corta', title:'Frase corta', icon:'💬', emotion:'curioso', text:'Dime una frase corta sobre cómo estás hoy.', subtitle:'Respuesta libre', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
  ]},
  { title:'Lenguaje', items:[
    { id:'sinonimos', title:'Sinónimos', icon:'🔁', emotion:'thoughtful1', text:'Dime una palabra parecida a contento.', subtitle:'Una palabra', awaitUser:true, requiresInput:true, vocabularyHint:'short' },
    { id:'opuestos', title:'Opuestos', icon:'↔️', emotion:'thoughtful1', text:'Si yo digo grande, tú puedes decir pequeño.', subtitle:'Una palabra', awaitUser:true, requiresInput:true, vocabularyHint:'short' },
  ]},
];

const EMERGENCY_GAME_ACTION_GROUPS = [
  { title:'Juegos, canciones y bailes', items:[
    { id:'animal_corto', title:'Animal rápido', icon:'🐶', emotion:'juego', text:'Guau guau. ¿Qué animal es?', subtitle:'Sonido + pregunta', sound:'dog', awaitUser:true, requiresInput:true, vocabularyHint:'animal' },
    { id:'cantar_saludo', title:'Cantar saludo', icon:'🎤', emotion:'alegre', text:'Cantamos un saludo: hola, hola, qué tal estás. Ahora puedes saludar tú.', subtitle:'Canto + turno', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'ritmo_palmas', title:'Ritmo con palmas', icon:'👏', emotion:'aplauso', text:'Escucha el ritmo: una, dos, una, dos. Ahora te toca a ti.', subtitle:'Ritmo + turno', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'palmas_lentas', title:'Palmas lentas', icon:'👏', emotion:'aplauso', text:'Damos palmas lentas: una… dos… una… dos. Ahora lo intentas tú.', subtitle:'Ritmo lento + turno', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'palmas_rapidas', title:'Palmas rápidas', icon:'⚡', emotion:'celebracion', text:'Ahora palmas rápidas: una, dos, tres. Ahora te toca a ti.', subtitle:'Ritmo rápido + turno', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'baile_suave', title:'Baile suave', icon:'🌊', emotion:'calma', text:'Nos movemos suave y tranquilos. Ahora puedes decir si quieres repetir.', subtitle:'Movimiento suave + turno', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
  ]},
];

const EMERGENCY_TUTOR_ACTION_GROUPS = [
  { title:'Tutoría y apoyo emocional', items:[
    { id:'respira', title:'Respira conmigo', icon:'🫁', emotion:'calma', text:'Respira conmigo. Inspiramos despacio y soltamos el aire.', subtitle:'Relajación guiada' },
    { id:'pedir_descanso', title:'Pedir descanso', icon:'☕', emotion:'calma', text:'Practicamos pedir descanso. Puedes decir: necesito descansar un poco.', subtitle:'Comunicación funcional', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'frase_segura', title:'Frase segura', icon:'🛟', emotion:'paciencia', text:'Puedes decir: necesito un momento. Está bien pedir una pausa.', subtitle:'Autoprotección', awaitUser:true, requiresInput:true, vocabularyHint:'open_text' },
    { id:'buen_trabajo', title:'Buen trabajo', icon:'⭐', emotion:'cheerful1', text:'¡Buen trabajo! Lo importante es intentarlo, y tú lo has intentado.', subtitle:'Refuerzo' },
  ]},
];

function gridHasCards(id){
  const root=$(id);
  return !!(root && root.querySelector('.action-card'));
}

function restoreActionCardsIfEmpty(reason='restore'){
  try{
    if(!gridHasCards('emotionActionGrid')){
      renderActionGroups((ACTION_GROUPS && ACTION_GROUPS.length) ? ACTION_GROUPS : [], 'emotionActionGrid');
    }
    if(!gridHasCards('directActionGrid')){
      const groups = [...(SHORT_ACTIVITY_GROUPS||[]), ...(DIRECT_ACTION_GROUPS||[])];
      renderActionGroups(groups.length ? groups : EMERGENCY_DIRECT_ACTION_GROUPS, 'directActionGrid');
    }
    if(!gridHasCards('gamesActionGrid')){
      const groups = (typeof effectiveGameGroups === 'function' ? effectiveGameGroups() : []);
      renderActionGroups(groups && groups.length ? groups : EMERGENCY_GAME_ACTION_GROUPS, 'gamesActionGrid');
    }
    if(!gridHasCards('tutorActionGrid')){
      renderActionGroups((typeof TUTOR_ACTION_GROUPS !== 'undefined' && TUTOR_ACTION_GROUPS.length) ? TUTOR_ACTION_GROUPS : EMERGENCY_TUTOR_ACTION_GROUPS, 'tutorActionGrid');
    }
    console.info('[Ritxi] Revisión de tarjetas', reason, {
      emociones:gridHasCards('emotionActionGrid'),
      actividades:gridHasCards('directActionGrid'),
      juegos:gridHasCards('gamesActionGrid'),
      tutor:gridHasCards('tutorActionGrid')
    });
  }catch(err){
    console.error('[Ritxi] Error restaurando tarjetas',err);
  }
}

// Inicializa la interfaz: pestañas, tarjetas, estado, eventos y servicios periódicos.

function setDefaultFastModelOnce(){
  const sel=$('modelSelect');
  if(sel && !sel.dataset.userTouched){
    sel.value='qwen3:0.6b';
    updateModelPills('qwen3:0.6b');
    logClient('info','ollama','Modelo rápido por defecto aplicado: qwen3:0.6b');
  }
}



async function testOfficialEmotionRuntime(emotionId='cheerful1'){
  // Diagnóstico manual desde consola: await testOfficialEmotionRuntime('cheerful1')
  const audio = await playOfficialRecordedAudio(emotionId, emotionId, {force:true, wait:false, official:true});
  const robot = await api('/api/robot/action',{method:'POST',body:JSON.stringify({
    emotion:emotionId,text:null,motion_enabled:true,audio_enabled:false,return_to_neutral:true,layer:'manual',wait:true,speech_motion:true
  })}).catch(err=>({error:String(err)}));
  logClient('info','selfcheck','Test emoción oficial ejecutado',{emotionId,audio,robot});
  return {audio,robot};
}
window.testOfficialEmotionRuntime = testOfficialEmotionRuntime;


function positiveAnimationSelfCheck(){
  try{
    const dummy={id:'selfcheck_dummy', title:'Selfcheck', emotion:'cheerful1', robotMotion:true};
    shouldUseRobotAnimationForInteraction(dummy, 'start');
    return true;
  }catch(err){
    logClient('error','selfcheck',`Error en regla de animación positiva: ${String(err)}`);
    return false;
  }
}

function selfCheckConversationAndCards(){
  const registry = {
    flags,
    chatFlagsForBackend,
    safeBotText,
    sendTurn,
    sendTextNow,
    setModulePreset,
    cardRuntime,
    executeAction,
    runActivity,
    playAutomaticEmotionAfterReply,
    playAutomaticRobotEmotionAfterReply,
  };
  const missing = Object.entries(registry)
    .filter(([_,fn]) => typeof fn !== 'function')
    .map(([name]) => name);

  if(missing.length){
    const msg = `Funciones críticas no disponibles: ${missing.join(', ')}`;
    logClient('error','selfcheck',msg,{version:'5.9.95'});
    setMicStatus(`Error interno: ${missing.join(', ')}. Revisa logs.`);
    const el=$('currentSubState');
    if(el) el.textContent=`Error de arranque: ${missing.join(', ')}`;
    return false;
  }

  try{
    const f = chatFlagsForBackend();
    const sample = safeBotText({text:'[ESCUCHA_ACTIVA]', emotion:'escucha_activa'}, 'Hola');
    const fastSample = fastActivityReply('prueba', {id:'escucha_activa', title:'Escucha activa'});
    logClient('info','selfcheck','Autocomprobación de arranque OK',{
      version:'5.9.95',
      activeInteractionMode,
      backend_robot_motion:f.robot_motion,
      safeBotText_sample:sample,
      fastActivityReply_open_sample:fastSample,
      note:'Los modos superiores afectan al chat; las fichas usan cardRuntime().'
    });
    const el=$('currentSubState');
    if(el) el.textContent='Autocomprobación OK · listo para conversar';
  }catch(err){
    logClient('error','selfcheck',`Autocomprobación fallida: ${String(err)}`,{version:'5.9.95'});
    setMicStatus(`Error interno de arranque: ${String(err)}.`);
    return false;
  }
  return true;
}




async function loadRobotMotionPolicy(){
  try{
    const detail = await api('/api/config/file?path=app/config/robot_motion_policy.json');
    const data = JSON.parse(detail.content || '{}');
    robotMotionPolicy = {...robotMotionPolicy, ...data};
    logClient('info','config','Política de robot cargada v5.9.95',{...robotMotionPolicy, emotions_validated:robotMotionPolicy.validated_visible_emotions});
  }catch(err){
    logClient('warn','config',`No se pudo cargar robot_motion_policy.json; usando política interna: ${String(err)}`);
  }
}


async function loadConversationPolicy(){
  try{
    const detail = await api('/api/config/file?path=conversation_policy');
    const data = JSON.parse(detail.content || '{}');
    conversationPolicy = {...conversationPolicy, ...data};
    logClient('info','config','Política de conversación cargada',{version:data.version, fallbacks:Object.keys(data.topic_fallbacks||{}).length});
  }catch(err){
    logClient('warn','config',`No se pudo cargar conversation_policy.json; usando valores internos: ${String(err)}`);
  }
}

function fallbackFromConversationPolicy(userText){
  const u=String(userText||'').toLowerCase();
  const t=creativityValue();
  const level = t <= 0.20 ? 'precise' : (t <= 0.65 ? 'balanced' : 'creative');

  const builtin = {
    hola:{
      precise:'Hola. Te escucho.',
      balanced:'Hola. ¿De qué quieres hablar hoy?',
      creative:'Hola. Me alegra verte. Dime un tema y lo exploramos juntos.'
    },
    naturaleza:{
      precise:'La naturaleza incluye plantas, animales, agua, aire y paisajes.',
      balanced:'La naturaleza es el conjunto de seres vivos y paisajes: plantas, animales, ríos, montañas, aire y agua.',
      creative:'La naturaleza es como una casa grande compartida: árboles, animales, ríos, montañas y personas vivimos dentro de ella.'
    },
    amor:{
      precise:'El amor es cariño y cuidado hacia alguien.',
      balanced:'El amor es sentir cariño, cuidar a alguien y querer que esté bien.',
      creative:'El amor es como una luz suave: ayuda a cuidar, acompañar y sentirse cerca de otra persona.'
    },
    jugar:{
      precise:'Jugar sirve para divertirse y aprender.',
      balanced:'Jugar sirve para divertirse, aprender reglas y compartir tiempo con otras personas.',
      creative:'Jugar es como abrir una puerta a la imaginación: pruebas, ríes y aprendes sin darte cuenta.'
    }
  };

  const topics = {...builtin, ...(conversationPolicy.topic_fallbacks || {})};
  for(const [key,values] of Object.entries(topics)){
    if(u.includes(key.toLowerCase())){
      return values[level] || values.balanced || values.precise || values.creative;
    }
  }
  const d={...{
    precise:'Te escucho. Dime una palabra o tema concreto.',
    balanced:'Te escucho. Dime un tema concreto y te respondo con una frase clara.',
    creative:'Dime un tema y lo convertimos en una explicación sencilla.'
  }, ...(conversationPolicy.default_fallbacks || {})};
  return d[level] || d.balanced || d.precise || 'Te escucho. Dime un tema concreto.';
}

function normalizeForRepeatCheck(text){
  return String(text||'').toLowerCase().replace(/\s+/g,' ').trim();
}

function userTopicChanged(prevUser,currentUser){
  const a=normalizeForRepeatCheck(prevUser);
  const b=normalizeForRepeatCheck(currentUser);
  if(!a || !b) return false;
  if(a===b) return false;
  const wa=new Set(a.split(' ').filter(w=>w.length>3));
  const wb=new Set(b.split(' ').filter(w=>w.length>3));
  let common=0;
  wb.forEach(w=>{if(wa.has(w)) common++;});
  return common===0 || b.includes('ahora') || b.includes('otra vez') || b.includes('he dicho');
}

function maybeReplaceRepetitiveReply(botText,userText){
  const guard=conversationPolicy.repetition_guard || {};
  if(!guard.enabled) return {text:botText, replaced:false};
  const clean=String(botText||'').trim();
  const last=String(lastAssistantVisibleText||'').trim();
  const minChars=Number(guard.min_repeated_chars || 25);
  const exactRepeat = clean.length>=minChars && normalizeForRepeatCheck(clean)===normalizeForRepeatCheck(last);
  const topicChanged = userTopicChanged(lastAssistantUserText,userText);
  if(exactRepeat && (guard.replace_exact_repetition || (guard.replace_when_user_topic_changes && topicChanged))){
    const replacement=fallbackFromConversationPolicy(userText);
    logClient('warn','chat','Respuesta repetida sustituida por política de conversación',{userText,lastAssistantUserText,old:clean,replacement});
    return {text:replacement, replaced:true};
  }
  return {text:clean, replaced:false};
}

async function loadInteractionPolicy(){
  try{
    const data = await api('/api/interaction_policy');
    interactionPolicy = {
      localActivityIds: new Set(data.local_activity_ids || []),
      ollamaActivityIds: new Set(data.ollama_activity_ids || []),
      defaults:data.defaults || interactionPolicy.defaults,
    };
    if(data.defaults?.chat_timeout_ms) window.RITXI_CHAT_TIMEOUT_MS = Number(data.defaults.chat_timeout_ms);
    if($('temperatureUi') && typeof data.defaults?.temperature === 'number') $('temperatureUi').value = String(data.defaults.temperature);
    updateCreativityUi();
    logClient('info','config','Política de interacción cargada desde app/config/interaction_policy.json',{version:data.version, local:[...interactionPolicy.localActivityIds].length, ollama:[...interactionPolicy.ollamaActivityIds].length});
  }catch(err){
    logClient('warn','config',`No se pudo cargar interaction_policy.json; usando valores internos: ${String(err)}`);
  }
}


function creativityProfile(temp=null){
  const t = temp ?? creativityValue();
  if(t <= 0.20) return {level:'precisa', label:'precisa', instruction:'Responde de forma directa, literal y breve. No adornes la respuesta.'};
  if(t <= 0.55) return {level:'equilibrada', label:'equilibrada', instruction:'Responde claro y añade un ejemplo sencillo si ayuda.'};
  if(t <= 0.80) return {level:'variada', label:'variada', instruction:'Responde de forma algo más variada, con un ejemplo distinto y natural.'};
  return {level:'creativa', label:'creativa', instruction:'Responde de forma creativa pero clara, usando una comparación sencilla o una imagen fácil de entender.'};
}

function updateSpeechRateUi(){
  const el=$('speechRateValue');
  if(el) el.textContent = Number($('speechRateUi')?.value || 0.95).toFixed(2);
}

function updateCreativityUi(){
  const el=$('temperatureValue');
  if(!el) return;
  const t=creativityValue();
  const p=creativityProfile(t);
  el.textContent = `${t.toFixed(2)} · ${p.label}`;
  el.className = `slider-value creativity-${p.level}`;
}

function applyCreativityInstruction(text){
  const t = creativityValue();
  const p = creativityProfile(t);
  return `${text}

[Estilo de respuesta: creatividad=${t.toFixed(2)} (${p.label}). ${p.instruction} Responde solo al último mensaje del usuario. No copies ejemplos. Si el usuario cambia de tema, responde al tema nuevo.]`;
}

function creativityValue(){
  return Math.max(0, Math.min(1, Number($('temperatureUi')?.value || interactionPolicy.defaults?.temperature || 0.25)));
}

function shouldUseLocalActivityReply(context){
  if(!context || !context.id) return false;
  return interactionPolicy.localActivityIds.has(context.id);
}

function shouldForceOllamaForActivity(context){
  if(!context || !context.id) return false;
  return interactionPolicy.ollamaActivityIds.has(context.id) || OPEN_CONVERSATION_ACTIVITY_IDS.has(context.id) || MAX_CREATIVE_ACTIVITY_IDS.has(context.id);
}

function boot(){
  renderTabs();
  ensureRecommendedModelSelected();
  updateCreativityUi();
  setDefaultFastModelOnce();
  initInlineConfigEditor();
  setModulePreset?.('text');

  // Render directo y con fallback. Evitamos filtros que puedan dejar pestañas vacías.
  renderActionGroups((ACTION_GROUPS && ACTION_GROUPS.length) ? ACTION_GROUPS : [], 'emotionActionGrid');
  renderActionGroups([...(SHORT_ACTIVITY_GROUPS||[]), ...(DIRECT_ACTION_GROUPS||[])], 'directActionGrid');
  renderActionGroups((typeof effectiveGameGroups === 'function' ? effectiveGameGroups() : []), 'gamesActionGrid');
  renderActionGroups((typeof TUTOR_ACTION_GROUPS !== 'undefined' ? TUTOR_ACTION_GROUPS : []), 'tutorActionGrid');
  restoreActionCardsIfEmpty('boot');
  setTimeout(()=>restoreActionCardsIfEmpty('post-boot'), 500);

  renderCharacterEmotionSelect();
  bindEvents();
  ensureFreshSessionId();
  initChat();
  logClient('info','app','Ritxi v5.9.95 iniciado: creatividad conectada y política externa de actividades');
  selfCheckConversationAndCards();
  positiveAnimationSelfCheck();
  loadSettings().then(loadCharacters).then(refreshStatus).then(()=>setTimeout(warmupWhisper,700));
  setInterval(refreshStatus,3500);
  refreshDaemon();
  setInterval(refreshDaemon,3500);
  renderLogs();
  enableTextInputAlways('boot');
  updateInteractionModeState('text');
  setInterval(()=>enableTextInputAlways('watchdog-texto'),1000);
}
boot();
