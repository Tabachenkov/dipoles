import pygame as pg
import numpy as np
pg.init()

COLOR_INACTIVE = pg.Color('black')
COLOR_ACTIVE = pg.Color('blue')


class InputBox:

    def __init__(self, x, y, w, h, app, text=''):
        self.rect = pg.Rect(*(np.array((x, y, w, h)) * app.scale))
        self.color = COLOR_INACTIVE
        self.text = text
        self.font = pg.font.SysFont('couriernew', int(35 * app.scale), bold=True)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            save = None
            if self.active:
                if event.key == pg.K_RETURN:
                    save = self.text
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, self.color)
            return save

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+10, self.rect.y +2))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 4)