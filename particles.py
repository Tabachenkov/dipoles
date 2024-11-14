from dataclasses import dataclass
import numpy as np
import pygame
from pygame.math import Vector2
from domain import *
import math

EPS = 1e-20

class DipoleState(Enum):
    NORMAL = 1
    STUCK = 2

def get_kinetic(dipole, mass=1, d_radius=5, r=15):
    return mass * np.sum(dipole.c_vel ** 2) + mass * ((4 * (d_radius ** 2) / 5) + ((r ** 2) / 2)) * (dipole.w ** 2)

class Dipole:
    def __init__(self, pos: np.array = np.array([0, 0]), actangle: float=0, c_vel: np.array = np.array([0, 0]).astype(float), w: float = 0):
        self.pos: np.ndarray = pos
        self.actangle: float = actangle
        self.c_vel: np.ndarray = np.zeros(2)
        self.w: float = 0.0
        self.state: DipoleState = DipoleState.NORMAL
        self.stuck_partner: 'Dipole' = None  # Партнер по "слипанию", если диполь слипающийся

@dataclass
class ParticleSystem:
    count: int
    radius: float
    max_width: float
    max_height: float
    avg_vel: float
    d_radius: float
    r: float
    charge: float
    charge_mass: float
    m: float
    ITERATION: int = 0

    def __post_init__(self) -> None:
        x_space = np.linspace(self.radius, self.max_width - self.radius, int(self.max_width // (2.5 * self.radius)))
        y_space = np.linspace(self.radius, self.max_height - self.radius, int(self.max_height // (2.5 * self.radius)))
        
        mesh = np.array(np.meshgrid(x_space, y_space)).T.reshape(-1, 2)
        choice = np.random.choice(mesh.shape[0], self.count + 4)
        x = mesh[choice][:, 0]
        y = mesh[choice][:, 1]
        if self.count > 0:

            vx = np.random.uniform(-1, 1, self.count)
            vy = np.random.uniform(-1, 1, self.count)
            
            zeroed = (vx == 0) & (vy == 0)
            vx[zeroed] = 1
            vy[zeroed] = -1

            v_mag = np.sqrt(vx ** 2 + vy ** 2)
            vx /= v_mag
            vx *= self.avg_vel
            vy /= v_mag
            vy *= self.avg_vel

            self.entities = np.vstack((x[:-4], y[:-4], vx, vy)).T

        self.dipoles = [0, 0]
        for i in range(2):
            q0 = np.array([x[-2 - 2 * i], y[-2 - 2 * i]])
            q1 = np.array([x[-1 - 2 * i], y[-1 - 2 * i]])
            if i == 0:
                q0[0] /= 2
                q1[0] /= 2
            else:
                q0[0] /= 2
                q1[0] /= 2
                q0[0] += self.max_width / 2
                q1[0] += self.max_width / 2
            pos = (q0 + q1) / 2
            dist = (q0 - q1) / 2
            dist_size = np.sqrt(dist[0] ** 2 + dist[1] ** 2).item()
            actangle = math.asin(dist[1] / dist_size)
            if dist[0] < 0:
                actangle += math.pi
            self.dipoles[i] = Dipole(pos, actangle)

        self.max_kin = self.charge_mass * np.sum(1500 ** 2) + self.charge_mass * ((4 * (self.d_radius ** 2) / 5) + ((self.r ** 2) / 2)) * (300 ** 2)
    
    def get_average_speed(self) -> float:
        if self.count == 0:
            return 0
        return np.sqrt(self.entities[:, 2] ** 2 + self.entities[:, 3] ** 2).mean()
    
    def update_dipole_pair(self):
        # Рассчитываем текущее расстояние между двумя диполями
        pairs = [(0, 2), (0, 3), (1, 2), (1, 3)]
        r_sizes = []
        for pair in pairs:
            if pair[0] % 2 == 0:
                pos0 = self.dipoles[pair[0] // 2].pos + self.r * np.array([math.cos(self.dipoles[pair[0] // 2].actangle), math.sin(self.dipoles[pair[0] // 2].actangle)])
            else:
                pos0 = self.dipoles[pair[0] // 2].pos - self.r * np.array([math.cos(self.dipoles[pair[0] // 2].actangle), math.sin(self.dipoles[pair[0] // 2].actangle)])
            if pair[1] % 2 == 0:
                pos1 = self.dipoles[pair[1] // 2].pos + self.r * np.array([math.cos(self.dipoles[pair[1] // 2].actangle), math.sin(self.dipoles[pair[1] // 2].actangle)])
            else:
                pos1 = self.dipoles[pair[1] // 2].pos - self.r * np.array([math.cos(self.dipoles[pair[1] // 2].actangle), math.sin(self.dipoles[pair[1] // 2].actangle)])
            r = pos0 - pos1
            r_size = np.sqrt(r[0] ** 2 + r[1] ** 2).item()
            r_sizes.append(r_size)
        distance = min(r_sizes)

        # Условие для слипания: если диполи достаточно близко и оба в состоянии NORMAL
        if distance < self.r and self.dipoles[0].state == DipoleState.NORMAL and self.dipoles[1].state == DipoleState.NORMAL:
            # Переключаем оба диполя на состояние STUCK
            self.dipoles[0].state = DipoleState.STUCK
            self.dipoles[1].state = DipoleState.STUCK
            self.dipoles[0].stuck_partner = self.dipoles[1]  # Устанавливаем партнера для слипания
            self.dipoles[1].stuck_partner = self.dipoles[0]  # Взаимно устанавливаем партнера

            # Вычисляем общую скорость и угловую скорость для движения как единого объекта
            center_velocity = (self.dipoles[0].c_vel + self.dipoles[1].c_vel) / 2
            self.dipoles[0].c_vel = center_velocity 
            self.dipoles[1].c_vel = center_velocity  # Присваиваем общую скорость
            angular_velocity = (self.dipoles[0].w + self.dipoles[1].w) / 2
            self.dipoles[0].w = angular_velocity
            self.dipoles[1].w = angular_velocity  # Присваиваем общую угловую скорость

        # Условие для разлипания: если слипшиеся диполи разошлись дальше порога разлипания
        elif self.dipoles[0].state == DipoleState.STUCK and self.dipoles[1].state == DipoleState.STUCK:
            if distance > 1.5 * self.r:
                # Переключаем оба диполя обратно на состояние NORMAL
                self.dipoles[0].state = DipoleState.NORMAL
                self.dipoles[1].state = DipoleState.NORMAL
                self.dipoles[0].stuck_partner = None  # Убираем партнера по слипанию
                self.dipoles[1].stuck_partner = None

    def set_average_speed(self, value: float) -> None:
        if self.count == 0:
            return None
        if value < 1e-3:
            self.entities[:, 2] = 0
            self.entities[:, 3] = 0
            return
        average_speed = self.get_average_speed()
        if average_speed < 1e-3:
            self.__post_init__()
            self.set_average_speed(value)
            return
        self.entities[:, 2] *= (value / average_speed)
        self.entities[:, 3] *= (value / average_speed)

    def get_full_kinetic(self):
        return sum([get_kinetic(self.dipoles[i], mass=self.charge_mass, d_radius=self.d_radius, r=self.r) for i in range(2)])
    
    def proceed(self, dt: float):
        self.max_kin = self.charge_mass * np.sum(1500 ** 2) + self.charge_mass * ((4 * (self.d_radius ** 2) / 5) + ((self.r ** 2) / 2)) * (300 ** 2)
        self.update_dipole_pair()
        if self.count > 0:
            self.entities[:, 0] += self.entities[:, 2] * dt
            self.entities[:, 1] += self.entities[:, 3] * dt
            mask = self.entities[:, 0] < 0
            self.entities[mask, 0] = 0
            self.entities[mask, 2] *= -1
            mask = self.entities[:, 0] > self.max_width
            self.entities[mask, 0] = self.max_width
            self.entities[mask, 2] *= -1
            mask = self.entities[:, 1] < 0
            self.entities[mask, 1] = 0
            self.entities[mask, 3] *= -1
            mask = self.entities[:, 1] > self.max_height
            self.entities[mask, 1] = self.max_height
            self.entities[mask, 3] *= -1

        for i in range(2):
            self.dipoles[i].pos += self.dipoles[i].c_vel * dt
            self.dipoles[i].actangle += self.dipoles[i].w * dt
            q0 = self.dipoles[i].pos + self.r * np.array([math.cos(self.dipoles[i].actangle), math.sin(self.dipoles[i].actangle)])
            q1 = self.dipoles[i].pos - self.r * np.array([math.cos(self.dipoles[i].actangle), math.sin(self.dipoles[i].actangle)])
            for j, q in enumerate([q0, q1]):
                if j == 0:
                    w_vel = self.dipoles[i].w * np.array([-math.sin(self.dipoles[i].actangle), math.cos(self.dipoles[i].actangle)])
                else:
                    w_vel = -self.dipoles[i].w * np.array([-math.sin(self.dipoles[i].actangle), math.cos(self.dipoles[i].actangle)])
                if q[0] < 0:
                    self.dipoles[i].pos[0] -= q[0]
                    self.dipoles[i].c_vel[0] = abs(self.dipoles[i].c_vel[0])
                    if w_vel[0] < 0:
                        self.dipoles[i].w *= -1
                if q[0] > self.max_width:
                    self.dipoles[i].pos[0] += self.max_width - q[0]
                    self.dipoles[i].c_vel[0] = -abs(self.dipoles[i].c_vel[0])
                    if w_vel[0] > 0:
                        self.dipoles[i].w *= -1
                if q[1] < 0:
                    self.dipoles[i].pos[1] -= q[1]
                    self.dipoles[i].c_vel[1] = abs(self.dipoles[i].c_vel[1])
                    if w_vel[1] < 0:
                        self.dipoles[i].w *= -1
                if q[1] > self.max_height:
                    self.dipoles[i].pos[1] += self.max_height - q[1]
                    self.dipoles[i].c_vel[1] = -abs(self.dipoles[i].c_vel[1])
                    if w_vel[1] > 0:
                        self.dipoles[i].w *= -1
        if self.count > 0:
            for i in range(4):
                cos = math.cos(self.dipoles[i // 2].actangle)
                sin = math.sin(self.dipoles[i // 2].actangle)
                if i % 2 == 0:
                    pos = self.dipoles[i // 2].pos + self.r * np.array([cos, sin])
                    vel = self.dipoles[i // 2].c_vel + self.dipoles[i // 2].w * np.array([-sin, cos])
                else:
                    pos = self.dipoles[i // 2].pos - self.r * np.array([cos, sin])
                    vel = self.dipoles[i // 2].c_vel - self.dipoles[i // 2].w * np.array([-sin, cos])
                charge = np.array([pos[0], pos[1], vel[0], vel[1]])
                arr = self.entities
                mask = (arr[:, 0] - charge[0]) ** 2 + (arr[:, 1] - charge[1]) ** 2 < ((self.radius + self.d_radius)** 2)
                if len(arr[mask]) > 0:
                    old_vx = charge[2]
                    old_vy = charge[3]
                    old_v = np.array([old_vx, old_vy])
                    old_r = charge[0:2]
                    
                    r_diff = arr[mask, 0:2] - old_r
                    r_mag2 = r_diff[:, 0] ** 2 + r_diff[:, 1] ** 2

                    scalar_dot = np.sum((self.m * arr[mask, 2:4] - self.charge_mass * old_v) * r_diff, axis=1) / r_mag2
                    temp = r_diff.copy()
                    temp[:, 0] *= scalar_dot
                    temp[:, 1] *= scalar_dot
                    arr[mask, 2:4] -= (temp / self.m)
                    delta_v = np.sum(temp, axis=0) / self.charge_mass
                    proj = np.sum(np.array([-sin, cos]) * delta_v)
                    self.dipoles[i // 2].c_vel += delta_v / 2
                    if i % 2 == 0:
                        self.dipoles[i // 2].w += proj / (3 * (self.r + 1))
                    else:
                        self.dipoles[i // 2].w -= proj / (3 * (self.r + 1))

            for i in range(self.count):
                arr = self.entities[i+1:]
                mask = (arr[:, 0] - self.entities[i, 0]) ** 2 + (arr[:, 1] - self.entities[i, 1]) ** 2 < ((2 * self.radius) ** 2)
                mask = mask & (((arr[:, 0] - self.entities[i, 0]) ** 2 + (arr[:, 1] - self.entities[i, 1]) ** 2) != 0)
                if len(arr[mask]) == 0:
                    continue
                old_vx = self.entities[i, 2]
                old_vy = self.entities[i, 3]
                old_v = np.array([old_vx, old_vy])
                old_r = self.entities[i, 0:2]

                r_diff = arr[mask, 0:2] - old_r
                r_mag2 = r_diff[:, 0] ** 2 + r_diff[:, 1] ** 2

                scalar_dot = np.sum((arr[mask, 2:4] - old_v) * r_diff, axis=1) / r_mag2
                temp = r_diff.copy()
                temp[:, 0] *= scalar_dot
                temp[:, 1] *= scalar_dot
                arr[mask, 2:4] -= temp
                self.entities[i, 2:4] += np.sum(temp, axis=0)
        
        pairs = [(0, 2), (0, 3), (1, 2), (1, 3)]
        for pair in pairs:
            if (pair[0] + pair[1]) % 2 == 0:
                q1q2 = self.charge ** 2
            else:
                q1q2 = -self.charge ** 2
            if pair[0] % 2 == 0:
                pos0 = self.dipoles[pair[0] // 2].pos + self.r * np.array([math.cos(self.dipoles[pair[0] // 2].actangle), math.sin(self.dipoles[pair[0] // 2].actangle)])
            else:
                pos0 = self.dipoles[pair[0] // 2].pos - self.r * np.array([math.cos(self.dipoles[pair[0] // 2].actangle), math.sin(self.dipoles[pair[0] // 2].actangle)])
            if pair[1] % 2 == 0:
                pos1 = self.dipoles[pair[1] // 2].pos + self.r * np.array([math.cos(self.dipoles[pair[1] // 2].actangle), math.sin(self.dipoles[pair[1] // 2].actangle)])
            else:
                pos1 = self.dipoles[pair[1] // 2].pos - self.r * np.array([math.cos(self.dipoles[pair[1] // 2].actangle), math.sin(self.dipoles[pair[1] // 2].actangle)])
            r = pos0 - pos1
            r_size = np.sqrt(r[0] ** 2 + r[1] ** 2).item()
            f_kulon = 9e9 * q1q2 * r / (r_size + self.d_radius) ** 3
            a = f_kulon / self.charge_mass
            self.dipoles[pair[0] // 2].c_vel = self.dipoles[pair[0] // 2].c_vel + dt * a
            proj = np.sum(a * np.array([-math.sin(self.dipoles[pair[0] // 2].actangle), math.cos(self.dipoles[pair[0] // 2].actangle)]))
            if pair[0] % 2 == 0:
                self.dipoles[pair[0] // 2].w += dt * proj / (3 * (self.r + 1))
            else:
                self.dipoles[pair[0] // 2].w -= dt * proj / (3 * (self.r + 1))
            a *= -1
            self.dipoles[pair[1] // 2].c_vel = self.dipoles[pair[1] // 2].c_vel + dt * a
            proj = np.sum(a * np.array([-math.sin(self.dipoles[pair[1] // 2].actangle), math.cos(self.dipoles[pair[1] // 2].actangle)]))
            if pair[1] % 2 == 0:
                self.dipoles[pair[1] // 2].w += dt * proj / (3 * (self.r + 1))
            else:
                self.dipoles[pair[1] // 2].w -= dt * proj / (3 * (self.r + 1))

        cur_kin = self.get_full_kinetic() 
        if cur_kin > self.max_kin:
            coef = math.sqrt(cur_kin / self.max_kin)
            for i in range(2):
                self.dipoles[i].c_vel /= coef
                self.dipoles[i].w /= coef
        
        return [get_kinetic(self.dipoles[i], mass=self.charge_mass, d_radius=self.d_radius, r=self.r) for i in range(2)]