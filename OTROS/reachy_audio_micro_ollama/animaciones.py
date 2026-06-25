import time
import math
import os
import random
import threading
import numpy as np
import pyttsx3
import pygame
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
import config

class GestorAnimaciones:
    def __init__(self):
        self.robot = None
        self.conectar_robot()
        self.ocupado = False  
        self.activo = True
        self.permitir_idle = False  # 🔒 MODIFICADO: Deshabilitado por defecto al arrancar
        
        try:
            pygame.mixer.init()
        except Exception:
            print("[AVISO] No se pudo inicializar pygame.mixer.")
        
        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty('rate', 170) 
        except Exception:
            self.tts = None
            print("[AVISO] No se pudo inicializar pyttsx3.")

        self.hilo_idle = threading.Thread(target=self._bucle_vida_autonoma, daemon=True)
        self.hilo_idle.start()

    def conectar_robot(self):
        try:
            print(f"[ROBOT] Conectando al simulador en {config.ROBOT_HOST}...")
            self.robot = ReachyMini(host=config.ROBOT_HOST, media_backend="no_media")
        except Exception:
            self.robot = None
            print("[ERROR] No se pudo conectar con el daemon de MuJoCo.")

    def reproducir_multimedia(self, texto, emocion, audio_activado):
        if not audio_activado:
            return
        ruta_sonido = f"sonidos/{emocion}.wav"
        if os.path.exists(ruta_sonido):
            try:
                pygame.mixer.music.load(ruta_sonido)
                pygame.mixer.music.play()
            except Exception:
                pass
        if self.tts and texto:
            print(f"[VOZ] Hablando: '{texto}'")
            self.tts.say(texto)
            self.tts.runAndWait()

    def ejecutar_movimiento(self, emocion: str, texto_a_hablar=None, audio_activado=True):
        if not self.robot:
            self.conectar_robot()
            if not self.robot: return

        # Bloqueo síncrono del hilo de impaciencia
        old_idle_state = self.permitir_idle
        self.permitir_idle = False 
        self.ocupado = True
        time.sleep(0.05) 
        
        print(f"[FISICO] Ejecutando: {emocion.upper()}")
        
        if emocion == "alegre":
            p_start = time.time()
            while time.time() - p_start < 1.0:
                t = time.time() - p_start
                self.robot.set_target(
                    head=create_head_pose(yaw=35*math.sin(t*5), pitch=-10+15*math.cos(t*9), roll=15*math.sin(t*5), degrees=True), 
                    antennas=np.deg2rad([60*math.sin(t*10), -60*math.sin(t*10)])
                )
                time.sleep(0.02)
            self.reproducir_multimedia(texto_a_hablar, "alegre", audio_activado)
                
        elif emocion == "asustado":
            p_start = time.time()
            while time.time() - p_start < 1.0:
                t = time.time() - p_start
                self.robot.set_target(
                    head=create_head_pose(yaw=3*math.sin(t*50), pitch=20+2*math.cos(t*55), roll=-5, degrees=True), 
                    antennas=np.deg2rad([-50, -50])
                )
                time.sleep(0.02)
            self.reproducir_multimedia(texto_a_hablar, "asustado", audio_activado)
                
        elif emocion == "pensando":
            self.robot.goto_target(head=create_head_pose(yaw=-20, pitch=15, roll=10, degrees=True), antennas=np.deg2rad([60, -20]), duration=0.3)
            self.reproducir_multimedia(texto_a_hablar, "pensando", audio_activado)
            
        elif emocion == "sorprendido":
            self.robot.goto_target(head=create_head_pose(yaw=0, pitch=-25, roll=0, degrees=True), antennas=np.deg2rad([85, 85]), duration=0.25)
            self.reproducir_multimedia(texto_a_hablar, "sorprendido", audio_activado)

        elif emocion == "miedo":
            p_start = time.time()
            while time.time() - p_start < 1.2:
                t = time.time() - p_start
                self.robot.set_target(
                    head=create_head_pose(yaw=8*math.sin(t*65), pitch=28+4*math.cos(t*70), roll=10*math.sin(t*40), degrees=True), 
                    antennas=np.deg2rad([-75, -75])
                )
                time.sleep(0.015)
            self.reproducir_multimedia(texto_a_hablar, "miedo", audio_activado)

        elif emocion == "baile":
            p_start = time.time()
            while time.time() - p_start < 2.0:
                t = time.time() - p_start
                self.robot.set_target(
                    head=create_head_pose(yaw=40*math.sin(t*6), pitch=-5+12*math.sin(t*12), roll=25*math.cos(t*6), degrees=True), 
                    antennas=np.deg2rad([70*math.cos(t*8), 70*math.sin(t*8)])
                )
                time.sleep(0.02)
            self.reproducir_multimedia(texto_a_hablar, "baile", audio_activado)

        elif emocion == "esconderse":
            self.robot.goto_target(head=create_head_pose(yaw=0, pitch=45, roll=0, degrees=True), antennas=np.deg2rad([-90, -90]), duration=0.5)
            self.reproducir_multimedia(texto_a_hablar, "esconderse", audio_activado)
            time.sleep(0.6)

        elif emocion == "triste":
            self.robot.goto_target(head=create_head_pose(yaw=10, pitch=30, roll=-10, degrees=True), antennas=np.deg2rad([-60, -60]), duration=0.5)
            self.reproducir_multimedia(texto_a_hablar, "triste", audio_activado)

        elif emocion == "enfadado":
            self.robot.goto_target(head=create_head_pose(yaw=0, pitch=-15, roll=0, degrees=True), antennas=np.deg2rad([90, 90]), duration=0.2)
            self.reproducir_multimedia(texto_a_hablar, "enfadado", audio_activado)

        elif emocion == "curioso":
            self.robot.goto_target(head=create_head_pose(yaw=25, pitch=-5, roll=20, degrees=True), antennas=np.deg2rad([10, 80]), duration=0.35)
            self.reproducir_multimedia(texto_a_hablar, "curioso", audio_activado)

        elif emocion == "timido":
            self.robot.goto_target(head=create_head_pose(yaw=-30, pitch=20, roll=-15, degrees=True), antennas=np.deg2rad([-30, -40]), duration=0.5)
            self.reproducir_multimedia(texto_a_hablar, "timido", audio_activado)

        elif emocion == "saludo":
            self.robot.goto_target(head=create_head_pose(yaw=-15, pitch=-10, roll=5, degrees=True), duration=0.25)
            self.robot.goto_target(head=create_head_pose(yaw=15, pitch=-10, roll=-5, degrees=True), duration=0.25)
            self.reproducir_multimedia(texto_a_hablar, "saludo", audio_activado)

        elif emocion == "asentir":
            for _ in range(2):
                self.robot.goto_target(head=create_head_pose(pitch=20, degrees=True), duration=0.15)
                self.robot.goto_target(head=create_head_pose(pitch=-10, degrees=True), duration=0.15)
            self.reproducir_multimedia(texto_a_hablar, "asentir", audio_activado)

        elif emocion == "negar":
            for _ in range(2):
                self.robot.goto_target(head=create_head_pose(yaw=25, degrees=True), duration=0.15)
                self.robot.goto_target(head=create_head_pose(yaw=-25, degrees=True), duration=0.15)
            self.reproducir_multimedia(texto_a_hablar, "negar", audio_activado)
            
        else:
            self.robot.goto_target(head=create_head_pose(yaw=0, pitch=0, roll=0, degrees=True), antennas=np.deg2rad([0, 0]), duration=0.3)
            if texto_a_hablar:
                self.reproducir_multimedia(texto_a_hablar, "neutral", audio_activado)
        
        self.ocupado = False
        self.permitir_idle = old_idle_state 

    def _bucle_vida_autonoma(self):
        while self.activo:
            if not self.ocupado and self.permitir_idle and self.robot:
                rand_yaw = random.uniform(-12, 12)
                rand_pitch = random.uniform(-8, 8)
                rand_roll = random.uniform(-5, 5)
                rand_antena_izq = random.uniform(-30, 40)
                rand_antena_der = random.uniform(-30, 40)
                
                try:
                    self.robot.goto_target(
                        head=create_head_pose(yaw=rand_yaw, pitch=rand_pitch, roll=rand_roll, degrees=True),
                        antennas=np.deg2rad([rand_antena_izq, rand_antena_der]),
                        duration=random.uniform(0.4, 0.8)
                    )
                except Exception:
                    pass
                time.sleep(random.uniform(2.5, 4.5))
            else:
                time.sleep(0.4)

    def desactivar(self):
        self.activo = False