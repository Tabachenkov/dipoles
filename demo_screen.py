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
from pygame_widgets.slider import Slider
import pygame_widgets
from pygame_widgets.textbox import TextBox
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('module://pygame_matplotlib.backend_pygame')
plt.rcParams["figure.figsize"] = (10, 5)

NOT_STARTED = 0
PAUSED = 1
ACTIVATED = 2

class DemoScreen():
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.scale = app.scale
        self.bg_color = (255, 255, 255)
        self.font = 'corbel'
        self.little_font = pygame.font.SysFont(self.font, int(30 * self.app.scale))
        self.middle_font = pygame.font.SysFont(self.font, int(40 * self.app.scale), bold=True)
        self.big_font = pygame.font.SysFont(self.font, int(50 * self.app.scale))
        self.buttons = [Button(self.app, "Начать" if self.app.russian else "Start", (1000, 800), (250, 70), font_size=30),
                        Button(self.app, "Назад" if self.app.russian else "Back", (1000, 900), (250, 70), font_size=30),
                        Button(self.app, "RUS/ENG", (1300, 900), (250, 70), font_size=30)]

        self.dipole_colors = [Color.GOLD, Color.BLACK]
        self.dt = 0.01
        self.radius = 1.0
        self.width = 1500
        self.height = 500
        self.d_radius = 5.0
        self.r = 15.0
        self.charge = 1
        self.charge_mass = 1
        self.m = 1

        pygame.draw.rect(self.screen, Color.WHITE.rgb, Rectangle(0, 0, self.width, self.height), 0)
        pygame.draw.rect(self.screen, Color.BLACK.rgb, Rectangle(0, 0, self.width, self.height), 1)

        self.mode = NOT_STARTED
        self.slider = Slider(self.screen, x=1600, y=50, width=250, height=10, min=0, max=2000, initial=0, step=1)
        self.textbox = TextBox(self.screen, 1710, 70, 40, 20, fontSize=10)
        self.particles_number = 1000
        self.speed = 500
        self.slider_s = Slider(self.screen, x=1600, y=150, width=250, height=10, min=1, max=1000, initial=500, step=1)
        self.textbox_s = TextBox(self.screen, 1710, 170, 40, 20, fontSize=10)
        self.slider_dt = Slider(self.screen, x=1600, y=250, width=250, height=10, min=0.005, max=0.1, initial=0.01, step=0.005)
        self.textbox_dt = TextBox(self.screen, 1710, 270, 40, 20, fontSize=10)
        self.slider_radius = Slider(self.screen, x=1600, y=350, width=250, height=10, min=1, max=10, initial=1, step=1)
        self.textbox_radius = TextBox(self.screen, 1710, 370, 40, 20, fontSize=10)
        self.slider_width = Slider(self.screen, x=1600, y=450, width=250, height=10, min=100, max=1500, initial=1500, step=100)
        self.textbox_width = TextBox(self.screen, 1710, 470, 40, 20, fontSize=10)
        self.slider_height = Slider(self.screen, x=1600, y=550, width=250, height=10, min=100, max=500, initial=500, step=100)
        self.textbox_height = TextBox(self.screen, 1710, 570, 40, 20, fontSize=10)
        self.slider_d_radius = Slider(self.screen, x=1600, y=650, width=250, height=10, min=1, max=15, initial=5, step=1)
        self.textbox_d_radius = TextBox(self.screen, 1710, 670, 40, 20, fontSize=10)
        self.slider_r = Slider(self.screen, x=1600, y=750, width=250, height=10, min=15, max=100, initial=15, step=1)
        self.textbox_r = TextBox(self.screen, 1710, 770, 40, 20, fontSize=10)
        self.slider_charge = Slider(self.screen, x=1600, y=850, width=250, height=10, min=1, max=10, initial=1, step=1)
        self.textbox_charge = TextBox(self.screen, 1710, 870, 40, 20, fontSize=10)
        self.slider_charge_mass = Slider(self.screen, x=1600, y=950, width=250, height=10, min=1, max=50, initial=1, step=1)
        self.textbox_charge_mass = TextBox(self.screen, 1710, 970, 40, 20, fontSize=10)
        self.slider_m = Slider(self.screen, x=1000, y=600, width=250, height=10, min=1, max=50, initial=1, step=1)
        self.textbox_m = TextBox(self.screen, 1000, 620, 40, 20, fontSize=10)

        self.strings = ["Количество частиц", "Средняя скорость частиц", "dt, сек.", 
        "Радиус частицы", "Ширина", "Высота", "Радиус заряда", "Расстояние между зарядами", "Величина заряда",
        "Масса заряда", "Масса частицы",
        "Средняя кин. энергия 1 диполя: 0", "Стандартное отклонение кин. энергии 1 диполя",
        "Средняя кин. энергия 2 диполя: 0", "Стандартное отклонение кин. энергии 2 диполя"]
        self.eng_strings = ["Number of particles", "Average speed of particles", "dt, sec.", 
        "Particle radius", "Width", "Height", "Charge radius", "Distance between charges", "Charge value",
        "Charge mass", "Particle mass",
        "Average kin. energy of 1 dipole: 0", "Standard dev. of 1 dipole: 0",
        "Average kin. energy of 2 dipole: 0", "Standard dev. of 2 dipole: 0"]
        self.positions = [(1620, 20), (1600, 120), (1600, 220), (1600, 320), (1600, 420), (1600, 520), (1600, 620), (1600, 720), (1600, 820), (1600, 920), 
                          (1000, 570),  
                          (1000, 660), (1000, 690), (1000, 720), (1000, 750)]
        self.eng_positions = [(1620, 20), (1600, 120), (1600, 220), (1600, 320), (1600, 420), (1600, 520), (1600, 620), (1600, 720), (1600, 820), (1600, 920),
                              (1000, 570),   
                              (1000, 660), (1000, 690), (1000, 720), (1000, 750)]

        self.data = [[], []]

        self.particle_system = ParticleSystem(self.particles_number, self.radius, max_width=self.width, max_height=self.height, 
                                                          avg_vel=self.speed, d_radius=self.d_radius, r=self.r, charge=self.charge, charge_mass=self.charge_mass, m=1)

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
        self.slider_dt.listen(events)
        self.slider_radius.listen(events)
        self.slider_width.listen(events)
        self.slider_height.listen(events)
        self.slider_d_radius.listen(events)
        self.slider_r.listen(events)
        self.slider_charge.listen(events)
        self.slider_charge_mass.listen(events)
        self.slider_m.listen(events)

        self.textbox.listen(events)
        self.textbox_s.listen(events)
        self.textbox_dt.listen(events)
        self.textbox_radius.listen(events)
        self.textbox_width.listen(events)
        self.textbox_height.listen(events)
        self.textbox_d_radius.listen(events)
        self.textbox_r.listen(events)
        self.textbox_charge.listen(events)
        self.textbox_charge_mass.listen(events)
        self.textbox_m.listen(events)

        self.textbox.setText(self.slider.getValue())
        self.textbox_s.setText(self.slider_s.getValue())
        self.textbox_dt.setText(self.slider_dt.getValue())
        self.textbox_radius.setText(self.slider_radius.getValue())
        self.textbox_width.setText(self.slider_width.getValue())
        self.textbox_height.setText(self.slider_height.getValue())
        self.textbox_d_radius.setText(self.slider_d_radius.getValue())
        self.textbox_r.setText(self.slider_r.getValue())
        self.textbox_charge.setText(self.slider_charge.getValue())
        self.textbox_charge_mass.setText(self.slider_charge_mass.getValue())
        self.textbox_m.setText(self.slider_m.getValue())

        self.particles_number = self.slider.getValue()
        self.speed = self.slider_s.getValue()
        self.dt = self.slider_dt.getValue()
        self.radius = self.slider_radius.getValue()
        self.width = self.slider_width.getValue()
        self.height = self.slider_height.getValue()
        self.d_radius = self.slider_d_radius.getValue()
        self.r = self.slider_r.getValue()
        self.charge = self.slider_charge.getValue()
        self.charge_mass = self.slider_charge_mass.getValue()
        self.m = self.slider_m.getValue()

        self.particle_system.charge = self.charge
        self.particle_system.charge_mass = self.charge_mass
        self.particle_system.m = self.m

    def _update_screen(self):
        self.screen.fill(self.bg_color)
        self.strings_surfaces = []
        for i in range(2):
            if len(self.data[i]) > 0:
                self.strings[-4 + 2 * i] = f"Средняя кин. энергия {i + 1} диполя: " + f'{int(np.average(np.array(self.data[0])).item())}'
                self.strings[-3 + 2 * i] = f"Стандарт. отклон. кин. энергии {i + 1} диполя: " + f'{int(np.sqrt(np.var(np.array(self.data[0]))).item())}'
                self.eng_strings[-4 + 2 * i] = f"Average kin. energy of {i + 1} dipole: " + f'{int(np.average(np.array(self.data[0])).item())}'
                self.eng_strings[-3 + 2 * i] = f"Standard dev. of {i + 1} dipole: " + f'{int(np.sqrt(np.var(np.array(self.data[0]))).item())}'
            else:
                self.strings[-4 + 2 * i] = f"Средняя кин. энергия {i + 1} диполя: 0"
                self.strings[-3 + 2 * i] = f"Стандарт. отклон. кин. энергии {i + 1} диполя: 0"
                self.eng_strings[-4 + 2 * i] = f"Average kin. energy of {i + 1} dipole: 0"
                self.eng_strings[-3 + 2 * i] = f"Standard dev. of {i + 1} dipole: 0"
        for index, string in enumerate(self.strings if self.app.russian else self.eng_strings):
            self.strings_surfaces.append(self.little_font.render(string, False, (0, 0, 0)))
        for index, surface in enumerate(self.strings_surfaces):
            self.screen.blit(surface, np.array(self.positions[index] if self.app.russian else self.eng_positions[index]) * self.scale)
        if self.mode == ACTIVATED:
            self.buttons = [Button(self.app, "Завершить" if self.app.russian else "Finish", (1000, 800), (250, 70), font_size=30),
                            Button(self.app, "Остановить" if self.app.russian else "Stop", (1300, 800), (250, 70), font_size=30),
                            Button(self.app, "Назад" if self.app.russian else "Back", (1000, 900), (250, 70), font_size=30),
                            Button(self.app, "RUS/ENG", (1300, 900), (250, 70), font_size=30)]
            pygame.draw.rect(self.screen, Color.WHITE.rgb, Rectangle(0, 0, self.width, self.height), 0)
            pygame.draw.rect(self.screen, Color.BLACK.rgb, Rectangle(0, 0, self.width, self.height), 1)
            res = self.particle_system.proceed(self.dt)
            if res != False:
                self.data[0].append(res[0])
                self.data[1].append(res[1])
                fig, axes = plt.subplots(1, 1)
                axes.plot(self.dt * np.arange(len(self.data[0])), self.data[0], color='gold')
                axes.plot(self.dt * np.arange(len(self.data[1])), self.data[1], color='black')
                axes.set_xlabel("Время, сек." if self.app.russian else "Time, sec.")
                axes.set_title("Кинетическая энергия диполей" if self.app.russian else "Kinematic energy of dipoles")
                axes.set_xlim(xmin=0)
                axes.set_ylim(ymin=0)
                fig.canvas.draw()
                self.screen.blit(fig, (0, 500))
                plt.close()
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
                    pos0 = self.particle_system.dipoles[i].pos + self.particle_system.r * np.array([cos, sin])
                    pos1 = self.particle_system.dipoles[i].pos - self.particle_system.r * np.array([cos, sin])
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
                    pygame.draw.line(self.screen, self.dipole_colors[i], (pos0[0], pos0[1]),
                                    (pos1[0], pos1[1]))
            else:
                self.mode = NOT_STARTED
        elif self.mode == PAUSED:
            self.buttons = [Button(self.app, "Завершить" if self.app.russian else "Finish", (1000, 800), (250, 70), font_size=30),
                            Button(self.app, "Возобновить" if self.app.russian else "Continue", (1300, 800), (250, 70), font_size=30),
                            Button(self.app, "Назад" if self.app.russian else "Back", (1000, 900), (250, 70), font_size=30),
                            Button(self.app, "RUS/ENG", (1300, 900), (250, 70), font_size=30)]
            pygame.draw.rect(self.screen, Color.WHITE.rgb, Rectangle(0, 0, self.width, self.height), 0)
            pygame.draw.rect(self.screen, Color.BLACK.rgb, Rectangle(0, 0, self.width, self.height), 1)
            fig, axes = plt.subplots(1, 1)
            axes.plot(self.dt * np.arange(len(self.data[0])), self.data[0], color='gold')
            axes.plot(self.dt * np.arange(len(self.data[1])), self.data[1], color='black')
            axes.set_xlabel("Время, сек." if self.app.russian else "Time, sec.")
            axes.set_title("Кинетическая энергия диполей" if self.app.russian else "Kinematic energy of dipoles")
            axes.set_xlim(xmin=0)
            axes.set_ylim(ymin=0)
            fig.canvas.draw()
            self.screen.blit(fig, (0, 500))
            plt.close()
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
                pos0 = self.particle_system.dipoles[i].pos + self.particle_system.r * np.array([cos, sin])
                pos1 = self.particle_system.dipoles[i].pos - self.particle_system.r * np.array([cos, sin])
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
                pygame.draw.line(self.screen, self.dipole_colors[i], (pos0[0], pos0[1]),
                                (pos1[0], pos1[1]))
        else:
            self.buttons = [Button(self.app, "Начать" if self.app.russian else "Start", (1000, 800), (250, 70), font_size=30),
                        Button(self.app, "Назад" if self.app.russian else "Back", (1000, 900), (250, 70), font_size=30),
                        Button(self.app, "RUS/ENG", (1300, 900), (250, 70), font_size=30)]
            pygame.draw.rect(self.screen, Color.WHITE.rgb, Rectangle(0, 0, self.width, self.height), 0)
            pygame.draw.rect(self.screen, Color.BLACK.rgb, Rectangle(0, 0, self.width, self.height), 1)
            fig, axes = plt.subplots(1, 1)
            axes.plot(self.dt * np.arange(len(self.data[0])), self.data[0], color='gold')
            axes.plot(self.dt * np.arange(len(self.data[1])), self.data[1], color='black')
            axes.set_xlabel("Время, сек." if self.app.russian else "Time, sec.")
            axes.set_title("Кинетическая энергия диполей" if self.app.russian else "Kinematic energy of dipoles")
            axes.set_xlim(xmin=0)
            axes.set_ylim(ymin=0)
            fig.canvas.draw()
            self.screen.blit(fig, (0, 500))
            plt.close()
        for button in self.buttons:
            button.draw_button()
        if self.mode == NOT_STARTED:
            self.slider.draw()
            self.slider_radius.draw()
            self.slider_width.draw()
            self.slider_height.draw()
            self.slider_d_radius.draw()
            self.slider_r.draw()
        self.textbox.draw()
        self.slider_s.draw()
        self.textbox_s.draw()
        self.slider_dt.draw()
        self.textbox_dt.draw()
        self.textbox_radius.draw()
        self.textbox_width.draw()
        self.textbox_height.draw()
        self.textbox_d_radius.draw()
        self.textbox_r.draw()
        self.slider_charge.draw()
        self.textbox_charge.draw()
        self.slider_charge_mass.draw()
        self.textbox_charge_mass.draw()
        self.slider_m.draw()
        self.textbox_m.draw()

    def _check_buttons(self, mouse_position):
        for index, button in enumerate(self.buttons):
            if button.rect.collidepoint(mouse_position):
                if button.msg == 'Назад' or button.msg == 'Back':
                    self.app.active_screen = self.app.menu_screen
                elif button.msg == 'Начать' or button.msg == 'Start':
                    self.mode = ACTIVATED
                    self.particle_system = ParticleSystem(self.particles_number, self.radius, max_width=self.width, max_height=self.height, 
                                                          avg_vel=self.speed, d_radius=self.d_radius, r=self.r, charge=self.charge, charge_mass=self.charge_mass, m=1)
                    self.data = [[], []]
                elif button.msg == 'Остановить' or button.msg == 'Stop':
                    self.mode = PAUSED
                elif button.msg == 'Возобновить' or button.msg == 'Continue':
                    self.mode = ACTIVATED
                elif button.msg == 'Завершить' or button.msg == 'Finish':
                    self.mode = NOT_STARTED
                elif button.msg == 'RUS/ENG':
                    self.app.russian = not self.app.russian
        