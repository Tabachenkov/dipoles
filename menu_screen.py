import pygame
import sys
from button import Button
import webbrowser
import numpy as np
from authors_screen import AuthorsScreen
from demo_screen import DemoScreen


import os

# Получить путь к ресурсу
def resource_path(relative_path):
    """ Получить путь к ресурсам, поддерживается работа из .exe """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class MenuScreen():
    def __init__(self, app):
        self.app = app
        self.scale = self.app.scale
        self.screen = app.screen
        self.bg_color = (255, 255, 255)
        self.font = 'corbel'
        self.little_font = pygame.font.SysFont(self.font, int(35 * self.app.scale[1]))
        self.middle_font = pygame.font.SysFont(self.font, int(40 * self.app.scale[1]), bold=True)
        self.big_font = pygame.font.SysFont(self.font, int(50 * self.app.scale[1]))
        self.msu_name = "Московский Государственный Университет им. М.В. Ломоносова"
        self.faculty_name = "Факультет вычислительной математики и кибернетики"
        self.demonstration_label = "Компьютерная демонстрация по курсу"
        self.subject_name = "Статистическая физика"
        self.demonstration_name = "Взаимодействие диполей"
        self.demonstration_name_2 = "в окружении идеального газа"
        self.strings = [self.msu_name, self.faculty_name, self.demonstration_label, self.subject_name,
                        self.demonstration_name, self.demonstration_name_2]
        self.eng_strings = ["Lomonosov Moscow State University", "Faculty of Computational Mathematics and Cybernetics",
                            "Computer demonstration of the course", "Statistical physics", "Dipoles' interaction",
                            "in an ideal gas environment"]
        self.positions = [(400, 100), (500, 150), (700, 250), (800, 300), (730, 400), (710, 470)]
        self.eng_positions = [(650, 100), (500, 150), (700, 250), (830, 300), (790, 400), (730, 470)]
        self.cmc_logo = pygame.transform.scale(pygame.image.load(resource_path("pictures/cmc_logo.jpg")), np.array((140, 140)) * np.array(self.scale))
        self.msu_logo = pygame.transform.scale(pygame.image.load(resource_path("pictures/msu_logo.jpg")), np.array((150, 150)) * np.array(self.scale))
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
            self.screen.blit(surface, np.array(self.positions[index] if self.app.russian else self.eng_positions[index]) * np.array(self.scale))
        self.screen.blit(self.cmc_logo, np.array((1600, 80)) * np.array(self.scale))
        self.screen.blit(self.msu_logo, np.array((180, 80)) * np.array(self.scale))
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