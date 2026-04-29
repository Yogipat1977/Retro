# 🎮 AUTOPILOT PONG — Hackathon Edition (v3.0)

> **A high-performance, AI-driven, neon-noir arcade experience built entirely in Python.**

Autopilot Pong isn't just a clone; it's a technical showcase of **procedural generation**, **computer vision**, and **advanced game physics**. Built for a 1280x720 HD display, it features zero external assets—all audio, visuals, and logic are generated in-code.

---

## 🚀 Key Innovation: Why This Wins
1.  **Threaded AI Hand Tracking**: Control your paddle with zero-latency webcam tracking via MediaPipe.
2.  **Procedural Synthwave Engine**: Real-time waveform synthesis for all SFX—no audio files needed.
3.  **Multi-Ball Chaos**: Difficulty scales by object density (1–5 simultaneous balls).
4.  **Adaptive AI Personalities**: 4 unique AI profiles that adjust their skill based on your performance.
5.  **Pure Code Visuals**: Custom neon particle engine, CRT scanline filters, and chromatic aberration.

---

## 🕹️ Controls

| Key | Action |
|-----|--------|
| **SPACE** | Start / Pause / Resume |
| **W / S** | Move Paddle (Up / Down) |
| **H** | **Toggle Hand Tracking (Webcam)** |
| **1 – 5** | Change Difficulty (Number of Balls) |
| **P** | Cycle AI Personalities |
| **M** | Return to Main Menu |
| **Q** | Quit Game |

---

## 🛠️ Technical Setup

### Option A: Automated (Recommended)
```bash
# Setup virtual environment and dependencies
chmod +x setup.sh && ./setup.sh

# Launch the HD Experience
./run.sh
```

### Option B: Manual (Python 3.10+)
```bash
pip install pygame numpy opencv-python mediapipe
python3 src/game.py
```

---

## 🧠 AI Personality Profiles
*   **ROOKIE**: Prone to mistakes, slow reactions.
*   **TACTICIAN**: Predicts ball trajectory and aims for corners.
*   **BERSERKER**: Maximum speed, aggressive charging.
*   **ZEN MASTER**: Near-flawless, efficient movement.

---

## ✨ Advanced Visuals
*   **Additive Glow**: Multi-layered neon glow around all game objects.
*   **Particle Engine**: Custom-built system for trails, sparks, and goal explosions.
*   **Post-Processing**: Real-time CRT scanlines and RGB color shifting (Chromatic Aberration).

---

## 🔧 Troubleshooting
*   **Camera Error**: The game automatically scans for camera indices (0, 1, 2) and fallback drivers. Ensure no other app is using your webcam.
*   **No Sound**: The game detects if your system supports `pygame.mixer` and gracefully switches to silent mode if needed.
*   **Performance**: If the game lags, the particle system automatically caps at 300 objects to maintain 60FPS.

---

## 📄 Final Status
*   **Resolution**: 1280 x 720 (HD)
*   **Engine**: Pure Python / Pygame
*   **Hand Tracking**: MediaPipe Tasks API v3.0 (Low-Latency)
*   **Assets**: 100% Code-Generated
