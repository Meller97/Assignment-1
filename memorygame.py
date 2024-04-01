import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 700
screen_arena_width = 600
screen_height = 500
screen_arena_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors
background_color = (255, 255, 255)
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
colors *= 2  # Duplicate colors for pairs

# Positions and sizes
grid_size = (4, 3)  # 4 columns, 3 rows
rect_width = screen_arena_width // grid_size[0]
rect_height = screen_arena_height // grid_size[1]
rects = [pygame.Rect(x * rect_width +50, y * rect_height + 50, rect_width, rect_height) for x in range(grid_size[0]) for y in range(grid_size[1])]

# Game variables
selected = []  # Keep track of rectangles that are currently selected
matched = []  # Keep track of rectangles that have been matched
running = True
revealed = [False] * len(rects)  # Keep track of which rectangles are currently revealed
game_end = True

# Shuffle the colors
random.shuffle(colors)

# Timer setup
start_ticks = pygame.time.get_ticks()  # Starter tick
font = pygame.font.Font("digital-7.ttf", 36)

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and len(selected) < 2:
            mouse_pos = event.pos
            for i, rect in enumerate(rects):
                if rect.collidepoint(mouse_pos) and i not in matched and i not in selected:
                    selected.append(i)
                    revealed[i] = True
                    if len(selected) == 2 and colors[selected[0]] == colors[selected[1]]:
                        matched.extend(selected)
                        selected = []
                    elif len(selected) == 2:
                        pygame.time.wait(500)  # Wait half a second
                        for idx in selected:
                            revealed[idx] = False
                        selected = []

    screen.fill(background_color)

    for i, rect in enumerate(rects):
        if revealed[i] or i in matched:
            pygame.draw.rect(screen, colors[i], rect)
            game_end = True
        else:
            game_end = False
            pygame.draw.rect(screen, (0, 0, 0), rect)  # Draw hidden rectangle

    # Timer display
    if(not game_end):
        elapsed_ticks = pygame.time.get_ticks() - start_ticks
        elapsed_seconds = elapsed_ticks // 1000  # Convert milliseconds to seconds
    timer_text = f'Time: {elapsed_seconds // 60}:{elapsed_seconds % 60:02}'  # Format: "Time: M:SS"
    timer_surface = font.render(timer_text, True, (0, 255, 0))
    screen.blit(timer_surface, (5, 5))  # Position the timer at the top-left corner

    pygame.display.flip()

pygame.quit()