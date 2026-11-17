import math
import random
import pygame
from game.button import ChoiceButton


class GameEngine:
    WIN_SCORE = 3  # Task 2: Target score to win the match

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.choices = ["ROCK", "PAPER", "SCISSORS"]
        btn_w, btn_h = 130, 50
        gap = 20
        total_w = 3 * btn_w + 2 * gap
        start_x = (width - total_w) // 2
        btn_y = height - 75

        self.buttons = [
            ChoiceButton("ROCK", pygame.Rect(start_x, btn_y, btn_w, btn_h), (160, 50, 50), (200, 70, 70)),
            ChoiceButton("PAPER", pygame.Rect(start_x + btn_w + gap, btn_y, btn_w, btn_h), (40, 100, 170), (60, 130, 210)),
            ChoiceButton("SCISSORS", pygame.Rect(start_x + 2 * (btn_w + gap), btn_y, btn_w, btn_h), (180, 140, 30), (220, 180, 50)),
        ]

        self.player_choice = None
        self.cpu_choice = None
        self.result_text = "Make your move! (First to 3 Wins)"
        self.result_color = (220, 225, 235)

        self.player_score = 0
        self.cpu_score = 0
        self.game_over = False
        self.winner = None

        # Task 3: Adaptive AI pattern tracking
        self.player_history = {"ROCK": 0, "PAPER": 0, "SCISSORS": 0}

        # Task 4: Animation & Timing state
        self.state = "IDLE"  # "IDLE", "ANIMATING", "SHOW_RESULT"
        self.anim_start_time = 0
        self.anim_duration = 1000  # 1 second shake countdown
        self.round_resolved_time = 0
        self.display_duration = 1800
        self.pending_player_choice = None

        self.font_title = pygame.font.SysFont(None, 34)
        self.font_hud = pygame.font.SysFont(None, 24)
        self.font_arena = pygame.font.SysFont(None, 26)
        self.font_banner = pygame.font.SysFont(None, 38)

    def determine_winner(self, player, cpu):
        """Task 1: Standard RPS outcome rules."""
        if player == cpu:
            return "TIE"
        rules = {
            ("ROCK", "SCISSORS"): "PLAYER",
            ("SCISSORS", "PAPER"): "PLAYER",
            ("PAPER", "ROCK"): "PLAYER",
            ("SCISSORS", "ROCK"): "CPU",
            ("PAPER", "SCISSORS"): "CPU",
            ("ROCK", "PAPER"): "CPU",
        }
        return rules.get((player, cpu), "TIE")

    def get_cpu_choice(self):
        """Task 3: Adaptive AI predicting and countering frequent throws."""
        total_throws = sum(self.player_history.values())
        counters = {"ROCK": "PAPER", "PAPER": "SCISSORS", "SCISSORS": "ROCK"}

        # Random play early on or 35% exploration rate to avoid predictability
        if total_throws < 2 or random.random() < 0.35:
            return random.choice(self.choices)

        # Find the player's most frequent move
        predicted_player_move = max(self.player_history, key=self.player_history.get)
        return counters[predicted_player_move]

    def start_round(self, choice):
        if self.game_over or self.state != "IDLE":
            return
        self.pending_player_choice = choice
        self.state = "ANIMATING"
        self.anim_start_time = pygame.time.get_ticks()
        self.result_text = "Rock... Paper... Scissors..."
        self.result_color = (200, 200, 210)

    def resolve_round(self):
        self.player_choice = self.pending_player_choice
        self.cpu_choice = self.get_cpu_choice()

        # Update pattern tracker
        self.player_history[self.player_choice] += 1

        outcome = self.determine_winner(self.player_choice, self.cpu_choice)
        if outcome == "PLAYER":
            self.player_score += 1
            self.result_text = f"You Win! {self.player_choice} beats {self.cpu_choice}."
            self.result_color = (80, 230, 120)
        elif outcome == "CPU":
            self.cpu_score += 1
            self.result_text = f"CPU Wins! {self.cpu_choice} beats {self.player_choice}."
            self.result_color = (240, 80, 80)
        else:
            self.result_text = f"Draw! Both chose {self.player_choice}."
            self.result_color = (240, 210, 80)

        # Check match victory (Task 2)
        if self.player_score >= self.WIN_SCORE:
            self.game_over = True
            self.winner = "PLAYER"
            self.result_text = "MATCH OVER: You are the Champion! Press 'R' to Restart."
            self.result_color = (80, 240, 140)
        elif self.cpu_score >= self.WIN_SCORE:
            self.game_over = True
            self.winner = "CPU"
            self.result_text = "MATCH OVER: CPU Wins the Match! Press 'R' to Restart."
            self.result_color = (255, 90, 90)

        self.state = "SHOW_RESULT"
        self.round_resolved_time = pygame.time.get_ticks()

    def reset_game(self):
        """Reset match state on 'R'."""
        self.player_score = 0
        self.cpu_score = 0
        self.player_choice = None
        self.cpu_choice = None
        self.game_over = False
        self.winner = None
        self.state = "IDLE"
        self.result_text = "New Match! First to 3 Wins."
        self.result_color = (220, 225, 235)
        self.player_history = {"ROCK": 0, "PAPER": 0, "SCISSORS": 0}

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.reset_game()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.game_over and self.state == "IDLE":
                for btn in self.buttons:
                    if btn.contains(event.pos):
                        self.start_round(btn.choice_name)
                        break

    def update(self):
        now = pygame.time.get_ticks()
        if self.state == "ANIMATING":
            if now - self.anim_start_time >= self.anim_duration:
                self.resolve_round()
        elif self.state == "SHOW_RESULT" and not self.game_over:
            if now - self.round_resolved_time >= self.display_duration:
                self.player_choice = None
                self.cpu_choice = None
                self.result_text = "Make your move!"
                self.result_color = (190, 195, 205)
                self.state = "IDLE"

    def draw_gesture_icon(self, screen, gesture, center_x, center_y, color=(235, 235, 240)):
        """Task 4: Procedural rendering of hand signs."""
        if gesture == "ROCK":
            # Faceted stone/fist polygon
            points = [
                (center_x - 18, center_y + 12),
                (center_x - 22, center_y - 8),
                (center_x - 8, center_y - 22),
                (center_x + 12, center_y - 20),
                (center_x + 22, center_y - 6),
                (center_x + 18, center_y + 16),
                (center_x - 4, center_y + 22),
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (30, 30, 35), points, 2)
        elif gesture == "PAPER":
            # Document/flat palm sheet
            rect = pygame.Rect(center_x - 16, center_y - 22, 32, 44)
            pygame.draw.rect(screen, color, rect, border_radius=3)
            pygame.draw.rect(screen, (30, 30, 35), rect, 2, border_radius=3)
            for offset_y in (-8, 0, 8):
                pygame.draw.line(screen, (100, 110, 125), (center_x - 10, center_y + offset_y), (center_x + 10, center_y + offset_y), 2)
        elif gesture == "SCISSORS":
            # Crossed blades & handles
            pygame.draw.circle(screen, color, (center_x - 10, center_y + 14), 7, 2)
            pygame.draw.circle(screen, color, (center_x + 10, center_y + 14), 7, 2)
            pygame.draw.line(screen, color, (center_x - 6, center_y + 8), (center_x + 16, center_y - 20), 3)
            pygame.draw.line(screen, color, (center_x + 6, center_y + 8), (center_x - 16, center_y - 20), 3)

    def render(self, screen):
        screen.fill((22, 26, 34))

        # Title and Win Condition
        title_surf = self.font_title.render("Rock Paper Scissors", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 10))

        sub_surf = self.font_hud.render(f"Race to {self.WIN_SCORE} Wins", True, (160, 170, 185))
        screen.blit(sub_surf, (self.width // 2 - sub_surf.get_width() // 2, 38))

        # Scores
        p_surf = self.font_hud.render(f"Player: {self.player_score}/{self.WIN_SCORE}", True, (100, 190, 255))
        c_surf = self.font_hud.render(f"CPU: {self.cpu_score}/{self.WIN_SCORE}", True, (255, 120, 120))
        screen.blit(p_surf, (35, 38))
        screen.blit(c_surf, (self.width - c_surf.get_width() - 35, 38))

        pygame.draw.line(screen, (45, 52, 66), (25, 66), (self.width - 25, 66), 2)

        # Arena Display with Procedural Icons & Reveal Shake Animation
        p_card = pygame.Rect(self.width // 2 - 190, 80, 160, 110)
        c_card = pygame.Rect(self.width // 2 + 30, 80, 160, 110)
        pygame.draw.rect(screen, (32, 38, 50), p_card, border_radius=8)
        pygame.draw.rect(screen, (32, 38, 50), c_card, border_radius=8)

        lbl_p = self.font_hud.render("YOU", True, (140, 150, 165))
        lbl_c = self.font_hud.render("CPU", True, (140, 150, 165))
        screen.blit(lbl_p, (p_card.centerx - lbl_p.get_width() // 2, p_card.y + 8))
        screen.blit(lbl_c, (c_card.centerx - lbl_c.get_width() // 2, c_card.y + 8))

        if self.state == "ANIMATING":
            # Task 4: Shake animation
            elapsed = pygame.time.get_ticks() - self.anim_start_time
            shake_offset = int(math.sin(elapsed * 0.04) * 8)
            self.draw_gesture_icon(screen, "ROCK", p_card.centerx, p_card.centery + 12 + shake_offset, (100, 190, 255))
            self.draw_gesture_icon(screen, "ROCK", c_card.centerx, c_card.centery + 12 - shake_offset, (255, 120, 120))
        elif self.state == "SHOW_RESULT":
            self.draw_gesture_icon(screen, self.player_choice, p_card.centerx, p_card.centery + 12, (100, 190, 255))
            self.draw_gesture_icon(screen, self.cpu_choice, c_card.centerx, c_card.centery + 12, (255, 120, 120))
        else:
            q_surf = self.font_arena.render("?", True, (100, 110, 125))
            screen.blit(q_surf, (p_card.centerx - q_surf.get_width() // 2, p_card.centery))
            screen.blit(q_surf, (c_card.centerx - q_surf.get_width() // 2, c_card.centery))

        # Outcome or Victory Banner
        res_surf = self.font_arena.render(self.result_text, True, self.result_color)
        screen.blit(res_surf, (self.width // 2 - res_surf.get_width() // 2, 205))

        # Buttons
        for btn in self.buttons:
            btn.render(screen)