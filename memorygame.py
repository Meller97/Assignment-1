import pygame
import random
import time

class Button:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (255, 255, 255)  # Default color: white
        self.text_color = (0, 0, 0)   # Text color: black
        self.font = pygame.font.Font(None, 32)  # Default font

    def get_text(self):
        return self.text
    
    def draw(self, screen):
        # Draw the button
        pygame.draw.rect(screen, self.color, self.rect, 0, 10)
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            # Center the text on the button
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
    
    def is_clicked(self, event_pos):
        return self.rect.collidepoint(event_pos)

class Menu:
    def __init__(self, moving_text, menu_width, menu_height, x, y, width, height, gap=10, background_alpha=200):
        self.moving_text = moving_text
        self.buttons = []
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.menu_width = menu_width
        self.menu_height = menu_height
        self.gap = gap  # Space between buttons
        self.background_alpha = background_alpha  # Alpha for semi-transparent background

        # Create a surface with per-pixel alpha
        self.surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        self.surface.fill((128, 128, 128, self.background_alpha))  # Semi-transparent background

        # Moving text attributes
        self.moving_text_color = (255, 255, 0)  # Yellow color
        self.moving_text_position = [0, menu_height // 2]  # Starting position of the text
        self.moving_text_speed = 0.5  # Pixels per frame
        self.font = pygame.font.Font(None, 32)  # You can use the same font as buttons or a different one

        self.pulsing_text_color = (255, 255, 0)  # Yellow color
        self.pulsing_text_size = 32
        self.pulsing_text_min_size = 24
        self.pulsing_text_max_size = 100
        self.pulsing_text_size_change = 0.07

    def add_button(self, text = None, button = None):
        # Calculate the position of the new button
        if button is not None:
            new_button = button
        else:
            if not self.buttons:
                new_x = self.x
            else:
                last_button = self.buttons[-1]
                new_x = last_button.rect.right + self.gap
            # Create a new button
            new_button = Button(new_x, self.y, self.width, self.height, text)
        self.buttons.append(new_button)
    
    def button_is_clicked(self, text, event_pos):
        for button in self.buttons:
            if button.get_text() == text:
                return button.is_clicked(event_pos)

    def update_and_draw_pulsing_text(self, screen):
        # Update font size
        self.pulsing_text_size += self.pulsing_text_size_change
        if self.pulsing_text_size > self.pulsing_text_max_size or self.pulsing_text_size < self.pulsing_text_min_size:
            self.pulsing_text_size_change *= -1  # Reverse the direction of size change

        # Create text surface with updated size
        font = pygame.font.Font(None, int(self.pulsing_text_size))
        text_surface = font.render(self.moving_text, True, self.pulsing_text_color)
        text_rect = text_surface.get_rect(center=(self.menu_width // 2, self.menu_height // 2))

        # Draw the text
        screen.blit(text_surface, text_rect)

    def update_and_draw_moving_text(self, screen):
        text_surface = self.font.render(self.moving_text, True, self.moving_text_color)
        text_rect = text_surface.get_rect(center=self.moving_text_position)

        # Draw the text on the screen
        screen.blit(text_surface, text_rect)

        # Update the position for the next frame
        self.moving_text_position[0] += self.moving_text_speed
        if self.moving_text_position[0] > screen.get_width():
            self.moving_text_position[0] = -text_rect.width  # Reset position to start from the left again


    def draw(self, screen, is_transparent):
        if is_transparent:
            # Blit the semi-transparent menu surface to the screen
            screen.blit(self.surface, (0, 0))
        else:
            pygame.draw.rect(screen, (128,128,128), [0, 0, self.menu_width, self.menu_height])
        self.update_and_draw_pulsing_text(screen)
        for button in self.buttons:
            button.draw(screen)

class MemoryGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Screen dimensions
        self.screen_width = 700
        self.screen_height = 500
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.background_color = (255, 255, 255)
        
        # Colors and sounds
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)] * 2
        self.match_sound = pygame.mixer.Sound('Win.wav')
        self.flip_sound = pygame.mixer.Sound('flip_sound.wav')
        self.gray = (128, 128, 128)


        # Game variables
        self.grid_size = (2, 2)
        self.rect_width = 600 // self.grid_size[0]
        self.rect_height = 400 // self.grid_size[1]
        self.rects = [pygame.Rect(x * self.rect_width + 60, y * self.rect_height + 60, self.rect_width - 20, self.rect_height - 20)
                      for x in range(self.grid_size[0]) for y in range(self.grid_size[1])]
        # random.shuffle(self.colors)
        self.revealed = [False] * len(self.rects)
        self.selected = []
        self.matched = []
        self.game_end = False
        self.waiting_to_hide = False
        self.last_check_time = 0
        #self.restart_button = pygame.Rect(10, self.screen_height - 40, 100, 20)
        self.rest_button = Button(10, self.screen_height - 40, 100, 30, 'rest')
        self.play_again_button = Button(self.screen_width/2 -100, self.screen_height-100, 200, 100, 'play again')
        self.win_menu =Menu("Well done!", self.screen_width, self.screen_height, self.screen_width/2, self.screen_height/2,200, 100)
        self.win_menu.add_button(None, self.play_again_button)


         # Load images
        image_paths = ['1.png', '2.png']
        # image_paths = ['1.png', '2.png', '3.png', '4.png', '5.png', '6.png', '7.png', '8.png']
        self.images = [pygame.transform.scale(pygame.image.load(path), (self.rect_width - 20, self.rect_height - 20)) for path in image_paths] * 2
        random.shuffle(self.images)

        # Timer
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_ticks = pygame.time.get_ticks() - self.start_ticks
        self.font = pygame.font.Font("digital-7.ttf", 36)

    def draw_backgrounds(self, transparent = None):
        if transparent:
            pygame.draw.rect(transparent, self.gray, [0, 0, self.screen_width, self.screen_height])
        else:
            pygame.draw.rect(self.screen, self.gray, [0, 0, self.screen_width, self.screen_height])
        # pygame.draw.rect(self.screen, self.gray, [0, 0, self.screen_width, 50])
        # pygame.draw.rect(self.screen, self.gray, [0, 50, self.screen_width, self.screen_height - 100])
        # pygame.draw.rect(self.screen, self.gray, [0, self.screen_height - 50, self.screen_width, 50])

    def draw_board(self):
        for i, rect in enumerate(self.rects):
            if self.revealed[i] or i in self.matched:
                self.screen.blit(self.images[i], rect.topleft)
            else:
                # Draw a black rectangle (or some background) for hidden tiles
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 0, 10)
        self.rest_button.draw(self.screen)

    #def win_menu(self):
        # self.draw_backgrounds()
        #self.play_again_button.draw(self.screen)


    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_end and self.win_menu.button_is_clicked('play again',event.pos):
                    self.restart_game()
                elif self.rest_button.is_clicked(event.pos):
                    self.restart_game()
                elif len(self.selected) < 2 and not self.waiting_to_hide:
                    self.handle_click(event.pos)
        return True

    def restart_game(self):
        self.revealed = [False] * len(self.rects)
        self.selected = []
        self.matched = []
        self.game_end = False
        self.waiting_to_hide = False
        self.last_check_time = 0
        random.shuffle(self.images)
        # Timer
        self.start_ticks = pygame.time.get_ticks()

    def handle_click(self, pos):
        for i, rect in enumerate(self.rects):
            if rect.collidepoint(pos) and i not in self.matched and i not in self.selected:
                self.selected.append(i)
                self.revealed[i] = True
                self.flip_sound.play()
                if len(self.selected) == 2:
                    self.check_match()

    def check_match(self):
        if self.images[self.selected[0]] != self.images[self.selected[1]]:
            self.waiting_to_hide = True
            self.last_check_time = time.time()
        else:
            self.match_sound.play()
            self.matched.extend(self.selected)
            self.selected = []

    def hide_non_matches(self):
        if time.time() - self.last_check_time >= 0.5:
            for i in self.selected:
                self.revealed[i] = False
            self.selected = []
            self.waiting_to_hide = False

    def check_win_condition(self):
        if len(self.matched) == len(self.rects) and not self.game_end:
            self.game_end = True

    def display_timer(self):
        if not self.game_end:
            self.elapsed_ticks = pygame.time.get_ticks() - self.start_ticks
        elapsed_seconds = self.elapsed_ticks // 1000
        timer_text = f'Time: {elapsed_seconds // 60}:{elapsed_seconds % 60:02}'
        timer_surface = self.font.render(timer_text, True, (0, 255, 0))
        self.screen.blit(timer_surface, (5, 5))

    def run(self):
        running = True
        while running:
            self.screen.fill(self.background_color)
            self.draw_backgrounds()
            self.draw_board()
            if self.game_end:
                self.win_menu.draw(self.screen, True)
            running = self.check_events()
            self.check_win_condition()
            if self.waiting_to_hide:
                self.hide_non_matches()
            self.display_timer()
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    game = MemoryGame()
    game.run()