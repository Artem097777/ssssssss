from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, StringProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse, Line, InstructionGroup
from kivy.graphics import Translate, PushMatrix, PopMatrix
from kivy.utils import platform
from kivy.metrics import dp
from kivy.animation import Animation
import math
import random
import json
import os

class SmartScreenDetector:
    """Класс для автоматического определения типа устройства и размера экрана"""
    
    @staticmethod
    def get_device_type():
        """Определяем тип устройства"""
        if platform == 'android' or platform == 'ios':
            # Мобильное устройство
            aspect_ratio = Window.width / Window.height if Window.height > 0 else 0
            
            if aspect_ratio > 1.4:
                return 'phone_landscape'
            elif aspect_ratio < 0.7:
                return 'phone_portrait'
            else:
                diagonal = math.sqrt(Window.width**2 + Window.height**2) / Window.dpi
                if diagonal > 7:
                    return 'tablet'
                else:
                    return 'phone'
        else:
            # Десктопное устройство
            if Window.width >= 1920 and Window.height >= 1080:
                return 'desktop_large'
            elif Window.width >= 1366 and Window.height >= 768:
                return 'desktop_medium'
            else:
                return 'desktop_small'
    
    @staticmethod
    def get_screen_metrics():
        """Получаем метрики экрана для адаптивной настройки"""
        device_type = SmartScreenDetector.get_device_type()
        
        metrics = {
            'device_type': device_type,
            'width': Window.width,
            'height': Window.height,
            'dpi': Window.dpi,
            'aspect_ratio': Window.width / Window.height if Window.height > 0 else 0,
            'is_mobile': platform in ['android', 'ios'],
            'is_tablet': device_type == 'tablet',
            'is_phone': 'phone' in device_type,
            'is_desktop': 'desktop' in device_type
        }
        
        # Диагональ в дюймах (приблизительно)
        if Window.dpi > 0:
            metrics['diagonal_inches'] = math.sqrt(
                (Window.width/Window.dpi)**2 + (Window.height/Window.dpi)**2
            )
        else:
            metrics['diagonal_inches'] = 0
        
        return metrics

class GameSettings:
    """Класс для управления настройками игры"""
    
    def __init__(self):
        self.settings_file = 'game_settings.json'
        self.default_settings = {
            'sound_volume': 0.8,
            'music_volume': 0.6,
            'vibration': True,
            'joystick_size': 0.8,
            'difficulty': 'medium',  # easy, medium, hard
            'show_tutorial': True,
            'graphics_quality': 'medium',  # low, medium, high
            'control_sensitivity': 0.7,
            'camera_smoothing': 0.9,
            'camera_follow_speed': 0.1
        }
        self.current_settings = self.load_settings()
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Объединяем с дефолтными настройки
                    for key in self.default_settings:
                        if key not in loaded_settings:
                            loaded_settings[key] = self.default_settings[key]
                    return loaded_settings
        except:
            pass
        return self.default_settings.copy()
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings, f, indent=2)
            return True
        except:
            return False
    
    def get_setting(self, key):
        """Получение значения настройки"""
        return self.current_settings.get(key, self.default_settings.get(key))
    
    def set_setting(self, key, value):
        """Установка значения настройки"""
        self.current_settings[key] = value
        self.save_settings()

class AnimatedButton(Button):
    """Анимированная кнопка с эффектами"""
    
    def __init__(self, **kwargs):
        super(AnimatedButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.bind(on_press=self.on_button_press)
        self.bind(on_release=self.on_button_release)
    
    def on_button_press(self, instance):
        """Анимация при нажатии"""
        # Анимация изменения цвета при нажатии
        anim = Animation(background_color=(0.1, 0.4, 0.6, 1), duration=0.1)
        anim.start(self)
    
    def on_button_release(self, instance):
        """Анимация при отпускании"""
        # Возвращаем исходный цвет
        anim = Animation(background_color=(0.2, 0.6, 0.8, 1), duration=0.1)
        anim.start(self)

class MenuButton(AnimatedButton):
    """Специальная кнопка для меню"""
    
    def __init__(self, **kwargs):
        super(MenuButton, self).__init__(**kwargs)
        self.font_size = dp(24)
        self.size_hint = (0.6, 0.1)
        self.pos_hint = {'center_x': 0.5}
        self.background_color = (0.2, 0.6, 0.8, 1)
        self.color = (1, 1, 1, 1)

class GameMenuButton(Button):
    """Кнопка меню для игрового экрана"""
    
    def __init__(self, **kwargs):
        super(GameMenuButton, self).__init__(**kwargs)
        self.font_size = dp(18)
        self.size_hint = (None, None)
        self.size = (dp(100), dp(40))
        self.background_color = (0.2, 0.6, 0.8, 1)
        self.color = (1, 1, 1, 1)
        self.background_normal = ''
        
    def on_press(self):
        """Анимация при нажатии"""
        self.background_color = (0.1, 0.4, 0.6, 1)
    
    def on_release(self):
        """Анимация при отпускании"""
        self.background_color = (0.2, 0.6, 0.8, 1)

class MainMenuScreen(Screen):
    """Главное меню игры"""
    
    def __init__(self, **kwargs):
        super(MainMenuScreen, self).__init__(**kwargs)
        self.name = 'main_menu'
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Заголовок игры
        title_label = Label(
            text='КРАСНЫЙ КВАДРАТ',
            font_size=dp(48),
            bold=True,
            color=(1, 0.2, 0.2, 1),
            size_hint=(1, 0.3)
        )
        layout.add_widget(title_label)
        
        # Версия игры
        version_label = Label(
            text='Версия 1.0',
            font_size=dp(16),
            color=(0.5, 0.5, 0.5, 1),
            size_hint=(1, 0.1)
        )
        layout.add_widget(version_label)
        
        # Кнопки меню
        buttons_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint=(1, 0.6))
        
        play_button = MenuButton(text='ИГРАТЬ')
        play_button.bind(on_press=self.start_game)
        buttons_layout.add_widget(play_button)
        
        settings_button = MenuButton(text='НАСТРОЙКИ')
        settings_button.bind(on_press=self.open_settings)
        buttons_layout.add_widget(settings_button)
        
        stats_button = MenuButton(text='СТАТИСТИКА')
        stats_button.bind(on_press=self.show_stats)
        buttons_layout.add_widget(stats_button)
        
        help_button = MenuButton(text='ПОМОЩЬ')
        help_button.bind(on_press=self.show_help)
        buttons_layout.add_widget(help_button)
        
        exit_button = MenuButton(text='ВЫХОД')
        exit_button.bind(on_press=self.exit_game)
        buttons_layout.add_widget(exit_button)
        
        layout.add_widget(buttons_layout)
        
        self.add_widget(layout)
    
    def start_game(self, instance):
        """Запуск игры"""
        self.manager.current = 'game'
        self.manager.get_screen('game').start_new_game()
    
    def open_settings(self, instance):
        """Открытие настроек"""
        self.manager.current = 'settings'
    
    def show_stats(self, instance):
        """Показать статистику"""
        self.manager.current = 'stats'
    
    def show_help(self, instance):
        """Показать помощь"""
        self.manager.current = 'help'
    
    def exit_game(self, instance):
        """Выход из игры"""
        App.get_running_app().stop()

class SettingsScreen(Screen):
    """Экран настроек"""
    
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.name = 'settings'
        self.settings = GameSettings()
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Заголовок
        title_label = Label(
            text='НАСТРОЙКИ',
            font_size=dp(36),
            bold=True,
            color=(0.2, 0.6, 0.8, 1),
            size_hint=(1, 0.2)
        )
        main_layout.add_widget(title_label)
        
        # Скроллируемая область для настроек
        from kivy.uix.scrollview import ScrollView
        scroll_view = ScrollView(size_hint=(1, 0.7))
        
        settings_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        settings_layout.bind(minimum_height=settings_layout.setter('height'))
        
        # Громкость звука
        sound_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        sound_label = Label(text='Громкость звука:', size_hint=(0.5, 1))
        sound_slider = Slider(min=0, max=1, value=self.settings.get_setting('sound_volume'), size_hint=(0.5, 1))
        sound_slider.bind(value=self.on_sound_volume_change)
        sound_layout.add_widget(sound_label)
        sound_layout.add_widget(sound_slider)
        settings_layout.add_widget(sound_layout)
        
        # Громкость музыки
        music_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        music_label = Label(text='Громкость музыки:', size_hint=(0.5, 1))
        music_slider = Slider(min=0, max=1, value=self.settings.get_setting('music_volume'), size_hint=(0.5, 1))
        music_slider.bind(value=self.on_music_volume_change)
        music_layout.add_widget(music_label)
        music_layout.add_widget(music_slider)
        settings_layout.add_widget(music_layout)
        
        # Вибрация
        vibro_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        vibro_label = Label(text='Вибрация:', size_hint=(0.5, 1))
        vibro_switch = Switch(active=self.settings.get_setting('vibration'), size_hint=(0.5, 1))
        vibro_switch.bind(active=self.on_vibration_change)
        vibro_layout.add_widget(vibro_label)
        vibro_layout.add_widget(vibro_switch)
        settings_layout.add_widget(vibro_layout)
        
        # Чувствительность управления
        sens_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        sens_label = Label(text='Чувствительность:', size_hint=(0.5, 1))
        sens_slider = Slider(min=0.1, max=1.5, value=self.settings.get_setting('control_sensitivity'), size_hint=(0.5, 1))
        sens_slider.bind(value=self.on_sensitivity_change)
        sens_layout.add_widget(sens_label)
        sens_layout.add_widget(sens_slider)
        settings_layout.add_widget(sens_layout)
        
        # Плавность камеры
        camera_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        camera_label = Label(text='Плавность камеры:', size_hint=(0.5, 1))
        camera_slider = Slider(min=0.5, max=0.99, value=self.settings.get_setting('camera_smoothing'), size_hint=(0.5, 1))
        camera_slider.bind(value=self.on_camera_smoothing_change)
        camera_layout.add_widget(camera_label)
        camera_layout.add_widget(camera_slider)
        settings_layout.add_widget(camera_layout)
        
        # Скорость следования камеры
        camera_speed_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        camera_speed_label = Label(text='Скорость камеры:', size_hint=(0.5, 1))
        camera_speed_slider = Slider(min=0.01, max=0.5, value=self.settings.get_setting('camera_follow_speed'), size_hint=(0.5, 1))
        camera_speed_slider.bind(value=self.on_camera_speed_change)
        camera_speed_layout.add_widget(camera_speed_label)
        camera_speed_layout.add_widget(camera_speed_slider)
        settings_layout.add_widget(camera_speed_layout)
        
        scroll_view.add_widget(settings_layout)
        main_layout.add_widget(scroll_view)
        
        # Кнопки
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint=(1, 0.1))
        
        back_button = MenuButton(text='НАЗАД')
        back_button.size_hint = (0.4, 1)
        back_button.bind(on_press=self.go_back)
        buttons_layout.add_widget(back_button)
        
        reset_button = MenuButton(text='СБРОС')
        reset_button.size_hint = (0.4, 1)
        reset_button.bind(on_press=self.reset_settings)
        buttons_layout.add_widget(reset_button)
        
        main_layout.add_widget(buttons_layout)
        
        self.add_widget(main_layout)
    
    def on_sound_volume_change(self, instance, value):
        self.settings.set_setting('sound_volume', value)
    
    def on_music_volume_change(self, instance, value):
        self.settings.set_setting('music_volume', value)
    
    def on_vibration_change(self, instance, value):
        self.settings.set_setting('vibration', value)
    
    def on_difficulty_change(self, instance, value):
        self.settings.set_setting('difficulty', value)
    
    def on_sensitivity_change(self, instance, value):
        self.settings.set_setting('control_sensitivity', value)
    
    def on_camera_smoothing_change(self, instance, value):
        self.settings.set_setting('camera_smoothing', value)
    
    def on_camera_speed_change(self, instance, value):
        self.settings.set_setting('camera_follow_speed', value)
    
    def reset_settings(self, instance):
        """Сброс настроек к значениям по умолчанию"""
        self.settings.current_settings = self.settings.default_settings.copy()
        self.settings.save_settings()
        self.manager.current = 'main_menu'
        self.manager.current = 'settings'  # Перезагружаем экран
    
    def go_back(self, instance):
        self.manager.current = 'main_menu'

class StatsScreen(Screen):
    """Экран статистики"""
    
    def __init__(self, **kwargs):
        super(StatsScreen, self).__init__(**kwargs)
        self.name = 'stats'
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Заголовок
        title_label = Label(
            text='СТАТИСТИКА',
            font_size=dp(36),
            bold=True,
            color=(0.2, 0.6, 0.8, 1),
            size_hint=(1, 0.2)
        )
        layout.add_widget(title_label)
        
        # Статистика
        from kivy.uix.gridlayout import GridLayout
        stats_grid = GridLayout(cols=2, spacing=dp(10), size_hint=(1, 0.6))
        
        stats_data = [
            ('Игр сыграно:', '15'),
            ('Рекорд:', '1250 очков'),
            ('Время игры:', '2ч 30м'),
            ('Препятствий пройдено:', '342'),
            ('Столкновений:', '87'),
            ('Уровень:', '5')
        ]
        
        for stat_name, stat_value in stats_data:
            name_label = Label(text=stat_name, font_size=dp(20), halign='right')
            value_label = Label(text=stat_value, font_size=dp(20), bold=True, color=(1, 0.2, 0.2, 1))
            stats_grid.add_widget(name_label)
            stats_grid.add_widget(value_label)
        
        layout.add_widget(stats_grid)
        
        # Кнопка назад
        back_button = MenuButton(text='НАЗАД')
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = 'main_menu'

class HelpScreen(Screen):
    """Экран помощи"""
    
    def __init__(self, **kwargs):
        super(HelpScreen, self).__init__(**kwargs)
        self.name = 'help'
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Заголовок
        title_label = Label(
            text='ПОМОЩЬ',
            font_size=dp(36),
            bold=True,
            color=(0.2, 0.6, 0.8, 1),
            size_hint=(1, 0.2)
        )
        layout.add_widget(title_label)
        
        # Текст помощи
        from kivy.uix.scrollview import ScrollView
        scroll_view = ScrollView(size_hint=(1, 0.7))
        
        help_text = """
        УПРАВЛЕНИЕ:
        
        • Мобильные устройства:
          Используйте джойстик в левом нижнем углу
          для управления красным квадратом.
        
        • Компьютер:
          Используйте клавиши WASD или стрелки
          для управления.
          R - сброс позиции квадрата
          C - центрировать камеру
        
        ЦЕЛЬ ИГРЫ:
        
        Управляйте красным квадратом по карте,
        избегая столкновений с границами и препятствиями.
        
        КАРТА:
        
        • Зеленые зоны - безопасные области
        • Красные границы - непроходимые стены
        • Синие препятствия - избегайте их
        
        ПОДСКАЗКИ:
        
        • Используйте плавные движения для
          лучшего контроля.
        
        • Изучайте карту перед началом движения.
        """
        
        help_label = Label(
            text=help_text,
            font_size=dp(18),
            halign='left',
            valign='top',
            text_size=(Window.width - dp(40), None),
            size_hint_y=None
        )
        help_label.bind(texture_size=help_label.setter('size'))
        
        scroll_view.add_widget(help_label)
        layout.add_widget(scroll_view)
        
        # Кнопка назад
        back_button = MenuButton(text='НАЗАД')
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = 'main_menu'

class GameWorld(Widget):
    """Игровой мир с картой и границами"""
    
    def __init__(self, **kwargs):
        super(GameWorld, self).__init__(**kwargs)
        
        # Размер карты
        self.world_width = Window.width * 5
        self.world_height = Window.height * 5
        
        # Границы карты (отступ от краев)
        self.border_thickness = dp(30)
        self.border_left = self.border_thickness
        self.border_right = self.world_width - self.border_thickness
        self.border_top = self.world_height - self.border_thickness
        self.border_bottom = self.border_thickness
        
        # Создаем мир
        with self.canvas.before:
            PushMatrix()
            self.translate = Translate(0, 0)
            
            # Фон карты
            self.create_background()
            
            # Границы карты
            self.create_borders()
            
            # Препятствия
            self.create_obstacles()
            
            # Зоны интереса
            self.create_zones()
            
        with self.canvas.after:
            PopMatrix()
    
    def create_background(self):
        """Создание фона карты"""
        # Основной фон
        Color(0.85, 0.9, 0.95, 1)
        self.bg_rect = Rectangle(pos=(0, 0), size=(self.world_width, self.world_height))
        
        # Сетка для карты
        cell_size = dp(100)
        grid_alpha = 0.15
        
        # Вертикальные линии
        for x in range(0, int(self.world_width) + 1, int(cell_size)):
            Color(0.4, 0.5, 0.6, grid_alpha)
            Line(points=[x, 0, x, self.world_height], width=1)
        
        # Горизонтальные линии
        for y in range(0, int(self.world_height) + 1, int(cell_size)):
            Color(0.4, 0.5, 0.6, grid_alpha)
            Line(points=[0, y, self.world_width, y], width=1)
    
    def create_borders(self):
        """Создание границ карты"""
        border_alpha = 0.8
        
        # Левая граница
        Color(1, 0.3, 0.3, border_alpha)
        Rectangle(
            pos=(0, 0),
            size=(self.border_thickness, self.world_height)
        )
        
        # Правая граница
        Rectangle(
            pos=(self.world_width - self.border_thickness, 0),
            size=(self.border_thickness, self.world_height)
        )
        
        # Верхняя граница
        Rectangle(
            pos=(0, self.world_height - self.border_thickness),
            size=(self.world_width, self.border_thickness)
        )
        
        # Нижняя граница
        Rectangle(
            pos=(0, 0),
            size=(self.world_width, self.border_thickness)
        )
        
        # Визуальные маркеры углов
        corner_size = dp(15)
        Color(1, 0.2, 0.2, 1)
        
        # Левый нижний угол
        Rectangle(
            pos=(0, 0),
            size=(corner_size, corner_size)
        )
        
        # Правый нижний угол
        Rectangle(
            pos=(self.world_width - corner_size, 0),
            size=(corner_size, corner_size)
        )
        
        # Левый верхний угол
        Rectangle(
            pos=(0, self.world_height - corner_size),
            size=(corner_size, corner_size)
        )
        
        # Правый верхний угол
        Rectangle(
            pos=(self.world_width - corner_size, self.world_height - corner_size),
            size=(corner_size, corner_size)
        )
    
    def create_obstacles(self):
        """Создание препятствий на карте"""
        self.obstacles = []
        
        # Центральное препятствие
        center_x = self.world_width / 2
        center_y = self.world_height / 2
        obstacle_size = dp(150)
        
        Color(0.2, 0.4, 0.8, 0.7)
        obstacle = Rectangle(
            pos=(center_x - obstacle_size/2, center_y - obstacle_size/2),
            size=(obstacle_size, obstacle_size)
        )
        self.obstacles.append({
            'rect': obstacle,
            'pos': (center_x - obstacle_size/2, center_y - obstacle_size/2),
            'size': (obstacle_size, obstacle_size)
        })
        
        # Препятствия в углах
        corner_obstacle_size = dp(100)
        
        # Левый верхний угол
        Color(0.2, 0.4, 0.8, 0.7)
        obstacle = Rectangle(
            pos=(self.border_thickness * 3, self.world_height - self.border_thickness * 3 - corner_obstacle_size),
            size=(corner_obstacle_size, corner_obstacle_size)
        )
        self.obstacles.append({
            'rect': obstacle,
            'pos': (self.border_thickness * 3, self.world_height - self.border_thickness * 3 - corner_obstacle_size),
            'size': (corner_obstacle_size, corner_obstacle_size)
        })
        
        # Правый нижний угол
        Color(0.2, 0.4, 0.8, 0.7)
        obstacle = Rectangle(
            pos=(self.world_width - self.border_thickness * 3 - corner_obstacle_size, self.border_thickness * 3),
            size=(corner_obstacle_size, corner_obstacle_size)
        )
        self.obstacles.append({
            'rect': obstacle,
            'pos': (self.world_width - self.border_thickness * 3 - corner_obstacle_size, self.border_thickness * 3),
            'size': (corner_obstacle_size, corner_obstacle_size)
        })
        
        # Препятствия по периметру
        perimeter_obstacle_size = dp(80)
        
        # Верхний ряд
        for i in range(3):
            x = self.world_width * 0.25 * (i + 1) - perimeter_obstacle_size/2
            y = self.world_height * 0.8
            Color(0.2, 0.4, 0.8, 0.7)
            obstacle = Rectangle(
                pos=(x, y),
                size=(perimeter_obstacle_size, perimeter_obstacle_size)
            )
            self.obstacles.append({
                'rect': obstacle,
                'pos': (x, y),
                'size': (perimeter_obstacle_size, perimeter_obstacle_size)
            })
        
        # Левый ряд
        for i in range(2):
            x = self.world_width * 0.1
            y = self.world_height * 0.3 * (i + 1) - perimeter_obstacle_size/2
            Color(0.2, 0.4, 0.8, 0.7)
            obstacle = Rectangle(
                pos=(x, y),
                size=(perimeter_obstacle_size, perimeter_obstacle_size)
            )
            self.obstacles.append({
                'rect': obstacle,
                'pos': (x, y),
                'size': (perimeter_obstacle_size, perimeter_obstacle_size)
            })
    
    def create_zones(self):
        """Создание специальных зон на карте"""
        # Стартовая зона (зеленая)
        start_zone_size = dp(200)
        start_x = self.border_thickness * 2
        start_y = self.border_thickness * 2
        
        Color(0.4, 0.8, 0.4, 0.3)
        Rectangle(
            pos=(start_x, start_y),
            size=(start_zone_size, start_zone_size)
        )
        
        # Текст "Старт"
        with self.canvas:
            Color(0.2, 0.6, 0.2, 0.8)
            # Упрощенная версия - просто квадрат с надписью
            Rectangle(
                pos=(start_x + start_zone_size/4, start_y + start_zone_size/4),
                size=(start_zone_size/2, start_zone_size/2)
            )
        
        # Финишная зона (желтая)
        finish_zone_size = dp(200)
        finish_x = self.world_width - self.border_thickness * 2 - finish_zone_size
        finish_y = self.world_height - self.border_thickness * 2 - finish_zone_size
        
        Color(1, 0.8, 0.2, 0.3)
        Rectangle(
            pos=(finish_x, finish_y),
            size=(finish_zone_size, finish_zone_size)
        )
        
        # Текст "Финиш"
        with self.canvas:
            Color(0.8, 0.6, 0.1, 0.8)
            # Упрощенная версия - просто квадрат с надписью
            Rectangle(
                pos=(finish_x + finish_zone_size/4, finish_y + finish_zone_size/4),
                size=(finish_zone_size/2, finish_zone_size/2)
            )
    
    def check_collision(self, x, y, size):
        """Проверка столкновения с границами и препятствиями"""
        # Проверка границ
        if (x < self.border_left or 
            x + size > self.border_right or 
            y < self.border_bottom or 
            y + size > self.border_top):
            return True
        
        # Проверка препятствий
        for obstacle in self.obstacles:
            obs_x, obs_y = obstacle['pos']
            obs_w, obs_h = obstacle['size']
            
            # Простая проверка пересечения прямоугольников
            if (x < obs_x + obs_w and
                x + size > obs_x and
                y < obs_y + obs_h and
                y + size > obs_y):
                return True
        
        return False
    
    def update_camera(self, camera_x, camera_y):
        """Обновление позиции камеры"""
        self.translate.x = -camera_x
        self.translate.y = -camera_y

class AdaptiveMovingSquare(Widget):
    """Адаптивный движущийся квадрат"""
    pos_x = NumericProperty(0)
    pos_y = NumericProperty(0)
    square_size = NumericProperty(0)
    current_speed_x = NumericProperty(0)
    current_speed_y = NumericProperty(0)
    max_speed = NumericProperty(0)
    acceleration = NumericProperty(0)
    deceleration = NumericProperty(0)
    target_direction_x = NumericProperty(0)
    target_direction_y = NumericProperty(0)
    
    def __init__(self, game_world, **kwargs):
        super(AdaptiveMovingSquare, self).__init__(**kwargs)
        
        self.metrics = SmartScreenDetector.get_screen_metrics()
        self.game_world = game_world
        self.world_width = game_world.world_width
        self.world_height = game_world.world_height
        
        self.adaptive_setup()
        self.init_graphics()
    
    def adaptive_setup(self):
        """Адаптивная настройка параметров"""
        min_side = min(Window.width, Window.height)
        
        # Адаптивный размер
        if self.metrics['is_phone']:
            self.square_size = min_side * 0.08  # 8% для телефонов
            self.max_speed = min_side * 0.3
        elif self.metrics['is_tablet']:
            self.square_size = min_side * 0.06  # 6% для планшетов
            self.max_speed = min_side * 0.25
        else:
            self.square_size = min_side * 0.05  # 5% для десктопов
            self.max_speed = min_side * 0.2
        
        # Адаптивное ускорение
        self.acceleration = self.max_speed * (1.5 if self.metrics['is_mobile'] else 2.0)
        self.deceleration = self.max_speed * (2.0 if self.metrics['is_mobile'] else 2.5)
        
        # Начальная позиция (в стартовой зоне)
        start_x = self.game_world.border_thickness * 2 + dp(50)
        start_y = self.game_world.border_thickness * 2 + dp(50)
        self.pos_x = start_x
        self.pos_y = start_y
    
    def init_graphics(self):
        """Инициализация графики с адаптивными параметрами"""
        with self.canvas:
            # Основной квадрат
            Color(1, 0.2, 0.2, 1)  # Красный цвет
            self.rect = Rectangle(pos=(self.pos_x, self.pos_y), size=(self.square_size, self.square_size))
    
    def update_position(self, dt):
        """Обновление позиции с проверкой столкновений"""
        # Плавное изменение скорости
        self.apply_smooth_acceleration(dt)
        
        # Пробуем переместиться
        new_x = self.pos_x + self.current_speed_x * dt
        new_y = self.pos_y + self.current_speed_y * dt
        
        # Проверяем столкновения
        if not self.game_world.check_collision(new_x, new_y, self.square_size):
            # Если нет столкновения - перемещаемся
            self.pos_x = new_x
            self.pos_y = new_y
        else:
            # Столкновение - отскакиваем
            self.handle_collision()
        
        # Замедление при отсутствии ввода
        if abs(self.target_direction_x) < 0.1 and abs(self.target_direction_y) < 0.1:
            self.apply_friction(dt)
        
        # Обновляем графику
        self.rect.pos = (self.pos_x, self.pos_y)
    
    def handle_collision(self):
        """Обработка столкновения"""
        # Отскок от препятствий
        bounce_factor = 0.5
        
        self.current_speed_x = -self.current_speed_x * bounce_factor
        self.current_speed_y = -self.current_speed_y * bounce_factor
        
        # Немного отодвигаем от места столкновения
        self.pos_x += self.current_speed_x * 0.1
        self.pos_y += self.current_speed_y * 0.1
    
    def apply_smooth_acceleration(self, dt):
        """Плавное ускорение"""
        target_speed_x = self.target_direction_x * self.max_speed
        target_speed_y = self.target_direction_y * self.max_speed
        
        speed_diff_x = target_speed_x - self.current_speed_x
        speed_diff_y = target_speed_y - self.current_speed_y
        
        # Адаптивная скорость изменения
        change_rate = self.acceleration * dt * (1.2 if self.metrics['is_desktop'] else 1.0)
        
        if abs(speed_diff_x) > 0.1:
            self.current_speed_x += math.copysign(
                min(abs(speed_diff_x), change_rate), 
                speed_diff_x
            )
        else:
            self.current_speed_x = target_speed_x
        
        if abs(speed_diff_y) > 0.1:
            self.current_speed_y += math.copysign(
                min(abs(speed_diff_y), change_rate), 
                speed_diff_y
            )
        else:
            self.current_speed_y = target_speed_y
    
    def apply_friction(self, dt):
        """Плавное замедление"""
        # Адаптивный коэффициент трения
        if self.metrics['is_mobile']:
            friction_base = 0.92
        else:
            friction_base = 0.88
        
        friction_factor = friction_base ** (dt * 60)
        
        self.current_speed_x *= friction_factor
        self.current_speed_y *= friction_factor
        
        # Порог остановки
        stop_threshold = 3 if self.metrics['is_mobile'] else 5
        if abs(self.current_speed_x) < stop_threshold:
            self.current_speed_x = 0
        if abs(self.current_speed_y) < stop_threshold:
            self.current_speed_y = 0
    
    def set_target_direction(self, dx, dy):
        """Установка целевого направления"""
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            normalized_length = min(length, 1.0)
            # Адаптивная чувствительность
            power = 0.6 if self.metrics['is_mobile'] else 0.7
            sensitivity = normalized_length ** power
            
            self.target_direction_x = (dx / length) * sensitivity
            self.target_direction_y = (dy / length) * sensitivity
        else:
            self.target_direction_x = 0
            self.target_direction_y = 0
    
    def reset_position(self):
        """Сброс позиции в стартовую зону"""
        # Плавное перемещение к старту
        self.target_direction_x = 0
        self.target_direction_y = 0
        self.current_speed_x = 0
        self.current_speed_y = 0
        
        # Возвращаем квадрат в стартовую зону
        start_x = self.game_world.border_thickness * 2 + dp(50)
        start_y = self.game_world.border_thickness * 2 + dp(50)
        self.pos_x = start_x
        self.pos_y = start_y

class SmoothCamera:
    """Плавная камера, следующая за игроком"""
    
    def __init__(self, settings):
        self.settings = settings
        self.camera_x = 0
        self.camera_y = 0
        self.target_x = 0
        self.target_y = 0
        
    def update(self, player_x, player_y, screen_width, screen_height):
        """Обновление позиции камеры"""
        # Цель камеры - позиция игрока в центре экрана
        self.target_x = player_x - screen_width / 2
        self.target_y = player_y - screen_height / 2
        
        # Плавное следование за игроком
        follow_speed = self.settings.get_setting('camera_follow_speed')
        
        # Интерполяция для плавного движения
        self.camera_x += (self.target_x - self.camera_x) * follow_speed
        self.camera_y += (self.target_y - self.camera_y) * follow_speed
        
        return self.camera_x, self.camera_y
    
    def reset(self, player_x, player_y, screen_width, screen_height):
        """Сброс камеры"""
        self.camera_x = player_x - screen_width / 2
        self.camera_y = player_y - screen_height / 2
        self.target_x = self.camera_x
        self.target_y = self.camera_y

class GameScreen(Screen):
    """Игровой экран с картой"""
    
    screen_width = NumericProperty(0)
    screen_height = NumericProperty(0)
    joystick_active = BooleanProperty(False)
    joystick_pos = ObjectProperty((0, 0))
    joystick_center = ObjectProperty((0, 0))
    joystick_radius = NumericProperty(0)
    game_active = BooleanProperty(False)
    menu_button = ObjectProperty(None)
    camera_x = NumericProperty(0)
    camera_y = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.name = 'game'
        self.game_active = False
        self.clock_event = None
        
        # Получаем метрики устройства
        self.metrics = SmartScreenDetector.get_screen_metrics()
        
        # Инициализация размеров
        self.screen_width = Window.width
        self.screen_height = Window.height
        
        # Настройки
        self.settings = GameSettings()
        
        # Камера
        self.camera = SmoothCamera(self.settings)
        
        # Создаем интерфейс
        self.create_interface()
        
        # Настройка управления
        self.setup_controls()
        
        # Отслеживаем изменение размера
        Window.bind(on_resize=self.on_window_resize)
    
    def create_interface(self):
        """Создание адаптивного интерфейса"""
        # Создаем игровой мир
        self.game_world = GameWorld()
        self.add_widget(self.game_world)
        
        # Создаем квадрат игрока
        self.square = AdaptiveMovingSquare(self.game_world)
        self.game_world.add_widget(self.square)
        
        # Джойстик (рисуется отдельно)
        self.init_joystick()
        
        # Кнопка меню в верхнем правом углу
        self.create_menu_button()
        
        # Отрисовываем джойстик
        self.draw_joystick()
    
    def create_menu_button(self):
        """Создание кнопки меню в верхнем правом углу"""
        self.menu_button = GameMenuButton(text='МЕНЮ')
        self.menu_button.pos = (self.screen_width - dp(110), self.screen_height - dp(50))
        self.menu_button.bind(on_press=self.return_to_menu)
        self.add_widget(self.menu_button)
    
    def init_joystick(self):
        """Инициализация адаптивного джойстика"""
        min_side = min(self.screen_width, self.screen_height)
        
        # Адаптивный размер джойстика
        if self.metrics['is_phone']:
            self.joystick_radius = min_side * 0.12
            joystick_margin = self.joystick_radius * 1.6
        elif self.metrics['is_tablet']:
            self.joystick_radius = min_side * 0.1
            joystick_margin = self.joystick_radius * 1.8
        else:
            self.joystick_radius = min_side * 0.08
            joystick_margin = self.joystick_radius * 2.0
        
        # Позиция джойстика (фиксированная относительно экрана)
        self.joystick_center = (joystick_margin, joystick_margin)
        self.joystick_pos = self.joystick_center
        
        # Адаптивное сглаживание
        if self.metrics['is_mobile']:
            self.joystick_smoothing = 0.7  # Быстрее реагирует на мобильных
        else:
            self.joystick_smoothing = 0.8
    
    def draw_joystick(self):
        """Отрисовка адаптивного джойстика"""
        with self.canvas:
            # Внешний круг джойстика
            Color(0.4, 0.4, 0.5, 0.3)
            Ellipse(
                pos=(self.joystick_center[0] - self.joystick_radius,
                     self.joystick_center[1] - self.joystick_radius),
                size=(self.joystick_radius * 2, self.joystick_radius * 2)
            )
            
            # Внутренний круг джойстика
            inner_size = 0.6
            Color(0.4, 0.4, 0.5, 0.5)
            
            pos_x = self.joystick_pos[0] - self.joystick_radius * inner_size
            pos_y = self.joystick_pos[1] - self.joystick_radius * inner_size
            size = self.joystick_radius * (inner_size * 2)
            
            self.joystick_circle = Ellipse(
                pos=(pos_x, pos_y),
                size=(size, size)
            )
    
    def setup_controls(self):
        """Настройка управления"""
        if not self.metrics['is_mobile']:
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
    
    def start_new_game(self):
        """Начать новую игру"""
        self.game_active = True
        self.square.reset_position()
        self.camera.reset(
            self.square.pos_x,
            self.square.pos_y,
            self.screen_width,
            self.screen_height
        )
        
        # Запуск игрового цикла
        if self.clock_event:
            self.clock_event.cancel()
        self.clock_event = Clock.schedule_interval(self.update_game, 1.0/60.0)
    
    def update_game(self, dt):
        """Обновление игры"""
        if not self.game_active:
            return
        
        # Обновляем позицию квадрата
        self.square.update_position(dt)
        
        # Обновляем камеру
        self.camera_x, self.camera_y = self.camera.update(
            self.square.pos_x,
            self.square.pos_y,
            self.screen_width,
            self.screen_height
        )
        
        # Обновляем трансформацию камеры в игровом мире
        self.game_world.update_camera(self.camera_x, self.camera_y)
        
        # Управление джойстиком
        if self.joystick_active:
            dx = self.joystick_pos[0] - self.joystick_center[0]
            dy = self.joystick_pos[1] - self.joystick_center[1]
            
            distance = math.sqrt(dx * dx + dy * dy)
            dead_zone = self.joystick_radius * (0.15 if self.metrics['is_mobile'] else 0.1)
            
            if distance > dead_zone:
                normalized_distance = min(distance / self.joystick_radius, 1.0)
                # Адаптивная кривая управления
                power = 1.3 if self.metrics['is_mobile'] else 1.5
                control_factor = normalized_distance ** power
                
                self.square.set_target_direction(
                    dx * control_factor,
                    dy * control_factor
                )
            else:
                self.square.set_target_direction(0, 0)
        else:
            self.square.set_target_direction(0, 0)
        
        # Обновление джойстика
        self.update_joystick_drawing()
    
    def update_joystick_drawing(self):
        """Обновление отрисовки джойстика"""
        inner_size = 0.6
        target_pos = (
            self.joystick_pos[0] - self.joystick_radius * inner_size,
            self.joystick_pos[1] - self.joystick_radius * inner_size
        )
        
        current_pos = self.joystick_circle.pos
        smooth_pos = (
            current_pos[0] * self.joystick_smoothing + target_pos[0] * (1 - self.joystick_smoothing),
            current_pos[1] * self.joystick_smoothing + target_pos[1] * (1 - self.joystick_smoothing)
        )
        
        self.joystick_circle.pos = smooth_pos
    
    def on_window_resize(self, window, width, height):
        """Обработка изменения размера окна"""
        self.screen_width = width
        self.screen_height = height
        self.metrics = SmartScreenDetector.get_screen_metrics()
        
        # Обновляем позицию кнопки меню
        if self.menu_button:
            self.menu_button.pos = (width - dp(110), height - dp(50))
        
        # Обновляем позицию камеры
        self.camera.reset(
            self.square.pos_x,
            self.square.pos_y,
            width,
            height
        )
    
    def _keyboard_closed(self):
        if hasattr(self, '_keyboard'):
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard.unbind(on_key_up=self._on_keyboard_up)
            self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        
        # Адаптивная скорость для клавиатуры
        speed = 0.8 if self.metrics['device_type'] == 'desktop_large' else 0.7
        
        if key in ('w', 'up'):
            self.square.target_direction_y = speed
        elif key in ('s', 'down'):
            self.square.target_direction_y = -speed
        elif key in ('a', 'left'):
            self.square.target_direction_x = -speed
        elif key in ('d', 'right'):
            self.square.target_direction_x = speed
        elif key == 'r':
            self.reset_game()
        elif key == 'c':
            self.center_camera()
        elif key == 'escape':
            self.return_to_menu()
        
        return True
    
    def _on_keyboard_up(self, keyboard, keycode):
        key = keycode[1]
        
        if key in ('w', 'up', 's', 'down'):
            self.square.target_direction_y = 0
        elif key in ('a', 'left', 'd', 'right'):
            self.square.target_direction_x = 0
        
        return True
    
    def on_touch_down(self, touch):
        touch_x, touch_y = touch.pos
        
        # Проверка джойстика (фиксированная позиция на экране)
        dx = touch_x - self.joystick_center[0]
        dy = touch_y - self.joystick_center[1]
        distance_to_joystick = math.sqrt(dx * dx + dy * dy)
        
        # Адаптивная зона касания джойстика
        touch_radius = self.joystick_radius * (1.8 if self.metrics['is_mobile'] else 1.5)
        
        if distance_to_joystick <= touch_radius:
            self.joystick_active = True
            self.joystick_pos = touch.pos
            touch.ud['is_joystick'] = True
            return True
        
        return super(GameScreen, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if 'is_joystick' in touch.ud:
            self.joystick_active = False
            self.joystick_pos = self.joystick_center
            return True
        
        return super(GameScreen, self).on_touch_up(touch)
    
    def on_touch_move(self, touch):
        if 'is_joystick' in touch.ud:
            touch_x, touch_y = touch.pos
            
            dx = touch_x - self.joystick_center[0]
            dy = touch_y - self.joystick_center[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > self.joystick_radius:
                scale = self.joystick_radius / distance
                self.joystick_pos = (
                    self.joystick_center[0] + dx * scale,
                    self.joystick_center[1] + dy * scale
                )
            else:
                self.joystick_pos = touch.pos
            
            return True
        
        return super(GameScreen, self).on_touch_move(touch)
    
    def reset_game(self, instance=None):
        """Сброс игры"""
        self.square.reset_position()
        self.camera.reset(
            self.square.pos_x,
            self.square.pos_y,
            self.screen_width,
            self.screen_height
        )
        self.game_active = True
    
    def center_camera(self):
        """Центрировать камеру на игроке"""
        self.camera.reset(
            self.square.pos_x,
            self.square.pos_y,
            self.screen_width,
            self.screen_height
        )
    
    def return_to_menu(self, instance=None):
        """Возврат в главное меню"""
        self.game_active = False
        if self.clock_event:
            self.clock_event.cancel()
        self.manager.current = 'main_menu'

class UniversalRedSquareGame(App):
    """Универсальное приложение для всех устройств"""
    
    def build(self):
        # Автоматическая настройка окна
        self.configure_window()
        
        # Создаем менеджер экранов
        sm = ScreenManager()
        
        # Добавляем экраны
        sm.add_widget(MainMenuScreen())
        sm.add_widget(SettingsScreen())
        sm.add_widget(StatsScreen())
        sm.add_widget(HelpScreen())
        sm.add_widget(GameScreen())
        
        return sm
    
    def configure_window(self):
        """Автоматическая настройка окна в зависимости от устройства"""
        metrics = SmartScreenDetector.get_screen_metrics()
        
        if metrics['is_mobile']:
            # Для мобильных - полноэкранный режим
            from kivy.config import Config
            Config.set('graphics', 'fullwidth', 'auto')
            
            # Отключаем мультитач если это не планшет
            if not metrics['is_tablet']:
                Config.set('input', 'multitouchscreen1', '')
        else:
            # Для десктопов - адаптивное окно
            if metrics['device_type'] == 'desktop_large':
                Window.size = (1200, 800)
            elif metrics['device_type'] == 'desktop_medium':
                Window.size = (1024, 768)
            else:
                Window.size = (800, 600)
            
            # Разрешаем изменение размера
            Window.borderless = False
            Window.resizable = True

if __name__ == '__main__':
    UniversalRedSquareGame().run()
