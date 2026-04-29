"""
AUTOPILOT PONG — Hand Tracker
MediaPipe-based hand tracking for paddle control via webcam.
Runs in a background thread for smooth 60fps gameplay.
"""

import threading
import time
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
    MP_AVAILABLE = True
except ImportError:
    MP_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class HandTracker:
    """
    Webcam-based hand tracking for paddle control.
    Uses MediaPipe to detect hand landmarks and maps vertical
    position to paddle Y coordinate.
    Runs capture + detection in a background thread.
    """

    def __init__(self, camera_index=None):
        self.camera_index = camera_index or HAND_TRACKING_CAMERA_INDEX
        self._available = CV2_AVAILABLE and MP_AVAILABLE
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

        # Shared state (protected by lock)
        self._paddle_y = 0.5          # Normalized 0.0 (top) to 1.0 (bottom)
        self._smoothed_y = 0.5
        self._frame = None            # Latest webcam frame as pygame Surface
        self._hand_detected = False

        # MediaPipe setup
        self._cap = None
        self._hands = None

    def is_available(self):
        """Check if hand tracking can be used."""
        return self._available

    def start(self):
        """Start the background hand tracking thread with auto-detection."""
        if not self._available:
            return False

        # Try multiple indices and backends
        found = False
        for index in [0, 1, 2, -1]:  # Try common indices
            try:
                # Try with V4L2 backend first on Linux
                self._cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
                if not self._cap.isOpened():
                    self._cap = cv2.VideoCapture(index)
                
                if self._cap.isOpened():
                    # Quick test grab
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
            print(f"❌ HandTracker: Could not open any camera.")
            return False

        try:
            # Set low resolution for speed
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

            # Initialize MediaPipe
            self._hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.5
            )

            self._running = True
            self._thread = threading.Thread(target=self._tracking_loop, daemon=True)
            self._thread.start()
            return True

        except Exception as e:
            print(f"❌ HandTracker Error: {e}")
            self._available = False
            return False

    def stop(self):
        """Stop tracking and release resources."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        if self._cap:
            self._cap.release()
        if self._hands:
            self._hands.close()

    def get_paddle_y(self):
        """Get the normalized paddle Y position (0.0 to 1.0)."""
        with self._lock:
            return self._smoothed_y

    def get_hand_detected(self):
        """Check if a hand is currently being tracked."""
        with self._lock:
            return self._hand_detected

    def get_frame(self):
        """Get the latest webcam frame as a pygame Surface for PiP display."""
        if not PYGAME_AVAILABLE:
            return None
        with self._lock:
            return self._frame

    def _tracking_loop(self):
        """Background thread: capture frames and detect hand landmarks."""
        while self._running:
            try:
                ret, frame = self._cap.read()
                if not ret:
                    time.sleep(0.01)
                    continue

                # Mirror horizontally for natural feel
                frame = cv2.flip(frame, 1)

                # Convert BGR to RGB for MediaPipe
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self._hands.process(rgb)

                hand_detected = False
                paddle_y = 0.5

                if results.multi_hand_landmarks:
                    hand = results.multi_hand_landmarks[0]
                    # Use landmark 9 (middle finger MCP) for stability
                    lm = hand.landmark[9]
                    paddle_y = lm.y  # Already normalized 0.0 to 1.0
                    hand_detected = True

                    # Draw hand landmarks on frame for PiP
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, hand,
                        mp.solutions.hands.HAND_CONNECTIONS
                    )

                # Smooth the Y value
                with self._lock:
                    self._hand_detected = hand_detected
                    if hand_detected:
                        alpha = HAND_TRACKING_SMOOTHING
                        self._smoothed_y = (
                            self._smoothed_y * (1 - alpha) + paddle_y * alpha
                        )
                        self._paddle_y = paddle_y

                    # Convert frame to pygame Surface
                    if PYGAME_AVAILABLE:
                        # Resize for PiP
                        pip_w, pip_h = HAND_TRACKING_PIP_SIZE
                        small = cv2.resize(frame, (pip_w, pip_h))
                        small_rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
                        # Transpose for pygame (OpenCV is HWC, pygame expects WHC)
                        self._frame = pygame.image.frombuffer(
                            small_rgb.tobytes(), (pip_w, pip_h), "RGB"
                        )

            except Exception:
                time.sleep(0.01)
                continue

            # Cap at ~30fps for tracking (no need for 60)
            time.sleep(0.033)
