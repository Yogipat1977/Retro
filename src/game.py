"""
AUTOPILOT PONG v2.0 — Hackathon Edition
Retro-futurist Pong with hand tracking, multi-ball difficulty,
power-ups, particle effects, and procedural audio.
"""

import pygame
import random
import math
import sys
from enum import Enum

from config import (
    WIDTH, HEIGHT, FPS, COLORS, FEATURES,
    PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, PADDLE_MARGIN, PADDLE_FRICTION,
    BALL_RADIUS, BALL_INITIAL_SPEED, BALL_SPEED_INCREMENT,
    BALL_MAX_SPEED, BALL_MOMENTUM_TRANSFER,
    MAX_DIFFICULTY_LEVEL, BALLS_PER_LEVEL, WIN_SCORE,
    AI_PROFILES
)
from particles import ParticleEmitter
from effects import (
    ScreenShake, draw_crt_overlay, draw_chromatic_aberration,
    draw_paddle_glow, draw_ball_glow, draw_speed_lines,
    draw_grid, draw_center_line, draw_background_pulse
)
from powerups import PowerUpManager
from ai_controller import AIController
from audio import AudioEngine
from ui import (
    ComboCounter, ScorePopup, TransitionManager,
    SpeedIndicator, DifficultyDisplay,
    draw_menu, draw_game_over, draw_paused
)

# Hand tracking is optional — import gracefully
try:
    from hand_tracker import HandTracker
    HAND_TRACKING_AVAILABLE = True
except ImportError:
    HAND_TRACKING_AVAILABLE = False


pygame.init()


# ── Game Mode Enum ───────────────────────────────────────

class GameMode(Enum):
    VS_AI = 1
    ZEN = 2
    SYMBIOSIS = 3


# ── Ball Object ──────────────────────────────────────────

class Ball:
    """A single ball with position, velocity, and state."""

    def __init__(self, x=None, y=None, vx=None, vy=None):
        self.x = x or WIDTH // 2
        self.y = y or HEIGHT // 2
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        self.vx = vx or (BALL_INITIAL_SPEED * random.choice([-1, 1]))
        self.vy = vy or (BALL_INITIAL_SPEED * math.sin(angle))
        self.active = True
        self.hit_count = 0
        self.ghost = False     # Ghost power-up
        self.fireball = False  # Fireball power-up

    def speed(self):
        return math.sqrt(self.vx ** 2 + self.vy ** 2)

    def to_dict(self):
        return {"x": self.x, "y": self.y, "vx": self.vx, "vy": self.vy,
                "active": self.active}


# ── Main Game ────────────────────────────────────────────

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("AUTOPILOT PONG — Hackathon Edition")
        self.clock = pygame.time.Clock()

        # Fonts
        self.small_font = pygame.font.Font(None, 28)
        self.font = pygame.font.Font(None, 48)
        self.big_font = pygame.font.Font(None, 96)
        self.hud_font = pygame.font.Font(None, 24)

        # Game state
        self.mode = GameMode.VS_AI
        self.state = "menu"        # menu, playing, paused, game_over
        self.difficulty_level = 1  # 1-5, controls number of balls
        self.menu_phase = 0        # Animation phase

        # Systems
        self.particles = ParticleEmitter()
        self.shake = ScreenShake()
        self.powerups = PowerUpManager()
        self.audio = AudioEngine()
        self.combo = ComboCounter()
        self.transition = TransitionManager()
        self.speed_indicator = SpeedIndicator()
        self.difficulty_display = DifficultyDisplay()
        self.score_popups = []

        # AI
        self.ai = AIController("TACTICIAN")
        self.ai_profile_index = 1
        self.ai_profile_names = list(AI_PROFILES.keys())

        # Hand tracking
        self.hand_tracker = None
        self.hand_tracking_active = False
        if HAND_TRACKING_AVAILABLE:
            self.hand_tracker = HandTracker()

        # Hit flash timer
        self.hit_flash = 0

        self.reset_game()

    def reset_game(self):
        """Reset all game state for a new match."""
        # Paddles
        self.player_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.ai_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.player_vel = 0
        self.player_paddle_h = PADDLE_HEIGHT
        self.ai_paddle_h = PADDLE_HEIGHT

        # Score
        self.player_score = 0
        self.ai_score = 0
        self.winner = None

        # Balls — create based on difficulty level
        self.balls = []
        self.spawn_balls(self.difficulty_level)

        # Reset systems
        self.particles.clear()
        self.powerups.reset()
        self.combo = ComboCounter()
        self.score_popups = []
        self.hit_flash = 0

        # Reset paddle sizes (power-up effects)
        self.freeze_timer = 0

    def spawn_balls(self, count):
        """Spawn the specified number of balls with staggered positions."""
        self.balls = []
        for i in range(count):
            # Stagger spawn positions and directions
            offset_y = (i - count // 2) * 60
            ball = Ball(
                x=WIDTH // 2,
                y=HEIGHT // 2 + offset_y,
            )
            # Alternate directions for multi-ball
            if i % 2 == 1:
                ball.vx = -ball.vx
            self.balls.append(ball)

    def handle_events(self):
        """Process all input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "paused"
                    elif self.state == "paused":
                        self.state = "playing"
                    else:
                        return False

                if event.key == pygame.K_SPACE:
                    if self.state == "menu":
                        self.audio.play("select")
                        self.state = "playing"
                        self.transition.fade_in()
                    elif self.state == "playing":
                        self.state = "paused"
                    elif self.state == "paused":
                        self.state = "playing"
                    elif self.state == "game_over":
                        self.reset_game()
                        self.state = "playing"
                        self.transition.fade_in()

                # Difficulty levels 1-5 (multi-ball)
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3,
                                 pygame.K_4, pygame.K_5):
                    new_level = event.key - pygame.K_0
                    if 1 <= new_level <= MAX_DIFFICULTY_LEVEL:
                        self.difficulty_level = new_level
                        self.difficulty_display.set_level(new_level)
                        if self.state == "menu":
                            # In menu, 2 and 3 also select modes
                            if new_level == 2:
                                self.mode = GameMode.ZEN
                            elif new_level == 3:
                                self.mode = GameMode.SYMBIOSIS
                            else:
                                self.mode = GameMode.VS_AI
                        elif self.state == "playing":
                            # Mid-game difficulty change: respawn balls
                            self.spawn_balls(BALLS_PER_LEVEL[new_level])
                            self.audio.play("levelup")

                # Mode selection (from menu)
                if self.state == "menu":
                    if event.key == pygame.K_z:
                        self.mode = GameMode.ZEN
                        self.audio.play("select")
                    elif event.key == pygame.K_x:
                        self.mode = GameMode.SYMBIOSIS
                        self.audio.play("select")

                # Toggle hand tracking
                if event.key == pygame.K_h:
                    self._toggle_hand_tracking()

                # Cycle AI profile with P key
                if event.key == pygame.K_p:
                    self.ai_profile_index = (
                        (self.ai_profile_index + 1) % len(self.ai_profile_names)
                    )
                    name = self.ai_profile_names[self.ai_profile_index]
                    self.ai.set_profile(name)
                    self.audio.play("select")

                # Return to menu with M key
                if event.key == pygame.K_m:
                    if self.state != "menu":
                        self.state = "menu"
                        self.audio.play("select")
                        self.reset_game()

                # Quit with Q key
                if event.key == pygame.K_q:
                    return False

        return True

    def _toggle_hand_tracking(self):
        """Toggle hand tracking on/off."""
        if not HAND_TRACKING_AVAILABLE or not self.hand_tracker:
            return

        if self.hand_tracking_active:
            self.hand_tracker.stop()
            self.hand_tracking_active = False
        else:
            if self.hand_tracker.is_available():
                success = self.hand_tracker.start()
                self.hand_tracking_active = success

    def update(self):
        """Main update loop."""
        if self.state != "playing":
            self.menu_phase += 0.02
            self.transition.update()
            return

        # ── Player Input ──
        if self.mode != GameMode.ZEN:
            if self.hand_tracking_active and self.hand_tracker:
                # Hand tracking control
                normalized_y = self.hand_tracker.get_paddle_y()
                target_y = normalized_y * (HEIGHT - self.player_paddle_h)
                self.player_vel = (target_y - self.player_y) * 0.3
            else:
                # Keyboard control
                keys = pygame.key.get_pressed()
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    self.player_vel = -PADDLE_SPEED
                elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    self.player_vel = PADDLE_SPEED
                else:
                    self.player_vel *= PADDLE_FRICTION
        else:
            # ZEN mode: AI controls left paddle too
            self.player_y = self._zen_left_ai()
            self.player_vel = 0

        self.player_y += self.player_vel
        self.player_y = max(0, min(HEIGHT - self.player_paddle_h, self.player_y))

        # ── Freeze check ──
        is_frozen = self.freeze_timer > 0
        if is_frozen:
            self.freeze_timer -= 1 / FPS

        # ── AI ──
        multi_ball_data = [b.to_dict() for b in self.balls if b.active]
        primary_ball = self.balls[0] if self.balls else None

        self.ai_y = self.ai.update(
            self.ai_y, self.ai_paddle_h,
            primary_ball.x if primary_ball else WIDTH // 2,
            primary_ball.y if primary_ball else HEIGHT // 2,
            primary_ball.vx if primary_ball else 0,
            primary_ball.vy if primary_ball else 0,
            WIDTH - PADDLE_MARGIN,
            self.player_score, self.ai_score,
            is_frozen=is_frozen,
            multi_balls=multi_ball_data
        )

        # ── Power-ups ──
        if FEATURES["powerups"]:
            self.powerups.update(1 / FPS)

            # Check collision with all balls
            for ball in self.balls:
                if not ball.active:
                    continue
                result = self.powerups.check_ball_collision(ball.x, ball.y)
                if result:
                    ptype, pos, color = result
                    self.audio.play("powerup")
                    self.particles.emit_powerup_pickup(pos[0], pos[1], color)
                    self._apply_powerup(ptype)

        # ── Paddle sizes (power-up effects) ──
        if self.powerups.has_effect("GROW"):
            self.player_paddle_h = PADDLE_HEIGHT * 2
        else:
            self.player_paddle_h = PADDLE_HEIGHT

        if self.powerups.has_effect("SHRINK"):
            self.ai_paddle_h = PADDLE_HEIGHT // 2
        else:
            self.ai_paddle_h = PADDLE_HEIGHT

        # ── Update all balls ──
        for ball in self.balls:
            if ball.active:
                self._update_ball(ball)

        # ── Ball effects from power-ups ──
        for ball in self.balls:
            ball.ghost = self.powerups.has_effect("GHOST")
            ball.fireball = self.powerups.has_effect("FIREBALL")

        # ── Clean up dead balls, check if we need respawn ──
        active_balls = [b for b in self.balls if b.active]
        if not active_balls and self.state == "playing":
            # All balls scored — respawn
            self.spawn_balls(BALLS_PER_LEVEL.get(self.difficulty_level, 1))

        # ── Systems update ──
        self.particles.update()
        self.shake.update()
        self.combo.update()
        self.transition.update()
        self.difficulty_display.update()

        # Speed indicator (fastest ball)
        if self.balls:
            max_speed = max((b.speed() for b in self.balls if b.active), default=0)
            self.speed_indicator.update(max_speed)

        # Score popups
        for popup in self.score_popups:
            popup.update()
        self.score_popups = [p for p in self.score_popups if p.alive]

        # Hit flash
        if self.hit_flash > 0:
            self.hit_flash -= 1

        self.menu_phase += 0.02

    def _zen_left_ai(self):
        """Simple AI for the left paddle in ZEN mode."""
        if not self.balls:
            return self.player_y

        # Track closest ball moving left
        target = HEIGHT // 2
        closest_dist = float('inf')
        for ball in self.balls:
            if ball.active and ball.vx < 0:
                dist = abs(PADDLE_MARGIN - ball.x)
                if dist < closest_dist:
                    closest_dist = dist
                    target = ball.y

        target_y = target - self.player_paddle_h // 2
        diff = target_y - self.player_y
        speed = 6
        if abs(diff) > 5:
            return self.player_y + (speed if diff > 0 else -speed)
        return self.player_y

    def _update_ball(self, ball):
        """Update a single ball: movement, collisions, scoring."""
        # Trail particles
        if FEATURES["particles"]:
            if ball.fireball:
                self.particles.emit_fire_trail(ball.x, ball.y)
            else:
                trail_color = COLORS["cyan"] if not ball.ghost else (100, 100, 120)
                self.particles.emit_trail(ball.x, ball.y, trail_color)

        # Move
        speed_mult = 2.0 if self.powerups.has_effect("FIREBALL") else 1.0
        ball.x += ball.vx * speed_mult
        ball.y += ball.vy * speed_mult

        # Wall bounce
        if ball.y <= BALL_RADIUS or ball.y >= HEIGHT - BALL_RADIUS:
            ball.vy *= -1
            ball.y = max(BALL_RADIUS, min(HEIGHT - BALL_RADIUS, ball.y))
            self.audio.play("wall")

        # ── Robust Collision Detection ──
        # Create thicker collision rects behind the paddles to catch fast balls
        player_collision_rect = pygame.Rect(
            0, self.player_y,
            PADDLE_MARGIN + PADDLE_WIDTH, self.player_paddle_h
        )
        ai_collision_rect = pygame.Rect(
            WIDTH - PADDLE_MARGIN - PADDLE_WIDTH, self.ai_y,
            PADDLE_MARGIN + PADDLE_WIDTH, self.ai_paddle_h
        )

        # Ball bounding box
        ball_rect = pygame.Rect(
            ball.x - BALL_RADIUS, ball.y - BALL_RADIUS,
            BALL_RADIUS * 2, BALL_RADIUS * 2
        )

        # Player paddle hit
        if player_collision_rect.colliderect(ball_rect) and ball.vx < 0:
            ball.vx = abs(ball.vx) + BALL_SPEED_INCREMENT
            ball.vx = min(BALL_MAX_SPEED, ball.vx)
            ball.vy += self.player_vel * BALL_MOMENTUM_TRANSFER
            ball.vy = max(-8, min(8, ball.vy))
            ball.x = PADDLE_MARGIN + PADDLE_WIDTH + BALL_RADIUS
            ball.hit_count += 1

            self.audio.play_pitch("paddle", ball.speed() / BALL_MAX_SPEED)
            self.combo.hit()
            self.hit_flash = 8

            if FEATURES["particles"]:
                self.particles.emit_sparks(
                    PADDLE_MARGIN + PADDLE_WIDTH, ball.y, 1, COLORS["cyan"]
                )

            # Combo milestone sound
            if self.combo.count % 5 == 0 and self.combo.count > 0:
                self.audio.play("combo")

        # AI paddle hit
        elif ai_collision_rect.colliderect(ball_rect) and ball.vx > 0:
            ball.vx = -(abs(ball.vx) + BALL_SPEED_INCREMENT)
            ball.vx = max(-BALL_MAX_SPEED, ball.vx)
            ball.vy += random.uniform(-1.5, 1.5)
            ball.x = WIDTH - PADDLE_MARGIN - PADDLE_WIDTH - BALL_RADIUS
            ball.hit_count += 1

            self.audio.play_pitch("paddle", ball.speed() / BALL_MAX_SPEED)
            self.hit_flash = 8

            if FEATURES["particles"]:
                self.particles.emit_sparks(
                    WIDTH - PADDLE_MARGIN - PADDLE_WIDTH, ball.y, -1, COLORS["magenta"]
                )

        # ── Scoring ──
        if ball.x < -BALL_RADIUS:
            # AI scores
            self.ai_score += 1
            self.audio.play("goal")
            self.shake.trigger(20, 8)
            self.combo.miss()

            if FEATURES["particles"]:
                self.particles.emit_burst(0, ball.y, COLORS["magenta"])

            self.score_popups.append(
                ScorePopup(WIDTH * 3 // 4, HEIGHT // 2, COLORS["magenta"])
            )

            ball.active = False
            self._check_win()

        elif ball.x > WIDTH + BALL_RADIUS:
            # Player scores
            self.player_score += 1
            self.audio.play("goal")
            self.shake.trigger(20, 8)

            if FEATURES["particles"]:
                self.particles.emit_burst(WIDTH, ball.y, COLORS["cyan"])

            self.score_popups.append(
                ScorePopup(WIDTH // 4, HEIGHT // 2, COLORS["cyan"])
            )

            ball.active = False
            self._check_win()

    def _apply_powerup(self, ptype):
        """Apply the effect of a collected power-up."""
        if ptype == "FREEZE":
            self.freeze_timer = 2.0
            if FEATURES["particles"]:
                self.particles.emit_freeze(
                    WIDTH - PADDLE_MARGIN, self.ai_y + self.ai_paddle_h // 2
                )
            self.audio.play("freeze")

        elif ptype == "MULTIBALL":
            # Split each active ball into 3
            new_balls = []
            for ball in self.balls:
                if ball.active:
                    for angle_offset in [-0.4, 0, 0.4]:
                        new_ball = Ball(ball.x, ball.y)
                        speed = ball.speed()
                        base_angle = math.atan2(ball.vy, ball.vx) + angle_offset
                        new_ball.vx = speed * math.cos(base_angle)
                        new_ball.vy = speed * math.sin(base_angle)
                        new_balls.append(new_ball)
            self.balls = new_balls
            self.audio.play("split")

        # FIREBALL, GHOST, GROW, SHRINK are handled via has_effect checks

    def _check_win(self):
        """Check if someone reached the win score."""
        if self.player_score >= WIN_SCORE or self.ai_score >= WIN_SCORE:
            self.winner = "PLAYER" if self.player_score >= WIN_SCORE else "AI"
            self.state = "game_over"
            self.audio.play("win")

    # ── Drawing ──────────────────────────────────────────

    def draw(self):
        """Main draw loop."""
        surface = pygame.Surface((WIDTH, HEIGHT))
        surface.fill(COLORS["bg"])

        # Background
        draw_grid(surface)
        draw_center_line(surface)

        if self.hit_flash > 0:
            draw_background_pulse(surface, self.hit_flash)

        # ── Game elements ──
        if self.state in ("playing", "paused", "game_over"):
            # Power-ups
            if FEATURES["powerups"]:
                self.powerups.draw(surface)

            # Particles (behind paddles)
            if FEATURES["particles"]:
                self.particles.draw(surface)

            # Paddles with glow
            draw_paddle_glow(surface,
                             PADDLE_MARGIN, self.player_y,
                             PADDLE_WIDTH, self.player_paddle_h,
                             COLORS["cyan"], self.menu_phase * 3)
            pygame.draw.rect(surface, COLORS["cyan"],
                             (PADDLE_MARGIN, self.player_y,
                              PADDLE_WIDTH, self.player_paddle_h),
                             border_radius=4)

            # AI paddle — blue tint if frozen
            ai_color = COLORS["ice_blue"] if self.freeze_timer > 0 else COLORS["magenta"]
            draw_paddle_glow(surface,
                             WIDTH - PADDLE_MARGIN - PADDLE_WIDTH, self.ai_y,
                             PADDLE_WIDTH, self.ai_paddle_h,
                             ai_color, self.menu_phase * 3)
            pygame.draw.rect(surface, ai_color,
                             (WIDTH - PADDLE_MARGIN - PADDLE_WIDTH, self.ai_y,
                              PADDLE_WIDTH, self.ai_paddle_h),
                             border_radius=4)

            # Balls
            for ball in self.balls:
                if not ball.active:
                    continue

                # Ghost effect: semi-transparent
                if ball.ghost:
                    alpha = 40 + int(30 * math.sin(self.menu_phase * 10))
                    ghost_surf = pygame.Surface((BALL_RADIUS * 4, BALL_RADIUS * 4),
                                                pygame.SRCALPHA)
                    pygame.draw.circle(ghost_surf,
                                       (255, 255, 255, alpha),
                                       (BALL_RADIUS * 2, BALL_RADIUS * 2),
                                       BALL_RADIUS)
                    surface.blit(ghost_surf,
                                 (int(ball.x) - BALL_RADIUS * 2,
                                  int(ball.y) - BALL_RADIUS * 2))
                else:
                    # Glow
                    ball_color = COLORS["orange"] if ball.fireball else (255, 255, 255)
                    draw_ball_glow(surface, ball.x, ball.y, BALL_RADIUS, ball_color)
                    pygame.draw.circle(surface, ball_color,
                                       (int(ball.x), int(ball.y)), BALL_RADIUS)

                # Speed lines
                if FEATURES["speed_lines"]:
                    draw_speed_lines(surface, ball.speed(), BALL_MAX_SPEED,
                                     ball.x, ball.y, ball.vx)

            # Symbiosis prediction line
            if self.mode == GameMode.SYMBIOSIS and self.state == "playing":
                self._draw_prediction_line(surface)

            # ── HUD ──
            # Scores
            p_score = self.big_font.render(str(self.player_score), True, COLORS["cyan"])
            a_score = self.big_font.render(str(self.ai_score), True, COLORS["magenta"])
            surface.blit(p_score, (WIDTH // 4 - p_score.get_width() // 2, 20))
            surface.blit(a_score, (WIDTH * 3 // 4 - a_score.get_width() // 2, 20))

            # Mode & AI info
            mode_info = f"{self.mode.name} | AI: {self.ai.profile_name}"
            mode_text = self.hud_font.render(mode_info, True, COLORS["gray"])
            surface.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2,
                                     HEIGHT - 18))

            # Difficulty display
            self.difficulty_display.draw(surface, self.small_font, self.font)

            # Speed indicator
            self.speed_indicator.draw(surface, self.hud_font)

            # Combo counter
            if FEATURES["combo_counter"]:
                self.combo.draw(surface, self.font, self.big_font)

            # Power-up HUD
            if FEATURES["powerups"]:
                self.powerups.draw_hud(surface, self.hud_font,
                                       x=10, y=HEIGHT - 80)

            # Score popups
            for popup in self.score_popups:
                popup.draw(surface, self.font)

            # Hand tracking indicator
            if self.hand_tracking_active:
                ht_text = self.hud_font.render("🖐 HAND TRACKING", True, COLORS["green"])
                surface.blit(ht_text, (10, 10))

                # PiP webcam overlay
                if self.hand_tracker:
                    frame = self.hand_tracker.get_frame()
                    if frame:
                        surface.blit(frame, (10, 30))

            # ZEN mode hint
            if self.mode == GameMode.ZEN and self.state == "playing":
                zen_text = self.hud_font.render("ZEN MODE — Watch the AI battle",
                                                True, COLORS["gray"])
                surface.blit(zen_text, (WIDTH // 2 - zen_text.get_width() // 2, 90))

        # ── State overlays ──
        if self.state == "menu":
            draw_menu(surface, self.font, self.big_font, self.small_font,
                      self.menu_phase)

        elif self.state == "paused":
            draw_paused(surface, self.font, self.big_font)

        elif self.state == "game_over":
            draw_game_over(surface, self.winner,
                           self.player_score, self.ai_score,
                           self.combo.best,
                           self.font, self.big_font, self.small_font)
            # Celebration particles
            if FEATURES["particles"]:
                self.particles.emit_confetti(WIDTH, HEIGHT)
                self.particles.update()

        # ── Post-processing ──
        if FEATURES["crt_effect"]:
            draw_crt_overlay(surface)
            aberration_intensity = 1.0 + (2.0 if self.shake.active else 0)
            draw_chromatic_aberration(surface, aberration_intensity)

        # Transitions
        self.transition.draw(surface)

        # Apply screen shake
        self.screen.fill((0, 0, 0))
        self.screen.blit(surface, self.shake.offset)

        pygame.display.flip()

    def _draw_prediction_line(self, surface):
        """Draw ball trajectory prediction in SYMBIOSIS mode."""
        for ball in self.balls:
            if not ball.active or ball.vx <= 0:
                continue

            pred_x, pred_y = ball.x, ball.y
            pred_vx, pred_vy = ball.vx, ball.vy

            points = [(int(pred_x), int(pred_y))]
            for _ in range(40):
                pred_x += pred_vx
                pred_y += pred_vy
                if pred_y <= BALL_RADIUS or pred_y >= HEIGHT - BALL_RADIUS:
                    pred_vy *= -1
                points.append((int(pred_x), int(pred_y)))
                if pred_x > WIDTH:
                    break

            if len(points) > 1:
                pred_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.lines(pred_surf, (*COLORS["yellow"][:3], 60),
                                  False, points, 2)
                surface.blit(pred_surf, (0, 0))

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        # Cleanup
        if self.hand_tracking_active and self.hand_tracker:
            self.hand_tracker.stop()
        pygame.quit()
        sys.exit()


# ── Entry Point ──────────────────────────────────────────

if __name__ == "__main__":
    game = Game()
    game.run()
