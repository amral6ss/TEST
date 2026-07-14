import pygame
import random
import sys
import math
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
GAME_WIDTH = 600
SIDEBAR_WIDTH = WINDOW_WIDTH - GAME_WIDTH
WINDOW_HEIGHT = 600
GRID_SIZE = 20
CELL_SIZE = GAME_WIDTH // GRID_SIZE

# Colors (RGB)
BLACK = (10, 10, 10)
WHITE = (220, 220, 220)
GREEN = (50, 220, 80)
DARK_GREEN = (30, 160, 50)
RED = (255, 60, 60)
DARK_RED = (200, 20, 20)
BLUE = (40, 120, 255)
DARK_BLUE = (20, 60, 200)
GRAY = (120, 120, 120)
LIGHT_GRAY = (50, 50, 50)
YELLOW = (255, 220, 40)
DARK_YELLOW = (200, 170, 20)
PURPLE = (160, 50, 255)
ORANGE = (255, 140, 40)
CYAN = (40, 220, 255)
BROWN = (140, 80, 30)
DARK_BG = (15, 15, 25)
SIDEBAR_BG = (20, 20, 35)
GRID_LINE = (30, 30, 45)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Food types
NORMAL = 0
GOLDEN = 1
POISON = 2

# ═══════════════════════════════════════════════════════
# 🎮  CONFIGURATION — Adjust all game values here
# ═══════════════════════════════════════════════════════
CONFIG = {
    # ── Speed ──
    "base_speed": 8,            # Initial game speed (FPS)
    "max_speed": 22,            # Maximum game speed cap
    "speed_per_level": 1.5,     # Speed increase per level

    # ── Food Distribution (probabilities must add up) ──
    "food_golden_chance": 0.15, # 15% chance for Golden food
    "food_poison_chance": 0.10, # 10% chance for Poison food
    # Normal food = remaining (75%)

    # ── Food Points ──
    "food_normal_points": 1,    # Points for Normal food
    "food_golden_points": 3,    # Points for Golden food
    "food_poison_points": -1,   # Points for Poison food

    # ── Walls ──
    "walls_per_level": 1,       # Number of walls added per level

    # ── Leveling ──
    "points_per_level": 5,      # Score needed per level (score // this + 1)
}
# ═══════════════════════════════════════════════════════

# Menu states
MENU = 0
SETTINGS = 1
PLAYING = 2


class MainMenu:
    def __init__(self):
        self.selected = 0
        self.options = ["Play", "Settings", "Quit"]
        self.frame = 0

    def draw(self, screen, font_large, font_medium, font_small, font_tiny, high_score):
        self.frame += 1

        # Title
        title = font_large.render("SNAKE", True, GREEN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 110))
        screen.blit(title, title_rect)

        subtitle = font_medium.render("EVOLUTION", True, CYAN)
        sub_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 160))
        screen.blit(subtitle, sub_rect)

        # Decorative animated snake
        for i in range(15):
            x = WINDOW_WIDTH // 2 - 120 + i * 17
            y = 200 + int(math.sin(self.frame * 0.08 + i * 0.5) * 5)
            pygame.draw.circle(screen, DARK_GREEN if i % 2 == 0 else GREEN, (x, y), 4)
        hx = WINDOW_WIDTH // 2 - 120 + 15 * 17
        hy = 200 + int(math.sin(self.frame * 0.08 + 15 * 0.5) * 5)
        pygame.draw.circle(screen, BLUE, (hx, hy), 6)

        # High score
        if high_score > 0:
            hs = font_small.render(f"Best Score: {high_score}", True, YELLOW)
            hs_rect = hs.get_rect(center=(WINDOW_WIDTH // 2, 240))
            screen.blit(hs, hs_rect)

        # Options
        option_start = 300
        option_spacing = 55

        for i, option in enumerate(self.options):
            if i == self.selected:
                color = YELLOW
                f = font_medium
                rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, option_start + i * option_spacing - 12, 200, 38)
                pygame.draw.rect(screen, (40, 40, 50), rect, border_radius=6)
                pygame.draw.rect(screen, YELLOW, rect, 2, border_radius=6)
            else:
                color = GRAY
                f = font_small

            text = f.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, option_start + i * option_spacing))
            screen.blit(text, text_rect)

        # Footer
        footer = font_tiny.render("Arrows/WASD to navigate  ENTER to select  ESC to quit", True, GRAY)
        footer_rect = footer.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40))
        screen.blit(footer, footer_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return ["play", "settings", "quit"][self.selected]
            elif event.key == pygame.K_ESCAPE:
                return "quit"
        return None


class SettingsMenu:
    def __init__(self):
        self.selected = 0
        self.editing = False
        self.items = [
            {"label": "Base Speed",          "key": "base_speed",          "min": 2,   "max": 30,  "step": 1,    "fmt": "{} fps"},
            {"label": "Max Speed",           "key": "max_speed",           "min": 5,   "max": 50,  "step": 1,    "fmt": "{} fps"},
            {"label": "Speed per Level",     "key": "speed_per_level",    "min": 0.1, "max": 10,  "step": 0.5,  "fmt": "{:.1f}"},
            {"label": "Golden Food %",       "key": "food_golden_chance", "min": 0,   "max": 80,  "step": 5,    "fmt": "{}%",   "mult": 100},
            {"label": "Poison Food %",       "key": "food_poison_chance", "min": 0,   "max": 80,  "step": 5,    "fmt": "{}%",   "mult": 100},
            {"label": "Normal Points",       "key": "food_normal_points", "min": 1,   "max": 20,  "step": 1,    "fmt": "{}"},
            {"label": "Golden Points",       "key": "food_golden_points", "min": 1,   "max": 50,  "step": 1,    "fmt": "{}"},
            {"label": "Poison Points",       "key": "food_poison_points", "min": -10, "max": 0,   "step": 1,    "fmt": "{}"},
            {"label": "Walls per Level",     "key": "walls_per_level",    "min": 0,   "max": 10,  "step": 1,    "fmt": "{}"},
            {"label": "Points per Level",    "key": "points_per_level",   "min": 1,   "max": 50,  "step": 1,    "fmt": "{}"},
        ]

    def get_display_value(self, item):
        raw = CONFIG[item["key"]]
        if "mult" in item:
            return int(raw * item["mult"])
        return raw

    def draw(self, screen, font_medium, font_small, font_tiny):
        screen.fill(DARK_BG)

        title = font_medium.render("SETTINGS", True, CYAN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 35))
        screen.blit(title, title_rect)
        pygame.draw.line(screen, GRID_LINE, (50, 60), (WINDOW_WIDTH - 50, 60), 1)

        start_y = 85
        line_height = 38

        for i, item in enumerate(self.items):
            val = self.get_display_value(item)
            y = start_y + i * line_height

            if i == self.selected:
                if self.editing:
                    rect = pygame.Rect(60, y, WINDOW_WIDTH - 120, line_height - 4)
                    pygame.draw.rect(screen, (30, 30, 60), rect, border_radius=4)
                    pygame.draw.rect(screen, BLUE, rect, 2, border_radius=4)
                else:
                    rect = pygame.Rect(60, y, WINDOW_WIDTH - 120, line_height - 4)
                    pygame.draw.rect(screen, (40, 40, 50), rect, border_radius=4)
                    pygame.draw.rect(screen, YELLOW, rect, 1, border_radius=4)

            label_color = WHITE if i == self.selected else GRAY
            label = font_tiny.render(item["label"], True, label_color)
            screen.blit(label, (75, y + 5))

            if i == self.selected and self.editing:
                val_text = font_small.render(f"\u25c0 {val} \u25b6", True, YELLOW)
            else:
                val_text = font_small.render(str(val), True, CYAN if i == self.selected else GRAY)
            val_rect = val_text.get_rect(midright=(WINDOW_WIDTH - 85, y + line_height // 2))
            screen.blit(val_text, val_rect)

        hint = font_tiny.render(
            "\u2191\u2193 Navigate  ENTER to edit  \u2190\u2192 Change  ESC Back",
            True, GRAY
        )
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25))
        screen.blit(hint, hint_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.editing:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    item = self.items[self.selected]
                    raw = CONFIG[item["key"]]
                    new_val = max(item["min"], raw - item["step"])
                    self._update_config(item, new_val)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    item = self.items[self.selected]
                    raw = CONFIG[item["key"]]
                    new_val = min(item["max"], raw + item["step"])
                    self._update_config(item, new_val)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    self.editing = False
                return None
            else:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.items)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.editing = True
                elif event.key == pygame.K_ESCAPE:
                    return "back"
        return None

    def _update_config(self, item, new_val):
        CONFIG[item["key"]] = new_val
        if item["key"] == "food_golden_chance":
            max_poison = 1.0 - CONFIG["food_golden_chance"]
            if CONFIG["food_poison_chance"] > max_poison:
                CONFIG["food_poison_chance"] = max(0, max_poison * 0.99)
        elif item["key"] == "food_poison_chance":
            max_golden = 1.0 - CONFIG["food_poison_chance"]
            if CONFIG["food_golden_chance"] > max_golden:
                CONFIG["food_golden_chance"] = max(0, max_golden * 0.99)


class Particle:
    def __init__(self, x, y, color, vel=None, life=30):
        self.x = x
        self.y = y
        self.color = color
        self.vel = vel or (random.uniform(-2, 2), random.uniform(-3, 0))
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vel[0]
        self.y += self.vel[1]
        self.vel = (self.vel[0] * 0.95, self.vel[1] + 0.1)
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            alpha = self.life / self.max_life
            size = int(self.size * alpha)
            if size > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

    @property
    def dead(self):
        return self.life <= 0


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        start_x = GRID_SIZE // 2
        start_y = GRID_SIZE // 2
        self.body = deque([(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)])
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.grow_flag = False
        self.shake_timer = 0
        self.pulse = 0

    def move(self):
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        self.body.appendleft(new_head)

        if self.grow_flag:
            self.grow_flag = False
        else:
            self.body.pop()

        self.pulse = (self.pulse + 1) % 60

    def grow(self):
        self.grow_flag = True

    def shrink(self):
        if len(self.body) > 3:
            self.body.pop()

    def check_collision(self, walls):
        head = self.body[0]
        # Wall collision
        if head[0] < 0 or head[0] >= GRID_SIZE or head[1] < 0 or head[1] >= GRID_SIZE:
            return True
        # Self collision
        if head in list(self.body)[1:]:
            return True
        # Wall obstacle collision
        if head in walls:
            return True
        return False

    def change_direction(self, new_dir):
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.next_direction = new_dir

    def draw(self, screen, offset_x=0):
        body_list = list(self.body)
        # Draw shadow
        for i, segment in enumerate(body_list):
            x, y = segment
            shadow_rect = pygame.Rect(
                offset_x + x * CELL_SIZE + 3, y * CELL_SIZE + 3,
                CELL_SIZE - 2, CELL_SIZE - 2
            )
            pygame.draw.rect(screen, (0, 0, 0, 80), shadow_rect, border_radius=4)

        for i, segment in enumerate(body_list):
            x, y = segment
            if i == 0:  # Head with pulse
                pulse_offset = math.sin(self.pulse * 0.2) * 1
                rect = pygame.Rect(
                    offset_x + x * CELL_SIZE + 1 - pulse_offset,
                    y * CELL_SIZE + 1 - pulse_offset,
                    CELL_SIZE - 2 + pulse_offset * 2,
                    CELL_SIZE - 2 + pulse_offset * 2
                )
                pygame.draw.rect(screen, BLUE, rect, border_radius=5)
                # Inner head glow
                inner = rect.inflate(-4, -4)
                pygame.draw.rect(screen, DARK_BLUE, inner, border_radius=4)
                # Eyes
                eye_size = 3
                dx, dy = self.direction
                if dx == 1:
                    eye1 = (offset_x + x * CELL_SIZE + CELL_SIZE - 6, y * CELL_SIZE + 5)
                    eye2 = (offset_x + x * CELL_SIZE + CELL_SIZE - 6, y * CELL_SIZE + CELL_SIZE - 8)
                elif dx == -1:
                    eye1 = (offset_x + x * CELL_SIZE + 6, y * CELL_SIZE + 5)
                    eye2 = (offset_x + x * CELL_SIZE + 6, y * CELL_SIZE + CELL_SIZE - 8)
                elif dy == 1:
                    eye1 = (offset_x + x * CELL_SIZE + 5, y * CELL_SIZE + CELL_SIZE - 6)
                    eye2 = (offset_x + x * CELL_SIZE + CELL_SIZE - 8, y * CELL_SIZE + CELL_SIZE - 6)
                else:
                    eye1 = (offset_x + x * CELL_SIZE + 5, y * CELL_SIZE + 6)
                    eye2 = (offset_x + x * CELL_SIZE + CELL_SIZE - 8, y * CELL_SIZE + 6)
                pygame.draw.circle(screen, WHITE, eye1, eye_size)
                pygame.draw.circle(screen, WHITE, eye2, eye_size)
                pygame.draw.circle(screen, BLACK, eye1, 1)
                pygame.draw.circle(screen, BLACK, eye2, 1)
            else:  # Body with gradient
                dist_from_head = i
                factor = max(0.3, 1 - dist_from_head / 30)
                color = (
                    int(DARK_GREEN[0] + (GREEN[0] - DARK_GREEN[0]) * factor),
                    int(DARK_GREEN[1] + (GREEN[1] - DARK_GREEN[1]) * factor),
                    int(DARK_GREEN[2] + (GREEN[2] - DARK_GREEN[2]) * factor),
                )
                margin = 2 if i % 2 == 0 else 3
                rect = pygame.Rect(
                    offset_x + x * CELL_SIZE + margin,
                    y * CELL_SIZE + margin,
                    CELL_SIZE - margin * 2,
                    CELL_SIZE - margin * 2
                )
                pygame.draw.rect(screen, color, rect, border_radius=3)


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.type = NORMAL
        self.glow = 0
        self.randomize([])

    def randomize(self, snake_body, walls=None):
        walls = walls or []
        while True:
            self.position = (random.randint(0, GRID_SIZE - 1),
                             random.randint(0, GRID_SIZE - 1))
            if self.position not in snake_body and self.position not in walls:
                break
        r = random.random()
        if r < CONFIG["food_golden_chance"]:
            self.type = GOLDEN
        elif r < CONFIG["food_golden_chance"] + CONFIG["food_poison_chance"]:
            self.type = POISON
        else:
            self.type = NORMAL

    def draw(self, screen, offset_x=0):
        x, y = self.position
        self.glow = (self.glow + 1) % 60
        glow_intensity = abs(math.sin(self.glow * 0.1))

        cx = offset_x + x * CELL_SIZE + CELL_SIZE // 2
        cy = y * CELL_SIZE + CELL_SIZE // 2

        if self.type == NORMAL:
            color = RED
            dark_color = DARK_RED
            glow_color = (255, 80, 80)
        elif self.type == GOLDEN:
            color = YELLOW
            dark_color = DARK_YELLOW
            glow_color = (255, 220, 60)
        else:  # POISON
            color = PURPLE
            dark_color = (120, 30, 200)
            glow_color = (180, 60, 255)

        # Glow effect
        glow_radius = int(CELL_SIZE // 2 + glow_intensity * 4)
        for r in range(glow_radius, 0, -2):
            alpha = int(100 * (r / glow_radius))
            gsurf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, (*glow_color, alpha), (CELL_SIZE // 2, CELL_SIZE // 2), r)
            screen.blit(gsurf, (offset_x + x * CELL_SIZE, y * CELL_SIZE))

        # Main shape
        if self.type == POISON:
            # Skull-like shape
            points = []
            for i in range(8):
                angle = i * math.pi / 4
                r = CELL_SIZE // 2 - 3
                px = cx + math.cos(angle) * r
                py = cy + math.sin(angle) * r
                points.append((px, py))
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, dark_color, points, 2)
            # Eyes
            pygame.draw.circle(screen, WHITE, (cx - 4, cy - 3), 3)
            pygame.draw.circle(screen, WHITE, (cx + 4, cy - 3), 3)
            pygame.draw.circle(screen, BLACK, (cx - 4, cy - 3), 1)
            pygame.draw.circle(screen, BLACK, (cx + 4, cy - 3), 1)
        else:
            rect = pygame.Rect(
                offset_x + x * CELL_SIZE + 2, y * CELL_SIZE + 2,
                CELL_SIZE - 4, CELL_SIZE - 4
            )
            pygame.draw.ellipse(screen, color, rect)
            highlight = pygame.Rect(
                offset_x + x * CELL_SIZE + 6, y * CELL_SIZE + 5,
                CELL_SIZE - 12, CELL_SIZE - 10
            )
            pygame.draw.ellipse(screen, dark_color, highlight)
            if self.type == GOLDEN:
                # Star sparkle
                pygame.draw.circle(screen, WHITE, (cx - 3, cy - 5), 2)
                pygame.draw.circle(screen, WHITE, (cx + 4, cy + 4), 1)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Evolution")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 42)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tiny = pygame.font.Font(None, 20)
        self.particles = []
        self.walls = set()
        self.high_score = 0
        self.start_time = 0
        self.flash_timer = 0
        self.reset()

    def reset(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.walls = set()
        self.particles = []
        self.start_time = pygame.time.get_ticks() if not self.game_over else pygame.time.get_ticks()

    def add_particles(self, x, y, color, count=8):
        cx = x * CELL_SIZE + CELL_SIZE // 2
        cy = y * CELL_SIZE + CELL_SIZE // 2
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            vel = (math.cos(angle) * speed, math.sin(angle) * speed - 1)
            self.particles.append(Particle(cx, cy, color, vel, random.randint(15, 30)))

    def generate_walls(self):
        self.walls = set()
        wall_count = self.level * CONFIG["walls_per_level"]
        for _ in range(wall_count):
            for attempt in range(50):
                wx = random.randint(2, GRID_SIZE - 3)
                wy = random.randint(2, GRID_SIZE - 3)
                pos = (wx, wy)
                if (pos not in self.snake.body and
                    pos != self.food.position and
                    pos not in self.walls and
                    abs(wx - self.snake.body[0][0]) > 3 and
                    abs(wy - self.snake.body[0][1]) > 3):
                    self.walls.add(pos)
                    break

    def draw_grid(self, offset_x=0):
        for x in range(0, GAME_WIDTH, CELL_SIZE):
            for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
                rect = pygame.Rect(offset_x + x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, GRID_LINE, rect, 1)

    def draw_sidebar(self):
        # Sidebar background
        sidebar_rect = pygame.Rect(GAME_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, SIDEBAR_BG, sidebar_rect)
        pygame.draw.line(self.screen, GRID_LINE, (GAME_WIDTH, 0), (GAME_WIDTH, WINDOW_HEIGHT), 2)

        # Title
        title = self.font_medium.render("SNAKE", True, GREEN)
        self.screen.blit(title, (GAME_WIDTH + 25, 30))
        title2 = self.font_small.render("EVOLUTION", True, CYAN)
        self.screen.blit(title2, (GAME_WIDTH + 35, 70))

        y_off = 130
        # Score
        score_label = self.font_tiny.render("SCORE", True, GRAY)
        self.screen.blit(score_label, (GAME_WIDTH + 25, y_off))
        score_val = self.font_large.render(str(self.score), True, WHITE)
        self.screen.blit(score_val, (GAME_WIDTH + 25, y_off + 25))

        y_off += 90
        # High Score
        hs_label = self.font_tiny.render("BEST", True, GRAY)
        self.screen.blit(hs_label, (GAME_WIDTH + 25, y_off))
        hs_val = self.font_medium.render(str(self.high_score), True, YELLOW)
        self.screen.blit(hs_val, (GAME_WIDTH + 25, y_off + 25))

        y_off += 80
        # Level
        lvl_label = self.font_tiny.render("LEVEL", True, GRAY)
        self.screen.blit(lvl_label, (GAME_WIDTH + 25, y_off))
        lvl_val = self.font_medium.render(str(self.level), True, ORANGE)
        self.screen.blit(lvl_val, (GAME_WIDTH + 25, y_off + 25))

        y_off += 80
        # Length
        len_label = self.font_tiny.render("LENGTH", True, GRAY)
        self.screen.blit(len_label, (GAME_WIDTH + 25, y_off))
        len_val = self.font_medium.render(str(len(self.snake.body)), True, GREEN)
        self.screen.blit(len_val, (GAME_WIDTH + 25, y_off + 25))

        y_off += 80
        # Time
        if not self.game_over and not self.paused:
            elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        elif self.game_over:
            elapsed = self.final_time
        else:
            elapsed = self.paused_time

        time_label = self.font_tiny.render("TIME", True, GRAY)
        self.screen.blit(time_label, (GAME_WIDTH + 25, y_off))
        mins = elapsed // 60
        secs = elapsed % 60
        time_str = f"{mins}:{secs:02d}"
        time_val = self.font_medium.render(time_str, True, CYAN)
        self.screen.blit(time_val, (GAME_WIDTH + 25, y_off + 25))

        # Food legend
        y_off += 90
        legend_title = self.font_tiny.render("FOOD TYPES", True, GRAY)
        self.screen.blit(legend_title, (GAME_WIDTH + 25, y_off))

        y_off += 30
        # Normal
        pygame.draw.circle(self.screen, RED, (GAME_WIDTH + 35, y_off + 5), 6)
        norm_txt = self.font_tiny.render("Normal  +1", True, WHITE)
        self.screen.blit(norm_txt, (GAME_WIDTH + 50, y_off))

        y_off += 25
        # Golden
        pygame.draw.circle(self.screen, YELLOW, (GAME_WIDTH + 35, y_off + 5), 6)
        gold_txt = self.font_tiny.render("Golden  +3", True, WHITE)
        self.screen.blit(gold_txt, (GAME_WIDTH + 50, y_off))

        y_off += 25
        # Poison
        pygame.draw.circle(self.screen, PURPLE, (GAME_WIDTH + 35, y_off + 5), 6)
        pois_txt = self.font_tiny.render("Poison  -1", True, WHITE)
        self.screen.blit(pois_txt, (GAME_WIDTH + 50, y_off))

        # Controls
        ctrl_y = WINDOW_HEIGHT - 130
        ctrl_title = self.font_tiny.render("CONTROLS", True, GRAY)
        self.screen.blit(ctrl_title, (GAME_WIDTH + 25, ctrl_y))
        ctrl_y += 25
        self.screen.blit(self.font_tiny.render("Arrows  Move", True, WHITE), (GAME_WIDTH + 25, ctrl_y))
        ctrl_y += 20
        self.screen.blit(self.font_tiny.render("P          Pause", True, WHITE), (GAME_WIDTH + 25, ctrl_y))
        ctrl_y += 20
        self.screen.blit(self.font_tiny.render("ESC       Quit", True, WHITE), (GAME_WIDTH + 25, ctrl_y))

    def draw(self):
        self.screen.fill(DARK_BG)
        self.draw_grid()

        # Draw walls
        for wx, wy in sorted(self.walls):
            wall_x = wx * CELL_SIZE
            wall_y = wy * CELL_SIZE
            # Animated wall
            phase = (wx + wy) * 0.5 + pygame.time.get_ticks() * 0.002
            color_shift = int((math.sin(phase) * 20))
            wall_color = (
                min(255, BROWN[0] + color_shift),
                min(255, BROWN[1] + color_shift),
                min(255, BROWN[2] + color_shift)
            )
            rect = pygame.Rect(wall_x + 1, wall_y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(self.screen, wall_color, rect, border_radius=2)
            # Brick pattern
            inner = pygame.Rect(wall_x + 3, wall_y + 3, CELL_SIZE - 6, CELL_SIZE - 6)
            pygame.draw.rect(self.screen, (max(0, wall_color[0]-30), max(0, wall_color[1]-30), max(0, wall_color[2]-30)), inner, border_radius=1)

        # Draw food
        if not self.game_over:
            self.food.draw(self.screen)

        # Draw snake
        self.snake.draw(self.screen)

        # Draw particles
        self.particles = [p for p in self.particles if not p.dead]
        for p in self.particles:
            p.update()
            p.draw(self.screen)

        # Draw sidebar
        self.draw_sidebar()

        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((GAME_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(140)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font_large.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(GAME_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
            self.screen.blit(game_over_text, text_rect)

            final_score = self.font_medium.render(f"Score: {self.score}", True, WHITE)
            score_rect = final_score.get_rect(center=(GAME_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(final_score, score_rect)

            level_text = self.font_small.render(f"Level: {self.level}  |  Length: {len(self.snake.body)}", True, GRAY)
            lvl_rect = level_text.get_rect(center=(GAME_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
            self.screen.blit(level_text, lvl_rect)

            if self.score == self.high_score and self.score > 0:
                new_best = self.font_small.render("NEW BEST!", True, YELLOW)
                best_rect = new_best.get_rect(center=(GAME_WIDTH // 2, WINDOW_HEIGHT // 2 + 75))
                self.screen.blit(new_best, best_rect)

            restart_text = self.font_small.render("Press SPACE to play again", True, GRAY)
            restart_rect = restart_text.get_rect(center=(GAME_WIDTH // 2, WINDOW_HEIGHT // 2 + 115))
            self.screen.blit(restart_text, restart_rect)

        # Pause overlay
        if self.paused and not self.game_over:
            overlay = pygame.Surface((GAME_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(100)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            pause_text = self.font_large.render("PAUSED", True, WHITE)
            text_rect = pause_text.get_rect(center=(GAME_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(pause_text, text_rect)

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.reset()
                else:
                    if event.key == pygame.K_p:
                        if not self.paused:
                            self.paused_time = (pygame.time.get_ticks() - self.start_time) // 1000
                        else:
                            self.start_time = pygame.time.get_ticks() - self.paused_time * 1000
                        self.paused = not self.paused

                    if not self.paused:
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.snake.change_direction(UP)
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.snake.change_direction(DOWN)
                        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.snake.change_direction(LEFT)
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.snake.change_direction(RIGHT)

        return True

    def update(self):
        if self.game_over or self.paused:
            return

        self.snake.move()

        # Check collision
        if self.snake.check_collision(self.walls):
            self.game_over = True
            self.final_time = (pygame.time.get_ticks() - self.start_time) // 1000
            if self.score > self.high_score:
                self.high_score = self.score
            # Death particles
            for seg in self.snake.body:
                self.add_particles(seg[0], seg[1], RED, 3)
            return

        # Check food collision
        if self.snake.body[0] == self.food.position:
            head_x, head_y = self.snake.body[0]
            if self.food.type == NORMAL:
                self.snake.grow()
                self.score += 1
                self.add_particles(head_x, head_y, RED, 6)
            elif self.food.type == GOLDEN:
                self.snake.grow()
                self.score += 3
                self.add_particles(head_x, head_y, YELLOW, 12)
            else:  # POISON
                self.snake.shrink()
                self.score = max(0, self.score - 1)
                self.add_particles(head_x, head_y, PURPLE, 8)

            self.food.randomize(list(self.snake.body), self.walls)

            # Level up every 5 points
            new_level = self.score // 5 + 1
            if new_level > self.level:
                self.level = new_level
                self.generate_walls()
                # Level up particles
                for _ in range(20):
                    px = random.randint(0, GRID_SIZE - 1)
                    py = random.randint(0, GRID_SIZE - 1)
                    if (px, py) not in self.snake.body and (px, py) not in self.walls:
                        self.add_particles(px, py, CYAN, 5)

    def run(self):
        running = True

        while running:
            running = self.handle_events()
            self.update()

            # Dynamic speed based on level (uses CONFIG values)
            speed = CONFIG["base_speed"] + (self.level - 1) * CONFIG["speed_per_level"]
            speed = min(speed, CONFIG["max_speed"])

            self.draw()
            self.clock.tick(int(speed))

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
