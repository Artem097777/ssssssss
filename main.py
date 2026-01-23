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
            'control_sensitivity': 0.7
        }
        self.current_settings = self.load_settings()
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Объединяем с дефолтными настройками
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
        
        ЦЕЛЬ ИГРЫ:
        
        Управляйте красным квадратом по экрану,
        избегая столкновений с границами экрана.
        
        ПОДСКАЗКИ:
        
        • Используйте плавные движения для
          лучшего контроля.
        
        • Экспериментируйте с разными способами
          управления.
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

class AdaptiveFloorTexture(InstructionGroup):
    """Адаптивная текстура пола"""
    def __init__(self, width, height, **kwargs):
        super(AdaptiveFloorTexture, self).__init__()
        
        self.width = width
        self.height = height
        self.metrics = SmartScreenDetector.get_screen_metrics()
        
        # Адаптивный размер ячейки
        min_side = min(width, height)
        if self.metrics['is_phone']:
            self.cell_size = max(int(dp(30)), int(min_side // 25))
        elif self.metrics['is_tablet']:
            self.cell_size = max(int(dp(40)), int(min_side // 20))
        else:
            self.cell_size = max(int(dp(50)), int(min_side // 15))
        
        self.create_texture()
    
    def create_texture(self):
        """Создание адаптивной текстуры"""
        # Основной фон
        if self.metrics['is_mobile']:
            self.add(Color(0.92, 0.92, 0.95, 1))
        else:
            self.add(Color(0.88, 0.88, 0.92, 1))
        
        self.add(Rectangle(pos=(0, 0), size=(self.width, self.height)))
        
        # Адаптивная сетка
        self.create_grid()
    
    def create_grid(self):
        """Создание адаптивной сетки"""
        # Основная сетка
        grid_alpha = 0.2 if self.metrics['is_mobile'] else 0.3
        
        self.add(Color(0.75, 0.75, 0.8, grid_alpha))
        line_width = 1 if self.metrics['is_phone'] else 1.5
        
        # Используем целочисленный cell_size для range
        cell_size_int = int(self.cell_size)
        
        # Вертикальные линии
        for x in range(0, int(self.width) + 1, cell_size_int):
            self.add(Line(points=[x, 0, x, self.height], width=line_width))
        
        # Горизонтальные линии
        for y in range(0, int(self.height) + 1, cell_size_int):
            self.add(Line(points=[0, y, self.width, y], width=line_width))
        
        # Вспомогательная сетка (мелкая) только для больших экранов
        if not self.metrics['is_phone'] and self.cell_size > dp(40):
            self.add(Color(0.8, 0.8, 0.85, grid_alpha * 0.5))
            small_cell = int(self.cell_size // 2)
            
            for x in range(0, int(self.width) + 1, small_cell):
                self.add(Line(points=[x, 0, x, self.height], width=0.5))
            
            for y in range(0, int(self.height) + 1, small_cell):
                self.add(Line(points=[0, y, self.width, y], width=0.5))
    
    def update_size(self, width, height):
        """Обновление размера текстуры"""
        self.width = width
        self.height = height
        self.metrics = SmartScreenDetector.get_screen_metrics()
        
        # Пересчитываем размер ячейки
        min_side = min(width, height)
        if self.metrics['is_phone']:
            self.cell_size = max(int(dp(30)), int(min_side // 25))
        elif self.metrics['is_tablet']:
            self.cell_size = max(int(dp(40)), int(min_side // 20))
        else:
            self.cell_size = max(int(dp(50)), int(min_side // 15))

class AdaptiveMovingSquare(Widget):
    """Адаптивный движущийся квадрат"""
    pos_x = NumericProperty(0)
    pos_y = NumericProperty(0)
    square_size = NumericProperty(0)  # Изменено с size на square_size
    current_speed_x = NumericProperty(0)
    current_speed_y = NumericProperty(0)
    max_speed = NumericProperty(0)
    acceleration = NumericProperty(0)
    deceleration = NumericProperty(0)
    target_direction_x = NumericProperty(0)
    target_direction_y = NumericProperty(0)
    
    def __init__(self, screen_width, screen_height, **kwargs):
        super(AdaptiveMovingSquare, self).__init__(**kwargs)
        
        self.metrics = SmartScreenDetector.get_screen_metrics()
        self.original_screen_width = screen_width
        self.original_screen_height = screen_height
        self.adaptive_setup(screen_width, screen_height)
        self.init_graphics()
    
    def adaptive_setup(self, screen_width, screen_height):
        """Адаптивная настройка параметров"""
        min_side = min(screen_width, screen_height)
        
        # Адаптивный размер
        if self.metrics['is_phone']:
            self.square_size = min_side * 0.1  # 10% для телефонов
            self.max_speed = min_side * 0.4
        elif self.metrics['is_tablet']:
            self.square_size = min_side * 0.08  # 8% для планшетов
            self.max_speed = min_side * 0.35
        else:
            self.square_size = min_side * 0.06  # 6% для десктопов
            self.max_speed = min_side * 0.3
        
        # Адаптивное ускорение
        self.acceleration = self.max_speed * (1.5 if self.metrics['is_mobile'] else 2.0)
        self.deceleration = self.max_speed * (2.0 if self.metrics['is_mobile'] else 2.5)
        
        # Начальная позиция (относительно экрана)
        self.pos_x = (screen_width - self.square_size) / 2
        self.pos_y = (screen_height - self.square_size) / 2
    
    def init_graphics(self):
        """Инициализация графики с адаптивными параметрами"""
        with self.canvas:
            # Основной квадрат
            Color(1, 0.2, 0.2, 1)  # Красный цвет
            self.rect = Rectangle(pos=(self.pos_x, self.pos_y), size=(self.square_size, self.square_size))
    
    def update_position(self, dt, screen_width, screen_height):
        """Обновление позиции с адаптивной логикой"""
        # Плавное изменение скорости
        self.apply_smooth_acceleration(dt)
        
        # Обновляем позицию
        self.pos_x += self.current_speed_x * dt
        self.pos_y += self.current_speed_y * dt
        
        # Адаптивные границы с отскоком
        self.handle_bounds(screen_width, screen_height)
        
        # Замедление при отсутствии ввода
        if abs(self.target_direction_x) < 0.1 and abs(self.target_direction_y) < 0.1:
            self.apply_friction(dt)
        
        # Обновляем графику
        self.rect.pos = (self.pos_x, self.pos_y)
    
    def handle_bounds(self, screen_width, screen_height):
        """Обработка границ экрана"""
        bounce_factor = 0.3 if self.metrics['is_mobile'] else 0.4
        
        if self.pos_x < 0:
            self.pos_x = 0
            self.current_speed_x = -self.current_speed_x * bounce_factor
        elif self.pos_x > screen_width - self.square_size:
            self.pos_x = screen_width - self.square_size
            self.current_speed_x = -self.current_speed_x * bounce_factor
            
        if self.pos_y < 0:
            self.pos_y = 0
            self.current_speed_y = -self.current_speed_y * bounce_factor
        elif self.pos_y > screen_height - self.square_size:
            self.pos_y = screen_height - self.square_size
            self.current_speed_y = -self.current_speed_y * bounce_factor
    
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
    
    def reset_position(self, screen_width, screen_height):
        """Сброс позиции"""
        # Плавное перемещение к центру вместо телепортации
        self.target_direction_x = 0
        self.target_direction_y = 0
        self.current_speed_x = 0
        self.current_speed_y = 0
        # Возвращаем квадрат в центр
        self.pos_x = (screen_width - self.square_size) / 2
        self.pos_y = (screen_height - self.square_size) / 2

class GameScreen(Screen):
    """Игровой экран"""
    
    square = ObjectProperty(None)
    screen_width = NumericProperty(0)
    screen_height = NumericProperty(0)
    joystick_active = BooleanProperty(False)
    joystick_pos = ObjectProperty((0, 0))
    joystick_center = ObjectProperty((0, 0))
    joystick_radius = NumericProperty(0)
    floor_texture = ObjectProperty(None)
    joystick_smoothing = NumericProperty(0.8)
    game_active = BooleanProperty(False)
    pause_button = ObjectProperty(None)
    
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
        
        # Создаем интерфейс
        self.create_interface()
        
        # Настройка управления
        self.setup_controls()
        
        # Отслеживаем изменение размера
        Window.bind(on_resize=self.on_window_resize)
    
    def create_interface(self):
        """Создание адаптивного интерфейса"""
        # Фон
        with self.canvas.before:
            Color(0.9, 0.9, 0.93, 1)
            self.bg_rect = Rectangle(pos=(0, 0), size=(self.screen_width, self.screen_height))
        
        # Текстура пола
        with self.canvas.before:
            self.floor_texture = AdaptiveFloorTexture(self.screen_width, self.screen_height)
            self.canvas.before.add(self.floor_texture)
        
        # Создаем квадрат игрока
        self.square = AdaptiveMovingSquare(self.screen_width, self.screen_height)
        
        # Добавляем квадрат на экран
        self.add_widget(self.square)
        
        # Джойстик
        self.init_joystick()
        self.draw_joystick()
        
        # Панель управления сверху
        self.create_top_panel()
    
    def create_top_panel(self):
        """Создание верхней панели с кнопками"""
        from kivy.uix.boxlayout import BoxLayout
        
        top_panel = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50))
        top_panel.pos = (0, self.screen_height - dp(50))
        
        # Кнопка меню
        menu_button = Button(
            text='МЕНЮ',
            size_hint=(0.5, 1),
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        menu_button.bind(on_press=self.return_to_menu)
        top_panel.add_widget(menu_button)
        
        # Кнопка сброса
        self.pause_button = Button(
            text='СБРОС',
            size_hint=(0.5, 1),
            background_color=(1, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        self.pause_button.bind(on_press=self.reset_game)
        top_panel.add_widget(self.pause_button)
        
        self.add_widget(top_panel)
    
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
        
        # Позиция джойстика
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
            # Внутренний круг джойстика (без тени)
            inner_size = 0.6
            Color(0.4, 0.4, 0.5, 0.5)
            
            # Вычисляем позицию и размер
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
        self.square.reset_position(self.screen_width, self.screen_height)
        
        # Запуск игрового цикла
        if self.clock_event:
            self.clock_event.cancel()
        self.clock_event = Clock.schedule_interval(self.update_game, 1.0/60.0)
    
    def update_game(self, dt):
        """Обновление игры"""
        if not self.game_active:
            return
        
        # Обновляем позицию квадрата
        self.square.update_position(dt, self.screen_width, self.screen_height)
        
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
        
        # Обновляем фон
        self.bg_rect.size = (width, height)
        
        # Обновляем текстуру пола
        self.canvas.before.remove(self.floor_texture)
        self.floor_texture = AdaptiveFloorTexture(width, height)
        self.canvas.before.add(self.floor_texture)
        
        # Обновляем квадрат
        self.square.adaptive_setup(width, height)
        
        # Обновляем джойстик
        self.init_joystick()
        
        # Перерисовываем графику джойстика
        if hasattr(self, 'joystick_circle'):
            self.canvas.remove(self.joystick_circle)
        self.draw_joystick()
        
        # Обновляем позицию верхней панели
        for child in self.children:
            if hasattr(child, 'pos'):
                if child.pos[1] == self.screen_height - dp(50):
                    child.pos = (0, height - dp(50))
    
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
        
        # Проверка джойстика
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
        self.square.reset_position(self.screen_width, self.screen_height)
        self.game_active = True
    
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
            Config.set('graphics', 'fullscreen', 'auto')
            
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
