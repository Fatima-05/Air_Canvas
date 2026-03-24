import cv2
import numpy as np
import mediapipe as mp
import math
import time
import threading
import winsound

class Config:
    WIDTH,HEIGHT=1280,720
    PINCH_THRESHOLD=40
    SMOOTHING=0.6
    BRUSH_SIZE=8
    ARC_CENTER=(640,0)
    ARC_RADIUS=150
    ARC_THICKNESS=60

class SoundEngine:
    def __init__(self):
        self.active=False
        self.velocity=0
        self.stop_event=threading.Event()
        self.thread.start()
    
    def set_drawing(self,is_drawing,velocity):
        self.active=is_drawing
        self.velocity=velocity

    def _loop(self):
        while not self.stop_event.is_set():
            if self.active:
                freq=int(200+(self.velocity*5))
                freq=max(100,min(freq,800))
                winsound.Beep(freq,30)
            else:
                time.sleep(0.05)

