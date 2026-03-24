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

class HandSystem:
    def __init__(self):
        self.mp_hands=mp.solutions_hands
        self.hands=self.mp_hands.Hands(max_num_hands=1,min_detection_confidence=0.7)

    def process(self,img):
        img_rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        results=self.hands.process(img_rgb)

        if results.multi_hand_landmarks:
            landmarks=results.multi_hand_landmarks[0].landmark
            h,w,_=img.shape
            return [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        return None
    
