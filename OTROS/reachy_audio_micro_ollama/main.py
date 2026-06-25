import ollama
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import time
import threading
import subprocess
import pygame
import config 
from animaciones import GestorAnimaciones
from reachy_mini.utils import create_head_pose
import numpy as np

app = FastAPI(title="Reachy Mini - Servidor Core Modular Avanzado")
gestor = GestorAnimaciones()

class UserMessage(BaseModel):
    text: str
    procesar_etiquetas: bool  
    motores_enabled: bool     
    audio_enabled: bool       

class IdleConfig(BaseModel):
    habilitado: bool

SYSTEM_PROMPT = """
Eres Reachy Mini, un robot interactivo, simpático y altamente expresivo.
Responde siempre de forma breve (máximo 1 o 2 oraciones).

OBLIGATORIO: Al inicio de tu respuesta debes incluir EXACTAMENTE una de las siguientes etiquetas en mayúsculas acorde al contexto de lo que dices:
[ALEGRE], [ASUSTADO], [PENSANDO], [SORPRENDIDO], [MIEDO], [BAILE], [ESCONDERSE], [TRISTE], [ENFADADO], [CURIOSO], [TIMIDO], [SALUDO], [ASENTIR], [NEGAR], [NEUTRAL].
"""

historial_mensajes = [{"role": "system", "content": SYSTEM_PROMPT}]

MAPA_LLM_A_ROBOT = {
    "ALEGRE": "alegre", "ASUSTADO": "asustado", "PENSANDO": "pensando", 
    "SORPRENDIDO": "sorprendido", "MIEDO": "miedo", "BAILE": "baile", 
    "ESCONDERSE": "esconderse", "TRISTE": "triste", "ENFADADO": "enfadado", 
    "CURIOSO": "curioso", "TIMIDO": "timido", "SALUDO": "saludo", 
    "ASENTIR": "asentir", "NEGAR": "negar", "NEUTRAL": "neutral"
}

@app.get("/", response_class=HTMLResponse)
def index():
    with open("interfaz.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/config/idle")
async def configurar_movimiento_idle(config_payload: IdleConfig):
    gestor.permitir_idle = config_payload.habilitado
    print(f"[CONFIG] Movimiento autónomo cambiado a: {gestor.permitir_idle}")
    if not gestor.permitir_idle:
        try: 
            gestor.robot.goto_target(head=create_head_pose(yaw=0, pitch=0, roll=0, degrees=True), antennas=np.deg2rad([0, 0]), duration=0.2)
        except Exception: 
            pass
    return {"estado": gestor.permitir_idle}

def ejecutor_hardware_asincrono(emocion, texto_hablar, usar_motores, usar_voz):
    try:
        print(f"[LOG_SINCRO] -> Ejecución de Fondo. Motores: {usar_motores} | TTS Voz: {usar_voz}")
        
        accion_emocion = emocion if usar_motores else "neutral"
        texto_tts = texto_hablar if usar_voz else None
        
        gestor.ejecutar_movimiento(accion_emocion, texto_a_hablar=texto_tts, audio_activado=usar_voz)
        
        if usar_voz and texto_hablar:
            num_palabras = len(texto_hablar.split())
            time.sleep(min((num_palabras / 2.5) + 0.4, 4.0))

        if usar_motores:
            gestor.ejecutar_movimiento("neutral", texto_a_hablar=None, audio_activado=False)
            print("[LOG_SINCRO] -> Motores reposicionados a Neutral.")
    except Exception as e:
        print(f"[LOG_SINCRO][ERROR ASYNC] Error en hardware: {e}")

@app.post("/api/chat")
async def chat_with_reachy(payload: UserMessage):
    global historial_mensajes
    user_text = payload.text.strip()
    
    if not user_text:
        raise HTTPException(status_code=400, detail="Texto vacío.")

    print(f"\n[LOG_SINCRO] === NUEVA INTERACCIÓN MODULAR ===")
    print(f"[LOG_SINCRO] Entrada: '{user_text}'")

    if user_text.startswith("COMANDO_MANUAL:"):
        emocion_directa = user_text.split(":")[1].lower()
        if emocion_directa in MAPA_LLM_A_ROBOT.values() or emocion_directa == "neutral":
            threading.Thread(target=ejecutor_hardware_asincrono, args=(emocion_directa, None, True, False), daemon=True).start()
            return {"robot_response": f"Movimiento manual '{emocion_directa}' despachado.", "emotion_executed": emocion_directa}

    if payload.motores_enabled:
        try: gestor.ejecutar_movimiento("pensando", texto_a_hablar=None, audio_activado=False)
        except Exception: pass

    historial_mensajes.append({"role": "user", "content": user_text})
    
    try:
        t_inicial_llm = time.time()
        response = ollama.chat(model=config.OLLAMA_MODEL, messages=historial_mensajes)
        reply = response['message']['content']
        historial_mensajes.append({"role": "assistant", "content": reply})
        print(f"[LOG_SINCRO] Inferencia LLM lista en {time.time() - t_inicial_llm:.2f}s")
        
        emocion_robot = "neutral"
        texto_limpio = reply
        
        if payload.procesar_etiquetas:
            reply_normalizado = reply.upper().replace("*", "").replace("[", "").replace("]", "")
            for tag, move_id in MAPA_LLM_A_ROBOT.items():
                raiz_corta = tag[:-1] if len(tag) > 4 else tag
                if f"[{tag}]" in reply_normalizado or reply_normalizado.startswith(tag) or f"[{raiz_corta}]" in reply_normalizado or reply_normalizado.startswith(raiz_corta):
                    emocion_robot = move_id
                    texto_limpio = reply.replace(f"[{tag}]", "").replace(f"**{tag}**", "").replace(tag, "")
                    texto_limpio = texto_limpio.replace(f"[{raiz_corta}]", "").replace(raiz_corta, "")
                    texto_limpio = texto_limpio.replace("[BAIL]", "").replace("BAIL", "")
                    texto_limpio = texto_limpio.replace("[TRIST]", "").replace("TRIST", "")
                    texto_limpio = texto_limpio.replace("[ASUNT]", "").replace("ASUNT", "")
                    break

        texto_limpio = texto_limpio.replace("*", "").strip()
        if texto_limpio.startswith((".", ",", " ", ":", "-")):
            texto_limpio = texto_limpio[1:].strip()

        threading.Thread(
            target=ejecutor_hardware_asincrono, 
            args=(emocion_robot, texto_limpio, payload.motores_enabled, payload.audio_enabled), 
            daemon=True
        ).start()

        return {"robot_response": texto_limpio, "emotion_executed": emocion_robot}

    except Exception as e:
        print(f"[LOG_SINCRO][CRITICAL] Error en api/chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/shutdown")
async def shutdown_system():
    print("\n[SISTEMA] Iniciando secuencia de apagado definitivo...")
    try:
        gestor.desactivar()
        gestor.ejecutar_movimiento("neutral", audio_activado=False)
        pygame.mixer.quit()
    except Exception: pass

    def aniquilar_arbol_procesos():
        time.sleep(0.4) 
        try:
            pid_actual = os.getpid()
            salida = subprocess.check_output(f"wmic process where processid={pid_actual} get parentprocessid", shell=True)
            ppid = int(salida.decode().split()[1])
            subprocess.Popen(f"taskkill /F /PID {ppid} /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pid_actual = os.getpid()
            subprocess.Popen(f"taskkill /F /FI \"PID eq {pid_actual}\" /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    threading.Thread(target=aniquilar_arbol_procesos, daemon=True).start()
    return {"status": "Ecosistema cerrado correctamente."}