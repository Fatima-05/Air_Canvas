import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import numpy as np
import mediapipe as mp
import math
import threading
import winsound

class Config:
    WIDTH, HEIGHT = 1280, 720
    SMOOTHING = 0.35
    BRUSH_SIZE = 12
    ARC_CENTER = (640, 0)
    ARC_RADIUS = 150
    ARC_THICKNESS = 60


class SoundEngine:
    def __init__(self):
        self.active = False
        self.velocity = 0
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True
        self.thread.start()
    
    def set_drawing(self, is_drawing, velocity):
        self.active = is_drawing
        self.velocity = velocity

    def _loop(self):
        while not self.stop_event.is_set():
            if self.active:
                freq = int(180 + (self.velocity * 6))
                freq = max(100, min(freq, 900))
                try:
                    winsound.Beep(freq, 20)
                except:
                    pass
            else:
                time.sleep(0.03)


class HandSystem:
    def __init__(self):
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

    def process(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0].landmark
            h, w, _ = img.shape
            return [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        return None

    def is_pointing_mode(self, landmarks):
        if not landmarks:
            return False

        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]

        index_extended = index_tip[1] < landmarks[6][1] - 20   

        middle_folded = middle_tip[1] > landmarks[10][1] - 10
        ring_folded   = ring_tip[1]   > landmarks[14][1] - 10
        pinky_folded  = pinky_tip[1]  > landmarks[18][1] - 10

        return index_extended and middle_folded and ring_folded and pinky_folded


class ArcPalette:
    def __init__(self):
        self.colors = [
            (0, 0, 255), (0, 165, 255), (0, 255, 255), (0, 255, 0),
            (255, 255, 0), (255, 0, 255), (255, 255, 255), (0, 0, 0)
        ]
        self.selected_index = 4

    def draw(self, img, hover_pt):
        cx, cy = Config.ARC_CENTER
        radius = Config.ARC_RADIUS
        num_colors = len(self.colors)
        sector_angle = 180 / num_colors
        hover_index = -1

        if hover_pt:
            hx, hy = hover_pt
            dist = math.hypot(hx - cx, hy - cy)
            if radius < dist < radius + Config.ARC_THICKNESS:
                angle = math.degrees(math.atan2(hy - cy, hx - cx))
                if angle < 0: angle += 360
                if 0 <= angle <= 180:
                    hover_index = int(angle / sector_angle)

        for i, color in enumerate(self.colors):
            start_ang = i * sector_angle
            end_ang = (i + 1) * sector_angle
            thick = Config.ARC_THICKNESS + (12 if i == hover_index else 0)
            cv2.ellipse(img, (cx, cy), (radius + thick//2, radius + thick//2),
                        0, start_ang, end_ang, color, thick)

        return hover_index


def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, Config.WIDTH)
    cap.set(4, Config.HEIGHT)

    hand_sys = HandSystem()
    palette = ArcPalette()
    sound = SoundEngine()

    canvas = np.zeros((Config.HEIGHT, Config.WIDTH, 3), dtype=np.uint8)
    
    smooth_x = smooth_y = 0
    prev_x = prev_y = 0
    current_color = (0, 255, 255)

    print("Air Canvas Activated - Pointing Mode")
    print("→ Extend your Index Finger to DRAW")
    print("→ Open your full hand to STOP drawing")
    print("Press 'q' to quit")

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        points = hand_sys.process(img)

        is_drawing = False
        velocity = 0

        if points:
            idx_tip = points[8]
            cx, cy = idx_tip

            if smooth_x == 0:
                smooth_x, smooth_y = cx, cy

            smooth_x = int(smooth_x * (1 - Config.SMOOTHING) + cx * Config.SMOOTHING)
            smooth_y = int(smooth_y * (1 - Config.SMOOTHING) + cy * Config.SMOOTHING)

            if hand_sys.is_pointing_mode(points):
                is_drawing = True
                velocity = math.hypot(smooth_x - cx, smooth_y - cy)

                if prev_x == 0:
                    prev_x, prev_y = smooth_x, smooth_y

                cv2.line(canvas, (prev_x, prev_y), (smooth_x, smooth_y),
                         current_color, Config.BRUSH_SIZE)

                prev_x, prev_y = smooth_x, smooth_y

            else:
                prev_x = prev_y = 0

            thumb_tip = points[4]
            dist = math.hypot(idx_tip[0] - thumb_tip[0], idx_tip[1] - thumb_tip[1])

            hover_idx = palette.draw(img, (smooth_x, smooth_y))

            if hover_idx != -1 and dist < 40:      
                if hover_idx == len(palette.colors) - 1: 
                    canvas[:] = 0
                else:
                    palette.selected_index = hover_idx
                    current_color = palette.colors[hover_idx]
                prev_x = prev_y = 0

        else:
            palette.draw(img, None)
            prev_x = prev_y = 0

        sound.set_drawing(is_drawing, velocity)

       
        img = cv2.add(img, canvas)
        cv2.imshow("Air Canvas - Pointing Mode", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    sound.stop_event.set()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
