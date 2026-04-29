# AUTOPILOT PONG v2.0 — Hackathon Spec

## Project Overview
- **Name**: Autopilot Pong — Hackathon Edition
- **Type**: Arcade Game / AI Spectator / Hand Tracking Demo
- **Core**: Retro Pong with multi-ball difficulty, hand tracking, power-ups, AI personalities
- **Stack**: Python 3 + Pygame + MediaPipe + OpenCV + NumPy

## Key Differentiators
1. **Hand Tracking**: Webcam-based paddle control via MediaPipe
2. **Multi-Ball Difficulty**: 1–5 simultaneous balls based on level
3. **Power-Up System**: 6 unique power-ups with visual effects
4. **AI Personalities**: 4 profiles with adaptive difficulty
5. **Zero External Assets**: All graphics and audio generated in code
6. **Modular Architecture**: 9 clean, self-contained modules

## Visual Specification

### Color Palette
- Primary: Cyan (#00ffff) — Player
- Secondary: Magenta (#ff00ff) — AI
- Accent: Yellow (#ffff00) — UI highlights
- Fireball: Orange (#ff8c00)
- Freeze: Ice Blue (#64c8ff)
- Background: Dark (#0a0a0f) with grid

### Effects
- CRT scanlines + vignette
- Additive-blended neon particle system (300 max)
- Chromatic aberration (intensifies during shake)
- Ball trails (cyan glow / fire trail)
- Pulsing paddle glow
- Speed lines at high velocity
- Confetti on win

## Game Modes
1. **VS AI** — Player vs AI, first to 11
2. **ZEN** — AI vs AI spectator mode
3. **SYMBIOSIS** — AI-assisted play with trajectory prediction

## Difficulty System
- Level 1: 1 ball (classic)
- Level 2: 2 balls
- Level 3: 3 balls
- Level 4: 4 balls
- Level 5: 5 balls (chaos)

## Power-Ups
- FIREBALL: 2x speed + fire trail (5s)
- FREEZE: Opponent paddle frozen (2s)
- GROW: Player paddle 2x size (5s)
- SHRINK: Opponent paddle 50% (5s)
- GHOST: Ball semi-invisible (5s)
- MULTIBALL: Splits all balls into 3

## AI Profiles
- ROOKIE: Clumsy, slow, sometimes wrong direction
- TACTICIAN: Trajectory prediction, corner shots
- BERSERKER: Max speed, aggressive
- ZEN MASTER: Near-perfect, minimal movement

## Physics
- Ball speed: starts 5, +0.2 per hit, max 12
- Paddle momentum transfer: 15%
- Wall bounce: simple reflection
- Fireball: 2x speed multiplier

## Audio (Procedural)
- Sine, square, sawtooth waveform synthesis
- Dynamic pitch based on ball speed
- Rising arpeggio on power-up pickup
- All generated in-memory (no files)

## Acceptance Criteria
- [x] Smooth 60fps gameplay
- [x] Multi-ball difficulty (1-5 balls)
- [x] Hand tracking via webcam (optional)
- [x] 6 power-ups with visual effects
- [x] 4 AI personality profiles
- [x] Neon particle system with additive blending
- [x] CRT scanline effect
- [x] Procedural audio
- [x] Combo counter
- [x] Adaptive AI difficulty
- [x] One-command setup (setup.sh/setup.bat)
- [x] Graceful fallback for missing dependencies
- [x] Comprehensive README for judges
