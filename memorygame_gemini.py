import pygame
import random

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Define dimensions
WIDTH = 800
HEIGHT = 600
MARGIN = 50

# Define card size
CARD_WIDTH = 100
CARD_HEIGHT = 100

# Define number of card pairs
NUM_PAIRS = 8

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Game")

# Load card back image (replace with your image path)
card_back_img = pygame.image.load("card_back.png").convert_alpha()


# Define a class for cards
class Card:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.flipped = False
        self.match = None

    def draw(self):
        if self.flipped:
            screen.blit(self.image, (self.x, self.y))
        else:
            screen.blit(card_back_img, (self.x, self.y))

    def flip(self):
        self.flipped = not self.flipped

    def set_match(self, other_card):
        self.match = other_card
        other_card.match = self


# Function to shuffle card images
def shuffle_cards(images):
    card_list = images * 2
    random.shuffle(card_list)
    return card_list[:NUM_PAIRS * 2]


# Load card face images (replace with your image paths)
images = [
    pygame.image.load("card_image1.png").convert_alpha(),
    pygame.image.load("card_image2.png").convert_alpha(),
    # ... add more images for more pairs
]

# Create card objects
cards = []
x = MARGIN
y = MARGIN
for image in shuffle_cards(images):
    card = Card(x, y, image)
    cards.append(card)
    x += CARD_WIDTH + MARGIN
    if x + CARD_WIDTH > WIDTH - MARGIN:
        x = MARGIN
        y += CARD_HEIGHT + MARGIN

# Selected cards variables
selected_cards = []

# Game loop (keeps the window open)
running = True
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

while running:
    # Handle events (user input)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for card in cards:
                if card.x < pos[0] < card.x + CARD_WIDTH and card.y < pos[1] < card.y + CARD_HEIGHT:
                    if len(selected_cards) < 2:
                        card.flip()
                        selected_cards.append(card)
                    if len(selected_cards) == 2:
                        if selected_cards[0].image == selected_cards[1].image:
                            # Match found
                            selected_cards[0].set_match(selected_cards[1])
                        else:
                            # No match, flip back later
                            pygame.time.delay(1000)
                            for card in selected_cards:
                                card.flip()
                        selected_cards = []

    # Clear the screen
    screen.fill(GRAY)

    # Draw the game board (cards)
    for card in cards:
        card.draw()

    # Check for win condition
    win = True
    for card in cards:
        if not card.flipped or not card.match:
            win = False
            break

    if win:
        text = font.render("You win!", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    # Update the display (refresh the window)
