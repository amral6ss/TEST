import pygame
import random
import sys

# Initialize pygame
pygame.init()

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

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


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
    rect = pygame.Rect(food.position[0] * CELL_SIZE, food.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, DARK_RED, rect)
    pygame.draw.rect(screen, RED, rect.inflate(-4, -4))


def show_game_over(screen, score):
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)

    # Dim background
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    game_over_text = font_large.render("GAME OVER", True, RED)
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    restart_text = font_small.render("Press SPACE to play again", True, WHITE)
    quit_text = font_small.render("Press ESC to quit", True, WHITE)

    screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 180))
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 270))
    screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 340))
    screen.blit(quit_text, (WINDOW_WIDTH // 2 - quit_text.get_width() // 2, 380))

    pygame.display.flip()


def show_start_screen(screen):
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    font_tiny = pygame.font.Font(None, 24)

    screen.fill(BLACK)
    draw_grid(screen)

    title = font_large.render("SNAKE", True, GREEN)
    subtitle = font_small.render("The Classic Game", True, WHITE)
    start_text = font_small.render("Press SPACE to start", True, WHITE)
    controls = font_tiny.render("Use arrow keys to move", True, GRAY)

    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 150))
    screen.blit(subtitle, (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 230))
    screen.blit(start_text, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, 320))
    screen.blit(controls, (WINDOW_WIDTH // 2 - controls.get_width() // 2, 380))

    pygame.display.flip()


def game_loop():
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake Game")

    # State
    state = "START"  # START, PLAYING, GAME_OVER
    score = 0
    snake = None
    food = None

    # Speed increases with score
    base_speed = 10

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if state == "START":
                    if event.key == pygame.K_SPACE:
                        state = "PLAYING"
                        score = 0
                        snake = Snake()
                        food = Food(snake.body)
                elif state == "PLAYING":
                    if event.key == pygame.K_UP:
                        snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(RIGHT)
                elif state == "GAME_OVER":
                    if event.key == pygame.K_SPACE:
                        state = "PLAYING"
                        score = 0
                        snake = Snake()
                        food = Food(snake.body)
                    elif event.key == pygame.K_ESCAPE:
                        running = False

        if state == "START":
            show_start_screen(screen)
            clock.tick(10)

        elif state == "PLAYING":
            snake.move()

            if snake.check_collision():
                state = "GAME_OVER"
                show_game_over(screen, score)
                continue

            if snake.check_food(food.position):
                snake.grow = True
                score += 1
                food.respawn(snake.body)

            # Draw everything
            screen.fill(BLACK)
            draw_grid(screen)
            draw_food(screen, food)
            draw_snake(screen, snake)

            # Draw score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))

            pygame.display.flip()

            # Speed increases with score, capped at 20
            speed = min(base_speed + score // 3, 20)
            clock.tick(speed)

        elif state == "GAME_OVER":
            show_game_over(screen, score)
            clock.tick(10)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game_loop()
