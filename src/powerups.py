"""
AUTOPILOT PONG — Power-Up System
Spawnable power-ups with unique effects, collision detection, and HUD display.
"""

import pygame
import random
import math
from config import (
    WIDTH, HEIGHT, COLORS,
    POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX, POWERUP_DURATION,
    POWERUP_SIZE, POWERUP_PULSE_SPEED, POWERUP_TYPES
)


class PowerUp:
    """A single power-up orb on the court."""

    def __init__(self, powerup_type):
        self.type = powerup_type
        self.info = POWERUP_TYPES[powerup_type]
        self.color = COLORS[self.info["color"]]
        self.x = WIDTH // 2 + random.randint(-150, 150)
        self.y = random.randint(80, HEIGHT - 80)
        self.radius = POWERUP_SIZE
        self.alive = True
        self.phase = random.uniform(0, math.pi * 2)

    def update(self, dt=1):
        """Update pulse animation."""
        self.phase += POWERUP_PULSE_SPEED * 0.05

    def draw(self, surface):
        """Draw power-up with pulsing glow."""
        pulse = 0.7 + 0.3 * math.sin(self.phase)

        # Outer glow layers (additive)
        for layer in range(4, 0, -1):
            glow_r = int(self.radius * (1 + layer * 0.5) * pulse)
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            alpha = int(40 / layer * pulse)
            pygame.draw.circle(glow_surf, (*self.color[:3], alpha),
                               (glow_r, glow_r), glow_r)
            surface.blit(glow_surf,
                         (int(self.x) - glow_r, int(self.y) - glow_r),
                         special_flags=pygame.BLEND_RGB_ADD)

        # Core circle
        pygame.draw.circle(surface, self.color,
                           (int(self.x), int(self.y)), int(self.radius * pulse))

        # Inner highlight
        highlight_r = int(self.radius * 0.4 * pulse)
        if highlight_r > 0:
            pygame.draw.circle(surface, (255, 255, 255),
                               (int(self.x), int(self.y) - 3),
                               highlight_r)

    def collides_with_ball(self, ball_x, ball_y, ball_radius=8):
        """Check if a ball hits this power-up."""
        dist = math.sqrt((self.x - ball_x) ** 2 + (self.y - ball_y) ** 2)
        return dist < self.radius + ball_radius


class ActiveEffect:
    """A currently active power-up effect with a countdown timer."""

    def __init__(self, effect_type, duration=None):
        self.type = effect_type
        self.info = POWERUP_TYPES[effect_type]
        self.color = COLORS[self.info["color"]]
        self.duration = duration or POWERUP_DURATION
        self.timer = self.duration
        self.active = True

    def update(self, dt):
        """Tick down the timer."""
        self.timer -= dt
        if self.timer <= 0:
            self.active = False

    @property
    def remaining_ratio(self):
        """0.0 to 1.0 — how much time is left."""
        return max(0, self.timer / self.duration)


class PowerUpManager:
    """Manages power-up spawning, collision, and active effects."""

    def __init__(self):
        self.current_powerup = None     # PowerUp on court (or None)
        self.active_effects = []        # List of ActiveEffect
        self.spawn_timer = random.uniform(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)

    def update(self, dt):
        """Update spawn timer, current power-up, and active effects."""
        # Spawn timer
        if self.current_powerup is None:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self._spawn()
        else:
            self.current_powerup.update(dt)

        # Active effects
        for effect in self.active_effects:
            effect.update(dt)
        self.active_effects = [e for e in self.active_effects if e.active]

    def _spawn(self):
        """Spawn a random power-up."""
        ptype = random.choice(list(POWERUP_TYPES.keys()))
        self.current_powerup = PowerUp(ptype)
        self.spawn_timer = random.uniform(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)

    def check_ball_collision(self, ball_x, ball_y):
        """Check if ball hits the current power-up. Returns type if collected, else None."""
        if self.current_powerup and self.current_powerup.collides_with_ball(ball_x, ball_y):
            collected_type = self.current_powerup.type
            collected_pos = (self.current_powerup.x, self.current_powerup.y)
            collected_color = self.current_powerup.color

            # Activate the effect
            self.active_effects.append(ActiveEffect(collected_type))
            self.current_powerup = None
            self.spawn_timer = random.uniform(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)

            return collected_type, collected_pos, collected_color
        return None

    def has_effect(self, effect_type):
        """Check if a specific effect is currently active."""
        return any(e.type == effect_type and e.active for e in self.active_effects)

    def draw(self, surface):
        """Draw the current power-up on the court."""
        if self.current_powerup:
            self.current_powerup.draw(surface)

    def draw_hud(self, surface, font, x=10, y=10):
        """Draw active effect indicators on the HUD."""
        for i, effect in enumerate(self.active_effects):
            # Background bar
            bar_w = 120
            bar_h = 20
            bar_x = x
            bar_y = y + i * 28

            # Background
            bg = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 120))
            surface.blit(bg, (bar_x, bar_y))

            # Fill bar
            fill_w = int(bar_w * effect.remaining_ratio)
            if fill_w > 0:
                fill = pygame.Surface((fill_w, bar_h), pygame.SRCALPHA)
                fill.fill((*effect.color[:3], 150))
                surface.blit(fill, (bar_x, bar_y))

            # Label
            label = font.render(effect.type, True, effect.color)
            surface.blit(label, (bar_x + 4, bar_y + 2))

            # Border
            pygame.draw.rect(surface, effect.color,
                             (bar_x, bar_y, bar_w, bar_h), 1)

    def reset(self):
        """Clear all power-ups and effects."""
        self.current_powerup = None
        self.active_effects.clear()
        self.spawn_timer = random.uniform(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)
