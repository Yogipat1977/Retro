import pygame
import random
import math
import sys
from enum import Enum

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

COLORS = {
    "bg": (10, 10, 15),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "yellow": (255, 255, 0),
    "white": (255, 255, 255),
    "gray": (40, 40, 50),
    "grid": (20, 20, 30),
}


class GameMode(Enum):
    VS_AI = 1
    ZEN = 2
    SYMBIOSIS = 3


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("AUTOPILOT PONG")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 40)
        self.big_font = pygame.font.Font(None, 80)
        self.small_font = pygame.font.Font(None, 24)

        self.mode = GameMode.VS_AI
        self.ai_difficulty = 2
        self.diff_names = {1: "EASY", 2: "MEDIUM", 3: "HARD"}

        self.state = "menu"
        self.shake_timer = 0
        self.shake_offset = [0, 0]

        self.trail = []
        self.max_trail = 8

        self.reset_game()
        self.sounds = {}
        self.load_sounds()

    def load_sounds(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

            def make_sound(freq, duration=0.1):
                sample_rate = 22050
                n = int(sample_rate * duration)
                buf = bytearray(n * 2)
                for i in range(n):
                    t = i / sample_rate
                    val = int(
                        32767 * math.sin(2 * math.pi * freq * t) * math.exp(-t * 20)
                    )
                    buf[i * 2] = val & 255
                    buf[i * 2 + 1] = (val >> 8) & 255
                return pygame.mixer.Sound(buffer=bytearray(buf))

            self.sounds = {
                "paddle": make_sound(440, 0.08),
                "wall": make_sound(220, 0.05),
                "goal": make_sound(150, 0.3),
                "win": make_sound(880, 0.2),
            }
        except Exception:
            self.sounds = {}

    def play_sound(self, name):
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except:
                pass

    def reset_game(self):
        self.player_y = HEIGHT // 2 - 50
        self.ai_y = HEIGHT // 2 - 50
        self.player_score = 0
        self.ai_score = 0

        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        self.ball_vx = 5 * random.choice([-1, 1])
        self.ball_vy = 5 * math.sin(angle)

        self.paddle_h = 100
        self.paddle_w = 12
        self.paddle_speed = 8
        self.player_vel = 0

        self.hit_count = 0
        self.trail = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE:
                    if self.state == "menu":
                        self.state = "playing"
                    elif self.state == "playing":
                        self.state = "paused"
                    elif self.state == "paused":
                        self.state = "playing"
                    elif self.state == "game_over":
                        self.reset_game()
                        self.state = "playing"
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    self.ai_difficulty = int(event.key) - 0
                    if event.key == pygame.K_1:
                        self.ai_difficulty = 1
                    elif event.key == pygame.K_2:
                        self.ai_difficulty = 2
                    elif event.key == pygame.K_3:
                        self.ai_difficulty = 3
                if event.key == pygame.K_2 and self.state == "menu":
                    self.mode = GameMode.ZEN
                    self.state = "playing"
                if event.key == pygame.K_3 and self.state == "menu":
                    self.mode = GameMode.SYMBIOSIS
                    self.state = "playing"
        return True

    def update(self):
        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()

        if self.mode != GameMode.ZEN:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.player_vel = -self.paddle_speed
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.player_vel = self.paddle_speed
            else:
                self.player_vel *= 0.8
        else:
            self.player_vel = 0

        self.player_y += self.player_vel
        self.player_y = max(0, min(HEIGHT - self.paddle_h, self.player_y))

        self.update_ai()
        self.update_ball()
        self.update_trail()
        self.update_shake()

    def update_ai(self):
        difficulty_map = {
            1: (0.4, 0.6, 4),
            2: (0.6, 0.85, 6),
            3: (0.85, 1.0, 8),
        }
        reaction, accuracy, speed = difficulty_map[self.ai_difficulty]

        if self.mode == GameMode.ZEN:
            reaction = min(1.0, reaction + 0.1)
            accuracy = min(1.0, accuracy + 0.05)

        target_y = self.ball_y - self.paddle_h // 2
        diff = target_y - self.ai_y

        if random.random() < reaction:
            if abs(diff) > 10:
                move = speed if diff > 0 else -speed
                if random.random() < accuracy:
                    self.ai_y += move
                else:
                    self.ai_y += move * random.uniform(0.3, 0.7)

        if self.mode == GameMode.SYMBIOSIS:
            player_center = self.player_y + self.paddle_h // 2
            dist = abs(self.ball_x - (WIDTH - 100))
            if dist < 200 and self.ball_vx > 0:
                target = (self.ball_y + player_center) / 2
                self.ai_y += (target - self.ai_y) * 0.1

        self.ai_y = max(0, min(HEIGHT - self.paddle_h, self.ai_y))

    def update_ball(self):
        self.trail.append((self.ball_x, self.ball_y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        if self.ball_y <= 10 or self.ball_y >= HEIGHT - 10:
            self.ball_vy *= -1
            self.play_sound("wall")

        player_paddle = pygame.Rect(30, self.player_y, self.paddle_w, self.paddle_h)
        ai_paddle = pygame.Rect(
            WIDTH - 30 - self.paddle_w, self.ai_y, self.paddle_w, self.paddle_h
        )

        if player_paddle.collidepoint(self.ball_x, self.ball_y):
            self.ball_vx = abs(self.ball_vx) + 0.2
            self.ball_vy += self.player_vel * 0.15
            self.ball_vy = max(-8, min(8, self.ball_vy))
            self.ball_x = player_paddle.right + 1
            self.hit_count += 1
            self.play_sound("paddle")
            self.update_pitch()

        if ai_paddle.collidepoint(self.ball_x, self.ball_y):
            self.ball_vx = -abs(self.ball_vx) - 0.2
            self.ball_vx = max(-12, self.ball_vx)
            self.ball_y += random.uniform(-2, 2)
            self.hit_count += 1
            self.play_sound("paddle")
            self.update_pitch()

        if self.ball_x < 0:
            self.ai_score += 1
            self.play_sound("goal")
            self.shake_timer = 15
            self.check_win()
            if self.state == "playing":
                self.reset_ball()

        if self.ball_x > WIDTH:
            self.player_score += 1
            self.play_sound("goal")
            self.shake_timer = 15
            self.check_win()
            if self.state == "playing":
                self.reset_ball()

    def update_pitch(self):
        if "paddle" not in self.sounds:
            return
        try:
            speed_factor = min(1.0, (abs(self.ball_vx) - 5) / 7)
            pitch = 1.0 + speed_factor * 0.5
            self.sounds["paddle"].set_volume(pitch)
        except:
            pass

    def reset_ball(self):
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        self.ball_vx = 5 * random.choice([-1, 1])
        self.ball_vy = 5 * math.sin(angle)
        self.trail = []

    def check_win(self):
        if self.player_score >= 11 or self.ai_score >= 11:
            self.state = "game_over"
            self.winner = "PLAYER" if self.player_score >= 11 else "AI"
            self.play_sound("win")

    def update_trail(self):
        pass

    def update_shake(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1
            self.shake_offset = [random.randint(-5, 5), random.randint(-5, 5)]
        else:
            self.shake_offset = [0, 0]

    def draw_crt(self, surface):
        offset = 2
        chroma_r = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        chroma_b = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        edge_rect_r = pygame.Rect(WIDTH - offset, 0, offset, HEIGHT)
        edge_rect_b = pygame.Rect(0, 0, offset, HEIGHT)

        chroma_r.fill((255, 0, 0, 8), edge_rect_r)
        chroma_b.fill((0, 0, 255, 8), edge_rect_b)
        surface.blit(chroma_r, (0, 0))
        surface.blit(chroma_b, (0, 0))

        for y in range(0, HEIGHT, 3):
            pygame.draw.line(surface, (0, 0, 0, 50), (0, y), (WIDTH, y))

        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(50):
            alpha = i * 3
            pygame.draw.rect(vignette, (0, 0, 0, alpha), (0, 0, WIDTH, HEIGHT), 1)
        surface.blit(vignette, (0, 0))

    def draw(self):
        surface = pygame.Surface((WIDTH, HEIGHT))
        surface.fill(COLORS["bg"])

        for y in range(0, HEIGHT, 40):
            pygame.draw.line(surface, COLORS["grid"], (0, y), (WIDTH, y), 1)
        for x in range(0, WIDTH, 40):
            pygame.draw.line(surface, COLORS["grid"], (x, 0), (x, HEIGHT), 1)

        pygame.draw.line(
            surface, COLORS["gray"], (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 3
        )
        for i in range(0, HEIGHT, 20):
            pygame.draw.line(
                surface, COLORS["gray"], (WIDTH // 2 - 5, i), (WIDTH // 2 + 5, i), 2
            )

        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i + 1) / len(self.trail) * 0.5)
            size = 8 + i
            glow = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*COLORS["cyan"][:3], alpha), (size, size), size)
            surface.blit(glow, (pos[0] - size, pos[1] - size))

        pygame.draw.rect(
            surface,
            COLORS["cyan"],
            (30, self.player_y, self.paddle_w, self.paddle_h),
            border_radius=4,
        )
        pygame.draw.rect(
            surface,
            COLORS["magenta"],
            (WIDTH - 30 - self.paddle_w, self.ai_y, self.paddle_w, self.paddle_h),
            border_radius=4,
        )

        glow_ball = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(glow_ball, (*COLORS["white"][:3], 100), (15, 15), 15)
        surface.blit(glow_ball, (self.ball_x - 15, self.ball_y - 15))
        pygame.draw.circle(
            surface, COLORS["white"], (int(self.ball_x), int(self.ball_y)), 8
        )

        if self.mode == GameMode.SYMBIOSIS and self.state == "playing":
            pred_x = self.ball_x
            pred_y = self.ball_y
            pred_vx = self.ball_vx
            pred_vy = self.ball_vy
            for _ in range(30):
                pred_x += pred_vx
                pred_y += pred_vy
                if pred_y <= 10 or pred_y >= HEIGHT - 10:
                    pred_vy *= -1
            if pred_vx > 0:
                pygame.draw.line(
                    surface,
                    (*COLORS["yellow"][:3], 100),
                    (int(self.ball_x), int(self.ball_y)),
                    (int(pred_x), int(pred_y)),
                    2,
                )

        score_text = self.font.render(f"{self.player_score}", True, COLORS["cyan"])
        ai_text = self.font.render(f"{self.ai_score}", True, COLORS["magenta"])
        surface.blit(score_text, (WIDTH // 4, 30))
        surface.blit(ai_text, (WIDTH * 3 // 4 - ai_text.get_width(), 30))

        mode_text = self.small_font.render(
            f"{self.mode.name} | AI: {self.diff_names[self.ai_difficulty]}",
            True,
            COLORS["gray"],
        )
        surface.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2, HEIGHT - 30))

        if self.state == "menu":
            title = self.big_font.render("AUTOPILOT PONG", True, COLORS["cyan"])
            surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

            instructions = [
                "1: VS AI",
                "2: ZEN (AI vs AI)",
                "3: SYMBIOSIS (AI Assist)",
                "",
                "SPACE: Start",
                "W/S or UP/DOWN: Move",
                "1/2/3: AI Difficulty",
                "ESC: Quit",
            ]
            for i, line in enumerate(instructions):
                text = self.font.render(line, True, COLORS["white"])
                surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 220 + i * 35))

        elif self.state == "paused":
            pause = self.big_font.render("PAUSED", True, COLORS["yellow"])
            surface.blit(pause, (WIDTH // 2 - pause.get_width() // 2, HEIGHT // 2 - 40))
            hint = self.font.render("SPACE to continue", True, COLORS["white"])
            surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

        elif self.state == "game_over":
            result = self.big_font.render(
                f"{self.winner} WINS!",
                True,
                COLORS["yellow"] if self.winner == "PLAYER" else COLORS["magenta"],
            )
            surface.blit(
                result, (WIDTH // 2 - result.get_width() // 2, HEIGHT // 2 - 40)
            )
            hint = self.font.render("SPACE to play again", True, COLORS["white"])
            surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 30))

        elif self.state == "playing" and self.mode == GameMode.ZEN:
            zen_hint = self.small_font.render(
                "ZEN MODE: Watch the AI battle", True, COLORS["gray"]
            )
            surface.blit(zen_hint, (WIDTH // 2 - zen_hint.get_width() // 2, 60))

        self.draw_crt(surface)

        final = pygame.transform.scale(surface, (WIDTH, HEIGHT))
        final.blit(pygame.Surface((0, 0)), self.shake_offset)

        self.screen.blit(final, self.shake_offset)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    Game().run()
