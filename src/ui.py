"""
AUTOPILOT PONG — UI System
Animated menus, HUD, combo counter, score popups, transitions.
"""

import pygame
import math
from config import WIDTH, HEIGHT, COLORS


class ComboCounter:
    """Tracks consecutive paddle hits and displays combo count."""

    def __init__(self):
        self.count = 0
        self.best = 0
        self.display_timer = 0
        self.flash_intensity = 0

    def hit(self):
        """Register a paddle hit."""
        self.count += 1
        self.best = max(self.best, self.count)
        self.display_timer = 90  # frames to display
        self.flash_intensity = 1.0

    def miss(self):
        """Reset on goal."""
        self.count = 0

    def update(self):
        if self.display_timer > 0:
            self.display_timer -= 1
        self.flash_intensity *= 0.95

    def draw(self, surface, font, big_font):
        if self.count < 2 or self.display_timer <= 0:
            return

        # Scale text based on combo
        text = f"COMBO x{self.count}"
        color_intensity = min(255, 100 + self.count * 20)

        if self.count >= 10:
            color = COLORS["yellow"]
            render_font = big_font
        elif self.count >= 5:
            color = COLORS["magenta"]
            render_font = font
        else:
            color = (color_intensity, color_intensity, color_intensity)
            render_font = font

        # Pulsing effect
        pulse = 1.0 + self.flash_intensity * 0.3
        text_surf = render_font.render(text, True, color)

        # Scale
        w = int(text_surf.get_width() * pulse)
        h = int(text_surf.get_height() * pulse)
        if w > 0 and h > 0:
            scaled = pygame.transform.scale(text_surf, (w, h))
            x = WIDTH // 2 - w // 2
            y = HEIGHT // 2 - 120
            surface.blit(scaled, (x, y))


class ScorePopup:
    """Animated '+1' that flies to the scoreboard."""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.target_y = 30
        self.color = color
        self.timer = 60
        self.max_timer = 60
        self.alive = True

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.alive = False
            return

        progress = 1 - (self.timer / self.max_timer)
        # Ease out
        ease = 1 - (1 - progress) ** 3
        self.y = self.start_y + (self.target_y - self.start_y) * ease
        self.x = self.start_x

    def draw(self, surface, font):
        if not self.alive:
            return
        alpha = int(255 * (self.timer / self.max_timer))
        text = font.render("+1", True, self.color)
        text.set_alpha(alpha)
        surface.blit(text, (int(self.x), int(self.y)))


class TransitionManager:
    """Fade-in / fade-out transitions between game states."""

    def __init__(self):
        self.alpha = 0
        self.target_alpha = 0
        self.speed = 10
        self.callback = None

    def fade_out(self, callback=None):
        """Fade to black, then call callback."""
        self.target_alpha = 255
        self.speed = 12
        self.callback = callback

    def fade_in(self):
        """Fade from black to transparent."""
        self.alpha = 255
        self.target_alpha = 0
        self.speed = 8

    def update(self):
        if self.alpha < self.target_alpha:
            self.alpha = min(255, self.alpha + self.speed)
            if self.alpha >= 255 and self.callback:
                self.callback()
                self.callback = None
                self.fade_in()
        elif self.alpha > self.target_alpha:
            self.alpha = max(0, self.alpha - self.speed)

    def draw(self, surface):
        if self.alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.alpha))
            surface.blit(overlay, (0, 0))

    @property
    def active(self):
        return self.alpha != self.target_alpha


class SpeedIndicator:
    """Visual bar showing current ball speed."""

    def __init__(self):
        self.current = 0
        self.max_speed = 12

    def update(self, speed):
        self.current = abs(speed)

    def draw(self, surface, font, x=WIDTH - 140, y=HEIGHT - 40):
        ratio = min(1.0, self.current / self.max_speed)

        # Background bar
        bar_w = 120
        bar_h = 8
        bg = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        bg.fill((30, 30, 40, 180))
        surface.blit(bg, (x, y))

        # Fill
        fill_w = int(bar_w * ratio)
        if fill_w > 0:
            # Color gradient: green → yellow → red
            if ratio < 0.5:
                r = int(255 * ratio * 2)
                g = 255
            else:
                r = 255
                g = int(255 * (1 - (ratio - 0.5) * 2))
            fill = pygame.Surface((fill_w, bar_h), pygame.SRCALPHA)
            fill.fill((r, g, 0, 200))
            surface.blit(fill, (x, y))

        # Border
        pygame.draw.rect(surface, COLORS["gray"], (x, y, bar_w, bar_h), 1)

        # Label
        label = font.render("SPEED", True, COLORS["white"])
        surface.blit(label, (x, y - 16))


class DifficultyDisplay:
    """Shows current difficulty level with ball count."""

    def __init__(self):
        self.level = 1
        self.flash_timer = 0

    def set_level(self, level):
        if level != self.level:
            self.level = level
            self.flash_timer = 60

    def update(self):
        if self.flash_timer > 0:
            self.flash_timer -= 1

    def draw(self, surface, font, big_font, x=WIDTH // 2, y=60):
        # Level text
        color = COLORS["yellow"] if self.flash_timer > 0 else COLORS["gray"]

        if self.flash_timer > 0:
            # Animated level-up display
            pulse = 1.0 + 0.3 * math.sin(self.flash_timer * 0.3)
            text = big_font.render(f"LEVEL {self.level}", True, COLORS["yellow"])
            w = int(text.get_width() * pulse)
            h = int(text.get_height() * pulse)
            if w > 0 and h > 0:
                scaled = pygame.transform.scale(text, (w, h))
                surface.blit(scaled, (x - w // 2, y - h // 2))

            balls_text = font.render(f"{self.level} BALL{'S' if self.level > 1 else ''}",
                                     True, COLORS["cyan"])
            surface.blit(balls_text, (x - balls_text.get_width() // 2, y + 30))
        else:
            text = font.render(f"LVL {self.level} • {self.level} BALL{'S' if self.level > 1 else ''}",
                               True, COLORS["white"])
            surface.blit(text, (x - text.get_width() // 2, y))


def draw_menu(surface, font, big_font, small_font, pulse_phase):
    """Draw the animated main menu."""
    # Title with pulsing glow
    pulse = 0.8 + 0.2 * math.sin(pulse_phase * 2)

    # Title glow layers
    title_text = "AUTOPILOT PONG"
    for layer in range(3, 0, -1):
        glow_font_size = int(80 + layer * 4)
        try:
            glow_font = pygame.font.Font(None, glow_font_size)
        except Exception:
            glow_font = big_font
        alpha = int(40 * pulse / layer)
        glow_surf = glow_font.render(title_text, True, COLORS["cyan"])
        glow_surf.set_alpha(alpha)
        surface.blit(glow_surf,
                     (WIDTH // 2 - glow_surf.get_width() // 2,
                      100 - layer * 2))

    # Main title
    title = big_font.render(title_text, True, COLORS["cyan"])
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

    # Subtitle
    sub = small_font.render("RETRO-FUTURIST ARCADE", True, COLORS["magenta"])
    surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 210))

    # Menu items with staggered animation
    items = [
        ("SPACE", "START GAME (VS AI)", COLORS["cyan"]),
        ("2", "ZEN MODE (AI vs AI)", COLORS["magenta"]),
        ("3", "SYMBIOSIS (AI ASSIST)", COLORS["yellow"]),
        ("", "", None),
        ("1-5", "DIFFICULTY LEVEL (BALLS)", COLORS["green"]),
        ("H", "TOGGLE HAND TRACKING", COLORS["orange"]),
        ("", "", None),
        ("W/S", "MOVE PADDLE", COLORS["white"]),
        ("Q", "QUIT GAME", COLORS["gray"]),
    ]

    y_start = 280
    for i, (key, desc, color) in enumerate(items):
        if not key:
            y_start += 15
            continue

        # Animate entry
        entry_offset = max(0, math.sin(pulse_phase * 1.5 - i * 0.2)) * 5

        y = y_start + i * 42 + int(entry_offset)

        if key:
            key_text = f"[{key}]"
            key_surf = font.render(key_text, True, color)
            desc_surf = small_font.render(desc, True, (180, 180, 190))

            # Left-align keys at a centered column
            key_x = WIDTH // 2 - 240
            desc_x = WIDTH // 2 - 80
            
            surface.blit(key_surf, (key_x, y))
            surface.blit(desc_surf, (desc_x, y + 6))

    # Version / credits
    ver = small_font.render("v2.0 • HACKATHON EDITION", True, COLORS["dark_gray"])
    surface.blit(ver, (WIDTH // 2 - ver.get_width() // 2, HEIGHT - 30))


def draw_game_over(surface, winner, player_score, ai_score, combo_best,
                   font, big_font, small_font):
    """Draw the game over screen with stats."""
    # Winner text
    if winner == "PLAYER":
        color = COLORS["cyan"]
        text = "VICTORY!"
    else:
        color = COLORS["magenta"]
        text = "DEFEATED"

    result = big_font.render(text, True, color)
    surface.blit(result, (WIDTH // 2 - result.get_width() // 2, HEIGHT // 2 - 80))

    # Score
    score = font.render(f"{player_score} - {ai_score}", True, COLORS["white"])
    surface.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 10))

    # Stats
    stats = [
        f"Best Combo: x{combo_best}",
    ]
    for i, stat in enumerate(stats):
        s = small_font.render(stat, True, COLORS["gray"])
        surface.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 40 + i * 25))

    # Replay prompt
    hint = font.render("SPACE to play again", True, COLORS["white"])
    surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 90))

    menu_hint = font.render("M: MENU  |  Q: QUIT", True, COLORS["cyan"])
    surface.blit(menu_hint, (WIDTH // 2 - menu_hint.get_width() // 2, HEIGHT // 2 + 130))


def draw_paused(surface, font, big_font):
    """Draw pause overlay."""
    # Dim background
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))

    pause = big_font.render("PAUSED", True, COLORS["yellow"])
    surface.blit(pause, (WIDTH // 2 - pause.get_width() // 2, HEIGHT // 2 - 40))

    hint = font.render("SPACE to continue", True, COLORS["white"])
    surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

    menu_hint = font.render("M: MENU  |  Q: QUIT", True, COLORS["cyan"])
    surface.blit(menu_hint, (WIDTH // 2 - menu_hint.get_width() // 2, HEIGHT // 2 + 60))
