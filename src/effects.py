"""
AUTOPILOT PONG — Visual Effects
CRT scanlines, chromatic aberration, screen shake, glow, speed lines.
"""

import pygame
import random
import math
from config import (
    WIDTH, HEIGHT, COLORS,
    CRT_SCANLINE_ALPHA, CRT_SCANLINE_SPACING,
    CHROMATIC_ABERRATION_OFFSET,
    SCREEN_SHAKE_INTENSITY, SCREEN_SHAKE_DECAY
)


class ScreenShake:
    """Smooth screen shake with dampening."""

    def __init__(self):
        self.timer = 0
        self.intensity = 0
        self.offset_x = 0
        self.offset_y = 0

    def trigger(self, duration=15, intensity=None):
        """Start a screen shake."""
        self.timer = duration
        self.intensity = intensity or SCREEN_SHAKE_INTENSITY

    def update(self):
        """Update shake offset."""
        if self.timer > 0:
            self.timer -= 1
            self.offset_x = random.uniform(-self.intensity, self.intensity)
            self.offset_y = random.uniform(-self.intensity, self.intensity)
            self.intensity *= SCREEN_SHAKE_DECAY
        else:
            self.offset_x = 0
            self.offset_y = 0

    @property
    def offset(self):
        return (int(self.offset_x), int(self.offset_y))

    @property
    def active(self):
        return self.timer > 0


def draw_crt_overlay(surface):
    """Draw CRT scanlines and vignette effect."""
    # Scanlines
    scanline_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(0, HEIGHT, CRT_SCANLINE_SPACING):
        pygame.draw.line(scanline_surf, (0, 0, 0, CRT_SCANLINE_ALPHA),
                         (0, y), (WIDTH, y), 1)
    surface.blit(scanline_surf, (0, 0))

    # Vignette (darkened edges)
    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    max_dist = math.sqrt(center_x ** 2 + center_y ** 2)

    # Draw concentric rectangles getting darker towards edges
    for i in range(0, 60, 2):
        alpha = int((i / 60) * 80)
        margin = i * 4
        if margin < min(WIDTH, HEIGHT) // 2:
            rect = pygame.Rect(margin, margin,
                               WIDTH - margin * 2, HEIGHT - margin * 2)
            pygame.draw.rect(vignette, (0, 0, 0, alpha), rect, 3)
    surface.blit(vignette, (0, 0))


def draw_chromatic_aberration(surface, intensity=1.0):
    """Draw RGB channel offset at screen edges."""
    offset = int(CHROMATIC_ABERRATION_OFFSET * intensity)
    if offset < 1:
        return

    # Red shift on right edge
    edge_r = pygame.Surface((offset * 2, HEIGHT), pygame.SRCALPHA)
    edge_r.fill((255, 0, 0, 12))
    surface.blit(edge_r, (WIDTH - offset * 2, 0))

    # Blue shift on left edge
    edge_b = pygame.Surface((offset * 2, HEIGHT), pygame.SRCALPHA)
    edge_b.fill((0, 0, 255, 12))
    surface.blit(edge_b, (0, 0))


def draw_paddle_glow(surface, x, y, w, h, color, pulse_phase=0):
    """Draw subtle neon glow around a paddle."""
    pulse = 0.6 + 0.4 * math.sin(pulse_phase)

    for layer in range(2, 0, -1):
        glow_surf = pygame.Surface(
            (w + layer * 4, h + layer * 4), pygame.SRCALPHA
        )
        alpha = int(20 * pulse / layer)
        glow_color = (*color[:3], alpha)
        pygame.draw.rect(glow_surf, glow_color,
                         (0, 0, w + layer * 4, h + layer * 4),
                         border_radius=3)
        surface.blit(glow_surf,
                     (x - layer * 2, y - layer * 2),
                     special_flags=pygame.BLEND_RGB_ADD)


def draw_ball_glow(surface, x, y, radius, color=(255, 255, 255)):
    """Draw subtle neon glow around the ball."""
    for layer in range(2, 0, -1):
        glow_size = radius + layer * 2
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        alpha = int(40 / layer)
        pygame.draw.circle(glow_surf, (*color[:3], alpha),
                           (glow_size, glow_size), glow_size)
        surface.blit(glow_surf,
                     (int(x) - glow_size, int(y) - glow_size),
                     special_flags=pygame.BLEND_RGB_ADD)


def draw_speed_lines(surface, ball_speed, max_speed, ball_x, ball_y, ball_vx):
    """Draw radial speed lines when ball is moving fast."""
    speed_ratio = abs(ball_speed) / max_speed
    if speed_ratio < 0.5:
        return

    alpha = int(80 * (speed_ratio - 0.5) * 2)
    direction = -1 if ball_vx > 0 else 1

    speed_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(int(8 * speed_ratio)):
        y_offset = random.randint(-HEIGHT // 3, HEIGHT // 3)
        length = random.randint(30, 80)
        start_x = ball_x + direction * random.randint(20, 60)
        pygame.draw.line(speed_surf, (255, 255, 255, alpha),
                         (start_x, ball_y + y_offset),
                         (start_x + direction * length, ball_y + y_offset), 1)
    surface.blit(speed_surf, (0, 0))


def draw_grid(surface):
    """Draw the background grid."""
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(surface, COLORS["grid"], (0, y), (WIDTH, y), 1)
    for x in range(0, WIDTH, 40):
        pygame.draw.line(surface, COLORS["grid"], (x, 0), (x, HEIGHT), 1)


def draw_center_line(surface):
    """Draw the center court divider."""
    pygame.draw.line(surface, COLORS["gray"],
                     (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 3)
    for i in range(0, HEIGHT, 20):
        pygame.draw.line(surface, COLORS["gray"],
                         (WIDTH // 2 - 5, i), (WIDTH // 2 + 5, i), 2)


def draw_background_pulse(surface, hit_timer):
    """Subtle background flash on ball hits."""
    if hit_timer > 0:
        alpha = int(15 * (hit_timer / 10))
        flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash.fill((255, 255, 255, alpha))
        surface.blit(flash, (0, 0))
