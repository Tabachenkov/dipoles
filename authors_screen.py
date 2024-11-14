import pygame
import sys
from button import Button
import numpy as np
from demo_screen import DemoScreen
class AuthorsScreen():
    def __init__(self, app):
        self.app = app
        self.scale = app.scale
        self.screen = app.screen
        self.bg_color = (255, 255, 255)
        self.font = 'corbel'
        self.little_font = pygame.font.SysFont(self.font, int(35 * self.app.scale))
        self.middle_font = pygame.font.SysFont(self.font, int(40 * self.app.scale), bold=True)
        self.big_font = pygame.font.SysFont(self.font, int(50  * self.app.scale))
        self.strings = ["Московский Государственный Университет им. М.В. Ломоносова",
                        "Факультет вычислительной математики и кибернетики", 
                        "Лектор: Григорьев Кирилл Сергеевич",
                        "Руководитель: Чичигина Ольга Александровна",
                        "Табаченков Андрей",
                        "Ильясов Эрик"]
        self.eng_strings = ["Lomonosov Moscow State University",
                            "Faculty of Computational Mathematics and Cybernetics",
                            "Lecturer: Grigoriev Kirill Sergeevich",
                            "Head: Olga Alexandrovna Chichigina",
                            "Tabachenkow Andrei",
                            "Ilyassov Erik"]
        self.russian = app.russian
        
        self.text_positions = np.array(((400, 100), (500, 150), (670, 850), (600, 790), (395, 720), (1270, 720)))

        self.eng_text_positions = np.array(((650, 100), (500, 150), (720, 850), (710, 790), (395, 720), (1270, 720)))
        
        self.pictures = [pygame.transform.scale(pygame.image.load("cmc_logo.jpg"), 
                                                (140 * self.app.scale, 140 * self.app.scale)),
                         pygame.transform.scale(pygame.image.load("msu_logo.jpg"), 
                                                (150 * self.app.scale, 150 * self.app.scale)),
                         pygame.transform.scale(pygame.image.load("andrei.jpg"), 
                                                (400 * self.app.scale, 400 * self.app.scale)),
                         pygame.transform.scale(pygame.image.load("eric.jpg"), 
                                                (400 * self.app.scale, 400 * self.app.scale))]
        
        self.pictures_positions = [(1600 * self.app.scale, 80 * self.app.scale), 
                                   (180 * self.app.scale, 80 * self.app.scale), 
                                   (340 * self.app.scale, 300 * self.app.scale), 
                                   (1160 * self.app.scale, 300 * self.app.scale)]
        self.buttons = [Button(app, "Назад", (1300, 900), (300, 80)), Button(app, "RUS/ENG", (1710, 900), (170, 70), font_size=30)]
    
    def _update_screen(self):
        self.screen.fill(self.bg_color)
        self.strings_surfaces = []
        self.buttons = [Button(self.app, "Назад" if self.app.russian else "Back", (1300, 900), (300, 80)), Button(self.app, "RUS/ENG", (1710, 900), (170, 70), font_size=30)]
        for index, string in enumerate(self.strings if self.app.russian else self.eng_strings):
            if index < 2:
                self.strings_surfaces.append(self.middle_font.render(string, False, (0, 0, 0)))
            else:
                self.strings_surfaces.append(self.little_font.render(string, False, (0, 0, 0)))

        for index, surface in enumerate(self.strings_surfaces):
            self.screen.blit(surface, (self.text_positions[index] if self.app.russian else self.eng_text_positions[index]) * self.scale)

        for index, picture in enumerate(self.pictures):
            self.screen.blit(picture, self.pictures_positions[index])

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
                    self.app.demo_screen = DemoScreen(self.app)