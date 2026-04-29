"""
AUTOPILOT PONG — Particle Engine
Neon glow particle system using additive blending (BLEND_RGB_ADD).
"""

import pygame
import random
import math
from config import (
    COLORS, MAX_PARTICLES, PARTICLE_GRAVITY, PARTICLE_FRICTION,
    PARTICLE_TRAIL_RATE, PARTICLE_BURST_COUNT, PARTICLE_SPARK_COUNT
)


class Particle:
    """A single particle with position, velocity, color, size, and lifetime."""
    __slots__ = ['x', 'y', 'vx', 'vy', 'color', 'size', 'lifetime',
                 'max_lifetime', 'gravity', 'has_gravity']

    def __init__(self, x, y, vx, vy, color, size=4, lifetime=30, gravity=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = PARTICLE_GRAVITY if gravity else 0
        self.has_gravity = gravity

    def update(self):
        """Update particle position and decay."""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= PARTICLE_FRICTION
        self.vy *= PARTICLE_FRICTION
        self.lifetime -= 1

    @property
    def alive(self):
        return self.lifetime > 0

    @property
    def alpha(self):
        """Current opacity based on remaining lifetime."""
        return max(0, min(255, int(255 * (self.lifetime / self.max_lifetime))))

    @property
    def current_size(self):
        """Size shrinks as particle dies."""
        ratio = self.lifetime / self.max_lifetime
        return max(1, int(self.size * ratio))


class ParticleEmitter:
    """Manages all particles in the game. Call emit methods to create effects."""

    def __init__(self):
        self.particles = []

    def update(self):
        """Update all particles and remove dead ones."""
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

        # Cap particle count for performance
        if len(self.particles) > MAX_PARTICLES:
            self.particles = self.particles[-MAX_PARTICLES:]

    def draw(self, surface):
        """Draw all particles with additive blending for neon glow."""
        for p in self.particles:
            size = p.current_size
            if size < 1:
                continue

            # Create glow surface
            glow_size = size * 3
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)

            # Outer glow (dim, large)
            alpha_outer = max(0, p.alpha // 4)
            color_outer = (*p.color[:3], alpha_outer)
            pygame.draw.circle(glow_surf, color_outer,
                               (glow_size, glow_size), glow_size)

            # Inner glow (brighter, smaller)
            alpha_inner = max(0, p.alpha // 2)
            color_inner = (*p.color[:3], alpha_inner)
            pygame.draw.circle(glow_surf, color_inner,
                               (glow_size, glow_size), size * 2)

            # Core (brightest, smallest)
            color_core = (*p.color[:3], p.alpha)
            pygame.draw.circle(glow_surf, color_core,
                               (glow_size, glow_size), size)

            # Blit with additive blending
            surface.blit(glow_surf,
                         (int(p.x) - glow_size, int(p.y) - glow_size),
                         special_flags=pygame.BLEND_RGB_ADD)

    # ── Emission Methods ─────────────────────────────────

    def emit_trail(self, x, y, color=None):
        """Continuous ball trail — call every frame."""
        if color is None:
            color = COLORS["cyan"]
        for _ in range(PARTICLE_TRAIL_RATE):
            self.particles.append(Particle(
                x + random.uniform(-3, 3),
                y + random.uniform(-3, 3),
                random.uniform(-0.5, 0.5),
                random.uniform(-0.5, 0.5),
                color, size=3, lifetime=15, gravity=False
            ))

    def emit_fire_trail(self, x, y):
        """Fireball power-up trail — intense orange/red particles."""
        for _ in range(PARTICLE_TRAIL_RATE * 2):
            color = random.choice([COLORS["orange"], COLORS["red"], COLORS["yellow"]])
            self.particles.append(Particle(
                x + random.uniform(-5, 5),
                y + random.uniform(-5, 5),
                random.uniform(-1, 1),
                random.uniform(-2, 0.5),
                color, size=5, lifetime=20, gravity=True
            ))

    def emit_burst(self, x, y, color=None, count=None):
        """Explosion burst — used on goals and power-up pickups."""
        if color is None:
            color = COLORS["cyan"]
        if count is None:
            count = PARTICLE_BURST_COUNT
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 8)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                color, size=random.randint(3, 7),
                lifetime=random.randint(20, 50),
                gravity=True
            ))

    def emit_sparks(self, x, y, direction=1, color=None):
        """Directional sparks — used on paddle hits."""
        if color is None:
            color = COLORS["white"]
        for _ in range(PARTICLE_SPARK_COUNT):
            angle = random.uniform(-math.pi / 3, math.pi / 3)
            speed = random.uniform(3, 7)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed * direction,
                math.sin(angle) * speed,
                color, size=random.randint(2, 4),
                lifetime=random.randint(10, 25),
                gravity=False
            ))

    def emit_confetti(self, width, height):
        """Win celebration — colorful confetti rain from top."""
        colors = [COLORS["cyan"], COLORS["magenta"], COLORS["yellow"],
                  COLORS["green"], COLORS["orange"]]
        for _ in range(5):  # Call every frame during celebration
            self.particles.append(Particle(
                random.uniform(0, width),
                -10,
                random.uniform(-1, 1),
                random.uniform(1, 4),
                random.choice(colors),
                size=random.randint(3, 6),
                lifetime=random.randint(60, 120),
                gravity=True
            ))

    def emit_powerup_pickup(self, x, y, color):
        """Radial burst when a power-up is collected."""
        self.emit_burst(x, y, color, count=30)
        # Add ring of particles
        for i in range(16):
            angle = (math.pi * 2 / 16) * i
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * 5,
                math.sin(angle) * 5,
                color, size=4, lifetime=25, gravity=False
            ))

    def emit_freeze(self, x, y):
        """Ice crystal burst when freeze activates."""
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            self.particles.append(Particle(
                x + random.uniform(-20, 20),
                y + random.uniform(-40, 40),
                math.cos(angle) * speed,
                math.sin(angle) * speed * 0.3,
                COLORS["ice_blue"], size=random.randint(2, 5),
                lifetime=random.randint(30, 60),
                gravity=False
            ))

    def clear(self):
        """Remove all particles."""
        self.particles.clear()
