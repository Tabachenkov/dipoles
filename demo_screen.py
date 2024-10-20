import pygame
import sys
from button import Button
import time
from option_box import OptionBox
from input_box import InputBox
import numpy as np
from domain import *
from particles import *
from pygame_plus import *
# from pygame_menu.widgets import RangeSlider
# from pygame_menu import Menu, themes
from pygame_widgets.slider import Slider
import pygame_widgets
from pygame_widgets.textbox import TextBox

NOT_STARTED = 0
PAUSED = 1
ACTIVATED = 2

class DemoScreen():
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.scale = app.scale
        self.speed = 0.5
        self.bg_color = (255, 255, 255)
        self.font = 'corbel'
        self.little_font = pygame.font.SysFont(self.font, int(35 * self.app.scale))
        self.middle_font = pygame.font.SysFont(self.font, int(40 * self.app.scale), bold=True)
        self.big_font = pygame.font.SysFont(self.font, int(50 * self.app.scale))
        self.active_summing = False
        self.step = 1
        self.limit = 200
        self.pause = False
        self.buttons = [Button(self.app, "Начать" if self.app.russian else "Start", (1000, 800), (250, 70), font_size=30),
                        Button(self.app, "Назад" if self.app.russian else "Back", (1300, 900), (250, 70), font_size=30)]
        self.time_check = time.time()
        pygame.draw.rect(self.screen, Color.WHITE.rgb, Rectangle(0, 0, 500, 500), 0)
        pygame.draw.rect(self.screen, Color.BLACK.rgb, Rectangle(0, 0, 500, 500), 1)
        self.mode = NOT_STARTED
        # self.settings = Menu(title="Настройки", width=300, height=300, theme=themes.THEME_GREEN)
        self.slider = Slider(self.screen, x=800, y=100, width=250, height=10, min=0, max=2000, step=1)
        self.textbox = TextBox(self.screen, 910, 120, 30, 15, fontSize=10)
        self.particles_number = 1000
        self.speed = 500
        self.slider_s = Slider(self.screen, x=800, y=200, width=250, height=10, min=1, max=1000, step=1)
        self.textbox_s = TextBox(self.screen, 910, 220, 30, 15, fontSize=10)

    def _check_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                self._check_buttons(mouse_position)
        pygame_widgets.update(events)
        self.slider.listen(events)
        self.slider_s.listen(events)
        self.particles_number = self.slider.getValue()
        self.textbox.listen(events)
        self.textbox_s.listen(events)
        self.textbox.setText(self.slider.getValue())
        self.speed = self.slider_s.getValue()
        self.textbox_s.setText(self.slider_s.getValue())

    def _update_screen(self):
        if self.mode == ACTIVATED:
            self.buttons = [Button(self.app, "Завершить" if self.app.russian else "Finish", (1000, 800), (250, 70), font_size=30),
                            Button(self.app, "Остановить" if self.app.russian else "Stop", (1300, 800), (250, 70), font_size=30),
                            Button(self.app, "Назад" if self.app.russian else "Back", (1300, 900), (250, 70), font_size=30)]
            self.screen.fill(self.bg_color)
            pygame.draw.rect(self.screen, Color.WHITE.rgb, Rectangle(0, 0, 500, 500), 0)
            pygame.draw.rect(self.screen, Color.BLACK.rgb, Rectangle(0, 0, 500, 500), 1)
            res = self.particle_system.proceed(0.01)
            if res:
                self.particle_system.set_average_speed(self.speed)
                if self.particle_system.count > 0:
                    for particle in self.particle_system.entities:
                        pygame_draw_filled_circle(
                            surface=self.screen,
                            pos=Position(
                                x=int(particle[0]),
                                y=int(particle[1])
                            ),
                            radius=int(self.particle_system.radius),
                            color=Color.GREEN
                        )
                for i in range(2):
                    cos = math.cos(self.particle_system.dipoles[i].actangle)
                    sin = math.sin(self.particle_system.dipoles[i].actangle)
                    pos0 = self.particle_system.dipoles[i].pos + 15.0 * np.array([cos, sin])
                    pos1 = self.particle_system.dipoles[i].pos - 15.0 * np.array([cos, sin])
                    pygame_draw_filled_circle(
                        surface=self.screen,
                        pos=Position(
                            x=int(pos0[0]),
                            y=int(pos0[1])
                        ),
                        radius=int(self.particle_system.d_radius),
                        color=Color.BLUE
                    )
                    pygame_draw_filled_circle(
                        surface=self.screen,
                        pos=Position(
                            x=int(pos1[0]),
                            y=int(pos1[1])
                        ),
                        radius=int(self.particle_system.d_radius),
                        color=Color.RED
                    )
                    pygame.draw.line(self.screen, Color.BLACK, (pos0[0], pos0[1]),
                                    (pos1[0], pos1[1]))
            else:
                self.mode = NOT_STARTED
        elif self.mode == PAUSED:
            self.buttons = [Button(self.app, "Завершить" if self.app.russian else "Finish", (1000, 800), (250, 70), font_size=30),
                            Button(self.app, "Возобновить" if self.app.russian else "Continue", (1300, 800), (250, 70), font_size=30),
                            Button(self.app, "Назад" if self.app.russian else "Back", (1300, 900), (250, 70), font_size=30)]
            self.screen.fill(self.bg_color)
            pygame.draw.rect(self.screen, Color.WHITE.rgb, Rectangle(0, 0, 500, 500), 0)
            pygame.draw.rect(self.screen, Color.BLACK.rgb, Rectangle(0, 0, 500, 500), 1)
            if self.particle_system.count > 0:
                for particle in self.particle_system.entities:
                    pygame_draw_filled_circle(
                        surface=self.screen,
                        pos=Position(
                            x=int(particle[0]),
                            y=int(particle[1])
                        ),
                        radius=int(self.particle_system.radius),
                        color=Color.GREEN
                    )
            for i in range(2):
                cos = math.cos(self.particle_system.dipoles[i].actangle)
                sin = math.sin(self.particle_system.dipoles[i].actangle)
                pos0 = self.particle_system.dipoles[i].pos + 15.0 * np.array([cos, sin])
                pos1 = self.particle_system.dipoles[i].pos - 15.0 * np.array([cos, sin])
                pygame_draw_filled_circle(
                    surface=self.screen,
                    pos=Position(
                        x=int(pos0[0]),
                        y=int(pos0[1])
                    ),
                    radius=int(self.particle_system.d_radius),
                    color=Color.BLUE
                )
                pygame_draw_filled_circle(
                    surface=self.screen,
                    pos=Position(
                        x=int(pos1[0]),
                        y=int(pos1[1])
                    ),
                    radius=int(self.particle_system.d_radius),
                    color=Color.RED
                )
                pygame.draw.line(self.screen, Color.BLACK, (pos0[0], pos0[1]),
                                (pos1[0], pos1[1]))
        else:
            self.buttons = [Button(self.app, "Начать" if self.app.russian else "Start", (1000, 800), (250, 70), font_size=30),
                        Button(self.app, "Назад" if self.app.russian else "Back", (1300, 900), (250, 70), font_size=30)]
            self.screen.fill(self.bg_color)
            pygame.draw.rect(self.screen, Color.WHITE.rgb, Rectangle(0, 0, 500, 500), 0)
            pygame.draw.rect(self.screen, Color.BLACK.rgb, Rectangle(0, 0, 500, 500), 1)
        for button in self.buttons:
            button.draw_button()
        self.slider.draw()
        self.textbox.draw()
        self.slider_s.draw()
        self.textbox_s.draw()
        #self.slider = Slider(self.screen, x=800, y=500, width=250, height=70, min=0, max=2000, step=1)

    def _check_buttons(self, mouse_position):
        for index, button in enumerate(self.buttons):
            if button.rect.collidepoint(mouse_position):
                if button.msg == 'Назад' or button.msg == 'Back':
                    self.app.active_screen = self.app.menu_screen
                elif button.msg == 'Начать' or button.msg == 'Start':
                    self.mode = ACTIVATED
                    self.particle_system = ParticleSystem(self.particles_number, 1.0, max_width=500, max_height=500, avg_vel=1000, d_radius=5.0, r=15.0)
                elif button.msg == 'Остановить' or button.msg == 'Stop':
                    self.mode = PAUSED
                elif button.msg == 'Возобновить' or button.msg == 'Continue':
                    self.mode = ACTIVATED
                elif button.msg == 'Завершить' or button.msg == 'Finish':
                    self.mode = NOT_STARTED
                
        