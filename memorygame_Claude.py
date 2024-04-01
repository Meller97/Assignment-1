import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_SIZE = (800, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Memory Game")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Set up the game
CARD_SIZE = 100
NUM_CARDS = 16
cards = list(range(NUM_CARDS // 2))  # List of unique card values
cards *= 2  # Duplicate the list to create pairs
random.shuffle(cards)  # Shuffle the cards
card_rects = []  # List of card rectangles
selected_cards = []  # List of selected cards
matched_cards = []  # List of matched cards

# Create the card rectangles
for i in range(NUM_CARDS):
    x = (i % 4) * CARD_SIZE
    y = (i // 4) * CARD_SIZE
    card_rects.append(pygame.Rect(x, y, CARD_SIZE, CARD_SIZE))

# Game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and len(selected_cards) < 2:
            # Check if a card was clicked
            for i, rect in enumerate(card_rects):
                if rect.collidepoint(event.pos) and i not in matched_cards:
                    selected_cards.append(i)
                    if len(selected_cards) == 2:
                        # Check if the selected cards match
                        if cards[selected_cards[0]] == cards[selected_cards[1]]:
                            matched_cards.extend(selected_cards)
                        # Reset the selected cards after a short delay
                        pygame.time.delay(500)
                        selected_cards = []

    # Clear the screen
    screen.fill(WHITE)

    # Draw the cards
    for i, rect in enumerate(card_rects):
        if i in matched_cards:
            # Draw a green rectangle for matched cards
            pygame.draw.rect(screen, (0, 255, 0), rect)
        elif i in selected_cards:
            # Draw the card value for selected cards
            pygame.draw.rect(screen, BLACK, rect)
            font = pygame.font.Font(None, 72)
            text = font.render(str(cards[i]), True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
        else:
            # Draw a gray rectangle for unselected cards
            pygame.draw.rect(screen, (128, 128, 128), rect)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()