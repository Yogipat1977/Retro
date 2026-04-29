# 🎮 AUTOPILOT PONG — Hackathon Edition

> **Retro-futurist Pong with hand tracking, multi-ball difficulty, power-ups, and AI battle modes.**

A cyberpunk arcade game built in Python featuring **webcam hand tracking**, **multi-ball difficulty scaling**, **6 unique power-ups**, **neon particle effects**, **4 AI personality profiles**, and **procedural synthwave audio** — all with zero external assets.

---

## 🚀 Quick Start (3 Steps)

### Option A: Automated Setup (Recommended)

```bash
# 1. Clone and enter the project
cd autopilot-pong

# 2. Run setup (creates venv + installs everything)
chmod +x setup.sh && ./setup.sh

# 3. Run the game!
./run.sh
```

### Option B: Manual Setup

```bash
# 1. Clone and enter the project
cd autopilot-pong

# 2. Install dependencies
pip install pygame numpy

# 3. (Optional) Install hand tracking dependencies
pip install opencv-python mediapipe

# 4. Run the game
cd src
python3 game.py
```

### Option C: Minimal (Just Pygame)

```bash
# If you only have pygame installed, the game still works!
# Hand tracking and enhanced audio will be disabled gracefully.
pip install pygame
cd autopilot-pong/src
python3 game.py
```

### Windows Users

```batch
cd autopilot-pong
setup.bat
run.bat
```

---

## 🎯 System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.7+ | 3.10+ |
| OS | Windows / macOS / Linux | Any |
| RAM | 256 MB | 512 MB |
| Webcam | Not required | Required for hand tracking |
| GPU | Not required | Not required |

### Dependencies

| Package | Required? | Purpose |
|---------|-----------|---------|
| `pygame` | ✅ Yes | Game engine |
| `numpy` | Optional | Better audio synthesis |
| `opencv-python` | Optional | Hand tracking (webcam) |
| `mediapipe` | Optional | Hand tracking (AI) |

> **Note**: The game runs perfectly with just `pygame`. All other dependencies add optional features and degrade gracefully if missing.

---

## 🕹️ Controls

| Key | Action |
|-----|--------|
| **W / ↑** | Move paddle up |
| **S / ↓** | Move paddle down |
| **SPACE** | Start / Pause / Restart |
| **1–5** | Set difficulty level (number of balls) |
| **H** | Toggle hand tracking (webcam) |
| **P** | Cycle AI personality |
| **ESC** | Pause (in-game) / Quit (menu) |

### 🖐️ Hand Tracking Mode

Press **H** to activate webcam hand tracking. Move your hand up and down in front of the camera to control the paddle. The webcam feed appears as a small picture-in-picture overlay.

> Requires `opencv-python` and `mediapipe` to be installed.

---

## 🎮 Game Modes

### 1. VS AI (Default)
Classic Pong — you (cyan paddle) vs the AI (magenta paddle). First to 11 wins.

### 2. ZEN Mode (Press 2 from menu)
Watch two AI personalities battle each other. Sit back and enjoy the light show.

### 3. SYMBIOSIS Mode (Press 3 from menu)
Play with AI assistance — the AI helps position your paddle for difficult shots. A yellow prediction line shows where the ball is heading.

---

## 🔥 Multi-Ball Difficulty System

**The core mechanic**: difficulty scales by adding MORE BALLS.

| Level | Balls | Description |
|-------|-------|-------------|
| 1 | 1 ball | Classic mode |
| 2 | 2 balls | Getting spicy |
| 3 | 3 balls | Chaos begins |
| 4 | 4 balls | Expert territory |
| 5 | 5 balls | Pure madness |

Press **1–5** during gameplay to change the level instantly. All balls are active simultaneously — miss any one and the opponent scores.

---

## ⚡ Power-Ups

Power-ups spawn randomly on the court. Hit the ball through them to activate!

| Power-Up | Color | Duration | Effect |
|----------|-------|----------|--------|
| 🔥 **FIREBALL** | Orange | 5s | Ball speed doubles + fire particle trail |
| 🧊 **FREEZE** | Ice Blue | 2s | Opponent's paddle freezes completely |
| 📏 **GROW** | Green | 5s | Your paddle grows to 2x size |
| 📐 **SHRINK** | Red | 5s | Opponent's paddle shrinks to 50% |
| 👻 **GHOST** | White | 5s | Ball becomes semi-invisible |
| 💥 **MULTIBALL** | Purple | Instant | Splits every ball into 3 |

Active power-ups are shown as countdown bars in the bottom-left HUD.

---

## 🧠 AI Personalities

Cycle through AI profiles with the **P** key:

| Profile | Style | Description |
|---------|-------|-------------|
| **ROOKIE** | Clumsy | Slow reactions, sometimes moves the wrong way |
| **TACTICIAN** | Strategic | Predicts ball trajectory, aims for corners |
| **BERSERKER** | Aggressive | Maximum speed, always charging |
| **ZEN MASTER** | Perfect | Near-flawless with minimal movement |

The AI also features **adaptive difficulty** — if you're losing badly, the AI subtly plays worse. If you're winning, it ramps up. Every game feels close.

---

## ✨ Visual Effects

- **CRT Scanlines**: Authentic retro TV overlay
- **Neon Particle System**: Additive-blended glow particles on every hit, goal, and power-up
- **Screen Shake**: Dampened camera shake on goals
- **Chromatic Aberration**: RGB color fringing at screen edges
- **Speed Lines**: Radial motion lines at high ball speeds
- **Paddle & Ball Glow**: Pulsing neon aura around all game objects
- **Confetti Celebration**: Particle rain on win screen

---

## 🎵 Audio

All sound effects are **procedurally generated** from waveform synthesis (sine, square, sawtooth waves). No external audio files are used.

- Paddle hit: Sharp square wave blip (pitch increases with ball speed)
- Wall bounce: Soft sine wave
- Goal: Descending sawtooth buzz
- Power-up: Rising arpeggio
- Level up: 5-note ascending fanfare
- Combo milestone: Every 5 consecutive hits

---

## 🏗️ Technical Architecture

```
autopilot-pong/
├── README.md              ← You are here
├── SPEC.md                ← Design specification
├── requirements.txt       ← pip dependencies
├── setup.sh / setup.bat   ← One-command setup
├── run.sh / run.bat       ← One-command run
└── src/
    ├── game.py            ← Main game loop, state machine, integration
    ├── config.py          ← All constants, colors, physics, toggles
    ├── particles.py       ← Neon particle engine (additive blending)
    ├── effects.py         ← CRT, glow, shake, chromatic aberration
    ├── powerups.py        ← Power-up spawning, collision, effects
    ├── ai_controller.py   ← AI personalities + adaptive difficulty
    ├── audio.py           ← Procedural waveform synthesis
    ├── hand_tracker.py    ← MediaPipe webcam tracking (threaded)
    └── ui.py              ← Menus, HUD, combo, transitions
```

### Design Principles
- **Modular**: Each feature is a self-contained module
- **Graceful Degradation**: Missing optional deps (numpy, opencv, mediapipe) are handled — game still runs
- **Zero External Assets**: Everything — graphics, audio, effects — is generated in code
- **Performance**: Particle system capped at 300 particles, hand tracking runs in a background thread at 30fps

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| **No sound** | Normal if `pygame.mixer` isn't available. Game runs silently. |
| **Hand tracking won't activate** | Install: `pip install opencv-python mediapipe` |
| **Low FPS** | Reduce particles in `config.py`: set `MAX_PARTICLES = 100` |
| **AVX2 warning** | Cosmetic only, safe to ignore |
| **Webcam not detected** | Check camera index in `config.py`: `HAND_TRACKING_CAMERA_INDEX` |

---

## 📄 License

Built for hackathon demonstration purposes.
