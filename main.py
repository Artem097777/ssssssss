from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.graphics import *
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.uix.togglebutton import ToggleButton
from math import sin, cos, radians, pi, sqrt
from collections import deque
import random

class MenuWidget(Widget):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.show_settings = False
        self.show_controls = False
        
        # Фон меню
        with self.canvas:
            Color(0.1, 0.1, 0.2, 0.95)
            Rectangle(pos=(0, 0), size=(Window.width, Window.height))
            
            # Текст заголовка
            Color(0.9, 0.9, 1, 1)
            Rectangle(pos=(Window.width/2 - 150, Window.height - 150), size=(300, 100))
            Color(0.1, 0.2, 0.4, 1)
            Rectangle(pos=(Window.width/2 - 145, Window.height - 145), size=(290, 90))
        
        # Создаем кнопки
        self.create_buttons()
        
    def create_buttons(self):
        # Удаляем старые виджеты
        self.clear_widgets()
        
        center_x = Window.width / 2
        button_width = 300
        button_height = 60
        spacing = 20
        
        if not self.show_settings and not self.show_controls:
            # Главное меню
            buttons = [
                ("ПРОДОЛЖИТЬ", self.resume_game),
                ("НОВАЯ ИГРА", self.new_game),
                ("НАСТРОЙКИ", self.show_settings_menu),
                ("УПРАВЛЕНИЕ", self.show_controls_info),
                ("ВЫХОД", self.exit_game)
            ]
            
            start_y = Window.height / 2 + 100
            
            for i, (text, callback) in enumerate(buttons):
                btn = MenuButton(
                    text=text,
                    size=(button_width, button_height),
                    pos=(center_x - button_width/2, start_y - i * (button_height + spacing)),
                    on_press=callback
                )
                self.add_widget(btn)
                
            # Заголовок
            title = Label(
                text='PYDOOM 3D',
                font_size=48,
                bold=True,
                color=(1, 0.5, 0, 1),
                pos=(center_x - 150, Window.height - 150)
            )
            self.add_widget(title)
            
        elif self.show_settings:
            # Меню настроек
            self.create_settings_menu()
        else:
            # Информация об управлении
            self.create_controls_info()

    def create_settings_menu(self):
        center_x = Window.width / 2
        button_width = 300
        button_height = 50
        spacing = 15
        
        # Заголовок
        title = Label(
            text='НАСТРОЙКИ',
            font_size=36,
            bold=True,
            color=(1, 0.8, 0, 1),
            pos=(center_x - 120, Window.height - 100)
        )
        self.add_widget(title)
        
        # Настройка громкости
        vol_label = Label(
            text='ГРОМКОСТЬ:',
            font_size=20,
            color=(1, 1, 1, 1),
            pos=(center_x - 200, Window.height - 200)
        )
        self.add_widget(vol_label)
        
        # Анимация времени
        time_label = Label(
            text='АНИМАЦИЯ ВРЕМЕНИ:',
            font_size=20,
            color=(1, 1, 1, 1),
            pos=(center_x - 200, Window.height - 270)
        )
        self.add_widget(time_label)
        
        time_check = CheckBox(
            active=self.game.auto_time_change,
            size=(40, 40),
            pos=(center_x + 100, Window.height - 275)
        )
        time_check.bind(active=self.game.set_auto_time)
        self.add_widget(time_check)
        
        # Полноэкранный режим
        fullscreen_label = Label(
            text='ПОЛНЫЙ ЭКРАН:',
            font_size=20,
            color=(1, 1, 1, 1),
            pos=(center_x - 200, Window.height - 340)
        )
        self.add_widget(fullscreen_label)
        
        fs_check = CheckBox(
            active=Window.fullscreen != '0',
            size=(40, 40),
            pos=(center_x + 100, Window.height - 345)
        )
        fs_check.bind(active=self.toggle_fullscreen)
        self.add_widget(fs_check)
        
        # Сложность
        diff_label = Label(
            text='СЛОЖНОСТЬ:',
            font_size=20,
            color=(1, 1, 1, 1),
            pos=(center_x - 200, Window.height - 410)
        )
        self.add_widget(diff_label)
        
        diff_buttons = BoxLayout(
            orientation='horizontal',
            size=(200, 40),
            pos=(center_x - 100, Window.height - 415)
        )
        
        easy_btn = ToggleButton(
            text='ЛЁГКАЯ',
            group='difficulty',
            state='down' if self.game.move_speed == 2.5 else 'normal'
        )
        easy_btn.bind(on_press=lambda x: self.set_difficulty(2.5))
        
        medium_btn = ToggleButton(
            text='НОРМАЛЬНАЯ',
            group='difficulty',
            state='down' if self.game.move_speed == 2.0 else 'normal'
        )
        medium_btn.bind(on_press=lambda x: self.set_difficulty(2.0))
        
        hard_btn = ToggleButton(
            text='СЛОЖНАЯ',
            group='difficulty',
            state='down' if self.game.move_speed == 1.5 else 'normal'
        )
        hard_btn.bind(on_press=lambda x: self.set_difficulty(1.5))
        
        diff_buttons.add_widget(easy_btn)
        diff_buttons.add_widget(medium_btn)
        diff_buttons.add_widget(hard_btn)
        self.add_widget(diff_buttons)
        
        # Кнопка назад
        back_btn = MenuButton(
            text='НАЗАД',
            size=(button_width, button_height),
            pos=(center_x - button_width/2, 100),
            on_press=self.back_to_main
        )
        self.add_widget(back_btn)

    def create_controls_info(self):
        center_x = Window.width / 2
        
        # Заголовок
        title = Label(
            text='УПРАВЛЕНИЕ',
            font_size=36,
            bold=True,
            color=(1, 0.8, 0, 1),
            pos=(center_x - 120, Window.height - 100)
        )
        self.add_widget(title)
        
        # Информация об управлении
        controls = [
            ("WASD", "Движение игрока"),
            ("МЫШЬ", "Поворот камеры"),
            ("ESC", "Меню/Пауза"),
            ("T", "Сменить время суток"),
            ("Y", "Вкл/Выкл авто-время"),
            ("P", "Вкл/Выкл дождь"),
            ("L", "Молния (только при дожде)"),
            ("M", "Миникарта"),
            ("R", "Сброс позиции"),
            ("F", "Полный экран")
        ]
        
        start_y = Window.height - 180
        
        for i, (key, desc) in enumerate(controls):
            key_label = Label(
                text=key,
                font_size=24,
                bold=True,
                color=(1, 0.6, 0, 1),
                pos=(center_x - 200, start_y - i * 40)
            )
            desc_label = Label(
                text=desc,
                font_size=20,
                color=(1, 1, 1, 1),
                pos=(center_x - 50, start_y - i * 40)
            )
            self.add_widget(key_label)
            self.add_widget(desc_label)
        
        # Кнопка назад
        back_btn = MenuButton(
            text='НАЗАД',
            size=(300, 60),
            pos=(center_x - 150, 100),
            on_press=self.back_to_main
        )
        self.add_widget(back_btn)

    def resume_game(self, instance):
        self.game.menu_active = False
        
    def new_game(self, instance):
        self.game.reset_game()
        self.game.menu_active = False
        
    def show_settings_menu(self, instance):
        self.show_settings = True
        self.show_controls = False
        self.create_buttons()
        
    def show_controls_info(self, instance):
        self.show_settings = False
        self.show_controls = True
        self.create_buttons()
        
    def exit_game(self, instance):
        App.get_running_app().stop()
        
    def back_to_main(self, instance):
        self.show_settings = False
        self.show_controls = False
        self.create_buttons()
        
    def toggle_fullscreen(self, checkbox, value):
        Window.fullscreen = 'auto' if value else False
        
    def set_difficulty(self, speed):
        self.game.move_speed = speed

class MenuButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.3, 0.5, 1)
        self.color = (1, 1, 1, 1)
        self.font_size = 24
        self.bold = True
        self.background_normal = ''
        self.background_down = ''
        
        with self.canvas.before:
            Color(0.1, 0.2, 0.4, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            
        self.bind(pos=self.update_rect, size=self.update_rect)
        
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        
    def on_press(self):
        with self.canvas:
            Color(0.3, 0.5, 0.8, 1)
            Rectangle(pos=self.pos, size=self.size)
        return super().on_press()

class RaycasterGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Состояние меню
        self.menu_active = True
        self.menu_widget = None
        
        # Игровые параметры
        self.player_x = 1.5
        self.player_y = 1.5
        self.player_angle = 0
        self.fov = 60
        
        # Время суток
        self.time_of_day = 1
        self.time_transition = 0.0
        self.time_speed = 0.1
        
        # Система дождя
        self.rain_intensity = 0.0
        self.rain_target_intensity = 0.0
        self.is_raining = False
        self.rain_particles = []
        self.max_rain_particles = 300
        
        # Погодные условия для времени суток
        self.weather_by_time = {
            0: {'rain_chance': 0.3, 'max_intensity': 0.6, 'thunder_chance': 0.1},
            1: {'rain_chance': 0.4, 'max_intensity': 0.8, 'thunder_chance': 0.2},
            2: {'rain_chance': 0.5, 'max_intensity': 1.0, 'thunder_chance': 0.3},
            3: {'rain_chance': 0.2, 'max_intensity': 0.4, 'thunder_chance': 0.4}
        }
        
        # Цветовые схемы для времени суток с дождем
        self.time_colors = {
            0: {  # Утро
                'sky': (0.6, 0.8, 1.0, 1),
                'sky_rainy': (0.4, 0.6, 0.8, 1),
                'floor': (0.4, 0.5, 0.3, 1),
                'floor_rainy': (0.3, 0.4, 0.25, 1),
                'fog': (0.8, 0.9, 1.0, 0.3),
                'fog_rainy': (0.6, 0.7, 0.8, 0.5),
                'light_mult': 1.3,
                'light_mult_rainy': 0.9,
                'wall_brightness': 1.2,
                'wall_brightness_rainy': 0.8,
                'ambient': 0.7,
                'rain_color': (0.7, 0.8, 1.0, 0.7)
            },
            1: {  # День
                'sky': (0.2, 0.3, 0.8, 1),
                'sky_rainy': (0.15, 0.25, 0.6, 1),
                'floor': (0.3, 0.3, 0.3, 1),
                'floor_rainy': (0.25, 0.25, 0.35, 1),
                'fog': (0.7, 0.8, 0.9, 0.1),
                'fog_rainy': (0.5, 0.6, 0.7, 0.3),
                'light_mult': 1.0,
                'light_mult_rainy': 0.6,
                'wall_brightness': 1.0,
                'wall_brightness_rainy': 0.6,
                'ambient': 0.8,
                'rain_color': (0.8, 0.9, 1.0, 0.8)
            },
            2: {  # Вечер
                'sky': (0.9, 0.5, 0.2, 1),
                'sky_rainy': (0.7, 0.4, 0.3, 1),
                'floor': (0.4, 0.3, 0.2, 1),
                'floor_rainy': (0.35, 0.25, 0.2, 1),
                'fog': (0.9, 0.6, 0.4, 0.4),
                'fog_rainy': (0.7, 0.5, 0.4, 0.6),
                'light_mult': 0.7,
                'light_mult_rainy': 0.4,
                'wall_brightness': 0.9,
                'wall_brightness_rainy': 0.5,
                'ambient': 0.6,
                'rain_color': (0.9, 0.7, 0.5, 0.6)
            },
            3: {  # Ночь
                'sky': (0.05, 0.05, 0.15, 1),
                'sky_rainy': (0.03, 0.03, 0.1, 1),
                'floor': (0.1, 0.1, 0.15, 1),
                'floor_rainy': (0.08, 0.08, 0.12, 1),
                'fog': (0.1, 0.1, 0.2, 0.6),
                'fog_rainy': (0.08, 0.08, 0.15, 0.8),
                'light_mult': 0.4,
                'light_mult_rainy': 0.2,
                'wall_brightness': 0.5,
                'wall_brightness_rainy': 0.3,
                'ambient': 0.3,
                'rain_color': (0.3, 0.4, 0.8, 0.5)
            }
        }
        
        # Звезды
        self.stars = []
        self.generate_stars()
        
        # Молнии
        self.lightning_flash = 0.0
        self.lightning_timer = 0
        self.lightning_duration = 0.1
        self.last_lightning_time = 0
        
        # Цвета стен
        self.wall_colors = {
            1: {'day': (1.0, 0.3, 0.3), 'rainy': (0.8, 0.25, 0.25)},
            2: {'day': (0.3, 1.0, 0.3), 'rainy': (0.25, 0.8, 0.25)},
            3: {'day': (0.3, 0.3, 1.0), 'rainy': (0.25, 0.25, 0.8)},
            4: {'day': (1.0, 1.0, 0.3), 'rainy': (0.8, 0.8, 0.25)},
            5: {'day': (1.0, 0.5, 0.0), 'rainy': (0.8, 0.4, 0.0)},
            6: {'day': (0.5, 0.0, 1.0), 'rainy': (0.4, 0.0, 0.8)},
            7: {'day': (0.0, 1.0, 1.0), 'rainy': (0.0, 0.8, 0.8)},
            8: {'day': (0.8, 0.8, 0.8), 'rainy': (0.6, 0.6, 0.6)}
        }
        
        # Карта
        self.map = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 2, 0, 0, 3, 0, 0, 0, 0, 0, 1],
            [1, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 1],
            [1, 0, 0, 0, 0, 6, 0, 0, 0, 0, 7, 0, 0, 0, 0, 1],
            [1, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 1],
            [1, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 8, 0, 0, 2, 0, 0, 3, 0, 0, 8, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 6, 0, 0, 5, 0, 0, 0, 0, 4, 0, 0, 7, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        
        # Управление
        self.keys_pressed = set()
        self.move_speed = 2.0
        self.rotation_speed = 30.0
        
        # Для плавного движения
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.angular_velocity = 0.0
        self.friction = 0.85
        
        # Оптимизация: предрассчитанные синусы и косинусы
        self.sin_cache = {}
        self.cos_cache = {}
        self._build_trig_cache()
        
        # Оптимизация: для мини-карты
        self.show_minimap = True
        self.minimap_scale = 10
        
        # Для FPS
        self.frame_times = deque(maxlen=60)
        self.last_time = Clock.get_time()
        self.fps = 0
        
        # Автоматическая смена времени
        self.auto_time_change = True
        self.time_change_timer = 0
        
        # Инициализация дождя
        self.init_rain()
        
        # Создаем меню
        self.create_menu()
        
        # Начинаем игровой цикл
        Clock.schedule_interval(self.update, 1.0/60.0)
        
        # Привязываем клавиши
        self._bind_keys()
        
        # Мышь
        Window.bind(mouse_pos=self.on_mouse_move)
        self.last_mouse_pos = None
        self.mouse_sensitivity = 0.3
        
    def create_menu(self):
        """Создание меню"""
        self.menu_widget = MenuWidget(self)
        self.add_widget(self.menu_widget)
        self.menu_widget.opacity = 1 if self.menu_active else 0
        self.menu_widget.disabled = not self.menu_active
        
    def generate_stars(self):
        """Генерирует звезды для ночного неба"""
        self.stars = []
        for _ in range(100):
            self.stars.append({
                'x': random.random(),
                'y': random.random() * 0.5 + 0.5,
                'size': random.random() * 2 + 1,
                'brightness': random.random() * 0.5 + 0.5,
                'twinkle_speed': random.random() * 2 + 1
            })
    
    def init_rain(self):
        """Инициализация частиц дождя"""
        self.rain_particles = []
        for _ in range(self.max_rain_particles):
            self.rain_particles.append({
                'x': random.random() * self.width,
                'y': random.random() * self.height,
                'z': random.random(),
                'speed': random.uniform(5, 15),
                'length': random.uniform(10, 25),
                'wind': random.uniform(-1, 1) * 0.5,
                'size': random.uniform(1, 2)
            })
    
    def update_weather(self, dt):
        """Обновление погодных условий"""
        # Плавное изменение интенсивности дождя
        if self.rain_intensity < self.rain_target_intensity:
            self.rain_intensity = min(self.rain_intensity + dt * 0.5, self.rain_target_intensity)
        elif self.rain_intensity > self.rain_target_intensity:
            self.rain_intensity = max(self.rain_intensity - dt * 0.5, self.rain_target_intensity)
        
        # Обновление частиц дождя
        for particle in self.rain_particles:
            particle['y'] -= particle['speed'] * (0.5 + self.rain_intensity * 1.5) * dt * 60
            particle['x'] += particle['wind'] * self.rain_intensity * dt * 60
            
            # Если частица ушла за пределы экрана, возвращаем ее наверх
            if particle['y'] < -particle['length']:
                particle['y'] = self.height + particle['length']
                particle['x'] = random.random() * self.width
                particle['z'] = random.random()
                
            if particle['x'] < -10:
                particle['x'] = self.width + 10
            elif particle['x'] > self.width + 10:
                particle['x'] = -10
        
        # Обновление молний
        if self.lightning_flash > 0:
            self.lightning_flash = max(0, self.lightning_flash - dt * 5)
        
        # Случайная молния во время дождя
        if self.rain_intensity > 0.5 and self.time_of_day in [1, 2, 3]:
            current_time = Clock.get_time()
            if current_time - self.last_lightning_time > random.uniform(5, 15):
                weather = self.weather_by_time[self.time_of_day]
                if random.random() < weather['thunder_chance'] * self.rain_intensity:
                    self.lightning_flash = 1.0
                    self.last_lightning_time = current_time
        
        # Случайное начало/конец дождя
        if self.time_change_timer > 0 and self.time_change_timer % 30 < 0.1:
            weather = self.weather_by_time[self.time_of_day]
            if random.random() < weather['rain_chance']:
                self.rain_target_intensity = random.uniform(0.3, weather['max_intensity'])
            else:
                self.rain_target_intensity = 0.0
    
    def _build_trig_cache(self):
        """Предрасчет тригонометрических значений"""
        for angle in range(3600):
            rad = radians(angle / 10.0)
            self.sin_cache[angle] = sin(rad)
            self.cos_cache[angle] = cos(rad)
    
    def _get_sin(self, angle):
        """Получение синуса с кэшированием"""
        angle_int = int(angle * 10) % 3600
        return self.sin_cache.get(angle_int, sin(radians(angle)))
    
    def _get_cos(self, angle):
        """Получение косинуса с кэшированием"""
        angle_int = int(angle * 10) % 3600
        return self.cos_cache.get(angle_int, cos(radians(angle)))
    
    def _bind_keys(self):
        """Привязка обработчиков клавиш"""
        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_key_up=self._on_key_up)
    
    def interpolate_colors(self, color1, color2, t):
        """Интерполяция между двумя цветами"""
        return (
            color1[0] * (1 - t) + color2[0] * t,
            color1[1] * (1 - t) + color2[1] * t,
            color1[2] * (1 - t) + color2[2] * t,
            color1[3] if len(color1) > 3 else 1
        )
    
    def get_current_time_colors(self):
        """Получение текущих цветов с учетом дождя"""
        next_time = (self.time_of_day + 1) % 4
        colors1 = self.time_colors[self.time_of_day]
        colors2 = self.time_colors[next_time]
        t = self.time_transition
        
        # Базовые цвета без дождя
        base_colors = {
            'sky': self.interpolate_colors(colors1['sky'], colors2['sky'], t),
            'floor': self.interpolate_colors(colors1['floor'], colors2['floor'], t),
            'fog': self.interpolate_colors(colors1['fog'], colors2['fog'], t),
            'light_mult': colors1['light_mult'] * (1 - t) + colors2['light_mult'] * t,
            'wall_brightness': colors1['wall_brightness'] * (1 - t) + colors2['wall_brightness'] * t,
            'ambient': colors1['ambient'] * (1 - t) + colors2['ambient'] * t,
            'rain_color': self.interpolate_colors(colors1['rain_color'], colors2['rain_color'], t)
        }
        
        # Если идет дождь, смешиваем с дождливыми цветами
        if self.rain_intensity > 0:
            rainy_colors = {
                'sky': self.interpolate_colors(colors1['sky_rainy'], colors2['sky_rainy'], t),
                'floor': self.interpolate_colors(colors1['floor_rainy'], colors2['floor_rainy'], t),
                'fog': self.interpolate_colors(colors1['fog_rainy'], colors2['fog_rainy'], t),
                'light_mult': (colors1['light_mult_rainy'] * (1 - t) + colors2['light_mult_rainy'] * t),
                'wall_brightness': (colors1['wall_brightness_rainy'] * (1 - t) + colors2['wall_brightness_rainy'] * t),
            }
            
            # Смешиваем в зависимости от интенсивности дождя
            rain_factor = self.rain_intensity
            return {
                'sky': self.interpolate_colors(base_colors['sky'], rainy_colors['sky'], rain_factor),
                'floor': self.interpolate_colors(base_colors['floor'], rainy_colors['floor'], rain_factor),
                'fog': self.interpolate_colors(base_colors['fog'], rainy_colors['fog'], rain_factor),
                'light_mult': base_colors['light_mult'] * (1 - rain_factor) + rainy_colors['light_mult'] * rain_factor,
                'wall_brightness': base_colors['wall_brightness'] * (1 - rain_factor) + rainy_colors['wall_brightness'] * rain_factor,
                'ambient': base_colors['ambient'] * (1 - rain_factor * 0.3),
                'rain_color': base_colors['rain_color']
            }
        
        return base_colors
    
    def cast_ray_optimized(self, angle):
        """Оптимизированный бросок луча"""
        rad = radians(angle)
        
        dir_x = cos(rad)
        dir_y = sin(rad)
        
        ray_x = self.player_x
        ray_y = self.player_y
        
        if dir_x != 0:
            delta_dist_x = abs(1 / dir_x)
        else:
            delta_dist_x = 1e30
            
        if dir_y != 0:
            delta_dist_y = abs(1 / dir_y)
        else:
            delta_dist_y = 1e30
        
        map_x = int(ray_x)
        map_y = int(ray_y)
        
        step_x = 1 if dir_x >= 0 else -1
        step_y = 1 if dir_y >= 0 else -1
        
        if dir_x < 0:
            side_dist_x = (ray_x - map_x) * delta_dist_x
        else:
            side_dist_x = (map_x + 1.0 - ray_x) * delta_dist_x
            
        if dir_y < 0:
            side_dist_y = (ray_y - map_y) * delta_dist_y
        else:
            side_dist_y = (map_y + 1.0 - ray_y) * delta_dist_y
        
        hit = 0
        side = 0
        
        max_steps = 200
        steps = 0
        
        while hit == 0 and steps < max_steps:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            
            if (map_x < 0 or map_x >= len(self.map[0]) or 
                map_y < 0 or map_y >= len(self.map)):
                break
            
            cell_value = self.map[map_y][map_x]
            if cell_value > 0:
                hit = cell_value
            
            steps += 1
        
        if side == 0:
            distance = (side_dist_x - delta_dist_x)
        else:
            distance = (side_dist_y - delta_dist_y)
        
        return distance, hit, side
    
    def reset_game(self):
        """Сброс игры"""
        self.player_x = 1.5
        self.player_y = 1.5
        self.player_angle = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.angular_velocity = 0
        self.time_of_day = 1
        self.time_transition = 0
        self.rain_target_intensity = 0
    
    def set_auto_time(self, checkbox, value):
        """Установка автоматической смены времени"""
        self.auto_time_change = value
    
    def on_mouse_move(self, window, pos):
        """Обработка движения мыши"""
        if self.menu_active or self.last_mouse_pos is None:
            self.last_mouse_pos = pos
            return
            
        dx = pos[0] - self.last_mouse_pos[0]
        self.player_angle += dx * self.mouse_sensitivity * 0.1
        
        if self.player_angle < 0:
            self.player_angle += 360
        elif self.player_angle >= 360:
            self.player_angle -= 360
            
        self.last_mouse_pos = pos
    
    def update(self, dt):
        """Обновление игры"""
        if self.menu_active:
            return
            
        current_time = Clock.get_time()
        self.frame_times.append(current_time - self.last_time)
        self.last_time = current_time
        
        if len(self.frame_times) > 0:
            self.fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
        
        # Обновление времени суток
        if self.auto_time_change:
            self.time_change_timer += dt
            if self.time_change_timer >= 30:
                self.time_of_day = (self.time_of_day + 1) % 4
                self.time_change_timer = 0
        
        # Плавный переход времени
        if self.time_transition < 1.0:
            self.time_transition += dt * self.time_speed
            if self.time_transition >= 1.0:
                self.time_transition = 0.0
                if self.auto_time_change:
                    self.time_of_day = (self.time_of_day + 1) % 4
        
        # Обновление погоды
        self.update_weather(dt)
        
        # Движение
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        self.angular_velocity *= self.friction
        
        move_acceleration = self.move_speed * dt
        rotation_acceleration = self.rotation_speed * dt
        
        if 'w' in self.keys_pressed:
            self.velocity_x += self._get_cos(self.player_angle) * move_acceleration
            self.velocity_y += self._get_sin(self.player_angle) * move_acceleration
            
        if 's' in self.keys_pressed:
            self.velocity_x -= self._get_cos(self.player_angle) * move_acceleration
            self.velocity_y -= self._get_sin(self.player_angle) * move_acceleration
            
        if 'a' in self.keys_pressed:
            self.angular_velocity -= rotation_acceleration
            
        if 'd' in self.keys_pressed:
            self.angular_velocity += rotation_acceleration
        
        max_speed = self.move_speed * dt * 3
        current_speed = (self.velocity_x**2 + self.velocity_y**2)**0.5
        if current_speed > max_speed:
            scale = max_speed / current_speed
            self.velocity_x *= scale
            self.velocity_y *= scale
        
        new_x = self.player_x + self.velocity_x
        new_y = self.player_y + self.velocity_y
        
        if self.map[int(new_y)][int(new_x)] == 0:
            self.player_x = new_x
            self.player_y = new_y
        else:
            if self.map[int(self.player_y)][int(new_x)] == 0:
                self.player_x = new_x
            if self.map[int(new_y)][int(self.player_x)] == 0:
                self.player_y = new_y
            self.velocity_x *= 0.1
            self.velocity_y *= 0.1
        
        self.player_angle += self.angular_velocity
        if self.player_angle < 0:
            self.player_angle += 360
        elif self.player_angle >= 360:
            self.player_angle -= 360
        
        self.canvas.clear()
        self.draw()
    
    def draw(self):
        """Отрисовка игры"""
        if self.menu_active:
            return
            
        width, height = self.size
        
        # Получаем текущие цвета времени суток
        time_colors = self.get_current_time_colors()
        
        with self.canvas:
            # Молния (вспышка)
            if self.lightning_flash > 0:
                flash_intensity = self.lightning_flash * 0.7
                Color(1, 1, 1, flash_intensity)
                Rectangle(pos=(0, 0), size=(width, height))
            
            # Рисуем небо
            sky_color = list(time_colors['sky'])
            if self.lightning_flash > 0:
                flash_factor = self.lightning_flash * 0.3
                sky_color = (
                    min(1.0, sky_color[0] + flash_factor),
                    min(1.0, sky_color[1] + flash_factor),
                    min(1.0, sky_color[2] + flash_factor),
                    sky_color[3]
                )
            Color(*sky_color)
            Rectangle(pos=(0, height/2), size=(width, height/2))
            
            # Звезды
            if (self.time_of_day == 3 or (self.time_of_day == 2 and self.time_transition > 0.5)) and self.rain_intensity < 0.5:
                star_alpha = time_colors['ambient'] * 0.8 * (1 - self.rain_intensity)
                for star in self.stars:
                    twinkle = (sin(Clock.get_time() * star['twinkle_speed'] + star['x'] * 10) * 0.2 + 0.8)
                    Color(1, 1, 1, star['brightness'] * star_alpha * twinkle)
                    Rectangle(
                        pos=(star['x'] * width, 
                             height/2 + star['y'] * height/2),
                        size=(star['size'], star['size'])
                    )
            
            # Рисуем пол
            Color(*time_colors['floor'])
            Rectangle(pos=(0, 0), size=(width, height/2))
            
            # Оптимизация: адаптивное количество лучей
            ray_count = min(1000, int(width / 2))
            half_fov = self.fov / 2
            
            # Рисуем стены
            for ray in range(ray_count):
                ray_angle = self.player_angle - half_fov + (self.fov * ray / ray_count)
                
                distance, wall_type, side = self.cast_ray_optimized(ray_angle)
                
                # Коррекция искажения
                angle_diff = ray_angle - self.player_angle
                distance = distance * cos(radians(angle_diff))
                
                # Вычисляем высоту стены
                wall_height = min(height, height / (distance + 0.0001))
                
                # Позиция по X на экране
                x_pos = (ray / ray_count) * width
                strip_width = width / ray_count + 1
                
                # Базовый цвет стены
                base_color = self.wall_colors.get(wall_type, {}).get('day', (1, 1, 1))
                
                # Если идет дождь, используем дождливый цвет
                if self.rain_intensity > 0:
                    rainy_color = self.wall_colors.get(wall_type, {}).get('rainy', (0.7, 0.7, 0.7))
                    rain_factor = self.rain_intensity * 0.7
                    base_color = (
                        base_color[0] * (1 - rain_factor) + rainy_color[0] * rain_factor,
                        base_color[1] * (1 - rain_factor) + rainy_color[1] * rain_factor,
                        base_color[2] * (1 - rain_factor) + rainy_color[2] * rain_factor
                    )
                
                # Темная сторона стены
                if side == 1:
                    base_color = (base_color[0] * 0.7, base_color[1] * 0.7, base_color[2] * 0.7)
                
                # Освещение
                brightness = min(1.0, 2.0 / (1.0 + distance * 0.3))
                brightness *= time_colors['wall_brightness']
                
                # Молния добавляет яркости
                if self.lightning_flash > 0:
                    brightness += self.lightning_flash * 0.5
                    brightness = min(1.5, brightness)
                
                # Добавляем атмосферную дымку
                fog_factor = min(1.0, distance * 0.1)
                color = (
                    base_color[0] * brightness * (1 - fog_factor) + time_colors['fog'][0] * fog_factor,
                    base_color[1] * brightness * (1 - fog_factor) + time_colors['fog'][1] * fog_factor,
                    base_color[2] * brightness * (1 - fog_factor) + time_colors['fog'][2] * fog_factor
                )
                
                # Рисуем вертикальную полосу
                Color(*color)
                Rectangle(
                    pos=(x_pos, (height - wall_height) / 2),
                    size=(strip_width, wall_height)
                )
            
            # Рисуем дождь
            if self.rain_intensity > 0.1:
                self.draw_rain(width, height, time_colors)
            
            # Отображаем HUD
            self.draw_hud()
    
    def draw_rain(self, width, height, time_colors):
        """Отрисовка дождя"""
        with self.canvas:
            # Рисуем капли дождя
            rain_color = list(time_colors['rain_color'])
            rain_color[3] *= self.rain_intensity
            
            # Основной дождь
            Color(*rain_color)
            for particle in self.rain_particles[:int(len(self.rain_particles) * 0.7)]:
                alpha = particle['z'] * 0.5 + 0.5
                Color(rain_color[0], rain_color[1], rain_color[2], rain_color[3] * alpha)
                Line(
                    points=[
                        particle['x'],
                        particle['y'],
                        particle['x'] + particle['wind'] * 3,
                        particle['y'] - particle['length']
                    ],
                    width=particle['size']
                )
    
    def draw_hud(self):
        """Отрисовка HUD"""
        with self.canvas:
            # Индикатор паузы
            if self.menu_active:
                Color(0, 0, 0, 0.7)
                Rectangle(pos=(10, self.height - 40), size=(200, 30))
                Color(1, 1, 0, 1)
            
            # FPS
            Color(0, 0, 0, 0.5)
            Rectangle(pos=(10, self.height - 40), size=(120, 30))
            Color(0, 1, 0, 1)
            
            # Время суток
            time_names = ["УТРО", "ДЕНЬ", "ВЕЧЕР", "НОЧЬ"]
            time_name = time_names[self.time_of_day]
            
            # Погода
            weather_text = ""
            if self.rain_intensity > 0.7:
                weather_text = "⚡ ЛИВЕНЬ"
            elif self.rain_intensity > 0.4:
                weather_text = "☂ ДОЖДЬ"
            elif self.rain_intensity > 0.1:
                weather_text = "☔ МОРОСЬ"
            else:
                weather_text = "☀ ЯСНО"
    
    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        """Обработка нажатия клавиш"""
        if key == 27:  # ESC
            self.menu_active = not self.menu_active
            if self.menu_widget:
                self.menu_widget.opacity = 1 if self.menu_active else 0
                self.menu_widget.disabled = not self.menu_active
                if self.menu_active:
                    self.menu_widget.create_buttons()
            return
            
        if self.menu_active:
            return
            
        if key == 119:  # W
            self.keys_pressed.add('w')
        elif key == 97:   # A
            self.keys_pressed.add('a')
        elif key == 115:  # S
            self.keys_pressed.add('s')
        elif key == 100:  # D
            self.keys_pressed.add('d')
        elif key == 109:  # M
            self.show_minimap = not self.show_minimap
        elif key == 114:  # R
            self.reset_game()
        elif key == 116:  # T
            self.time_of_day = (self.time_of_day + 1) % 4
            self.time_transition = 0.0
            self.time_change_timer = 0
        elif key == 121:  # Y
            self.auto_time_change = not self.auto_time_change
        elif key == 112:  # P
            if self.rain_target_intensity > 0:
                self.rain_target_intensity = 0.0
            else:
                weather = self.weather_by_time[self.time_of_day]
                self.rain_target_intensity = weather['max_intensity'] * 0.7
        elif key == 108:  # L
            self.lightning_flash = 1.0
            self.last_lightning_time = Clock.get_time()
        elif key == 102:  # F
            Window.fullscreen = 'auto' if not Window.fullscreen else False
    
    def _on_key_up(self, window, key, scancode):
        """Обработка отпускания клавиш"""
        if key == 119:  # W
            self.keys_pressed.discard('w')
        elif key == 97:   # A
            self.keys_pressed.discard('a')
        elif key == 115:  # S
            self.keys_pressed.discard('s')
        elif key == 100:  # D
            self.keys_pressed.discard('d')

class Doom3DApp(App):
    def build(self):
        Window.size = (1024, 768)
        Window.title = "PyDoom 3D - ESC: Меню, WASD: движение, T: время, P: дождь, F: полный экран"
        game = RaycasterGame()
        return game

if __name__ == '__main__':
    Doom3DApp().run()
