from dataclasses import dataclass
import numpy as np
import pygame
from pygame.math import Vector2
from domain import *
import math
from copy import deepcopy

EPS = 1e-20
K = 9e9 * 1e1
MIN_DIST = 20

class DipoleState(Enum):
    NORMAL = 1
    STUCK = 2

def get_kinetic(dipole: Dipole, mass=1, d_radius=5, r=15, center=None):
    if center is None:
        return mass * np.sum(dipole.c_vel ** 2) + 0.5 * mass * ((4 * (d_radius ** 2) / 5) + (2 * (r ** 2))) * (dipole.w ** 2)
    p_1, p_2 = dipole.get_positions()
    r1 = np.linalg.norm(center - p_1).item()
    r2 = np.linalg.norm(center - p_2).item()
    return mass * np.sum(dipole.c_vel ** 2) + 0.5 * mass * ((4 * (d_radius ** 2) / 5) + (r1 ** 2) + (r2 ** 2)) * (dipole.w ** 2)

class Dipole:
    def __init__(self, pos: np.array = np.array([0, 0]), r: float = 15, actangle: float=0, 
                c_vel: np.array = np.array([0, 0]).astype(float), w: float = 0, state=DipoleState.NORMAL):
        self.pos: np.ndarray = pos
        self.actangle: float = actangle
        self.c_vel: np.ndarray = c_vel
        self.w: float = w
        self.state: DipoleState = state
        self.r = r

    def get_positions(self):
        pos1 = self.pos + np.array([self.r * math.cos(self.actangle), self.r * math.sin(self.actangle)])
        pos2 = self.pos - np.array([self.r * math.cos(self.actangle), self.r * math.sin(self.actangle)])
        return pos1, pos2
    
    def __add__(self, dipole: Dipole):
        return Dipole(self.pos + dipole.pos, self.r, self.actangle + dipole.actangle, self.c_vel + dipole.c_vel, self.w + dipole.w, self.state)

    def __truediv__(self, num):
        return Dipole(self.pos / num, self.r, self.actangle / num, self.c_vel / num, self.w / num, self.state)

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
    dipoles = [Dipole(), Dipole()]
    prev_charge: float = 0
    prev_charge_mass: float = 0
    prev_m: float = 0
    dv = [[0, 0], [0, 0]]
    dw = [0, 0]

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
            self.dipoles[i] = Dipole(pos, self.r, actangle)

        MIN_DIST = self.r
        self.full = self.get_full_potential()
        self.full_p = self.count * self.m * ((self.avg_vel) ** 2) / 2
        self.prev_charge = self.charge
        self.prev_charge_mass = self.charge_mass
        self.prev_m = self.m
        self.dv = np.array([[0, 0], [0, 0]])
        self.dw = np.array([0, 0])

    
    def get_average_speed(self) -> float:
        if self.count == 0:
            return 0
        return np.sqrt(self.entities[:, 2] ** 2 + self.entities[:, 3] ** 2).mean()
    
    def update_dipole_pair(self, dt, forced=False):
        if not forced:
            # Рассчитываем текущее расстояние между двумя диполями
            pairs = [(0, 2), (0, 3), (1, 2), (1, 3)]
            r_sizes = []
            stucks_neg = []
            stucks_pos = []
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
                if abs(pair[0] - pair[1]) % 2 == 0:
                    stucks_neg.append(r_size)
                else:
                    stucks_pos.append(r_size)
            distance = min(r_sizes)
            stucks_pos = [dist for dist in stucks_pos if (dist == distance)]
            stucks_neg = [dist for dist in stucks_neg if (dist == distance)]

            # Условие для слипания: если диполи достаточно близко и оба в состоянии NORMAL
            if self.dipoles[0].state == DipoleState.NORMAL and self.dipoles[1].state == DipoleState.NORMAL:
                if distance <= MIN_DIST:
                    if len(stucks_pos) > 0:
                # Переключаем оба диполя на состояние STUCK
                        self.dipoles[0].state = DipoleState.STUCK
                        self.dipoles[1].state = DipoleState.STUCK

                        # Вычисляем общую скорость и угловую скорость для движения как единого объекта
                        center_velocity = (self.dipoles[0].c_vel + self.dipoles[1].c_vel) / 2
                        self.dipoles[0].c_vel = center_velocity 
                        self.dipoles[1].c_vel = center_velocity  # Присваиваем общую скорость
                        angular_velocity = (self.dipoles[0].w + self.dipoles[1].w) / 2
                        self.dipoles[0].w = angular_velocity
                        self.dipoles[1].w = angular_velocity  # Присваиваем общую угловую скорость

            # Условие для разлипания: если слипшиеся диполи разошлись дальше порога разлипания
            elif self.dipoles[0].state == DipoleState.STUCK and self.dipoles[1].state == DipoleState.STUCK:
                if distance > MIN_DIST or len(stucks_neg) > 0:
                    # Переключаем оба диполя обратно на состояние NORMAL
                    self.dipoles[0].state = DipoleState.NORMAL
                    self.dipoles[1].state = DipoleState.NORMAL
                else:
                    center_velocity = (self.dipoles[0].c_vel + self.dipoles[1].c_vel) / 2
                    self.dipoles[0].c_vel = center_velocity 
                    self.dipoles[1].c_vel = center_velocity  # Присваиваем общую скорость
                    angular_velocity = (self.dipoles[0].w + self.dipoles[1].w) / 2
                    self.dipoles[0].w = angular_velocity
                    self.dipoles[1].w = angular_velocity  # Присваиваем общую угловую скорость
                
        if self.dipoles[0].state == DipoleState.NORMAL:
            self.runge_knuta_4(dt)
        else:
            center = (self.dipoles[0].pos + self.dipoles[1].pos) / 2 
            self.dipoles[0].actangle += self.dipoles[0].w * dt
            self.dipoles[1].actangle += self.dipoles[1].w * dt
            dact = self.dipoles[0].w * dt
            for i in range(2):
                diff = self.dipoles[i].pos - center
                rotation_matrix = np.array([[math.cos(dact), -math.sin(dact)],
                                 [math.sin(dact), math.cos(dact)]])
                self.dipoles[i].pos = center + (rotation_matrix @ diff)

            self.dipoles[0].pos += self.dipoles[0].c_vel * dt
            self.dipoles[1].pos += self.dipoles[1].c_vel * dt

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
        if self.dipoles[0].state == DipoleState.NORMAL:
            center = None
        else:
            center = (self.dipoles[0].pos + self.dipoles[1].pos) / 2
        return sum([get_kinetic(self.dipoles[i], mass=self.charge_mass, d_radius=self.d_radius, r=self.r, center=center) for i in range(2)])

    def get_full_potential(self):
        p1_1, p1_2 = self.dipoles[0].get_positions()
        p2_1, p2_2 = self.dipoles[1].get_positions()
        p1 = self.charge * (p1_1 - p1_2)
        p2 = self.charge * (p2_1 - p2_2)
        r = self.dipoles[0].pos - self.dipoles[1].pos
        r_size = np.linalg.norm(r).item()
        return K * ((p1 @ p2) * (r_size ** 2) - 3 * (p1 @ r) * (p2 @ r)) / ((r_size + self.r) ** 5)
    
    def get_full_particles_energy(self):
        if self.count == 0:
            return 0
        return self.m * np.sum(self.entities[:, 2] ** 2 + self.entities[:, 3] ** 2) / 2
    
    def get_full_energy(self):
        return self.get_full_kinetic() + self.get_full_potential() + self.get_full_particles_energy()
    
    def force(self, q1, q2, r):
        return K * q1 * q2 * r / (np.linalg.norm(r).item() + self.r) ** 3
    
    def derivatives(self, dipole1: Dipole, dipole2: Dipole, dt):
        p1_1, p1_2 = dipole1.get_positions()
        p2_1, p2_2 = dipole2.get_positions()

        f11 = self.force(self.charge, self.charge, p1_1 - p2_1)
        f12 = self.force(self.charge, -self.charge, p1_1 - p2_2)
        f21 = self.force(-self.charge, self.charge, p1_2 - p2_1)
        f22 = self.force(-self.charge, -self.charge, p1_2 - p2_2)

        dpos1 = dt * dipole1.c_vel
        dpos2 = dt * dipole2.c_vel

        dact1 = dt * dipole1.w
        dact2 = dt * dipole2.w

        dvel1 = dt * (f11 + f12 + f21 + f22) / (2 * self.charge_mass)
        dvel2 = -dt * (f11 + f12 + f21 + f22) / (2 * self.charge_mass)

        moment1 = np.cross(p1_1 - dipole1.pos, f11 + f12) + np.cross(p1_2 - dipole1.pos, f21 + f22)
        moment2 = -np.cross(p2_1 - dipole2.pos, f11 + f21) - np.cross(p2_2 - dipole2.pos, f22 + f12)

        inertial1 = self.charge_mass * ((4 * (self.d_radius ** 2) / 5) + (2 * (self.r ** 2)))
        inertial2 = self.charge_mass * ((4 * (self.d_radius ** 2) / 5) + (2 * (self.r ** 2)))

        e1 = moment1 / inertial1
        e2 = moment2 / inertial2

        dw1 = dt * e1
        dw2 = dt * e2

        return [Dipole(pos=dpos1, r=self.r, actangle=dact1, c_vel=dvel1, w=dw1), Dipole(dpos2, self.r, dact2, dvel2, dw2)]
    
    def runge_knuta_4(self, dt):
        k1 = self.derivatives(self.dipoles[0], self.dipoles[1], dt)
        k2 = self.derivatives(self.dipoles[0] + k1[0] / 2, self.dipoles[1] + k1[1] / 2, dt / 2)
        k3 = self.derivatives(self.dipoles[0] + k2[0] / 2, self.dipoles[1] + k2[1] / 2, dt / 2)
        k4 = self.derivatives(self.dipoles[0] + k3[0], self.dipoles[1] + k3[1], dt)
        self.dipoles[0] = self.dipoles[0] + (k1[0] / 6) + (k2[0] / 3) + (k3[0] / 3) + (k4[0] / 6)
        self.dipoles[1] = self.dipoles[1] + (k1[1] / 6) + (k2[1] / 3) + (k3[1] / 3) + (k4[1] / 6)

    
    def proceed(self, dt: float):
        self.dv = np.array([[0, 0], [0, 0]])
        self.dw = np.array([0, 0])
        forced = False
        if self.prev_charge != self.charge or self.prev_m != self.m or self.prev_charge_mass != self.charge_mass:
            self.full = self.get_full_potential() + self.get_full_kinetic()
            self.full_p = self.get_full_particles_energy()
            self.prev_charge = self.charge
            self.prev_charge_mass = self.charge_mass
            self.prev_m = self.m
        if self.charge == 0:
            self.dipoles[0].state = DipoleState.NORMAL
            self.dipoles[1].state = DipoleState.NORMAL
            forced = True
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
            #self.dipoles[i].pos += self.dipoles[i].c_vel * dt
            #self.dipoles[i].actangle += self.dipoles[i].w * dt
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
                    if self.dipoles[i].state == DipoleState.STUCK:
                        self.dipoles[1 - i].pos[0] -= q[0]
                        self.dipoles[1 - i].c_vel[0] = abs(self.dipoles[1 - i].c_vel[0])
                        if w_vel[0] < 0:
                            self.dipoles[1 - i].w *= -1
                if q[0] > self.max_width:
                    self.dipoles[i].pos[0] += self.max_width - q[0]
                    self.dipoles[i].c_vel[0] = -abs(self.dipoles[i].c_vel[0])
                    if w_vel[0] > 0:
                        self.dipoles[i].w *= -1
                    if self.dipoles[i].state == DipoleState.STUCK:
                        self.dipoles[1 - i].pos[0] += self.max_width - q[0]
                        self.dipoles[1 - i].c_vel[0] = -abs(self.dipoles[1 - i].c_vel[0])
                        if w_vel[0] > 0:
                            self.dipoles[1 - i].w *= -1
                if q[1] < 0:
                    self.dipoles[i].pos[1] -= q[1]
                    self.dipoles[i].c_vel[1] = abs(self.dipoles[i].c_vel[1])
                    if w_vel[1] < 0:
                        self.dipoles[i].w *= -1
                    if self.dipoles[i].state == DipoleState.STUCK:
                        self.dipoles[1 - i].pos[1] -= q[1]
                        self.dipoles[1 - i].c_vel[1] = abs(self.dipoles[1 - i].c_vel[1])
                        if w_vel[1] < 0:
                            self.dipoles[1 - i].w *= -1
                if q[1] > self.max_height:
                    self.dipoles[i].pos[1] += self.max_height - q[1]
                    self.dipoles[i].c_vel[1] = -abs(self.dipoles[i].c_vel[1])
                    if w_vel[1] > 0:
                        self.dipoles[i].w *= -1
                    if self.dipoles[i].state == DipoleState.STUCK:
                        self.dipoles[1 - i].pos[1] += self.max_height - q[1]
                        self.dipoles[1 - i].c_vel[1] = -abs(self.dipoles[1 - i].c_vel[1])
                        if w_vel[1] > 0:
                            self.dipoles[1 - i].w *= -1

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
                mask = mask & (((arr[:, 0] - charge[0]) ** 2 + (arr[:, 1] - charge[1]) ** 2) != 0)
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
                    # self.dipoles[i // 2].c_vel += delta_v / 2
                    self.dv[(i // 2),:] = self.dv[(i // 2),:] + (delta_v / 2)
                    L = np.cross(pos - self.dipoles[i // 2].pos, self.charge_mass * delta_v)
                    I = self.charge_mass * ((2 * (self.d_radius ** 2) / 5) + (1 * (self.r ** 2)))
                    # self.dipoles[i // 2].w += L / I
                    self.dw[i // 2] += L / I
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
        for i in range(2):
            self.dipoles[i].pos += self.dv[i] * dt
            self.dipoles[i].actangle += self.dw[i] * dt
        self.update_dipole_pair(dt, forced=forced)
        for i in range(2):
            self.dipoles[i].c_vel += self.dv[i]
            self.dipoles[i].w += self.dw[i]
        it = 0
        while True:
            it += 1
            kin_est = (self.full + self.full_p) - self.get_full_potential()
            if self.charge > 0 or self.count > 0:
                try:
                    coef = math.sqrt(kin_est / (self.get_full_kinetic() + self.get_full_particles_energy()))
                except:
                    print(kin_est)
                    assert False
                for i in range(2):
                    self.dipoles[i].c_vel *= coef
                    self.dipoles[i].w *= coef
                if self.count > 0:
                    self.entities[:, 2:] *= coef
            if abs(kin_est - self.get_full_kinetic()) < EPS or it == 5:
                break
        if self.dipoles[0].state == DipoleState.NORMAL:
            center = None
        else:
            center = (self.dipoles[0].pos + self.dipoles[1].pos) / 2
        '''
        try:
            assert abs(kin_est - self.get_full_kinetic()) < EPS
        except:
            print(kin_est, self.get_full_kinetic())
            assert False
        '''

        return [get_kinetic(self.dipoles[i], mass=self.charge_mass, d_radius=self.d_radius, r=self.r, center=center) for i in range(2)] + [self.get_full_potential(), self.get_full_energy()]