import numpy as np
import matplotlib.pyplot as plt

# Константа Кулона
k = 8.99e9  # Н·м²/Кл²

# Параметры диполя
class Dipole:
    def __init__(self, position, charge, distance, mass, rotation_speed):
        self.position = np.array(position)  # Центр диполя
        self.charge = charge  # Заряд (положительный и отрицательный)
        self.distance = distance  # Расстояние между зарядами
        self.mass = mass  # Масса диполя
        self.rotation_speed = rotation_speed  # Угловая скорость (рад/с)
        self.angle = 0  # Начальный угол диполя
        self.velocity = np.array([0.0, 0.0])  # Начальная скорость центра диполя
        self.angular_velocity = 0.0  # Начальная угловая скорость

    def get_positions(self):
        # Позиции зарядов в диполе
        half_distance = self.distance / 2
        pos1 = self.position + np.array([half_distance * np.cos(self.angle), half_distance * np.sin(self.angle)])
        pos2 = self.position - np.array([half_distance * np.cos(self.angle), half_distance * np.sin(self.angle)])
        return pos1, pos2

# Функция для вычисления силы между двумя зарядами
def coulomb_force(q1, q2, r):
    return k * q1 * q2 / r**2

# Функция для вычисления производных
def derivatives(t, state, dipole1, dipole2):
    # Извлекаем состояния
    x1, y1, vx1, vy1, x2, y2, vx2, vy2 = state
    
    # Обновляем позиции зарядов диполей
    dipole1.position = np.array([x1, y1])
    dipole2.position = np.array([x2, y2])
    
    # Получаем позиции зарядов
    p1_1, p1_2 = dipole1.get_positions()
    p2_1, p2_2 = dipole2.get_positions()
    
    # Силы между зарядами
    F12 = coulomb_force(dipole1.charge, -dipole1.charge, np.linalg.norm(p1_1 - p2_1))
    F21 = coulomb_force(-dipole1.charge, dipole2.charge, np.linalg.norm(p1_2 - p2_2))
    
    # Силы на диполи
    force1 = (F12 * (p2_1 - p1_1) / np.linalg.norm(p2_1 - p1_1)) + (F21 * (p2_2 - p1_2) / np.linalg.norm(p2_2 - p1_2))
    force2 = (-F12 * (p1_1 - p2_1) / np.linalg.norm(p1_1 - p2_1)) + (-F21 * (p1_2 - p2_2) / np.linalg.norm(p1_2 - p2_2))
    
    # Угловые скорости
    dipole1.angle += dipole1.rotation_speed * dt
    dipole2.angle += dipole2.rotation_speed * dt

    # Обновляем скорости центров диполей
    dipole1.velocity += force1 / dipole1.mass * dt  # Используем массу
    dipole2.velocity += force2 / dipole2.mass * dt  # Используем массу
    
    # Обновляем положение центров диполей
    dipole1.position += dipole1.velocity * dt
    dipole2.position += dipole2.velocity * dt

    # Вычисляем угловое ускорение
    moment1 = np.cross(dipole1.get_positions()[0] - dipole1.get_positions()[1], force1)
    moment2 = np.cross(dipole2.get_positions()[0] - dipole2.get_positions()[1], force2)

    # Примерный момент инерции
    inertia1 = dipole1.mass * (dipole1.distance ** 2) / 4
    inertia2 = dipole2.mass * (dipole2.distance ** 2) / 4

    angular_acceleration1 = moment1 / inertia1  # Используем момент инерции
    angular_acceleration2 = moment2 / inertia2  # Используем момент инерции

    # Обновляем угловые скорости
    dipole1.rotation_speed += angular_acceleration1 * dt
    dipole2.rotation_speed += angular_acceleration2 * dt

    # Возвращаем производные
    return np.array([dipole1.position[0], dipole1.position[1], dipole1.velocity[0], dipole1.velocity[1], 
                     dipole2.position[0], dipole2.position[1], dipole2.velocity[0], dipole2.velocity[1]])

# Метод Рунге-Кутты 4-го порядка
def runge_kutta_4(t, state, dt, dipole1, dipole2):
    k1 = derivatives(t, state, dipole1, dipole2)
    k2 = derivatives(t + dt / 2, state + dt / 2 * k1, dipole1, dipole2)
    k3 = derivatives(t + dt / 2, state + dt / 2 * k2, dipole1, dipole2)
    k4 = derivatives(t + dt, state + dt * k3, dipole1, dipole2)
    
    return state + (dt / 6) * (k1 + 2*k2 + 2*k3 + k4)

# Начальные условия
dipole1 = Dipole(position=[0, 0], charge=1e-6, distance=0.1, mass=0.01, rotation_speed=0.1)
dipole2 = Dipole(position=[1, 0], charge=-1e-6, distance=0.1, mass=0.01, rotation_speed=-0.1)

# Время и шаг интегрирования
dt = 0.01
t_end = 5

# Список для хранения траектории
trajectory1 = []
trajectory2 = []

# Начальное состояние
state = np.array([dipole1.position[0], dipole1.position[1], dipole1.velocity[0], dipole1.velocity[1], 
                  dipole2.position[0], dipole2.position[1], dipole2.velocity[0], dipole2.velocity[1]])

# Основной цикл интегрирования
t = 0
while t < t_end:
    trajectory1.append(dipole1.get_positions())
    trajectory2.append(dipole2.get_positions())
    state = runge_kutta_4(t, state, dt, dipole1, dipole2)
    t += dt

# Преобразование траекторий в массивы
trajectory1 = np.array(trajectory1)
trajectory2 = np.array(trajectory2)

# Визуализация
plt.figure(figsize=(10, 8))
plt.plot(trajectory1[:, 0, 0], trajectory1[:, 0, 1], label='Диполь 1', color='blue')
plt.plot(trajectory1[:, 1, 0], trajectory1[:, 1, 1], color='blue', linestyle='--')
plt.plot(trajectory2[:, 0, 0], trajectory2[:, 0, 1], label='Диполь 2', color='red')
plt.plot(trajectory2[:, 1, 0], trajectory2[:, 1, 1], color='red', linestyle='--')
plt.title('Движение диполей под действием закона Кулона')
plt.xlabel('x (м)')
plt.ylabel('y (м)')
plt.legend()
plt.grid()
plt.axis('equal')
plt.show()

