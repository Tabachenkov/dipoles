import pygame
import sys
from button import Button
from authors_screen import AuthorsScreen
from demo_screen import DemoScreen
from menu_screen import MenuScreen
from theory_screen import TheoryScreen

import ctypes
import os
import sys

if sys.platform == "win32":
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception as e:
        print(f"Ошибка установки DPI: {e}")

class App:
    def __init__(self) -> None:
        pygame.init()
        self.scale = pygame.display.Info().current_w / 1920
        self.screen = pygame.display.set_mode((1920 * self.scale, 1080 * self.scale))
        self.russian = True
        self.menu_screen = MenuScreen(self)
        self.authors_screen = AuthorsScreen(self)
        self.demo_screen = DemoScreen(self)
        self.theory_screen = TheoryScreen(self)
        self.active_screen = self.menu_screen

    def run(self):
        while True:
            self.active_screen._check_events()
            self.active_screen._update_screen()
            pygame.display.flip()

if __name__ == '__main__':
    app = App()
    app.run()