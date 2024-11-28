import pygame.font
import numpy as np

class Button:
    def __init__(self, app, msg, position, button_size, font_size=36, font='corbel'):
        """Инициализирует атрибуты кнопки."""
        self.screen = app.screen
        self.screen_rect = self.screen.get_rect()
        self.font = font
        # Назначение размеров и свойств кнопок.
        self.width, self.height = np.array(button_size) * np.array(app.scale)
        self.button_color = (240, 240, 240)
        self.text_color = (0, 0, 0)
        self.font = pygame.font.SysFont(self.font, int(font_size * app.scale[1]), bold=True)
        self.active = False

        # Построение объекта rect кнопки и выравнивание по центру экрана.
        self.rect = pygame.Rect(*(np.array(position) * np.array(app.scale)), self.width, self.height)
        
        # Сообщение кнопки создается только один раз.
        self._prep_msg(msg)
        self.msg = msg

    def _prep_msg(self, msg):
        self.msg_image = self.font.render(msg, True, self.text_color,
                                            self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        # Отображение пустой кнопки и вывод сообщения.
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)