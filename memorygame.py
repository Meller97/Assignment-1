from vosk import Model, KaldiRecognizer
import os
import sys
import json
import pyaudio
import pygame
import pygame.transform
import random
import time


    
class Button:
    def __init__(self, x, y, width, height, text='', disabled = False, click_sound = "click.mp3", image=None, color = (255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color  # Default color: white
        self.text_color = (0, 0, 0)   # Text color: black
        self.font = pygame.font.Font(None, 32)  # Default font
        self.disabled = disabled # check if the button clickable'
        self.click_sound = pygame.mixer.Sound(click_sound)
        self.image = pygame.image.load(image) if image else None

    def get_text(self):
        return self.text
    
    def button_disable(self):
        self.disabled = True
        self.color = (200, 200, 200)
        self.text_color = (70, 70, 70)
    
    def button_enable(self):
        self.disabled = False
        self.color = (255, 255, 255)
        self.text_color = (0, 0, 0)
    
    def draw(self, screen):
        # Draw the button
        pygame.draw.rect(screen, self.color, self.rect, 0, 10)
        if self.image:
            # Resize image to fit the button
            image_surface = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
            screen.blit(image_surface, self.rect)
        elif self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            # Center the text on the button
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
    
    def is_clicked(self, event_pos):
        if self.disabled:
            return False
        else:
            check_click = self.rect.collidepoint(event_pos)
            if check_click:
                self.click_sound.play()
            return check_click

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
        text_rect = text_surface.get_rect(center=(self.menu_width // 2, 80))

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
            pygame.draw.rect(screen, (72.9, 72.2, 42.4), [0, 0, self.menu_width, self.menu_height])
        self.update_and_draw_pulsing_text(screen)
        for button in self.buttons:
            button.draw(screen)

class Player:
    def __init__(self, player_number, score=0, color = (0,0,0)):
        self.player_number = player_number
        self.score = score
        self.color = color

    def update_score(self, points):
        # Add points to the player's score
        self.score += points

    def reset_score(self):
        # Reset the player's score to zero
        self.score = 0

class MemoryGame:
    def __init__(self, game_mode = 1):
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
        self.Lose_sound = pygame.mixer.Sound('Lose.wav')
        self.flip_sound = pygame.mixer.Sound('flip_sound.wav')
        self.start_sound = pygame.mixer.Sound('IDF.mp3')
        self.gray = (128, 128, 128)

        # Load the Vosk model
        self.model_path = "vosk-model-small-en-us-0.15"
        if not os.path.exists(self.model_path):
            exit(1)
        self.model = Model(self.model_path)
        self.stream_start = False
        self.number_words = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
                        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
                        'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
                        'nineteen': 19, 'twenty': 20}

        # Game variables
        self.grid_size = (4, 4)
        self.rect_width = 600 // self.grid_size[0]
        self.rect_height = 400 // self.grid_size[1]
        self.rects = [pygame.Rect(x * self.rect_width + 60, y * self.rect_height + 60, self.rect_width - 20, self.rect_height - 20)
                      for x in range(self.grid_size[0]) for y in range(self.grid_size[1])]
        self.is_fliping = [False] * self.grid_size[0] * self.grid_size[1]
        # random.shuffle(self.colors)
        self.revealed = [False] * len(self.rects)
        self.selected = []
        self.selected_for_help = []
        self.matched = []
        self.game_end = False
        self.waiting_to_hide = False
        self.waiting_to_hide_help = False
        self.last_check_time = 0
        #self.restart_button = pygame.Rect(10, self.screen_height - 40, 100, 20)
        # mode menu endle
        self.main_menu = Menu("IDF memory game", self.screen_width, self.screen_height, self.screen_width/20, self.screen_height/3,200, 50)
        self.main_menu.add_button("Time Attack")
        self.main_menu.add_button("1 Player")
        self.main_menu.add_button("2 Players")
        self.voice_button = Button(self.screen_width/20 + 210, self.screen_height/3 +60, 200, 50, 'Voice Control')
        self.main_menu.add_button(None, self.voice_button)
        self.in_main_menu = True


        # flip array to store the stage in the flip for every tile when 0 is face down and 10 is face up
        self.flip_arry = [0]*(self.grid_size[0]*self.grid_size[1])

        # attack mode
        self.time_attack_mode = False
        self.time_limit = 60  # Starting time limit for Time Attack mode

        self.rest_button = Button(10, self.screen_height - 40, 100, 30, 'reset')
        self.help_button = Button(200, 20, 300, 30, 'help', False, "Lose.wav",'helper.png')
        self.play_again_button = Button(self.screen_width/2 -100, self.screen_height-100, 200, 100, 'play again')
        self.Mute_button = Button(self.screen_width-40, 10, 30, 30, 'Mute', False, "click.mp3", "mute.png", (72.9, 72.2, 42.4))
        self.win_menu =Menu("Well done!", self.screen_width, self.screen_height, self.screen_width/2, self.screen_height/2,200, 100)
        self.win_menu.add_button(None, self.play_again_button)
        self.help = False
        self.is_mute = False
        self.sound_paused = False
        self.help_timer = 0

        # players endle
        self.game_mode = game_mode
        self.voice_control_mode = False
        self.current_player = Player(0)
        self.players  = [self.current_player]
        

         # Load images
        #image_paths = ['1.png', '2.png']
        self.image_paths = ['1.png', '2.png', '3.png', '4.png', '5.png', '6.png', '7.png', '8.png']
        self.images = [pygame.transform.scale(pygame.image.load(path), (10, self.rect_height - 20)) for path in self.image_paths] * 2
        self.images1 = [pygame.transform.scale(pygame.image.load(path), (self.rect_width - 80, self.rect_height - 20)) for path in self.image_paths] * 2
        self.images2 = [pygame.transform.scale(pygame.image.load(path), (self.rect_width - 40, self.rect_height - 20)) for path in self.image_paths] * 2
        self.images3 = [pygame.transform.scale(pygame.image.load(path), (self.rect_width - 20, self.rect_height - 20)) for path in self.image_paths] * 2
        self.image_stage =[0]*16
        
        # Zip the lists to combine corresponding elements from each list into tuples
        self.combined_images = list(zip(self.images, self.images1, self.images2, self.images3, self.image_stage))

        # Since zip creates tuples, convert each tuple to a list
        self.combined_images = [list(group) for group in self.combined_images]
        random.shuffle(self.combined_images)
        random.shuffle(self.images)
        

        # Timer
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_ticks = pygame.time.get_ticks() - self.start_ticks
        self.font = pygame.font.Font("digital-7.ttf", 36)

    def draw_backgrounds(self, transparent = None):
        if transparent:
            pygame.draw.rect(transparent, self.gray, [0, 0, self.screen_width, self.screen_height])
        else:
            pygame.draw.rect(self.screen, (72.9, 72.2, 42.4), [0, 0, self.screen_width, self.screen_height])
        # pygame.draw.rect(self.screen, self.gray, [0, 0, self.screen_width, 50])
        # pygame.draw.rect(self.screen, self.gray, [0, 50, self.screen_width, self.screen_height - 100])
        # pygame.draw.rect(self.screen, self.gray, [0, self.screen_height - 50, self.screen_width, 50])


    def draw_board(self):
        for i, rect in enumerate(self.rects):
            if self.revealed[i] or i in self.matched:
                if not self.is_fliping[i]:
                    # flip revealed tile
                    if self.combined_images[i][len(self.combined_images[i])-1] < (len(self.combined_images[i])-1)*100:
                        self.screen.blit(self.combined_images[i][int((self.combined_images[i][len(self.combined_images[i])-1])/100)], rect.topleft)
                        jump = 1
                        if self.voice_control_mode == True:
                            jump = 50
                        self.combined_images[i][len(self.combined_images[i])-1] += jump
                    else:
                        self.screen.blit(self.combined_images[i][len(self.combined_images[i])-2], rect.topleft)
                else:
                    self.is_fliping[i] = False
            else:
                self.combined_images[i][len(self.combined_images[i])-1] = 0
                # Draw a black rectangle (or some background) for hidden tiles
                pygame.draw.rect(self.screen, self.current_player.color, rect, 0, 10)
                text_surface = self.font.render(str(i+1), True, (255, 255, 255))
                # Center the text on the button
                text_rect = text_surface.get_rect(center=rect.center)
                self.screen.blit(text_surface, text_rect)

        self.rest_button.draw(self.screen)
        self.help_button.draw(self.screen)

    #def win_menu(self):
        # self.draw_backgrounds()
        #self.play_again_button.draw(self.screen)

    def add_player(self):
        if self.game_mode ==2:
            self.players.append(Player(1, 0,(255, 0, 0)))
            self.players[0].color = (0, 0, 255)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.in_main_menu:
                    if self.Mute_button.is_clicked(event.pos):
                        if(not self.sound_paused):
                            self.is_mute = True
                        else:
                            self.is_mute = False
                    if self.main_menu.button_is_clicked("Time Attack", event.pos):
                        self.game_mode = 1  # Assuming single player for Time Attack
                        self.time_attack_mode = True
                        self.time_limit = 60  # Reset time limit for the first round
                        self.in_main_menu = False
                    elif self.main_menu.button_is_clicked("1 Player",event.pos):
                        self.game_mode = 1
                        self.time_attack_mode = False
                        self.in_main_menu = False
                    elif self.main_menu.button_is_clicked("2 Players",event.pos):
                        self.game_mode = 2
                        self.add_player()
                        self.time_attack_mode = False
                        self.in_main_menu = False
                    # Check if Voice Control button is clicked
                    elif self.main_menu.button_is_clicked("Voice Control", event.pos):
                        self.game_mode = 1
                        self.time_attack_mode = False
                        self.in_main_menu = False
                        self.voice_control_mode = True
                elif not self.game_end and self.help_button.is_clicked(event.pos):
                    self.help_button.button_disable()
                    self.reveal_a_pair()
                elif self.game_end and self.win_menu.button_is_clicked('play again',event.pos):
                    self.time_attack_mode = False
                    self.restart_game()
                elif not self.game_end and self.rest_button.is_clicked(event.pos):
                    self.time_attack_mode = False
                    self.restart_game()
                elif not self.game_end and len(self.selected) < 2 and not self.waiting_to_hide:
                    self.handle_click(event.pos)
        return True

    def restart_game(self):
        self.revealed = [False] * len(self.rects)
        self.selected = []
        self.matched = []
        self.game_end = False
        self.waiting_to_hide = False
        self.voice_control_mode = False
        if not self.time_attack_mode:
            self.in_main_menu = True
        self.current_player = Player(0)
        self.players  = [self.current_player]
        self.last_check_time = 0
        random.shuffle(self.combined_images)
        random.shuffle(self.images)
        self.help_button.button_enable()
        self.current_player = self.players[0]
        # Timer
        self.start_ticks = pygame.time.get_ticks()
        if self.time_attack_mode:
            self.time_limit = max(10, self.time_limit - 5)  # Example: decrease time limit, but no less than 10 seconds
            self.start_ticks = pygame.time.get_ticks()  # Reset the timer

    def handle_click(self, pos):
        for i, rect in enumerate(self.rects):
            if rect.collidepoint(pos) and i not in self.matched and i not in self.selected:
                self.selected.append(i)
                self.revealed[i] = True
                self.is_fliping[i] = True
                self.flip_sound.play()
                if len(self.selected) == 2:
                    self.check_match()

    def check_match(self):
        if self.combined_images[self.selected[0]][0] != self.combined_images[self.selected[1]][0]:
            self.waiting_to_hide = True
            self.last_check_time = time.time()
            self.current_player = self.players[(self.current_player.player_number + 1) % self.game_mode]
        else:
            self.match_sound.play()
            self.matched.extend(self.selected)
            self.selected = []
    
    def check_match_help(self):
        self.waiting_to_hide_help = True
        self.last_check_time = time.time()

    def hide_non_matches(self):
        if time.time() - self.last_check_time >= 0.5:
            for i in self.selected:
                self.revealed[i] = False
            self.selected = []
            self.waiting_to_hide = False

    def hide_non_matches_help(self):
        if time.time() - self.last_check_time >= 0.9:
            for i in self.selected_for_help:
                self.revealed[i] = False
            self.selected_for_help = []
            self.waiting_to_hide_help = False

    def check_win_condition(self):
        if len(self.matched) == len(self.rects) and not self.game_end:
            if self.time_attack_mode:
                # Logic to restart the game with a shorter time limit
                self.restart_game()
            else:
                self.game_end = True

    def reveal_a_pair(self):
        # Find a pair that has not been revealed or matched yet
        for i, image1 in enumerate(self.combined_images):
            if not self.revealed[i] and i not in self.matched:
                for j, image2 in enumerate(self.combined_images):
                    if i != j and image1[0] == image2[0] and not self.revealed[j] and j not in self.matched:
                        # Temporarily reveal the pair
                        self.revealed[i] = True
                        self.revealed[j] = True
                        self.flip_sound.play()

                        self.selected_for_help.append(i)
                        self.selected_for_help.append(j)
                        self.check_match_help()
                        

                        return  # Exit after revealing one pair

    def voice_control_start(self):
        # Setup for voice recognition
        rec = KaldiRecognizer(self.model, 16000)
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()
        self.stream_start = True

        #print("Voice control mode started. Say a card number to flip...")
        return rec, stream


    def voice_control_read(self, stream, rec):
        data = stream.read(4000, exception_on_overflow=False)
        if len(data) == 0:
            return
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            #print(result)
            if 'text' in result:
                try:
                    card_number = self.number_words.get(result['text'].lower(), None)

                    if card_number is not None and 1 <= card_number <= len(self.rects):
                        self.handle_click(self.number_to_tile_pos(card_number))
                except ValueError:
                    pass

    def number_to_tile_pos(self, tile_number):
        for i, rect in enumerate(self.rects):
            if(tile_number == i+1):
                return rect.center

    def display_timer(self):
        if not self.game_end:
            self.elapsed_ticks = pygame.time.get_ticks() - self.start_ticks
        elapsed_seconds = self.elapsed_ticks // 1000
        timer_text = f'Time: {elapsed_seconds // 60}:{elapsed_seconds % 60:02}'
        timer_surface = self.font.render(timer_text, True, (0, 255, 0))
        self.screen.blit(timer_surface, (5, 5))

    def display_time_attack_timer(self):
        if self.time_attack_mode:
            remaining_time = self.time_limit - (pygame.time.get_ticks() - self.start_ticks) // 1000
            if remaining_time <= 0:
                # Handle game over due to time running out
                self.game_end = True 
                self.Lose_sound.play()
                # Here you could also trigger a transition to show the player's score or a "time's up" message
            timer_text = f'Time Left: {max(0, remaining_time)}'
            if remaining_time <= 10:
                timer_surface = self.font.render(timer_text, True, (255, 0, 0))
            else:
                timer_surface = self.font.render(timer_text, True, (0, 255, 0))
            self.screen.blit(timer_surface, (5, 5))

    def run(self):
        running = True
        while running:
            if self.is_mute:
                if(not self.sound_paused):
                    pygame.mixer.pause()
                    self.sound_paused = True
            else:
                if self.sound_paused:
                    pygame.mixer.unpause()
                    self.sound_paused = False
                    
            self.screen.fill(self.background_color)
            self.draw_backgrounds()
            self.draw_board()
            if self.in_main_menu:
                self.main_menu.draw(self.screen, False)
                self.start_ticks = pygame.time.get_ticks()
                self.start_sound.play()
                self.Mute_button.draw(self.screen)
            else:
                self.start_sound.stop()
            if self.game_end:
                self.win_menu.draw(self.screen, True)

            # handle Voice control feature
            if self.voice_control_mode and len(self.selected) < 2 and not self.waiting_to_hide:
                if not self.stream_start:
                    rec, stream = self.voice_control_start()
                self.voice_control_read(stream, rec)
            running = self.check_events()
            self.check_win_condition()
            if self.waiting_to_hide:
                self.hide_non_matches()
            if self.waiting_to_hide_help:
                self.hide_non_matches_help()
            if not self.in_main_menu:
                if self.time_attack_mode:
                    self.display_time_attack_timer()
                else:
                    self.display_timer()
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    game = MemoryGame()
    game.run()