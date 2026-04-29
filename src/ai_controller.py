"""
AUTOPILOT PONG — AI Controller
AI profiles with distinct personalities and adaptive difficulty.
"""

import random
import math
from config import AI_PROFILES, AI_ADAPTIVE_THRESHOLD, HEIGHT


class AIController:
    """Enhanced AI with personality profiles and adaptive difficulty."""

    def __init__(self, profile_name="TACTICIAN"):
        self.set_profile(profile_name)
        self.target_y = HEIGHT // 2
        self.predicted_y = None

    def set_profile(self, name):
        """Switch AI personality profile."""
        self.profile_name = name
        profile = AI_PROFILES[name]
        self.base_reaction = profile["reaction"]
        self.base_accuracy = profile["accuracy"]
        self.base_speed = profile["speed"]
        self.reaction = self.base_reaction
        self.accuracy = self.base_accuracy
        self.speed = self.base_speed

    def adapt_difficulty(self, player_score, ai_score):
        """Dynamically adjust difficulty based on score gap."""
        gap = player_score - ai_score

        if gap > AI_ADAPTIVE_THRESHOLD:
            # Player is winning hard — AI gets better
            boost = min(0.15, (gap - AI_ADAPTIVE_THRESHOLD) * 0.05)
            self.reaction = min(1.0, self.base_reaction + boost)
            self.accuracy = min(1.0, self.base_accuracy + boost)
            self.speed = min(10, self.base_speed + gap * 0.3)
        elif gap < -AI_ADAPTIVE_THRESHOLD:
            # AI is winning hard — AI gets worse
            nerf = min(0.2, (abs(gap) - AI_ADAPTIVE_THRESHOLD) * 0.05)
            self.reaction = max(0.2, self.base_reaction - nerf)
            self.accuracy = max(0.3, self.base_accuracy - nerf)
            self.speed = max(2, self.base_speed - abs(gap) * 0.3)
        else:
            # Close game — use base stats
            self.reaction = self.base_reaction
            self.accuracy = self.base_accuracy
            self.speed = self.base_speed

    def predict_ball_y(self, ball_x, ball_y, ball_vx, ball_vy, target_x):
        """Predict where the ball will be when it reaches target_x using ray-casting."""
        if ball_vx == 0:
            return ball_y

        # Only predict when ball is moving towards AI
        if (target_x > ball_x and ball_vx < 0) or (target_x < ball_x and ball_vx > 0):
            return ball_y

        pred_x = ball_x
        pred_y = ball_y
        pred_vy = ball_vy

        # Simulate ball path
        steps = int(abs(target_x - ball_x) / max(1, abs(ball_vx)))
        for _ in range(min(steps, 200)):
            pred_x += ball_vx
            pred_y += pred_vy

            # Wall bounces
            if pred_y <= 10:
                pred_y = 10
                pred_vy = abs(pred_vy)
            elif pred_y >= HEIGHT - 10:
                pred_y = HEIGHT - 10
                pred_vy = -abs(pred_vy)

            if (ball_vx > 0 and pred_x >= target_x) or \
               (ball_vx < 0 and pred_x <= target_x):
                break

        self.predicted_y = pred_y
        return pred_y

    def update(self, ai_y, paddle_h, ball_x, ball_y, ball_vx, ball_vy,
               target_x, player_score=0, ai_score=0, is_frozen=False,
               multi_balls=None):
        """
        Calculate AI paddle movement.
        Returns the new ai_y position.
        """
        if is_frozen:
            return ai_y

        # Adaptive difficulty
        self.adapt_difficulty(player_score, ai_score)

        # Choose which ball to track (closest threatening ball)
        track_y = ball_y
        if multi_balls:
            closest_ball = None
            closest_dist = float('inf')
            for b in multi_balls:
                if b.get("active", True):
                    # Track the ball that's closest to AI side and moving towards it
                    dist = abs(target_x - b["x"])
                    is_approaching = (b["vx"] > 0 and target_x > b["x"]) or \
                                     (b["vx"] < 0 and target_x < b["x"])
                    if is_approaching and dist < closest_dist:
                        closest_dist = dist
                        closest_ball = b
            if closest_ball:
                ball_x = closest_ball["x"]
                ball_y = closest_ball["y"]
                ball_vx = closest_ball["vx"]
                ball_vy = closest_ball["vy"]
                track_y = ball_y

        # Use prediction for TACTICIAN and ZEN_MASTER
        if self.profile_name in ("TACTICIAN", "ZEN_MASTER"):
            predicted = self.predict_ball_y(ball_x, ball_y, ball_vx, ball_vy, target_x)
            track_y = predicted
        else:
            track_y = ball_y

        # Add ROOKIE randomness
        if self.profile_name == "ROOKIE":
            track_y += random.uniform(-30, 30)
            # Occasionally move wrong direction
            if random.random() < 0.05:
                track_y = HEIGHT - track_y

        target_y = track_y - paddle_h // 2
        diff = target_y - ai_y

        # Reaction check
        if random.random() < self.reaction:
            if abs(diff) > 5:
                # BERSERKER always moves at max speed
                if self.profile_name == "BERSERKER":
                    move = self.speed if diff > 0 else -self.speed
                else:
                    move = min(self.speed, abs(diff)) * (1 if diff > 0 else -1)

                # Accuracy check
                if random.random() < self.accuracy:
                    ai_y += move
                else:
                    ai_y += move * random.uniform(0.2, 0.6)

        # ZEN_MASTER: minimal movement, maximum efficiency
        if self.profile_name == "ZEN_MASTER" and abs(diff) < 3:
            pass  # Don't jitter

        # Clamp to screen
        ai_y = max(0, min(HEIGHT - paddle_h, ai_y))
        return ai_y
