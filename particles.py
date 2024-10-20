from dataclasses import dataclass
import numpy as np
import pygame
from pygame.math import Vector2
from domain import *
import math

EPS = 1e-20

@dataclass
class ParticleSystem:
    count: int
    radius: float
    max_width: float
    max_height: float
    avg_vel: float
    d_radius: float
    r: float
    ITERATION: int = 0
    #dipoles

    def __post_init__(self) -> None:
        x_space = np.linspace(self.radius, self.max_width - self.radius, int(self.max_width // (2.5 * self.radius)))
        y_space = np.linspace(self.radius, self.max_height - self.radius, int(self.max_height // (2.5 * self.radius)))
        
        mesh = np.array(np.meshgrid(x_space, y_space)).T.reshape(-1, 2)
        choice = np.random.choice(mesh.shape[0], self.count + 4, replace=False)
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
    
    def get_average_speed(self) -> float:
        if self.count == 0:
            return 0
        return np.sqrt(self.entities[:, 2] ** 2 + self.entities[:, 3] ** 2).mean()

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
    
    def proceed(self, dt: float):
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
        if self.ITERATION < 20:
            #print(self.dipoles[0].pos, self.dipoles[0].c_vel, self.dipoles[0].actangle, self.dipoles[0].w)
            self.ITERATION += 1
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

                    scalar_dot = np.sum((arr[mask, 2:4] - old_v) * r_diff, axis=1) / r_mag2
                    temp = r_diff.copy()
                    temp[:, 0] *= scalar_dot
                    temp[:, 1] *= scalar_dot
                    arr[mask, 2:4] -= temp
                    delta_v = np.sum(temp, axis=0) 
                    proj = np.sum(np.array([-sin, cos]) * delta_v)
                    self.dipoles[i // 2].c_vel += delta_v / 2
                    if i % 2 == 0:
                        self.dipoles[i // 2].w += proj / (3 * self.r)
                    else:
                        self.dipoles[i // 2].w -= proj / (3 * self.r)

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
                q1q2 = 1
            else:
                q1q2 = -1
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
            if r_size < self.radius + self.d_radius:
                return False
            f_kulon = 9e7 * q1q2 * r / (r_size) ** 3
            # if self.ITERATION < 20:
            #    print(dt * f_kulon, self.dipoles[pair[0] // 2].c_vel + dt * f_kulon)
            self.dipoles[pair[0] // 2].c_vel = self.dipoles[pair[0] // 2].c_vel + dt * f_kulon
            proj = np.sum(f_kulon * np.array([-math.sin(self.dipoles[pair[0] // 2].actangle), math.cos(self.dipoles[pair[0] // 2].actangle)]))
            if pair[0] % 2 == 0:
                self.dipoles[pair[0] // 2].w += dt * proj / (3 * self.r)
            else:
                self.dipoles[pair[0] // 2].w -= dt * proj / (3 * self.r)
            f_kulon *= -1
            self.dipoles[pair[1] // 2].c_vel = self.dipoles[pair[1] // 2].c_vel + dt * f_kulon
            proj = np.sum(f_kulon * np.array([-math.sin(self.dipoles[pair[1] // 2].actangle), math.cos(self.dipoles[pair[1] // 2].actangle)]))
            if pair[1] % 2 == 0:
                self.dipoles[pair[1] // 2].w += dt * proj / (3 * self.r)
            else:
                self.dipoles[pair[1] // 2].w -= dt * proj / (3 * self.r)
        
        return True