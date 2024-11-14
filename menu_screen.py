import pygame
import sys
from button import Button
import webbrowser
import numpy as np
from authors_screen import AuthorsScreen
from demo_screen import DemoScreen
class MenuScreen():
    def __init__(self, app):
        self.app = app
        self.scale = self.app.scale
        self.screen = app.screen
        self.bg_color = (255, 255, 255)
        self.font = 'corbel'
        self.little_font = pygame.font.SysFont(self.font, int(35 * self.app.scale))
        self.middle_font = pygame.font.SysFont(self.font, int(40 * self.app.scale), bold=True)
        self.big_font = pygame.font.SysFont(self.font, int(50 * self.app.scale))
        self.msu_name = "Московский Государственный Университет им. М.В. Ломоносова"
        self.faculty_name = "Факультет вычислительной математики и кибернетики"
        self.demonstration_label = "Компьютерная демонстрация по курсу"
        self.subject_name = "Статистическая физика"
        self.demonstration_name = "Взаимодействие диполей"
        self.demonstration_name_2 = "в идеальном газе"
        self.strings = [self.msu_name, self.faculty_name, self.demonstration_label, self.subject_name,
                        self.demonstration_name, self.demonstration_name_2]
        self.eng_strings = ["Lomonosov Moscow State University", "Faculty of Computational Mathematics and Cybernetics",
                            "Computer demonstration of the course", "Statistical physics", "Dipoles' interaction",
                            "in the ideal gas"]
        self.positions = [(400, 100), (500, 150), (700, 250), (800, 300), (730, 400), (810, 470)]
        self.eng_positions = [(650, 100), (500, 150), (700, 250), (830, 300), (790, 400), (830, 470)]
        self.cmc_logo = pygame.transform.scale(pygame.image.load("cmc_logo.jpg"), np.array((140, 140)) * self.scale)
        self.msu_logo = pygame.transform.scale(pygame.image.load("msu_logo.jpg"), np.array((150, 150)) * self.scale)
        self.buttons = [Button(app, "Демонстрация", (750, 600), (400, 80)), 
                        Button(app, "Теория", (750, 700), (400, 80)),
                        Button(app, "Авторы", (750, 800), (400, 80)), 
                         Button(app, "Выход", (750, 900), (400, 80)),
                         Button(app, "RUS/ENG", (1710, 900), (170, 70), font_size=30)]
        self.russian = True

    def _update_screen(self):
        self.buttons = [Button(self.app, "Демонстрация" if self.app.russian else "Demonstration", (750, 600), (400, 80)), 
                        Button(self.app, "Теория" if self.app.russian else "Theory", (750, 700), (400, 80)),
                        Button(self.app, "Авторы" if self.app.russian else "Authors", (750, 800), (400, 80)), 
                         Button(self.app, "Выход" if self.app.russian else "Exit", (750, 900), (400, 80)),
                         Button(self.app, "RUS/ENG", (1710, 900), (170, 70), font_size=30)]
        self.screen.fill(self.bg_color)
        self.strings_surfaces = []
        for index, string in enumerate(self.strings if self.app.russian else self.eng_strings):
            if index < 2:
                self.strings_surfaces.append(self.middle_font.render(string, False, (0, 0, 0)))
            elif index < 4:
                self.strings_surfaces.append(self.little_font.render(string, False, (0, 0, 0)))
            else:
                self.strings_surfaces.append(self.big_font.render(string, False, (0, 0, 0)))
        for index, surface in enumerate(self.strings_surfaces):
            self.screen.blit(surface, np.array(self.positions[index] if self.app.russian else self.eng_positions[index]) * self.scale)
        self.screen.blit(self.cmc_logo, np.array((1600, 80)) * self.scale)
        self.screen.blit(self.msu_logo, np.array((180, 80)) * self.scale)
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
                    self.app.active_screen = self.app.demo_screen
                elif index == 1:
                    self.app.active_screen = self.app.theory_screen
                    #continue
                elif index == 2:
                    self.app.active_screen = self.app.authors_screen
                elif index == 3:
                    sys.exit()
                elif index == 4:
                    self.app.russian = not self.app.russian
                    self.app.authors_screen = AuthorsScreen(self.app)
                    self.app.demo_screen = DemoScreen(self.app)