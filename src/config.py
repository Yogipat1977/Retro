"""
AUTOPILOT PONG — Configuration & Constants
All game settings, colors, physics, and feature toggles.
"""

# ── Display ──────────────────────────────────────────────
WIDTH = 1280
HEIGHT = 720
FPS = 60

# ── Colors (Cyberpunk Palette) ───────────────────────────
COLORS = {
    # Base
    "bg":           (10, 10, 15),
    "grid":         (20, 20, 30),
    "gray":         (40, 40, 50),
    "dark_gray":    (25, 25, 35),
    "white":        (255, 255, 255),

    # Neon
    "cyan":         (0, 255, 255),
    "magenta":      (255, 0, 255),
    "yellow":       (255, 255, 0),
    "orange":       (255, 140, 0),
    "green":        (0, 255, 100),
    "red":          (255, 50, 50),
    "ice_blue":     (100, 200, 255),
    "purple":       (180, 0, 255),

    # Dim versions for glow layers
    "cyan_dim":     (0, 80, 80),
    "magenta_dim":  (80, 0, 80),
    "yellow_dim":   (80, 80, 0),
}

# ── Paddle ───────────────────────────────────────────────
PADDLE_WIDTH = 4
PADDLE_HEIGHT = 80
PADDLE_SPEED = 10
PADDLE_MARGIN = 30       # Distance from screen edge
PADDLE_FRICTION = 0.8    # Velocity decay when no input

# ── Ball ─────────────────────────────────────────────────
BALL_RADIUS = 4
BALL_INITIAL_SPEED = 7.0
BALL_SPEED_INCREMENT = 0.3    # Per paddle hit
BALL_MAX_SPEED = 18.0
BALL_MOMENTUM_TRANSFER = 0.15  # % of paddle velocity inherited

# ── Multi-Ball Difficulty ────────────────────────────────
# Level 1 = 1 ball, Level 2 = 2 balls, etc.
MAX_DIFFICULTY_LEVEL = 5
BALLS_PER_LEVEL = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
}

# ── AI ───────────────────────────────────────────────────
AI_PROFILES = {
    "ROOKIE":     {"reaction": 0.35, "accuracy": 0.55, "speed": 3, "label": "ROOKIE"},
    "TACTICIAN":  {"reaction": 0.65, "accuracy": 0.85, "speed": 6, "label": "TACTICIAN"},
    "BERSERKER":  {"reaction": 0.90, "accuracy": 0.70, "speed": 9, "label": "BERSERKER"},
    "ZEN_MASTER": {"reaction": 0.95, "accuracy": 0.98, "speed": 7, "label": "ZEN MASTER"},
}

# Adaptive difficulty: AI adjusts based on score gap
AI_ADAPTIVE_THRESHOLD = 3  # Score gap before AI adjusts

# ── Power-ups ────────────────────────────────────────────
POWERUP_SPAWN_MIN = 8.0   # seconds
POWERUP_SPAWN_MAX = 15.0  # seconds
POWERUP_DURATION = 5.0    # seconds active
POWERUP_SIZE = 18          # radius
POWERUP_PULSE_SPEED = 3.0  # glow pulse speed

POWERUP_TYPES = {
    "FIREBALL":   {"color": "orange",   "icon": "🔥", "desc": "Ball speed x2 + fire trail"},
    "FREEZE":     {"color": "ice_blue", "icon": "🧊", "desc": "Freeze opponent 2s"},
    "GROW":       {"color": "green",    "icon": "📏", "desc": "Your paddle grows 2x"},
    "SHRINK":     {"color": "red",      "icon": "📐", "desc": "Opponent paddle 50%"},
    "GHOST":      {"color": "white",    "icon": "👻", "desc": "Ball goes invisible"},
    "MULTIBALL":  {"color": "purple",   "icon": "💥", "desc": "Splits into 3 balls"},
}

# ── Particles ────────────────────────────────────────────
MAX_PARTICLES = 300
PARTICLE_TRAIL_RATE = 2       # Particles per frame for ball trail
PARTICLE_BURST_COUNT = 40     # Particles on goal
PARTICLE_SPARK_COUNT = 12     # Particles on paddle hit
PARTICLE_GRAVITY = 0.1
PARTICLE_FRICTION = 0.98

# ── Effects ──────────────────────────────────────────────
CRT_SCANLINE_ALPHA = 30
CRT_SCANLINE_SPACING = 3
CHROMATIC_ABERRATION_OFFSET = 2
SCREEN_SHAKE_DURATION = 15    # frames
SCREEN_SHAKE_INTENSITY = 5   # pixels
SCREEN_SHAKE_DECAY = 0.85

# ── Score ────────────────────────────────────────────────
WIN_SCORE = 11

# ── Feature Toggles ─────────────────────────────────────
FEATURES = {
    "crt_effect": True,
    "particles": True,
    "screen_shake": True,
    "hand_tracking": False,    # Toggled with H key
    "powerups": True,
    "adaptive_ai": True,
    "combo_counter": True,
    "speed_lines": True,
}

# ── Hand Tracking ────────────────────────────────────────
HAND_TRACKING_CAMERA_INDEX = 0
HAND_TRACKING_PIP_SIZE = (160, 120)  # Picture-in-picture size
HAND_TRACKING_SMOOTHING = 0.6        # Higher = more responsive, lower = smoother
