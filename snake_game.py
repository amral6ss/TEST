import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
GRID_SIZE = 20
CELL_SIZE = WINDOW_WIDTH // GRID_SIZE

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (200, 0, 0)
DARK_RED = (150, 0, 0)
GRAY = (40, 40, 40)
LIGHT_GRAY = (60, 60, 60)
BLUE = (50, 100, 255)
DARK_BLUE = (30, 70, 200)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (200, 50, 255)
PINK = (255, 50, 150)
CYAN = (0, 255, 255)

# Difficulty settings
DIFFICULTIES = {
    "Easy": {"speed": 8, "obstacle_score": 30, "desc": "\u0628\u0637\u064a\u0621 - \u0633\u0647\u0644"},
    "Medium": {"speed": 12, "obstacle_score": 20, "desc": "\u0645\u062a\u0648\u0633\u0637"},
    "Hard": {"speed": 18, "obstacle_score": 10, "desc": "\u0633\u0631\u064a\u0639 - \u0635\u0639\u0628"},
}

HIGH_SCORE_FILE = "highscore.txt"


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(score))
    except Exception:
        pass


# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


# ─── Obstacle ────────────────────────────────────────────────────────────────


class Obstacle:
    def __init__(self):
        self.positions = []

    def generate(self, snake_body, food_pos, num_obstacles=5):
        self.positions = []
        for _ in range(num_obstacles):
            while True:
                pos = (random.randint(1, GRID_SIZE - 2), random.randint(1, GRID_SIZE - 2))
                if pos not in snake_body and pos != food_pos and pos not in self.positions:
                    self.positions.append(pos)
                    break


# ─── Power-Up Food ───────────────────────────────────────────────────────────


class PowerUp:
    def __init__(self):
        self.position = None
        self.type = None
        self.timer = 0
        self.active = False
        self.types = ["speed_boost", "slow_down", "score_bonus"]

    def spawn(self, snake_body, food_pos, obstacles):
        if self.active:
            return
        self.active = True
        self.timer = 120  # ~10 seconds
        self.type = random.choice(self.types)
        while True:
            pos = (random.randint(1, GRID_SIZE - 2), random.randint(1, GRID_SIZE - 2))
            if (
                pos not in snake_body
                and pos != food_pos
                and pos not in obstacles.positions
            ):
                self.position = pos
                break

    def update(self):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False
                self.position = None

    def collect(self, score):
        if not self.active:
            return score
        self.active = False
        self.position = None
        if self.type == "speed_boost":
            return score + 2
        elif self.type == "slow_down":
            return score + 1
        elif self.type == "score_bonus":
            return score + 5
        return score


class Snake:
    def __init__(self):
        start_x = GRID_SIZE // 2
        start_y = GRID_SIZE // 2
        self.body = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.grow = False

    def change_direction(self, direction):
        # Prevent reversing into itself
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.next_direction = direction

    def move(self):
        self.direction = self.next_direction
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)

        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def check_collision(self):
        head = self.body[0]
        # Wall collision
        if head[0] < 0 or head[0] >= GRID_SIZE or head[1] < 0 or head[1] >= GRID_SIZE:
            return True
        # Self collision
        if head in self.body[1:]:
            return True
        return False

    def check_food(self, food_pos):
        return self.body[0] == food_pos

    def check_obstacle(self, obstacles):
        return self.body[0] in obstacles.positions


class Food:
    def __init__(self, snake_body):
        self.position = self.spawn(snake_body)

    def spawn(self, snake_body):
        while True:
            pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            if pos not in snake_body:
                return pos

    def respawn(self, snake_body):
        self.position = self.spawn(snake_body)


def draw_grid(screen):
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            if (x // CELL_SIZE + y // CELL_SIZE) % 2 == 0:
                pygame.draw.rect(screen, GRAY, rect)
            else:
                pygame.draw.rect(screen, LIGHT_GRAY, rect)


def draw_snake(screen, snake):
    for i, segment in enumerate(snake.body):
        rect = pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if i == 0:
            # Head
            pygame.draw.rect(screen, DARK_GREEN, rect)
            pygame.draw.rect(screen, GREEN, rect.inflate(-4, -4))
            # Eyes
            eye_size = 4
            cx, cy = segment[0] * CELL_SIZE + CELL_SIZE // 2, segment[1] * CELL_SIZE + CELL_SIZE // 2
            if snake.direction == RIGHT:
                pygame.draw.circle(screen, WHITE, (cx + 4, cy - 4), eye_size)
                pygame.draw.circle(screen, WHITE, (cx + 4, cy + 4), eye_size)
                pygame.draw.circle(screen, BLACK, (cx + 6, cy - 4), 2)
                pygame.draw.circle(screen, BLACK, (cx + 6, cy + 4), 2)
            elif snake.direction == LEFT:
                pygame.draw.circle(screen, WHITE, (cx - 4, cy - 4), eye_size)
                pygame.draw.circle(screen, WHITE, (cx - 4, cy + 4), eye_size)
                pygame.draw.circle(screen, BLACK, (cx - 6, cy - 4), 2)
                pygame.draw.circle(screen, BLACK, (cx - 6, cy + 4), 2)
            elif snake.direction == UP:
                pygame.draw.circle(screen, WHITE, (cx - 4, cy - 4), eye_size)
                pygame.draw.circle(screen, WHITE, (cx + 4, cy - 4), eye_size)
                pygame.draw.circle(screen, BLACK, (cx - 4, cy - 6), 2)
                pygame.draw.circle(screen, BLACK, (cx + 4, cy - 6), 2)
            elif snake.direction == DOWN:
                pygame.draw.circle(screen, WHITE, (cx - 4, cy + 4), eye_size)
                pygame.draw.circle(screen, WHITE, (cx + 4, cy + 4), eye_size)
                pygame.draw.circle(screen, BLACK, (cx - 4, cy + 6), 2)
                pygame.draw.circle(screen, BLACK, (cx + 4, cy + 6), 2)
        else:
            pygame.draw.rect(screen, DARK_GREEN, rect)
            pygame.draw.rect(screen, GREEN, rect.inflate(-4, -4))


def draw_food(screen, food):
    rect = pygame.Rect(
        food.position[0] * CELL_SIZE,
        food.position[1] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE,
    )
    pygame.draw.rect(screen, DARK_RED, rect)
    inner = rect.inflate(-4, -4)
    pygame.draw.rect(screen, RED, inner)
    # Stem
    stem_rect = pygame.Rect(
        food.position[0] * CELL_SIZE + CELL_SIZE // 2 - 2,
        food.position[1] * CELL_SIZE,
        4,
        6,
    )
    pygame.draw.rect(screen, DARK_GREEN, stem_rect)


def draw_obstacles(screen, obstacles):
    for pos in obstacles.positions:
        rect = pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, DARK_BLUE, rect)
        inner = rect.inflate(-3, -3)
        pygame.draw.rect(screen, BLUE, inner)
        inner2 = rect.inflate(-8, -8)
        pygame.draw.rect(screen, CYAN, inner2)


def draw_powerup(screen, powerup):
    if not powerup.active or powerup.position is None:
        return
    rect = pygame.Rect(
        powerup.position[0] * CELL_SIZE,
        powerup.position[1] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE,
    )
    pulse = abs((pygame.time.get_ticks() // 200) % 4 - 2)
    if powerup.type == "speed_boost":
        color = ORANGE
        dark = (200, 100, 0)
    elif powerup.type == "slow_down":
        color = CYAN
        dark = (0, 150, 150)
    else:
        color = YELLOW
        dark = (180, 180, 0)
    pygame.draw.rect(screen, dark, rect)
    inner = rect.inflate(-4 - pulse, -4 - pulse)
    pygame.draw.rect(screen, color, inner)
    font = pygame.font.Font(None, CELL_SIZE - 6)
    symbol = ""
    if powerup.type == "speed_boost":
        symbol = ">>"
    elif powerup.type == "slow_down":
        symbol = "<<"
    else:
        symbol = "+5"
    text = font.render(symbol, True, WHITE)
    screen.blit(
        text,
        (
            powerup.position[0] * CELL_SIZE + (CELL_SIZE - text.get_width()) // 2,
            powerup.position[1] * CELL_SIZE + (CELL_SIZE - text.get_height()) // 2,
        ),
    )


def draw_hud(screen, score, high_score, level_name, speed, powerup=None):
    font = pygame.font.Font(None, 28)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    hs_text = font.render(f"Best: {high_score}", True, YELLOW)
    screen.blit(hs_text, (10, 35))
    lvl_text = font.render(f"{level_name}  Speed: {speed}", True, LIGHT_GRAY)
    screen.blit(lvl_text, (10, 60))
    if powerup and powerup.active and powerup.timer:
        timer_sec = powerup.timer // 10
        pu_text = font.render(f"Power-up: {timer_sec}s", True, ORANGE)
        screen.blit(pu_text, (WINDOW_WIDTH - pu_text.get_width() - 10, 10))


def show_game_over(screen, score, high_score):
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    game_over_text = font_large.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 150))

    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 230))

    hs_text = font_small.render(f"Best: {high_score}", True, YELLOW)
    screen.blit(hs_text, (WINDOW_WIDTH // 2 - hs_text.get_width() // 2, 290))

    if score > high_score:
        new_record = font_medium.render("NEW RECORD!", True, YELLOW)
        screen.blit(new_record, (WINDOW_WIDTH // 2 - new_record.get_width() // 2, 340))

    restart_text = font_small.render("Press SPACE to play again", True, WHITE)
    screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 410))

    menu_text = font_small.render("Press M for menu", True, WHITE)
    screen.blit(menu_text, (WINDOW_WIDTH // 2 - menu_text.get_width() // 2, 450))

    quit_text = font_small.render("Press ESC to quit", True, WHITE)
    screen.blit(quit_text, (WINDOW_WIDTH // 2 - quit_text.get_width() // 2, 490))

    pygame.display.flip()


def show_start_screen(screen, high_score):
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 42)
    font_small = pygame.font.Font(None, 28)
    font_tiny = pygame.font.Font(None, 22)

    difficulties = ["Easy", "Medium", "Hard"]
    selected = 0
    selecting = True

    while selecting:
        screen.fill(BLACK)
        draw_grid(screen)

        title = font_large.render("SNAKE", True, GREEN)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 60))

        subtitle = font_medium.render("Classic Game", True, WHITE)
        screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 135))

        hs_text = font_small.render(f"Best Score: {high_score}", True, YELLOW)
        screen.blit(hs_text, (WINDOW_WIDTH // 2 - hs_text.get_width() // 2, 190))

        diff_title = font_small.render("Choose Difficulty:", True, WHITE)
        screen.blit(diff_title, (WINDOW_WIDTH // 2 - diff_title.get_width() // 2, 250))

        for i, d in enumerate(difficulties):
            color = GREEN if i == selected else GRAY
            prefix = "> " if i == selected else "  "
            diff_text = font_medium.render(f"{prefix}{d} - {DIFFICULTIES[d]['desc']}", True, color)
            screen.blit(diff_text, (WINDOW_WIDTH // 2 - diff_text.get_width() // 2, 300 + i * 50))

        controls = font_tiny.render("Use UP/DOWN arrows to select, SPACE to start", True, LIGHT_GRAY)
        screen.blit(controls, (WINDOW_WIDTH // 2 - controls.get_width() // 2, 470))
        controls2 = font_tiny.render("Arrow keys to move, P to pause", True, LIGHT_GRAY)
        screen.blit(controls2, (WINDOW_WIDTH // 2 - controls2.get_width() // 2, 500))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(difficulties)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(difficulties)
                elif event.key == pygame.K_SPACE:
                    selecting = False
                    return difficulties[selected]
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    return "Medium"


def game_loop():
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake Game")

    pygame.mixer.init()
    sounds = {
        "eat": None,
        "game_over": None,
        "powerup": None,
    }

    high_score = load_high_score()
    difficulty = "Medium"
    state = "START"
    score = 0
    snake = None
    food = None
    obstacles = None
    powerup = None
    paused = False
    powerup_active = False

    base_speed = DIFFICULTIES["Medium"]["speed"]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if state == "START":
                    if event.key == pygame.K_SPACE:
                        state = "PLAYING"
                        score = 0
                        powerup_active = False
                        snake = Snake()
                        food = Food(snake.body)
                        obstacles = Obstacle()
                        powerup = PowerUp()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif state == "PLAYING":
                    if event.key == pygame.K_UP:
                        snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(RIGHT)
                    elif event.key == pygame.K_p:
                        paused = not paused
                    elif event.key == pygame.K_ESCAPE:
                        paused = not paused
                elif state == "GAME_OVER":
                    if event.key == pygame.K_SPACE:
                        state = "PLAYING"
                        score = 0
                        powerup_active = False
                        snake = Snake()
                        food = Food(snake.body)
                        obstacles = Obstacle()
                        powerup = PowerUp()
                    elif event.key == pygame.K_m:
                        state = "START"
                    elif event.key == pygame.K_ESCAPE:
                        running = False

        if state == "START":
            difficulty = show_start_screen(screen, high_score)
            state = "PLAYING"
            score = 0
            powerup_active = False
            snake = Snake()
            food = Food(snake.body)
            obstacles = Obstacle()
            powerup = PowerUp()

        elif state == "PLAYING":
            if paused:
                font = pygame.font.Font(None, 72)
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.set_alpha(180)
                overlay.fill(BLACK)
                screen.blit(overlay, (0, 0))
                pause_text = font.render("PAUSED", True, WHITE)
                screen.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2, 250))
                resume_text = pygame.font.Font(None, 36).render("Press P or ESC to resume", True, LIGHT_GRAY)
                screen.blit(resume_text, (WINDOW_WIDTH // 2 - resume_text.get_width() // 2, 330))
                pygame.display.flip()
                clock.tick(10)
                continue

            snake.move()

            if snake.check_collision():
                state = "GAME_OVER"
                new_high = False
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                    new_high = True
                show_game_over(screen, score, high_score)
                continue

            if snake.check_food(food.position):
                snake.grow = True
                score += 1
                food.respawn(snake.body)

            if obstacles and snake.check_obstacle(obstacles):
                state = "GAME_OVER"
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                show_game_over(screen, score, high_score)
                continue

            obs_score = DIFFICULTIES[difficulty]["obstacle_score"]
            if obstacles and len(obstacles.positions) == 0 and score >= obs_score:
                obstacles.generate(snake.body, food.position)

            if obstacles and powerup and score >= obs_score + 5 and not powerup.active:
                powerup.spawn(snake.body, food.position, obstacles)

            if powerup:
                powerup.update()

            if powerup and powerup.active and snake.check_food(powerup.position):
                score = powerup.collect(score)
                powerup_active = True
                powerup.active = False
                powerup.position = None

            screen.fill(BLACK)
            draw_grid(screen)
            draw_food(screen, food)
            if powerup:
                draw_powerup(screen, powerup)
            if obstacles:
                draw_obstacles(screen, obstacles)
            draw_snake(screen, snake)

            speed = DIFFICULTIES[difficulty]["speed"]
            speed = min(speed + score // 5, 25)
            draw_hud(screen, score, high_score, difficulty, speed, powerup if powerup and powerup.active else None)

            pygame.display.flip()
            clock.tick(speed)

        elif state == "GAME_OVER":
            show_game_over(screen, score, high_score)
            clock.tick(10)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game_loop()
