# AUTOPILOT PONG — Hackathon Spec

## Project Overview
- **Name**: Autopilot Pong
- **Type**: Arcade Game / AI Spectator
- **Core**: Retro Pong with AI battle modes and cyberpunk aesthetics
- **Target**: Hackathon demo (3hr build time)

## Visual Specification

### Scene Setup
- **Resolution**: 800x600, scaled to window
- **Background**: Dark (#0a0a0f) with subtle grid lines
- **Court**: Classic center line (dashed), neon glow

### Color Palette
- Primary: Cyan (#00ffff)
- Secondary: Magenta (#ff00ff)
- Accent: Yellow (#ffff00)
- Ball: White with cyan glow
- Player paddle: Cyan
- AI paddle: Magenta

### Effects
- CRT scanlines overlay
- Chromatic aberration on edges
- Ball trail (motion blur)
- Glow/bloom on paddles and ball
- Screen shake on goal

## Game Modes

### 1. VS AI (Default)
- Player controls left paddle (UP/DOWN or W/S)
- AI controls right paddle
- First to 11 wins

### 2. ZEN MODE (AI vs AI)
- Both paddles controlled by AI
- Player watches and presses SPACE to "nudge" difficulty
- Real-time difficulty display

### 3. SYMBIOSIS MODE (AI Assist)
- AI helps catch difficult balls (rubber-band assist)
- Trajectory prediction line shown
- Reduced difficulty curve

## Physics
- Ball speed: starts 5, increases 0.2 per hit
- Max ball speed: 12
- Paddle momentum: ball inherits 20% paddle velocity
- Wall bounce: simple reflection
- Goal: ball passes paddle edge

## AI Behavior
- **Easy**: 60% accuracy, slow reaction
- **Medium**: 80% accuracy, moderate reaction
- **Hard**: 95% accuracy, instant reaction

## Audio
- Procedural blip on paddle hit (pitch varies with ball speed)
- Blip on wall bounce
- Buzz on goal
- Beat pulse on scoring (if time permits)

## Controls
- **W/S or Arrow UP/DOWN**: Move paddle
- **SPACE**: Pause / Start / Mode select
- **ESC**: Quit
- **1/2/3**: Switch AI difficulty

## Acceptance Criteria
- [ ] Smooth 60fps gameplay
- [ ] Ball physics feel "right" (responsive, predictable)
- [ ] AI is beatable but challenging
- [ ] CRT effect visible but not distracting
- [ ] Sound effects on all interactions
- [ ] Score tracked correctly
- [ ] Win condition triggers replay option
