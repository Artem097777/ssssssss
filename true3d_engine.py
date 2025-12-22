import math
import random
from kivy.graphics import Mesh, Color, Rectangle, Line, PushMatrix, PopMatrix, Rotate, Translate, Scale
from kivy.graphics.transformation import Matrix

class Vector3:
    """3D вектор с математическими операциями"""
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
    
    def __truediv__(self, scalar):
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def dot(self, other):
        """Скалярное произведение"""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        """Векторное произведение"""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def length(self):
        """Длина вектора"""
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
    
    def normalize(self):
        """Нормализация"""
        l = self.length()
        if l > 0:
            return Vector3(self.x/l, self.y/l, self.z/l)
        return Vector3(0, 0, 0)
    
    def rotate_x(self, angle):
        """Вращение вокруг оси X"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        y = self.y * cos_a - self.z * sin_a
        z = self.y * sin_a + self.z * cos_a
        return Vector3(self.x, y, z)
    
    def rotate_y(self, angle):
        """Вращение вокруг оси Y"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        x = self.x * cos_a + self.z * sin_a
        z = -self.x * sin_a + self.z * cos_a
        return Vector3(x, self.y, z)
    
    def rotate_z(self, angle):
        """Вращение вокруг оси Z"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        x = self.x * cos_a - self.y * sin_a
        y = self.x * sin_a + self.y * cos_a
        return Vector3(x, y, self.z)
    
    def distance_to(self, other):
        """Расстояние до другой точки"""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def to_tuple(self):
        return (self.x, self.y, self.z)
    
    def copy(self):
        return Vector3(self.x, self.y, self.z)

class Matrix4:
    """4x4 матрица для 3D преобразований"""
    def __init__(self, matrix=None):
        if matrix is None:
            self.matrix = [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ]
        else:
            self.matrix = matrix
    
    @staticmethod
    def perspective(fov, aspect, near, far):
        """Матрица перспективной проекции"""
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        return Matrix4([
            [f/aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
            [0, 0, -1, 0]
        ])
    
    @staticmethod
    def look_at(eye, target, up):
        """Матрица вида (look at)"""
        z = (eye - target).normalize()
        x = up.cross(z).normalize()
        y = z.cross(x)
        
        return Matrix4([
            [x.x, x.y, x.z, -x.dot(eye)],
            [y.x, y.y, y.z, -y.dot(eye)],
            [z.x, z.y, z.z, -z.dot(eye)],
            [0, 0, 0, 1]
        ])
    
    def multiply_vector(self, v):
        """Умножение матрицы на вектор"""
        x = v.x * self.matrix[0][0] + v.y * self.matrix[0][1] + v.z * self.matrix[0][2] + self.matrix[0][3]
        y = v.x * self.matrix[1][0] + v.y * self.matrix[1][1] + v.z * self.matrix[1][2] + self.matrix[1][3]
        z = v.x * self.matrix[2][0] + v.y * self.matrix[2][1] + v.z * self.matrix[2][2] + self.matrix[2][3]
        w = v.x * self.matrix[3][0] + v.y * self.matrix[3][1] + v.z * self.matrix[3][2] + self.matrix[3][3]
        
        if w != 0:
            return Vector3(x/w, y/w, z/w)
        return Vector3(x, y, z)
    
    def multiply(self, other):
        """Умножение матриц"""
        result = [[0]*4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                result[i][j] = (
                    self.matrix[i][0] * other.matrix[0][j] +
                    self.matrix[i][1] * other.matrix[1][j] +
                    self.matrix[i][2] * other.matrix[2][j] +
                    self.matrix[i][3] * other.matrix[3][j]
                )
        return Matrix4(result)

class Triangle:
    """Треугольник для полигонального рендеринга"""
    def __init__(self, v1, v2, v3, color):
        self.vertices = [v1, v2, v3]
        self.color = color
        self.normal = None
        self.calculate_normal()
    
    def calculate_normal(self):
        """Вычисление нормали треугольника"""
        v1 = self.vertices[0]
        v2 = self.vertices[1]
        v3 = self.vertices[2]
        
        edge1 = v2 - v1
        edge2 = v3 - v1
        self.normal = edge1.cross(edge2).normalize()
    
    def get_center(self):
        """Центр треугольника"""
        return (self.vertices[0] + self.vertices[1] + self.vertices[2]) / 3
    
    def is_facing_camera(self, camera_pos):
        """Проверка, смотрит ли треугольник на камеру"""
        center = self.get_center()
        view_dir = (camera_pos - center).normalize()
        return self.normal.dot(view_dir) < 0

class Mesh3D:
    """3D модель из треугольников"""
    def __init__(self):
        self.triangles = []
        self.position = Vector3(0, 0, 0)
        self.rotation = Vector3(0, 0, 0)
        self.scale = Vector3(1, 1, 1)
        self.color = [1, 1, 1, 1]
    
    def create_cube(self, size=1):
        """Создание куба"""
        s = size / 2
        vertices = [
            Vector3(-s, -s, -s), Vector3(s, -s, -s), Vector3(s, s, -s), Vector3(-s, s, -s),  # Задняя грань
            Vector3(-s, -s, s), Vector3(s, -s, s), Vector3(s, s, s), Vector3(-s, s, s)       # Передняя грань
        ]
        
        # Грани куба (каждая грань - 2 треугольника)
        faces = [
            # Задняя грань
            (0, 1, 2, [0.8, 0.2, 0.2, 1]),  # Красная
            (0, 2, 3, [0.8, 0.2, 0.2, 1]),
            
            # Передняя грань
            (4, 5, 6, [0.2, 0.8, 0.2, 1]),  # Зеленая
            (4, 6, 7, [0.2, 0.8, 0.2, 1]),
            
            # Левая грань
            (0, 3, 7, [0.2, 0.2, 0.8, 1]),  # Синяя
            (0, 7, 4, [0.2, 0.2, 0.8, 1]),
            
            # Правая грань
            (1, 5, 6, [0.8, 0.8, 0.2, 1]),  # Желтая
            (1, 6, 2, [0.8, 0.8, 0.2, 1]),
            
            # Верхняя грань
            (3, 2, 6, [0.8, 0.2, 0.8, 1]),  # Пурпурная
            (3, 6, 7, [0.8, 0.2, 0.8, 1]),
            
            # Нижняя грань
            (0, 1, 5, [0.2, 0.8, 0.8, 1]),  # Голубая
            (0, 5, 4, [0.2, 0.8, 0.8, 1])
        ]
        
        for face in faces:
            v1_idx, v2_idx, v3_idx, color = face
            triangle = Triangle(
                vertices[v1_idx].copy(),
                vertices[v2_idx].copy(),
                vertices[v3_idx].copy(),
                color
            )
            self.triangles.append(triangle)
    
    def create_pyramid(self, height=1, base_size=1):
        """Создание пирамиды"""
        s = base_size / 2
        vertices = [
            Vector3(-s, 0, -s),  # 0 - левый нижний зад
            Vector3(s, 0, -s),   # 1 - правый нижний зад
            Vector3(s, 0, s),    # 2 - правый нижний перед
            Vector3(-s, 0, s),   # 3 - левый нижний перед
            Vector3(0, height, 0) # 4 - вершина
        ]
        
        # Грани пирамиды
        faces = [
            # Основание
            (0, 1, 2, [0.5, 0.5, 0.5, 1]),
            (0, 2, 3, [0.5, 0.5, 0.5, 1]),
            
            # Боковые грани
            (0, 1, 4, [1, 0.5, 0, 1]),  # Оранжевая
            (1, 2, 4, [1, 0.8, 0, 1]),  # Светло-оранжевая
            (2, 3, 4, [1, 0.5, 0, 1]),
            (3, 0, 4, [1, 0.8, 0, 1])
        ]
        
        for face in faces:
            v1_idx, v2_idx, v3_idx, color = face
            triangle = Triangle(
                vertices[v1_idx].copy(),
                vertices[v2_idx].copy(),
                vertices[v3_idx].copy(),
                color
            )
            self.triangles.append(triangle)
    
    def create_sphere(self, radius=1, segments=8):
        """Создание сферы (аппроксимация)"""
        vertices = []
        
        # Создание вершин сферы
        for i in range(segments + 1):
            lat = math.pi * i / segments
            for j in range(segments):
                lon = 2 * math.pi * j / segments
                
                x = radius * math.sin(lat) * math.cos(lon)
                y = radius * math.cos(lat)
                z = radius * math.sin(lat) * math.sin(lon)
                
                vertices.append(Vector3(x, y, z))
        
        # Создание треугольников
        for i in range(segments):
            for j in range(segments):
                v1 = i * segments + j
                v2 = i * segments + (j + 1) % segments
                v3 = (i + 1) * segments + j
                v4 = (i + 1) * segments + (j + 1) % segments
                
                # Цвет зависит от высоты
                color = [0.2, 0.6, 1.0, 1.0] if i < segments/2 else [0.1, 0.4, 0.8, 1.0]
                
                # Два треугольника на ячейку
                self.triangles.append(Triangle(
                    vertices[v1].copy(), vertices[v2].copy(), vertices[v3].copy(), color
                ))
                self.triangles.append(Triangle(
                    vertices[v2].copy(), vertices[v4].copy(), vertices[v3].copy(), color
                ))
    
    def transform_vertex(self, vertex):
        """Применение преобразований к вершине"""
        # Масштабирование
        v = Vector3(
            vertex.x * self.scale.x,
            vertex.y * self.scale.y,
            vertex.z * self.scale.z
        )
        
        # Вращение
        v = v.rotate_x(self.rotation.x)
        v = v.rotate_y(self.rotation.y)
        v = v.rotate_z(self.rotation.z)
        
        # Позиционирование
        v = v + self.position
        
        return v
    
    def update(self, dt):
        """Обновление анимации"""
        self.rotation.y += dt * 1.0
        self.rotation.x += dt * 0.5

class Camera3D:
    """3D камера с управлением от первого лица"""
    def __init__(self):
        self.position = Vector3(0, 1.7, 0)  # Рост человека
        self.rotation = Vector3(0, 0, 0)    # Углы Эйлера (pitch, yaw, roll)
        
        self.move_speed = 5.0
        self.look_speed = 0.003
        self.fov = 70
        self.near = 0.1
        self.far = 100.0
        
        self.forward = Vector3(0, 0, 1)
        self.right = Vector3(1, 0, 0)
        self.up = Vector3(0, 1, 0)
        
        self.update_vectors()
    
    def update_vectors(self):
        """Обновление векторов направления"""
        # Вычисляем направление взгляда из углов Эйлера
        self.forward = Vector3(
            math.sin(self.rotation.y) * math.cos(self.rotation.x),
            math.sin(self.rotation.x),
            math.cos(self.rotation.y) * math.cos(self.rotation.x)
        ).normalize()
        
        self.right = Vector3(0, 1, 0).cross(self.forward).normalize()
        self.up = self.forward.cross(self.right).normalize()
    
    def move_forward(self, dt):
        self.position += self.forward * self.move_speed * dt
    
    def move_backward(self, dt):
        self.position -= self.forward * self.move_speed * dt
    
    def move_left(self, dt):
        self.position -= self.right * self.move_speed * dt
    
    def move_right(self, dt):
        self.position += self.right * self.move_speed * dt
    
    def move_up(self, dt):
        self.position += Vector3(0, 1, 0) * self.move_speed * dt
    
    def move_down(self, dt):
        self.position -= Vector3(0, 1, 0) * self.move_speed * dt
    
    def rotate_with_keys(self, dx, dy):
        """Вращение камеры с помощью клавиш"""
        self.rotation.y += dx * self.look_speed * 50  # Горизонтальное вращение
        self.rotation.x += dy * self.look_speed * 50  # Вертикальное вращение (вверх/вниз)
        
        # Ограничиваем вертикальный поворот (нельзя смотреть выше 90 градусов вверх или вниз)
        self.rotation.x = max(-math.pi/2 + 0.01, min(math.pi/2 - 0.01, self.rotation.x))
        
        self.update_vectors()
    
    def look(self, dx, dy):
        """Поворот камеры мышью"""
        self.rotation.y += dx * self.look_speed  # Горизонтальное вращение
        self.rotation.x += dy * self.look_speed  # Вертикальное вращение (вверх/вниз)
        
        # Ограничиваем вертикальный поворот
        self.rotation.x = max(-math.pi/2 + 0.01, min(math.pi/2 - 0.01, self.rotation.x))
        
        self.update_vectors()
    
    def get_view_matrix(self):
        """Получить матрицу вида"""
        target = self.position + self.forward
        return Matrix4.look_at(self.position, target, Vector3(0, 1, 0))
    
    def get_projection_matrix(self, aspect_ratio):
        """Получить матрицу проекции"""
        return Matrix4.perspective(self.fov, aspect_ratio, self.near, self.far)

class GridMap:
    """Карта с сеткой и объектами"""
    def __init__(self, width=40, depth=40, cell_size=2):
        self.width = width
        self.depth = depth
        self.cell_size = cell_size
        self.grid = []
        self.objects = []
        
        self.create_grid()
        self.place_objects()
    
    def create_grid(self):
        """Создание сетки карты"""
        half_width = self.width * self.cell_size / 2
        half_depth = self.depth * self.cell_size / 2
        
        # Создаем пол с текстурой сетки
        for x in range(self.width):
            for z in range(self.depth):
                # Координаты центра ячейки
                cell_x = -half_width + x * self.cell_size + self.cell_size / 2
                cell_z = -half_depth + z * self.cell_size + self.cell_size / 2
                
                # Цвет ячейки (шахматный порядок)
                if (x + z) % 2 == 0:
                    color = [0.7, 0.7, 0.7, 1]  # Светло-серый
                else:
                    color = [0.5, 0.5, 0.5, 1]  # Темно-серый
                
                # Создаем квадрат (2 треугольника)
                half_cell = self.cell_size / 2
                vertices = [
                    Vector3(cell_x - half_cell, 0, cell_z - half_cell),
                    Vector3(cell_x + half_cell, 0, cell_z - half_cell),
                    Vector3(cell_x + half_cell, 0, cell_z + half_cell),
                    Vector3(cell_x - half_cell, 0, cell_z + half_cell)
                ]
                
                self.grid.append({
                    'x': cell_x,
                    'z': cell_z,
                    'triangles': [
                        Triangle(vertices[0], vertices[1], vertices[2], color),
                        Triangle(vertices[0], vertices[2], vertices[3], color)
                    ]
                })
    
    def place_objects(self):
        """Размещение объектов на карте"""
        half_width = self.width * self.cell_size / 2
        half_depth = self.depth * self.cell_size / 2
        
        # Создаем стены по краям карты
        wall_height = 3
        wall_color = [0.4, 0.4, 0.4, 1]
        
        # Северная стена (z = -half_depth)
        for x in range(self.width):
            if x % 4 == 0:  # Размещаем стены через каждые 4 ячейки
                wall_x = -half_width + x * self.cell_size + self.cell_size / 2
                wall_z = -half_depth
                self.objects.append(self.create_wall_segment(wall_x, wall_z, wall_height, wall_color, 'north'))
        
        # Южная стена (z = half_depth)
        for x in range(self.width):
            if x % 4 == 0:
                wall_x = -half_width + x * self.cell_size + self.cell_size / 2
                wall_z = half_depth
                self.objects.append(self.create_wall_segment(wall_x, wall_z, wall_height, wall_color, 'south'))
        
        # Западная стена (x = -half_width)
        for z in range(self.depth):
            if z % 4 == 0:
                wall_x = -half_width
                wall_z = -half_depth + z * self.cell_size + self.cell_size / 2
                self.objects.append(self.create_wall_segment(wall_x, wall_z, wall_height, wall_color, 'west'))
        
        # Восточная стена (x = half_width)
        for z in range(self.depth):
            if z % 4 == 0:
                wall_x = half_width
                wall_z = -half_depth + z * self.cell_size + self.cell_size / 2
                self.objects.append(self.create_wall_segment(wall_x, wall_z, wall_height, wall_color, 'east'))
        
        # Случайные колонны
        for _ in range(20):
            col_x = random.uniform(-half_width + 5, half_width - 5)
            col_z = random.uniform(-half_depth + 5, half_depth - 5)
            col_height = random.uniform(2, 5)
            col_radius = random.uniform(0.3, 0.8)
            self.objects.append(self.create_column(col_x, col_z, col_height, col_radius))
        
        # Платформы
        for _ in range(10):
            plat_x = random.uniform(-half_width + 5, half_width - 5)
            plat_z = random.uniform(-half_depth + 5, half_depth - 5)
            plat_height = random.uniform(1, 3)
            plat_size = random.uniform(2, 5)
            self.objects.append(self.create_platform(plat_x, plat_z, plat_height, plat_size))
    
    def create_wall_segment(self, x, z, height, color, direction):
        """Создание сегмента стены"""
        half_cell = self.cell_size / 2
        wall = []
        
        if direction == 'north' or direction == 'south':
            # Стена ориентирована по оси X
            vertices = [
                Vector3(x - half_cell, 0, z),
                Vector3(x + half_cell, 0, z),
                Vector3(x + half_cell, height, z),
                Vector3(x - half_cell, height, z)
            ]
        else:  # west или east
            # Стена ориентирована по оси Z
            vertices = [
                Vector3(x, 0, z - half_cell),
                Vector3(x, 0, z + half_cell),
                Vector3(x, height, z + half_cell),
                Vector3(x, height, z - half_cell)
            ]
        
        # Два треугольника для стены
        wall.append(Triangle(vertices[0], vertices[1], vertices[2], color))
        wall.append(Triangle(vertices[0], vertices[2], vertices[3], color))
        
        return wall
    
    def create_column(self, x, z, height, radius):
        """Создание колонны"""
        column = []
        segments = 8  # Количество граней
        
        # Цвет колонны
        color = [0.6, 0.6, 0.6, 1]
        
        # Создаем грани колонны
        for i in range(segments):
            angle1 = 2 * math.pi * i / segments
            angle2 = 2 * math.pi * (i + 1) / segments
            
            x1 = x + math.cos(angle1) * radius
            z1 = z + math.sin(angle1) * radius
            x2 = x + math.cos(angle2) * radius
            z2 = z + math.sin(angle2) * radius
            
            # Боковая грань (4 треугольника)
            column.append(Triangle(
                Vector3(x1, 0, z1),
                Vector3(x2, 0, z2),
                Vector3(x2, height, z2),
                color
            ))
            column.append(Triangle(
                Vector3(x1, 0, z1),
                Vector3(x2, height, z2),
                Vector3(x1, height, z1),
                color
            ))
        
        return column
    
    def create_platform(self, x, z, height, size):
        """Создание платформы"""
        platform = []
        half_size = size / 2
        
        # Цвет платформы
        color = [0.8, 0.6, 0.4, 1]
        
        # Верх платформы
        vertices = [
            Vector3(x - half_size, height, z - half_size),
            Vector3(x + half_size, height, z - half_size),
            Vector3(x + half_size, height, z + half_size),
            Vector3(x - half_size, height, z + half_size)
        ]
        
        platform.append(Triangle(vertices[0], vertices[1], vertices[2], color))
        platform.append(Triangle(vertices[0], vertices[2], vertices[3], color))
        
        # Боковые грани
        side_color = [0.6, 0.4, 0.2, 1]
        
        # Передняя грань
        platform.append(Triangle(
            Vector3(x - half_size, 0, z - half_size),
            Vector3(x + half_size, 0, z - half_size),
            Vector3(x + half_size, height, z - half_size),
            side_color
        ))
        platform.append(Triangle(
            Vector3(x - half_size, 0, z - half_size),
            Vector3(x + half_size, height, z - half_size),
            Vector3(x - half_size, height, z - half_size),
            side_color
        ))
        
        # Задняя грань
        platform.append(Triangle(
            Vector3(x - half_size, 0, z + half_size),
            Vector3(x + half_size, height, z + half_size),
            Vector3(x + half_size, 0, z + half_size),
            side_color
        ))
        platform.append(Triangle(
            Vector3(x - half_size, 0, z + half_size),
            Vector3(x - half_size, height, z + half_size),
            Vector3(x + half_size, height, z + half_size),
            side_color
        ))
        
        # Левая грань
        platform.append(Triangle(
            Vector3(x - half_size, 0, z - half_size),
            Vector3(x - half_size, height, z - half_size),
            Vector3(x - half_size, height, z + half_size),
            side_color
        ))
        platform.append(Triangle(
            Vector3(x - half_size, 0, z - half_size),
            Vector3(x - half_size, height, z + half_size),
            Vector3(x - half_size, 0, z + half_size),
            side_color
        ))
        
        # Правая грань
        platform.append(Triangle(
            Vector3(x + half_size, 0, z - half_size),
            Vector3(x + half_size, height, z + half_size),
            Vector3(x + half_size, height, z - half_size),
            side_color
        ))
        platform.append(Triangle(
            Vector3(x + half_size, 0, z - half_size),
            Vector3(x + half_size, 0, z + half_size),
            Vector3(x + half_size, height, z + half_size),
            side_color
        ))
        
        return platform

class Sky:
    """Небо с градиентом и облаками"""
    def __init__(self):
        self.clouds = []
        self.create_clouds()
    
    def create_clouds(self):
        """Создание облаков"""
        for _ in range(20):
            self.clouds.append({
                'x': random.uniform(-100, 100),
                'y': random.uniform(20, 50),
                'z': random.uniform(-100, 100),
                'size': random.uniform(5, 15),
                'speed': random.uniform(0.1, 0.5)
            })
    
    def update(self, dt):
        """Обновление облаков"""
        for cloud in self.clouds:
            cloud['x'] += cloud['speed'] * dt
            # Если облако улетело за пределы, перемещаем его обратно
            if cloud['x'] > 100:
                cloud['x'] = -100
                cloud['y'] = random.uniform(20, 50)
                cloud['z'] = random.uniform(-100, 100)

class Enemy3D:
    """3D враг"""
    def __init__(self, position, enemy_type='demon'):
        self.position = position.copy()
        self.type = enemy_type
        self.health = 100 if enemy_type == 'demon' else 50
        self.alive = True
        self.mesh = Mesh3D()
        self.mesh.position = position.copy()
        
        if enemy_type == 'demon':
            self.mesh.create_pyramid(height=1.5, base_size=0.8)
            self.mesh.color = [1, 0.2, 0.2, 1]
        else:
            self.mesh.create_cube(size=0.8)
            self.mesh.color = [0.2, 1, 0.2, 1]
        
        self.animation_time = 0
        self.bobbing_speed = 3
        self.bobbing_height = 0.1
    
    def update(self, dt, player_pos):
        """Обновление состояния врага"""
        if not self.alive:
            return
        
        self.animation_time += dt
        
        # Покачивание на месте
        bob = math.sin(self.animation_time * self.bobbing_speed) * self.bobbing_height
        self.mesh.position.y = self.position.y + bob
        
        # Поворот к игроку
        dx = player_pos.x - self.position.x
        dz = player_pos.z - self.position.z
        angle_to_player = math.atan2(dx, dz)
        self.mesh.rotation.y = angle_to_player
        
        # Обновление меша
        self.mesh.update(dt)
    
    def take_damage(self, amount):
        """Получение урона"""
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            return True
        return False

class True3DEngine:
    """Полноценный 3D движок"""
    def __init__(self):
        self.camera = Camera3D()
        self.map = GridMap(width=40, depth=40, cell_size=2)
        self.sky = Sky()
        
        # Объекты в мире
        self.objects = []
        self.enemies = []
        
        # Игровые параметры
        self.player_health = 100
        self.player_ammo = 50
        self.score = 0
        self.level = 1
        
        # Оружие
        self.weapon_state = 'idle'
        self.weapon_frame = 0
        self.reload_time = 0
        
        # Эффекты
        self.hit_marker = 0
        self.screen_shake = 0
        self.blood_overlay = 0
        
        # Создаем объекты
        self.create_scene()
    
    def create_scene(self):
        """Создание начальной сцены"""
        # Добавляем врагов
        map_width = self.map.width * self.map.cell_size / 2
        map_depth = self.map.depth * self.map.cell_size / 2
        
        for i in range(8):
            enemy_type = 'demon' if i % 2 == 0 else 'zombie'
            x = random.uniform(-map_width + 5, map_width - 5)
            z = random.uniform(-map_depth + 5, map_depth - 5)
            self.enemies.append(Enemy3D(Vector3(x, 0, z), enemy_type))
    
    def fire_weapon(self):
        """Выстрел из оружия"""
        if self.weapon_state != 'reloading' and self.player_ammo > 0:
            self.weapon_state = 'firing'
            self.weapon_frame = 0
            self.player_ammo -= 1
            self.screen_shake = 5
            
            # Проверка попадания
            hit_enemy = False
            for enemy in self.enemies:
                if enemy.alive:
                    # Вектор от камеры к врагу
                    to_enemy = enemy.position - self.camera.position
                    distance = to_enemy.length()
                    
                    # Нормализуем и смотрим, находится ли враг в прицеле
                    to_enemy_norm = to_enemy.normalize()
                    dot_product = self.camera.forward.dot(to_enemy_norm)
                    
                    # Если враг в поле зрения и достаточно близко
                    if dot_product > 0.9 and distance < 10:
                        if enemy.take_damage(50):
                            self.score += 100 if enemy.type == 'demon' else 50
                        hit_enemy = True
                        self.hit_marker = 10
            
            if hit_enemy:
                self.blood_overlay = 15
            
            return True
        return False
    
    def reload_weapon(self):
        """Перезарядка оружия"""
        if self.weapon_state != 'reloading':
            self.weapon_state = 'reloading'
            self.reload_time = 90  # 1.5 секунды при 60 FPS
            return True
        return False
    
    def update(self, dt):
        """Обновление состояния игры"""
        # Обновление оружия
        if self.weapon_state == 'firing':
            self.weapon_frame += 1
            if self.weapon_frame > 10:
                self.weapon_state = 'idle'
        
        elif self.weapon_state == 'reloading':
            self.reload_time -= 1
            if self.reload_time <= 0:
                self.weapon_state = 'idle'
                self.player_ammo = min(50, self.player_ammo + 30)
        
        # Обновление эффектов
        if self.hit_marker > 0:
            self.hit_marker -= 1
        
        if self.screen_shake > 0:
            self.screen_shake -= 1
        
        if self.blood_overlay > 0:
            self.blood_overlay -= 1
        
        # Обновление неба (облака)
        self.sky.update(dt)
        
        # Обновление врагов
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(dt, self.camera.position)
    
    def render_sky(self, canvas, width, height):
        """Отрисовка неба"""
        with canvas:
            # Градиентное небо (от светло-голубого вверху к темно-синему внизу)
            # Верхняя часть (светло-голубая)
            Color(0.5, 0.7, 1.0, 1)
            Rectangle(pos=(0, height // 2), size=(width, height // 2))
            
            # Нижняя часть (темно-синяя)
            Color(0.1, 0.2, 0.4, 1)
            Rectangle(pos=(0, 0), size=(width, height // 2))
            
            # Солнце
            Color(1, 1, 0.8, 0.8)
            sun_x = width * 0.8
            sun_y = height * 0.8
            sun_size = 60
            # Лучи солнца
            for i in range(12):
                angle = math.pi * 2 * i / 12
                ray_length = sun_size * 1.5
                end_x = sun_x + math.cos(angle) * ray_length
                end_y = sun_y + math.sin(angle) * ray_length
                Line(points=[sun_x, sun_y, end_x, end_y], width=3)
            
            # Солнце (круг)
            Color(1, 1, 0.5, 1)
            from kivy.graphics import Ellipse
            Ellipse(pos=(sun_x - sun_size/2, sun_y - sun_size/2), 
                   size=(sun_size, sun_size))
            
            # Облака (простые овалы)
            for cloud in self.sky.clouds:
                # Проецируем облако на экран (упрощенная проекция)
                cloud_x = (cloud['x'] - self.camera.position.x) * 0.5 + width / 2
                cloud_y = (cloud['y'] - self.camera.position.y) * 0.5 + height / 2
                cloud_size = cloud['size'] * 5
                
                if 0 < cloud_x < width and 0 < cloud_y < height:
                    Color(1, 1, 1, 0.7)
                    # Несколько овалов для каждого облака
                    for i in range(3):
                        offset_x = random.uniform(-10, 10)
                        offset_y = random.uniform(-5, 5)
                        Ellipse(pos=(cloud_x - cloud_size/2 + offset_x, 
                                    cloud_y - cloud_size/4 + offset_y), 
                               size=(cloud_size, cloud_size/2))
    
    def render(self, canvas, width, height):
        """Отрисовка 3D сцены"""
        canvas.clear()
        
        # Отрисовка неба
        self.render_sky(canvas, width, height)
        
        with canvas:
            # Матрицы проекции и вида
            aspect = width / height
            projection = self.camera.get_projection_matrix(aspect)
            view = self.camera.get_view_matrix()
            view_projection = projection.multiply(view)
            
            # Список всех треугольников для сортировки
            all_triangles = []
            
            # Добавляем треугольники карты
            for cell in self.map.grid:
                for triangle in cell['triangles']:
                    all_triangles.append((triangle, triangle.color, False))
            
            # Добавляем треугольники объектов карты
            for obj in self.map.objects:
                for triangle in obj:
                    all_triangles.append((triangle, triangle.color, True))
            
            # Добавляем треугольники врагов
            for enemy in self.enemies:
                if enemy.alive:
                    for triangle in enemy.mesh.triangles:
                        v1 = enemy.mesh.transform_vertex(triangle.vertices[0])
                        v2 = enemy.mesh.transform_vertex(triangle.vertices[1])
                        v3 = enemy.mesh.transform_vertex(triangle.vertices[2])
                        
                        transformed_tri = Triangle(v1, v2, v3, triangle.color)
                        all_triangles.append((transformed_tri, triangle.color, True))
            
            # Сортируем треугольники по удаленности от камеры (painter's algorithm)
            def triangle_depth(tri):
                center = tri[0].get_center()
                return (self.camera.position - center).length()
            
            all_triangles.sort(key=triangle_depth, reverse=True)
            
            # Отрисовываем треугольники
            for triangle, color, is_object in all_triangles:
                # Проверяем, смотрит ли треугольник на камеру
                if not triangle.is_facing_camera(self.camera.position) and is_object:
                    continue
                
                # Проецируем вершины
                v1_proj = view_projection.multiply_vector(triangle.vertices[0])
                v2_proj = view_projection.multiply_vector(triangle.vertices[1])
                v3_proj = view_projection.multiply_vector(triangle.vertices[2])
                
                # Проверяем, находятся ли вершины перед камерой
                if (v1_proj.z > 0 and v1_proj.z < 1 and
                    v2_proj.z > 0 and v2_proj.z < 1 and
                    v3_proj.z > 0 and v3_proj.z < 1):
                    
                    # Преобразуем в координаты экрана
                    def to_screen(v):
                        x = (v.x + 1) * 0.5 * width
                        y = (1 - v.y) * 0.5 * height
                        return (x, y)
                    
                    screen1 = to_screen(v1_proj)
                    screen2 = to_screen(v2_proj)
                    screen3 = to_screen(v3_proj)
                    
                    # Рисуем треугольник
                    Color(*color)
                    Mesh(
                        vertices=[screen1[0], screen1[1], 0, 0,
                                 screen2[0], screen2[1], 0, 0,
                                 screen3[0], screen3[1], 0, 0],
                        indices=[0, 1, 2],
                        mode='triangles'
                    )
            
            # Эффект попадания по врагу
            if self.hit_marker > 0:
                Color(1, 0, 0, 0.3)
                Rectangle(pos=(0, 0), size=(width, height))
            
            # Кровавый экран при получении урона
            if self.blood_overlay > 0:
                alpha = self.blood_overlay / 15.0
                Color(1, 0, 0, alpha * 0.5)
                Rectangle(pos=(0, 0), size=(width, height))
            
            # Эффект тряски экрана при выстреле
            if self.screen_shake > 0:
                shake_x = random.randint(-3, 3)
                shake_y = random.randint(-3, 3)
                Translate(shake_x, shake_y)
