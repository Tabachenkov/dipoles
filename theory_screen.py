import pygame
import sys
from button import Button
import numpy as np
from demo_screen import DemoScreen

class TheoryScreen():
    def __init__(self, app):
        self.app = app
        self.scale = app.scale
        self.screen = app.screen
        self.bg_color = (255, 255, 255)
        self.font = 'corbel'
        self.little_font = pygame.font.SysFont(self.font, int(35 * self.app.scale[1]))
        self.middle_font = pygame.font.SysFont(self.font, int(50 * self.app.scale[1]), bold=True)
        self.big_font = pygame.font.SysFont(self.font, int(50  * self.app.scale[1]))
        self.strings = ["Теория к демонстрации"]
        self.eng_strings = ["Theory for demonstration"]
        self.russian = app.russian
        
        self.text_positions = np.array(((700, 50),))

        self.eng_text_positions = np.array(((700, 50),))
        
        self.theory_pictures = [pygame.transform.scale(pygame.image.load("th1.png"), (908, 596)),
                                pygame.transform.scale(pygame.image.load("th2.png"), (908, 596)),
                                pygame.transform.scale(pygame.image.load("th3.png"), (908, 596)),
                                pygame.transform.scale(pygame.image.load("th4.png"), (908, 596)),
                                pygame.transform.scale(pygame.image.load("th5.png"), (908, 596))]

        self.active_picture = 0
        self.pictures_positions = [(1600 * self.app.scale[0], 80 * self.app.scale[1]), 
                                   (1600 * self.app.scale[0], 80 * self.app.scale[1]), 
                                   (1600 * self.app.scale[0], 80 * self.app.scale[1]), 
                                   (1600 * self.app.scale[0], 80 * self.app.scale[1]),
                                   (1600 * self.app.scale[0], 80 * self.app.scale[1])]
        
        self.theory_positions = ((250, 130), (250, 130), (250, 130), (250, 130), (320, 130), (320, 130))

        self.buttons = [Button(app, "Назад", (1400, 960), (300, 80)), Button(app, "RUS/ENG", (1710, 980), (170, 70), font_size=30), 
                        Button(app, "<", (750, 920), (70, 70)), Button(app, ">", (1150, 920), (70, 70))]
    
    def _update_screen(self):
        self.screen.fill(self.bg_color)
        self.strings_surfaces = []
        self.buttons[:2] = [Button(self.app, "Назад" if self.app.russian else "Back", (1350, 920), (300, 80)), Button(self.app, "RUS/ENG", (1710, 920), (170, 70), font_size=30)]
        for index, string in enumerate(self.strings if self.app.russian else self.eng_strings):
            if index < 2:
                self.strings_surfaces.append(self.middle_font.render(string, False, (0, 0, 0)))
            else:
                self.strings_surfaces.append(self.little_font.render(string, False, (0, 0, 0)))

        for index, surface in enumerate(self.strings_surfaces):
            self.screen.blit(surface, (self.text_positions[index] if self.app.russian else self.eng_text_positions[index]) * np.array(self.scale))

        self.screen.blit(self.little_font.render(f"Страница {self.active_picture + 1} из {len(self.theory_pictures)}" if self.app.russian 
                                                 else f"Page {self.active_picture + 1} of {len(self.theory_pictures)}", 
                                                 False, (0, 0, 0)), (np.array((870, 950)) if self.app.russian else np.array((900, 950))) * np.array(self.scale))

        self.screen.blit(self.theory_pictures[self.active_picture], self.theory_positions[self.active_picture])

        for button in self.buttons:
            button.draw_button()
    
    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                self._check_buttons(mouse_position)
    
    def _check_buttons(self, mouse_position):
        for index, button in enumerate(self.buttons):
            if button.rect.collidepoint(mouse_position):
                if index == 0:
                    self.app.active_screen = self.app.menu_screen
                if index == 1:
                    self.app.russian = not self.app.russian
                    #self.app.menu_screen = MenuScreen(self.app)
                    self.app.demo_screen = DemoScreen(self.app)
                if index == 3:
                    self.active_picture = min(self.active_picture + 1, len(self.theory_pictures) - 1)
                if index == 2:
                    self.active_picture = max(0, self.active_picture - 1)