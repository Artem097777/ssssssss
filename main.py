import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import *
import math
import random

# Настройки окна
Window.size = (1024, 768)
Window.clearcolor = (0.1, 0.1, 0.1, 1)

class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __copy__(self):
        return Vector3(self.x, self.y, self.z)
    
    def copy(self):
        return Vector3(self.x, self.y, self.z)
    
    def normalize(self):
        length = math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
        if length > 0:
            return Vector3(self.x/length, self.y/length, self.z/length)
        return Vector3(0, 0, 0)
    
    def length(self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
    
    def rotate_y(self, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        x = self.x * cos_a + self.z * sin_a
        z = -self.x * sin_a + self.z * cos_a
        return Vector3(x, self.y, z)
    
    def rotate_x(self, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        y = self.y * cos_a - self.z * sin_a
        z = self.y * sin_a + self.z * cos_a
        return Vector3(self.x, y, z)
    
    def cross(self, other):
        """Векторное произведение"""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def dot(self, other):
        """Скалярное произведение"""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def distance(self, other):
        """Расстояние до другой точки"""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def distance2d(self, other):
        """Расстояние только по XZ плоскости"""
        dx = self.x - other.x
        dz = self.z - other.z
        return math.sqrt(dx*dx + dz*dz)

class BoundingBox:
    """Ограничивающая рамка для столкновений"""
    def __init__(self, min_point, max_point):
        self.min = Vector3(min(min_point.x, max_point.x), 
                          min(min_point.y, max_point.y), 
                          min(min_point.z, max_point.z))
        self.max = Vector3(max(min_point.x, max_point.x), 
                          max(min_point.y, max_point.y), 
                          max(min_point.z, max_point.z))
    
    def get_center(self):
        return Vector3(
            (self.min.x + self.max.x) / 2,
            (self.min.y + self.max.y) / 2,
            (self.min.z + self.max.z) / 2
        )
    
    def intersects(self, other):
        """Проверка пересечения с другой рамкой"""
        return (self.min.x <= other.max.x and self.max.x >= other.min.x and
                self.min.y <= other.max.y and self.max.y >= other.min.y and
                self.min.z <= other.max.z and self.max.z >= other.min.z)
    
    def contains_point(self, point, margin=0):
        """Проверяет, содержит ли рамка точку"""
        return (self.min.x - margin <= point.x <= self.max.x + margin and
                self.min.y - margin <= point.y <= self.max.y + margin and
                self.min.z - margin <= point.z <= self.max.z + margin)

class Camera:
    def __init__(self):
        self.position = Vector3(2, 1.8, 2)
        self.rotation = Vector3(0, math.pi/4, 0)
        self.forward = Vector3(0, 0, 1)
        self.right = Vector3(1, 0, 0)
        self.up = Vector3(0, 1, 0)
        
        # Размеры коллизии игрока (цилиндр)
        self.radius = 0.4  # радиус коллизии
        self.height = 1.8  # высота игрока
        
        # Физические параметры
        self.velocity = Vector3(0, 0, 0)
        self.gravity = -25.0
        self.grounded = True
        self.jump_power = 10.0
        self.move_speed = 4.0
        self.run_speed = 7.0
        self.current_speed = self.move_speed
        self.acceleration = 30.0
        self.friction = 15.0
        self.jump_count = 0
        self.max_jumps = 2
        self.on_stairs = False
        self.stair_speed = 3.0
        
        # Параметры взгляда
        self.look_speed = 0.1
        self.mouse_sensitivity = 0.003
        
        self.update_vectors()
    
    def update_vectors(self):
        cos_y = math.cos(self.rotation.y)
        sin_y = math.sin(self.rotation.y)
        cos_x = math.cos(self.rotation.x)
        sin_x = math.sin(self.rotation.x)
        
        self.forward = Vector3(
            sin_y * cos_x,
            sin_x,
            cos_y * cos_x
        ).normalize()
        
        world_up = Vector3(0, 1, 0)
        self.right = world_up.cross(self.forward).normalize()
        self.up = self.forward.cross(self.right).normalize()
    
    def get_bounding_box(self):
        """Возвращает ограничивающую рамку игрока"""
        # Для простоты используем куб вместо цилиндра
        half_size = self.radius
        return BoundingBox(
            Vector3(self.position.x - half_size, 
                   self.position.y, 
                   self.position.z - half_size),
            Vector3(self.position.x + half_size, 
                   self.position.y + self.height, 
                   self.position.z + half_size)
        )
    
    def check_wall_collision(self, walls, old_pos):
        """Проверяет столкновение со стенами и корректирует позицию"""
        # Сначала проверяем по горизонтали (XZ)
        test_pos = self.position.copy()
        
        # Проверяем каждую стену
        for wall in walls:
            wall_bb = wall.get_bounding_box()
            player_bb = self.get_bounding_box()
            
            if wall_bb.intersects(player_bb):
                # Столкновение обнаружено, корректируем позицию
                dx = 0
                dz = 0
                
                # Определяем, с какой стороны произошло столкновение
                player_center = player_bb.get_center()
                wall_center = wall_bb.get_center()
                
                # Расстояние по осям
                dist_x = abs(player_center.x - wall_center.x)
                dist_z = abs(player_center.z - wall_center.z)
                
                # Толщина стенки для выталкивания
                penetration = self.radius + 0.1
                
                if dist_x > dist_z:
                    # Столкновение с левой/правой стороной
                    if player_center.x < wall_center.x:
                        dx = wall_bb.min.x - player_bb.max.x - 0.01
                    else:
                        dx = wall_bb.max.x - player_bb.min.x + 0.01
                    self.velocity.x = 0
                else:
                    # Столкновение с передней/задней стороной
                    if player_center.z < wall_center.z:
                        dz = wall_bb.min.z - player_bb.max.z - 0.01
                    else:
                        dz = wall_bb.max.z - player_bb.min.z + 0.01
                    self.velocity.z = 0
                
                # Применяем корректировку
                self.position.x += dx
                self.position.z += dz
        
        # После коррекции проверяем вертикальные столкновения
        for wall in walls:
            wall_bb = wall.get_bounding_box()
            player_bb = self.get_bounding_box()
            
            if wall_bb.intersects(player_bb):
                # Вертикальное столкновение (потолок/пол стены)
                player_center = player_bb.get_center()
                wall_center = wall_bb.get_center()
                
                # Если игрок падает на стену сверху
                if old_pos.y > wall_bb.max.y and self.position.y <= wall_bb.max.y:
                    self.position.y = wall_bb.max.y + 0.01
                    self.velocity.y = 0
                # Если игрок ударяется головой о стену снизу
                elif old_pos.y + self.height < wall_bb.min.y and self.position.y + self.height >= wall_bb.min.y:
                    self.position.y = wall_bb.min.y - self.height - 0.01
                    self.velocity.y = 0
    
    def update_physics(self, dt, walls, floor_y=0):
        """Обновление физики с учетом столкновений"""
        old_pos = self.position.copy()
        
        # Если на лестнице - другая физика
        if self.on_stairs:
            self.velocity.y = 0
            self.grounded = True
            return
        
        # Применяем гравитацию
        if not self.grounded:
            self.velocity.y += self.gravity * dt
        
        # Применяем трение по горизонтали
        if self.grounded:
            self.velocity.x *= 1 - self.friction * dt
            self.velocity.z *= 1 - self.friction * dt
            
            if abs(self.velocity.x) < 0.1:
                self.velocity.x = 0
            if abs(self.velocity.z) < 0.1:
                self.velocity.z = 0
        
        # Обновляем позицию
        self.position.x += self.velocity.x * dt
        self.position.z += self.velocity.z * dt
        self.position.y += self.velocity.y * dt
        
        # Проверяем столкновение со стенами
        self.check_wall_collision(walls, old_pos)
        
        # Проверяем столкновение с землей
        if self.position.y < floor_y + 1.8:
            self.position.y = floor_y + 1.8
            self.velocity.y = 0
            self.grounded = True
            self.jump_count = 0
    
    def move(self, direction_x, direction_z, dt, on_stairs=False):
        """Движение в направлении"""
        if on_stairs:
            if direction_z != 0:
                self.position.y += direction_z * self.stair_speed * dt
        else:
            if direction_x != 0 or direction_z != 0:
                move_direction = Vector3(direction_x, 0, direction_z).normalize()
                
                rotated_direction = Vector3(
                    move_direction.x * self.right.x + move_direction.z * self.forward.x,
                    0,
                    move_direction.x * self.right.z + move_direction.z * self.forward.z
                ).normalize()
                
                target_velocity_x = rotated_direction.x * self.current_speed
                target_velocity_z = rotated_direction.z * self.current_speed
                
                self.velocity.x += (target_velocity_x - self.velocity.x) * self.acceleration * dt
                self.velocity.z += (target_velocity_z - self.velocity.z) * self.acceleration * dt
    
    def move_on_stairs(self, direction, dt):
        """Движение вверх/вниз по лестнице"""
        self.position.y += direction * self.stair_speed * dt
    
    def jump(self):
        """ПРЫЖОК - ПРОСТОЙ И МОМЕНТАЛЬНЫЙ"""
        if not self.on_stairs:  # Не прыгать на лестнице
            if self.jump_count < self.max_jumps:
                self.velocity.y = self.jump_power
                self.grounded = False
                self.jump_count += 1
                return True
        return False
    
    def run(self, is_running):
        """Режим бега"""
        if is_running:
            self.current_speed = self.run_speed
        else:
            self.current_speed = self.move_speed
    
    def rotate_with_keys(self, dx, dy):
        """Поворот камеры с помощью клавиш"""
        self.rotation.y += dx * self.look_speed
        self.rotation.x += dy * self.look_speed
        
        self.rotation.x = max(-math.pi/2 + 0.1, min(math.pi/2 - 0.1, self.rotation.x))
        self.update_vectors()
    
    def look(self, dx, dy):
        """Поворот камеры мышью"""
        self.rotation.y += dx * self.mouse_sensitivity
        self.rotation.x += dy * self.mouse_sensitivity
        
        self.rotation.x = max(-math.pi/2 + 0.1, min(math.pi/2 - 0.1, self.rotation.x))
        self.update_vectors()

class Wall:
    """Стена лабиринта с физической коллизией"""
    def __init__(self, x=0, y=0, z=0, width=1, depth=1, height=3):
        self.position = Vector3(x, y, z)
        self.width = width
        self.depth = depth
        self.height = height
        self.color = (0.7, 0.7, 0.7, 1)
    
    def get_bounding_box(self):
        """Возвращает ограничивающую рамку стены"""
        w2 = self.width / 2
        d2 = self.depth / 2
        
        return BoundingBox(
            Vector3(self.position.x - w2, 
                   self.position.y, 
                   self.position.z - d2),
            Vector3(self.position.x + w2, 
                   self.position.y + self.height, 
                   self.position.z + d2)
        )
    
    def get_vertices(self):
        """Возвращает вершины стены"""
        w2 = self.width / 2
        d2 = self.depth / 2
        
        vertices = [
            Vector3(-w2, 0, -d2),
            Vector3(w2, 0, -d2),
            Vector3(w2, 0, d2),
            Vector3(-w2, 0, d2),
            Vector3(-w2, self.height, -d2),
            Vector3(w2, self.height, -d2),
            Vector3(w2, self.height, d2),
            Vector3(-w2, self.height, d2)
        ]
        
        for i in range(8):
            vertices[i] = vertices[i] + self.position
        
        return vertices
    
    def get_faces(self):
        """Возвращает грани стены"""
        vertices = self.get_vertices()
        
        faces = [
            [vertices[4], vertices[5], vertices[1], vertices[0]],
            [vertices[7], vertices[6], vertices[2], vertices[3]],
            [vertices[4], vertices[0], vertices[3], vertices[7]],
            [vertices[5], vertices[1], vertices[2], vertices[6]],
            [vertices[4], vertices[5], vertices[6], vertices[7]],
            [vertices[0], vertices[1], vertices[2], vertices[3]]
        ]
        
        return faces
    
    def is_player_colliding(self, player_pos, player_radius, player_height):
        """Проверяет столкновение игрока со стеной"""
        # Упрощенная проверка столкновения AABB с цилиндром
        wall_bb = self.get_bounding_box()
        
        # Находим ближайшую точку стены к игроку
        closest_x = max(wall_bb.min.x, min(player_pos.x, wall_bb.max.x))
        closest_y = max(wall_bb.min.y, min(player_pos.y, wall_bb.max.y))
        closest_z = max(wall_bb.min.z, min(player_pos.z, wall_bb.max.z))
        
        # Проверяем расстояние по горизонтали
        dx = player_pos.x - closest_x
        dz = player_pos.z - closest_z
        horizontal_distance = math.sqrt(dx*dx + dz*dz)
        
        # Проверяем пересечение по вертикали
        vertical_overlap = (player_pos.y < wall_bb.max.y and 
                           player_pos.y + player_height > wall_bb.min.y)
        
        return horizontal_distance < player_radius and vertical_overlap

class Staircase:
    """Лестница между этажами"""
    def __init__(self, x=0, z=0, width=2, depth=6, height=5, steps=12):
        self.position = Vector3(x, 0, z)
        self.width = width
        self.depth = depth
        self.height = height
        self.steps = steps
        self.step_height = height / steps
        self.step_depth = depth / steps
        self.color = (0.6, 0.4, 0.2, 1)
    
    def get_bounding_box(self):
        """Возвращает ограничивающую рамку всей лестницы"""
        w2 = self.width / 2
        d2 = self.depth / 2
        
        return BoundingBox(
            Vector3(self.position.x - w2, 
                   self.position.y, 
                   self.position.z - d2),
            Vector3(self.position.x + w2, 
                   self.position.y + self.height, 
                   self.position.z + d2)
        )
    
    def get_steps_vertices(self):
        """Возвращает вершины всех ступенек"""
        steps_vertices = []
        
        for i in range(self.steps):
            step_y = i * self.step_height
            step_z = i * self.step_depth
            
            w2 = self.width / 2
            vertices = [
                Vector3(-w2, step_y, -self.depth/2 + step_z),
                Vector3(w2, step_y, -self.depth/2 + step_z),
                Vector3(w2, step_y, -self.depth/2 + step_z + self.step_depth),
                Vector3(-w2, step_y, -self.depth/2 + step_z + self.step_depth),
                Vector3(-w2, step_y + self.step_height, -self.depth/2 + step_z),
                Vector3(w2, step_y + self.step_height, -self.depth/2 + step_z),
                Vector3(w2, step_y + self.step_height, -self.depth/2 + step_z + self.step_depth),
                Vector3(-w2, step_y + self.step_height, -self.depth/2 + step_z + self.step_depth)
            ]
            
            for j in range(8):
                vertices[j] = vertices[j] + self.position
            
            steps_vertices.append(vertices)
        
        return steps_vertices
    
    def is_player_near(self, player_pos, radius=3.0):
        """Проверяет, находится ли игрок рядом с лестницей"""
        distance = math.sqrt(
            (player_pos.x - self.position.x)**2 +
            (player_pos.z - self.position.z)**2
        )
        return distance < radius and player_pos.y < self.height + 2

class Game3D(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Текущий этаж
        self.current_floor = 1
        self.floor_height = 5
        
        # Создаем камеру
        self.camera = Camera()
        self.camera.update_vectors()
        
        # Создаем лабиринт
        self.walls_first_floor = []
        self.walls_second_floor = []
        self.create_maze()
        
        # Создаем лестницу
        self.staircase = Staircase(x=-5, z=-5, width=3, depth=8, height=5, steps=15)
        
        # Создаем пол
        self.create_floors()
        
        # Управление
        self.keys_pressed = set()
        self.last_mouse_pos = None
        self.mouse_sensitivity = 0.003
        
        # Простая переменная для прыжка
        self.space_pressed = False
        
        # FPS счетчик
        self.frame_count = 0
        self.fps = 0
        self.fps_timer = 0
        
        # UI
        self.setup_ui()
        
        # Отладочная информация о столкновениях
        self.collision_info = "Нет столкновений"
        self.collision_count = 0
        
        # Настройка ввода
        self.setup_input()
        
        # Запуск игрового цикла
        Clock.schedule_interval(self.update, 1.0 / 60.0)
    
    def create_maze(self):
        """Создание простого лабиринта для двух этажей"""
        maze_size = 10
        cell_size = 4
        wall_height = 3
        
        # Первый этаж - больше стен
        maze_layout_first = [
            [1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,1,1,1,0,1],
            [1,0,0,0,0,0,0,1,0,1],
            [1,0,1,1,1,1,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1]
        ]
        
        # Второй этаж - другой лабиринт
        maze_layout_second = [
            [1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,0,0,0,0,0,0,1],
            [1,0,1,0,0,0,0,0,0,1],
            [1,0,1,0,0,0,0,0,0,1],
            [1,0,1,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,0,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1]
        ]
        
        for x in range(maze_size):
            for z in range(maze_size):
                if maze_layout_first[x][z] == 1:
                    wall_x = (x - maze_size/2) * cell_size
                    wall_z = (z - maze_size/2) * cell_size
                    wall = Wall(wall_x, 0, wall_z, cell_size, cell_size, wall_height)
                    self.walls_first_floor.append(wall)
        
        for x in range(maze_size):
            for z in range(maze_size):
                if maze_layout_second[x][z] == 1:
                    wall_x = (x - maze_size/2) * cell_size
                    wall_z = (z - maze_size/2) * cell_size
                    wall = Wall(wall_x, self.floor_height, wall_z, cell_size, cell_size, wall_height)
                    self.walls_second_floor.append(wall)
        
        # Добавляем несколько случайных стен для тестирования коллизий
        for _ in range(5):
            wall = Wall(
                random.uniform(-15, 15),
                0,
                random.uniform(-15, 15),
                random.uniform(2, 4),
                random.uniform(2, 4),
                wall_height
            )
            self.walls_first_floor.append(wall)
        
        print(f"Создано стен: 1 этаж - {len(self.walls_first_floor)}, 2 этаж - {len(self.walls_second_floor)}")
    
    def create_floors(self):
        """Создание полов для двух этажей"""
        self.floor_lines = []
        size = 25
        step = 2
        
        for i in range(-size, size + 1, step):
            self.floor_lines.append((
                Vector3(-size, 0, i),
                Vector3(size, 0, i)
            ))
            self.floor_lines.append((
                Vector3(i, 0, -size),
                Vector3(i, 0, size)
            ))
        
        for i in range(-size, size + 1, step):
            self.floor_lines.append((
                Vector3(-size, self.floor_height, i),
                Vector3(size, self.floor_height, i)
            ))
            self.floor_lines.append((
                Vector3(i, self.floor_height, -size),
                Vector3(i, self.floor_height, size)
            ))
    
    def setup_ui(self):
        """Настройка интерфейса"""
        from kivy.uix.label import Label
        
        self.fps_label = Label(
            text='FPS: 0',
            font_size='14sp',
            color=(1, 1, 1, 1),
            pos_hint={'right': 0.98, 'top': 0.98},
            size_hint=(None, None),
            size=(100, 30)
        )
        self.add_widget(self.fps_label)
        
        self.instructions = Label(
            text='WASD: Движение | Мышка: Вращение | ПРОБЕЛ: ПРЫЖОК | Shift: Бег | На лестнице: W/S | ESC: Выход',
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 0.8),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            size_hint=(None, None),
            size=(700, 30)
        )
        self.add_widget(self.instructions)
        
        self.pos_label = Label(
            text='X: 0 Y: 1.8 Z: 0 Этаж: 1',
            font_size='14sp',
            color=(0.6, 0.8, 1.0, 0.8),
            pos_hint={'x': 0.02, 'y': 0.02},
            size_hint=(None, None),
            size=(250, 30)
        )
        self.add_widget(self.pos_label)
        
        self.state_label = Label(
            text='На земле',
            font_size='14sp',
            color=(0.8, 1.0, 0.6, 0.8),
            pos_hint={'x': 0.02, 'y': 0.06},
            size_hint=(None, None),
            size=(200, 30)
        )
        self.add_widget(self.state_label)
        
        self.jump_label = Label(
            text='Прыжков: 0/2',
            font_size='14sp',
            color=(1.0, 0.8, 0.6, 0.8),
            pos_hint={'right': 0.98, 'y': 0.06},
            size_hint=(None, None),
            size=(150, 30)
        )
        self.add_widget(self.jump_label)
        
        self.collision_label = Label(
            text='Столкновений: 0',
            font_size='12sp',
            color=(1.0, 0.6, 0.6, 0.8),
            pos_hint={'right': 0.98, 'y': 0.1},
            size_hint=(None, None),
            size=(150, 30)
        )
        self.add_widget(self.collision_label)
        
        self.debug_label = Label(
            text='DEBUG: Коллизии активны',
            font_size='12sp',
            color=(0.6, 1.0, 0.6, 0.8),
            pos_hint={'x': 0.02, 'top': 0.98},
            size_hint=(None, None),
            size=(300, 30)
        )
        self.add_widget(self.debug_label)
    
    def setup_input(self):
        """Настройка ввода"""
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)
        
        Window.bind(mouse_pos=self._on_mouse_move)
        Window.show_cursor = False
    
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1].lower()
        
        if key == 'escape':
            App.get_running_app().stop()
        elif key == 'space':
            # НАЖИМАЕМ ПРОБЕЛ - СРАЗУ ПРЫГАЕМ!
            if not self.camera.on_stairs and self.camera.jump_count < self.camera.max_jumps:
                self.camera.jump()
                self.space_pressed = True
        elif key in ['w', 'a', 's', 'd', 'shift', 'left', 'right', 'up', 'down']:
            self.keys_pressed.add(key)
        
        return True
    
    def _on_keyboard_up(self, keyboard, keycode):
        key = keycode[1].lower()
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
        
        if key == 'space':
            self.space_pressed = False
        
        return True
    
    def _on_mouse_move(self, window, pos):
        if self.last_mouse_pos:
            dx = pos[0] - self.last_mouse_pos[0]
            dy = pos[1] - self.last_mouse_pos[1]
            
            self.camera.look(dx, -dy)
        
        self.last_mouse_pos = pos
    
    def check_stair_collision(self):
        """Проверяет столкновение с лестницей"""
        if self.staircase.is_player_near(self.camera.position):
            # Если игрок достаточно близко к лестнице, он может по ней двигаться
            self.camera.on_stairs = True
            return True
        
        self.camera.on_stairs = False
        return False
    
    def check_collisions_debug(self):
        """Отладочная проверка столкновений"""
        self.collision_count = 0
        walls = self.walls_first_floor if self.current_floor == 1 else self.walls_second_floor
        
        for wall in walls:
            if wall.is_player_colliding(self.camera.position, self.camera.radius, self.camera.height):
                self.collision_count += 1
        
        self.collision_label.text = f'Столкновений: {self.collision_count}'
    
    def update(self, dt):
        """Игровой цикл"""
        # Счетчик FPS
        self.frame_count += 1
        self.fps_timer += dt
        if self.fps_timer >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_timer = 0
            self.fps_label.text = f'FPS: {self.fps}'
        
        # Определяем текущий этаж
        if self.camera.position.y < self.floor_height + 1.0:
            self.current_floor = 1
            floor_y = 0
            current_walls = self.walls_first_floor
        else:
            self.current_floor = 2
            floor_y = self.floor_height
            current_walls = self.walls_second_floor
        
        # Проверяем столкновение с лестницей
        on_stairs = self.check_stair_collision()
        
        # Определяем направление движения
        move_x = 0
        move_z = 0
        stair_move = 0
        
        if 'w' in self.keys_pressed:
            if on_stairs:
                stair_move += 1
            else:
                move_z += 1
        if 's' in self.keys_pressed:
            if on_stairs:
                stair_move -= 1
            else:
                move_z -= 1
        if 'a' in self.keys_pressed and not on_stairs:
            move_x -= 1
        if 'd' in self.keys_pressed and not on_stairs:
            move_x += 1
        
        # Движение по лестнице
        if on_stairs and stair_move != 0:
            self.camera.move_on_stairs(stair_move, dt)
        
        # Применяем движение
        if not on_stairs and (move_x != 0 or move_z != 0):
            self.camera.move(move_x, move_z, dt, on_stairs)
        
        # Бег
        if 'shift' in self.keys_pressed and not on_stairs:
            self.camera.run(True)
        else:
            self.camera.run(False)
        
        # ПРЫЖОК УЖЕ ОБРАБОТАН В _on_keyboard_down - моментальный прыжок при нажатии!
        
        # Обновление физики камеры С УЧЕТОМ СТОЛКНОВЕНИЙ СО СТЕНАМИ
        self.camera.update_physics(dt, current_walls, floor_y)
        
        # Проверяем столкновения для отладки
        self.check_collisions_debug()
        
        # Поворот камеры
        if 'left' in self.keys_pressed:
            self.camera.rotate_with_keys(-1, 0)
        if 'right' in self.keys_pressed:
            self.camera.rotate_with_keys(1, 0)
        if 'up' in self.keys_pressed:
            self.camera.rotate_with_keys(0, 1)
        if 'down' in self.keys_pressed:
            self.camera.rotate_with_keys(0, -1)
        
        # Обновление UI
        cam = self.camera.position
        floor_text = f'Этаж: {self.current_floor}'
        self.pos_label.text = f'X: {cam.x:.1f} Y: {cam.y:.1f} Z: {cam.z:.1f} {floor_text}'
        
        # Отображаем состояние
        if on_stairs:
            self.state_label.text = 'На лестнице'
        elif self.camera.grounded:
            speed = math.sqrt(self.camera.velocity.x**2 + self.camera.velocity.z**2)
            if speed > 5:
                self.state_label.text = 'Бежит'
            elif speed > 0.1:
                self.state_label.text = 'Идет'
            else:
                self.state_label.text = 'Стоит'
        else:
            vertical_speed = self.camera.velocity.y
            if vertical_speed > 0:
                self.state_label.text = 'Прыжок ↑'
            else:
                self.state_label.text = 'Падение ↓'
        
        # Отображаем состояние прыжка
        self.jump_label.text = f'Прыжков: {self.camera.jump_count}/{self.camera.max_jumps}'
        
        # Отрисовка
        self.draw()
    
    def draw(self):
        """Отрисовка сцены"""
        self.canvas.clear()
        
        with self.canvas:
            # Темный фон
            Color(0.05, 0.05, 0.05, 1)
            Rectangle(pos=(0, 0), size=(self.width, self.height))
            
            # Рисуем пол первого этажа
            Color(0.3, 0.3, 0.3, 1)
            ground_size = 50
            ground_vertices = [
                Vector3(-ground_size, 0, -ground_size),
                Vector3(ground_size, 0, -ground_size),
                Vector3(ground_size, 0, ground_size),
                Vector3(-ground_size, 0, ground_size)
            ]
            
            proj_ground = []
            for v in ground_vertices:
                proj = self.project_to_screen(v, self.camera)
                if proj[2] > 0.1:
                    proj_ground.append((proj[0], proj[1]))
            
            if len(proj_ground) >= 4:
                Mesh(
                    vertices=[
                        proj_ground[0][0], proj_ground[0][1], 0, 0,
                        proj_ground[1][0], proj_ground[1][1], 0, 0,
                        proj_ground[2][0], proj_ground[2][1], 0, 0,
                        proj_ground[3][0], proj_ground[3][1], 0, 0
                    ],
                    indices=[0, 1, 2, 0, 2, 3],
                    mode='triangles'
                )
            
            # Рисуем пол второго этажа
            Color(0.35, 0.35, 0.35, 1)
            second_floor_vertices = [
                Vector3(-ground_size, self.floor_height, -ground_size),
                Vector3(ground_size, self.floor_height, -ground_size),
                Vector3(ground_size, self.floor_height, ground_size),
                Vector3(-ground_size, self.floor_height, ground_size)
            ]
            
            proj_second_floor = []
            for v in second_floor_vertices:
                proj = self.project_to_screen(v, self.camera)
                if proj[2] > 0.1:
                    proj_second_floor.append((proj[0], proj[1]))
            
            if len(proj_second_floor) >= 4:
                Mesh(
                    vertices=[
                        proj_second_floor[0][0], proj_second_floor[0][1], 0, 0,
                        proj_second_floor[1][0], proj_second_floor[1][1], 0, 0,
                        proj_second_floor[2][0], proj_second_floor[2][1], 0, 0,
                        proj_second_floor[3][0], proj_second_floor[3][1], 0, 0
                    ],
                    indices=[0, 1, 2, 0, 2, 3],
                    mode='triangles'
                )
            
            # Рисуем сетку пола
            Color(0.4, 0.4, 0.4, 0.5)
            for line in self.floor_lines:
                p1 = line[0]
                p2 = line[1]
                
                proj1 = self.project_to_screen(p1, self.camera)
                proj2 = self.project_to_screen(p2, self.camera)
                
                if proj1[2] > 0.1 and proj2[2] > 0.1:
                    Line(points=[proj1[0], proj1[1], proj2[0], proj2[1]], width=1)
            
            # Рисуем стены первого этажа
            for wall in self.walls_first_floor:
                self.draw_wall(wall, self.camera)
            
            # Рисуем стены второго этажа
            for wall in self.walls_second_floor:
                self.draw_wall(wall, self.camera)
            
            # Рисуем лестницу
            self.draw_staircase(self.staircase, self.camera)
            
            # Отладочная отрисовка коллизий игрока
            if self.collision_count > 0:
                Color(1.0, 0.2, 0.2, 0.3)
                player_bb = self.camera.get_bounding_box()
                self.draw_bounding_box(player_bb, self.camera)
    
    def draw_bounding_box(self, bbox, camera):
        """Отрисовка ограничивающей рамки для отладки"""
        vertices = [
            Vector3(bbox.min.x, bbox.min.y, bbox.min.z),
            Vector3(bbox.max.x, bbox.min.y, bbox.min.z),
            Vector3(bbox.max.x, bbox.min.y, bbox.max.z),
            Vector3(bbox.min.x, bbox.min.y, bbox.max.z),
            Vector3(bbox.min.x, bbox.max.y, bbox.min.z),
            Vector3(bbox.max.x, bbox.max.y, bbox.min.z),
            Vector3(bbox.max.x, bbox.max.y, bbox.max.z),
            Vector3(bbox.min.x, bbox.max.y, bbox.max.z)
        ]
        
        # Проектируем вершины
        proj_vertices = []
        for v in vertices:
            proj = self.project_to_screen(v, camera)
            if proj[2] > 0.1:
                proj_vertices.append((proj[0], proj[1]))
            else:
                return
        
        if len(proj_vertices) < 8:
            return
        
        # Рисуем линии рамки
        edges = [
            (0,1), (1,2), (2,3), (3,0),  # нижний квадрат
            (4,5), (5,6), (6,7), (7,4),  # верхний квадрат
            (0,4), (1,5), (2,6), (3,7)   # вертикальные линии
        ]
        
        for edge in edges:
            Line(points=[
                proj_vertices[edge[0]][0], proj_vertices[edge[0]][1],
                proj_vertices[edge[1]][0], proj_vertices[edge[1]][1]
            ], width=1.5)
    
    def draw_staircase(self, staircase, camera):
        """Отрисовка лестницы"""
        with self.canvas:
            steps_vertices = staircase.get_steps_vertices()
            
            for step_idx, vertices in enumerate(steps_vertices):
                step_color = (
                    staircase.color[0] * (1 - step_idx/staircase.steps * 0.3),
                    staircase.color[1] * (1 - step_idx/staircase.steps * 0.3),
                    staircase.color[2],
                    staircase.color[3]
                )
                
                Color(*step_color)
                
                faces = [
                    [vertices[4], vertices[5], vertices[6], vertices[7]],
                    [vertices[4], vertices[5], vertices[1], vertices[0]],
                    [vertices[5], vertices[1], vertices[2], vertices[6]],
                    [vertices[4], vertices[0], vertices[3], vertices[7]]
                ]
                
                for face in faces:
                    proj_vertices = []
                    all_behind = False
                    
                    for v in face:
                        proj = self.project_to_screen(v, camera)
                        if proj[2] <= 0.1:
                            all_behind = True
                            break
                        proj_vertices.append((proj[0], proj[1]))
                    
                    if all_behind or len(proj_vertices) < 4:
                        continue
                    
                    Mesh(
                        vertices=[
                            proj_vertices[0][0], proj_vertices[0][1], 0, 0,
                            proj_vertices[1][0], proj_vertices[1][1], 0, 0,
                            proj_vertices[2][0], proj_vertices[2][1], 0, 0,
                            proj_vertices[3][0], proj_vertices[3][1], 0, 0
                        ],
                        indices=[0, 1, 2, 0, 2, 3],
                        mode='triangles'
                    )
    
    def draw_wall(self, wall, camera):
        """Отрисовка стены лабиринта"""
        with self.canvas:
            faces = wall.get_faces()
            face_colors = [
                (0.6, 0.6, 0.6, 1),
                (0.5, 0.5, 0.5, 1),
                (0.7, 0.7, 0.7, 1),
                (0.7, 0.7, 0.7, 1),
                (0.8, 0.8, 0.8, 1),
                (0.4, 0.4, 0.4, 1),
            ]
            
            faces_to_draw = []
            
            for i, face in enumerate(faces):
                vertices_2d = []
                avg_z = 0
                all_behind = False
                
                for v in face:
                    proj = self.project_to_screen(v, camera)
                    if proj[2] <= 0.1:
                        all_behind = True
                        break
                    vertices_2d.append((proj[0], proj[1]))
                    avg_z += proj[2]
                
                if all_behind:
                    continue
                
                avg_z /= 4
                
                faces_to_draw.append({
                    'vertices': vertices_2d,
                    'color': face_colors[i],
                    'z': avg_z
                })
            
            faces_to_draw.sort(key=lambda f: f['z'], reverse=True)
            
            for face in faces_to_draw:
                Color(*face['color'])
                
                if len(face['vertices']) >= 4:
                    Mesh(
                        vertices=[
                            face['vertices'][0][0], face['vertices'][0][1], 0, 0,
                            face['vertices'][1][0], face['vertices'][1][1], 0, 0,
                            face['vertices'][2][0], face['vertices'][2][1], 0, 0,
                            face['vertices'][3][0], face['vertices'][3][1], 0, 0
                        ],
                        indices=[0, 1, 2, 0, 2, 3],
                        mode='triangles'
                    )
            
            # Отладочная отрисовка коллизий стен (только при столкновениях)
            if self.collision_count > 0:
                # Проверяем, сталкивается ли игрок с этой стеной
                if wall.is_player_colliding(self.camera.position, self.camera.radius, self.camera.height):
                    Color(1.0, 0.0, 0.0, 0.3)
                    wall_bb = wall.get_bounding_box()
                    self.draw_bounding_box(wall_bb, camera)
    
    def project_to_screen(self, point, camera):
        """Проекция 3D точки на экран"""
        dx = point.x - camera.position.x
        dy = point.y - camera.position.y
        dz = point.z - camera.position.z
        
        cos_y = math.cos(-camera.rotation.y)
        sin_y = math.sin(-camera.rotation.y)
        cos_x = math.cos(-camera.rotation.x)
        sin_x = math.sin(-camera.rotation.x)
        
        x = dx * cos_y + dz * sin_y
        z = -dx * sin_y + dz * cos_y
        
        y = dy * cos_x - z * sin_x
        z = dy * sin_x + z * cos_x
        
        if z > 0.1:
            factor = 500 / z
            screen_x = x * factor + self.width / 2
            screen_y = y * factor + self.height / 2
        else:
            screen_x = x * 5000 + self.width / 2
            screen_y = y * 5000 + self.height / 2
        
        return (screen_x, screen_y, z)

class TwoFloorMazeApp(App):
    def build(self):
        self.title = "Двухэтажный 3D Лабиринт с ФИЗИКОЙ СТЕН - ПРОБЕЛ = ПРЫЖОК!"
        return Game3D()

if __name__ == '__main__':
    TwoFloorMazeApp().run()
