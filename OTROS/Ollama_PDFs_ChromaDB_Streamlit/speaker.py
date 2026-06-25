import pyttsx3
import threading
import config

def hablar_texto(texto: str):
    """
    Habla el texto proporcionado usando el motor TTS (Text-to-Speech) del sistema.
    Se ejecuta de forma asincrona para no congelar la aplicacion.
    """
    def _hablar():
        try:
            # Iniciamos el motor en cada hilo para evitar conflictos
            engine = pyttsx3.init()
            
            # Configurar velocidad de la voz y volumen desde config.py
            engine.setProperty('rate', config.TTS_RATE)
            engine.setProperty('volume', config.TTS_VOLUME)
            
            # Cambiar a la voz en el idioma configurado
            voices = engine.getProperty('voices')
            for voice in voices:
                if config.TTS_LANGUAGE.lower() in voice.name.lower() or 'es' in voice.languages:
                    engine.setProperty('voice', voice.id)
                    break
                    
            engine.say(texto)
            engine.runAndWait()
        except Exception as e:
            print(f"Error reproduciendo voz: {e}")

    # Lanzamos en un hilo separado para que Streamlit siga fluyendo
    hilo_voz = threading.Thread(target=_hablar)
    hilo_voz.start()
