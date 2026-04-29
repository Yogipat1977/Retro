"""
AUTOPILOT PONG — Hand Tracker (v3.0 - Tasks API)
MediaPipe-based hand tracking for paddle control via webcam.
Compatible with MediaPipe 0.10.0+ (Tasks API).
"""

import threading
import time
import os
import numpy as np
from config import (
    HEIGHT, HAND_TRACKING_CAMERA_INDEX,
    HAND_TRACKING_PIP_SIZE, HAND_TRACKING_SMOOTHING
)

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MP_AVAILABLE = True
except ImportError:
    MP_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class HandTracker:
    def __init__(self, camera_index=None):
        self.camera_index = camera_index or HAND_TRACKING_CAMERA_INDEX
        self._available = CV2_AVAILABLE and MP_AVAILABLE
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

        # Shared state
        self._paddle_y = 0.5
        self._smoothed_y = 0.5
        self._frame = None
        self._hand_detected = False

        self._cap = None
        self._detector = None
        
        # Path to the model file
        self.model_path = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")

    def is_available(self):
        return self._available and os.path.exists(self.model_path)

    def start(self):
        if not self.is_available():
            return False

        # Try multiple indices
        found = False
        for index in [0, 1, 2, -1]:
            try:
                self._cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
                if not self._cap.isOpened():
                    self._cap = cv2.VideoCapture(index)
                
                if self._cap.isOpened():
                    ret, _ = self._cap.read()
                    if ret:
                        self.camera_index = index
                        found = True
                        break
                    else:
                        self._cap.release()
            except Exception:
                continue

        if not found:
            return False

        try:
            # Initialize MediaPipe Tasks Detector
            base_options = python.BaseOptions(model_asset_path=self.model_path)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=1,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self._detector = vision.HandLandmarker.create_from_options(options)

            self._running = True
            self._thread = threading.Thread(target=self._tracking_loop, daemon=True)
            self._thread.start()
            return True
        except Exception as e:
            print(f"❌ HandTracker Error: {e}")
            return False

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        if self._cap:
            self._cap.release()
        if self._detector:
            self._detector.close()

    def get_paddle_y(self):
        with self._lock:
            return self._smoothed_y

    def get_hand_detected(self):
        with self._lock:
            return self._hand_detected

    def get_frame(self):
        with self._lock:
            return self._frame

    def _tracking_loop(self):
        while self._running:
            try:
                ret, frame = self._cap.read()
                if not ret:
                    time.sleep(0.01)
                    continue

                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to MediaPipe Image
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                
                # Detect
                result = self._detector.detect(mp_image)

                hand_detected = False
                paddle_y = 0.5

                if result.hand_landmarks:
                    hand_detected = True
                    # Use landmark 9 (Middle finger MCP) for stability
                    # result.hand_landmarks is a list of lists of landmarks
                    lm = result.hand_landmarks[0][9]
                    paddle_y = lm.y

                    # Draw a simple dot on the frame for feedback (manual drawing)
                    h, w, _ = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 255), -1)

                with self._lock:
                    self._hand_detected = hand_detected
                    if hand_detected:
                        alpha = HAND_TRACKING_SMOOTHING
                        self._smoothed_y = (
                            self._smoothed_y * (1 - alpha) + paddle_y * alpha
                        )
                    
                    if PYGAME_AVAILABLE:
                        pip_w, pip_h = HAND_TRACKING_PIP_SIZE
                        small = cv2.resize(frame, (pip_w, pip_h))
                        small_rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
                        self._frame = pygame.image.frombuffer(
                            small_rgb.tobytes(), (pip_w, pip_h), "RGB"
                        )

            except Exception:
                time.sleep(0.01)
                continue

            time.sleep(0.033)
