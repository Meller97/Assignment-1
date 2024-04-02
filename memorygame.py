import pygame
import random
import time

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
        self.grid_size = (4, 3)
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
        self.restart_button = pygame.Rect(10, self.screen_height - 40, 100, 20)
        self.play_again_button = pygame.Rect(self.screen_width/2, self.screen_height/2, 200, 100)

         # Load images
        image_paths = ['1.png', '2.png', '3.png', '4.png', '5.png', '6.png']
        self.images = [pygame.transform.scale(pygame.image.load(path), (self.rect_width - 20, self.rect_height - 20)) for path in image_paths] * 2
        random.shuffle(self.images)

        # Timer
        self.start_ticks = pygame.time.get_ticks()
        self.font = pygame.font.Font("digital-7.ttf", 36)

    def draw_backgrounds(self):
        pygame.draw.rect(self.screen, self.gray, [0, 0, self.screen_width, 50])
        pygame.draw.rect(self.screen, self.gray, [0, 50, self.screen_width, self.screen_height - 100])
        pygame.draw.rect(self.screen, self.gray, [0, self.screen_height - 50, self.screen_width, 50])

    def draw_board(self):
        for i, rect in enumerate(self.rects):
            if self.revealed[i] or i in self.matched:
                self.screen.blit(self.images[i], rect.topleft)
            else:
                # Draw a black rectangle (or some background) for hidden tiles
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 0, 10)
        pygame.draw.rect(self.screen, (255,255,255), self.restart_button, 0, 10)

    def win_menu(self):
        # self.draw_backgrounds()
        pygame.draw.rect(self.screen, (255,255,255), self.play_again_button, 0, 10)


    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_end and self.play_again_button.collidepoint(event.pos):
                    self.restart_game()
                elif self.restart_button.collidepoint(event.pos):
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
        elapsed_ticks = pygame.time.get_ticks() - self.start_ticks
        elapsed_seconds = elapsed_ticks // 1000
        timer_text = f'Time: {elapsed_seconds // 60}:{elapsed_seconds % 60:02}'
        timer_surface = self.font.render(timer_text, True, (0, 255, 0))
        self.screen.blit(timer_surface, (5, 5))

    def run(self):
        running = True
        while running:
            self.screen.fill(self.background_color)
            self.draw_backgrounds()
            if self.game_end:
                self.win_menu()
            else:
                self.draw_board()
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