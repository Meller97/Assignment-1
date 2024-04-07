if 49 < self.flip_arry[i] < 110:
                        rect.width += 2.1
                        self.flip_arry[i] += 1
                        self.images[i] = pygame.transform.scale(self.images[i], (rect.width, rect.height))
                        self.screen.blit(self.images[i], rect.topleft)
                    elif 0 < self.flip_arry[i] < 50:
                        rect.width -= 2.1
                        self.flip_arry[i] += 1
                        pygame.draw.rect(self.screen, self.current_player.color, rect, 0, 10)
                        text_surface = self.font.render(str(i+1), True, (255, 255, 255))
                        text_rect = text_surface.get_rect(center=rect.center)
                        self.screen.blit(text_surface, text_rect)
                    elif self.flip_arry[i] == 110:
                        rect.width = 130
                        self.screen.blit(self.images[i], rect.topleft)
                    elif self.flip_arry[i] == 0:
                        rect.width = 130
                        pygame.draw.rect(self.screen, self.current_player.color, rect, 0, 10)
                        text_surface = self.font.render(str(i+1), True, (255, 255, 255))
                        # Center the text on the button
                        text_rect = text_surface.get_rect(center=rect.center)
                        self.screen.blit(text_surface, text_rect)
                        self.flip_arry[i] += 1