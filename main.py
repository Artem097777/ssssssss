from kivy.config import Config
# Отключаем WM_PenProvider для Windows
Config.set('input', 'wm_pen', 'disable')
Config.set('input', 'wm_touch', 'disable')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown
from kivy.graphics import *
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
import math
import json
import os

class VirtualJoystick(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.center = [0, 0]
        self.stick_pos = [0, 0]
        self.active = False
        self.max_distance = 50
        
        with self.canvas:
            Color(0.5, 0.5, 0.5, 0.5)
            self.outer_circle = Ellipse(pos=(0, 0), size=(100, 100))
            Color(0.8, 0.8, 0.8, 0.7)
            self.inner_circle = Ellipse(pos=(0, 0), size=(60, 60))
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.center = touch.pos
            self.outer_circle.pos = (self.center[0] - 50, self.center[1] - 50)
            self.inner_circle.pos = (self.center[0] - 30, self.center[1] - 30)
            self.active = True
            touch.grab(self)
            return True
        return False
    
    def on_touch_move(self, touch):
        if touch.grab_current is self:
            dx = touch.x - self.center[0]
            dy = touch.y - self.center[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > self.max_distance:
                dx = dx * self.max_distance / distance
                dy = dy * self.max_distance / distance
                distance = self.max_distance
            
            self.stick_pos = [dx / self.max_distance, dy / self.max_distance]
            self.inner_circle.pos = (self.center[0] - 30 + dx, self.center[1] - 30 + dy)
            return True
        return False
    
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.active = False
            self.stick_pos = [0, 0]
            self.inner_circle.pos = (self.center[0] - 30, self.center[1] - 30)
            touch.ungrab(self)
            return True
        return False

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'menu'
        
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)
        
        # Заголовок
        title = Label(
            text='RAYCASTER 3D',
            font_size=60,
            color=(1, 0.5, 0, 1),
            bold=True
        )
        
        # Кнопки меню
        btn_play = Button(
            text='ИГРАТЬ',
            font_size=40,
            size_hint=(1, 0.2),
            background_color=(0.2, 0.6, 0.2, 1),
            background_normal=''
        )
        btn_play.bind(on_press=self.play_game)
        
        btn_settings = Button(
            text='НАСТРОЙКИ',
            font_size=40,
            size_hint=(1, 0.2),
            background_color=(0.2, 0.5, 0.8, 1),
            background_normal=''
        )
        btn_settings.bind(on_press=self.open_settings)
        
        btn_maps = Button(
            text='ВЫБОР КАРТЫ',
            font_size=40,
            size_hint=(1, 0.2),
            background_color=(0.8, 0.5, 0.2, 1),
            background_normal=''
        )
        btn_maps.bind(on_press=self.open_maps)
        
        btn_exit = Button(
            text='ВЫХОД',
            font_size=40,
            size_hint=(1, 0.2),
            background_color=(0.8, 0.2, 0.2, 1),
            background_normal=''
        )
        btn_exit.bind(on_press=self.exit_game)
        
        # Версия игры
        version = Label(
            text='Версия 1.0',
            font_size=20,
            color=(0.7, 0.7, 0.7, 1)
        )
        
        layout.add_widget(title)
        layout.add_widget(btn_play)
        layout.add_widget(btn_settings)
        layout.add_widget(btn_maps)
        layout.add_widget(btn_exit)
        layout.add_widget(version)
        
        self.add_widget(layout)
    
    def play_game(self, instance):
        app = App.get_running_app()
        app.sm.current = 'game'
        app.game_screen.start_game()
    
    def open_settings(self, instance):
        app = App.get_running_app()
        app.sm.current = 'settings'
    
    def open_maps(self, instance):
        app = App.get_running_app()
        app.sm.current = 'maps'
    
    def exit_game(self, instance):
        App.get_running_app().stop()

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Заголовок
        title = Label(
            text='НАСТРОЙКИ',
            font_size=50,
            color=(0.2, 0.6, 1, 1)
        )
        
        # Контейнер для настроек
        content = BoxLayout(orientation='vertical', spacing=15)
        
        # Настройки графики
        graphics_label = Label(text='Графика:', font_size=30, color=(1, 1, 1, 1))
        
        # Количество лучей
        rays_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        rays_label = Label(text='Качество (лучи):', font_size=25)
        self.rays_slider = Slider(min=60, max=240, value=120, step=30)
        self.rays_value = Label(text='120', font_size=25)
        self.rays_slider.bind(value=self.update_rays_label)
        rays_layout.add_widget(rays_label)
        rays_layout.add_widget(self.rays_slider)
        rays_layout.add_widget(self.rays_value)
        
        # FPS ограничение
        fps_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        fps_label = Label(text='Макс. FPS:', font_size=25)
        self.fps_slider = Slider(min=30, max=120, value=60, step=30)
        self.fps_value = Label(text='60', font_size=25)
        self.fps_slider.bind(value=self.update_fps_label)
        fps_layout.add_widget(fps_label)
        fps_layout.add_widget(self.fps_slider)
        fps_layout.add_widget(self.fps_value)
        
        # Настройки управления
        control_label = Label(text='Управление:', font_size=30, color=(1, 1, 1, 1))
        
        # Чувствительность
        sens_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        sens_label = Label(text='Чувствительность:', font_size=25)
        self.sens_slider = Slider(min=0.5, max=3, value=1.5)
        self.sens_value = Label(text='1.5', font_size=25)
        self.sens_slider.bind(value=self.update_sens_label)
        sens_layout.add_widget(sens_label)
        sens_layout.add_widget(self.sens_slider)
        sens_layout.add_widget(self.sens_value)
        
        # Инвертировать ось Y
        invert_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        invert_label = Label(text='Инвертировать ось Y:', font_size=25)
        self.invert_check = CheckBox()
        invert_layout.add_widget(invert_label)
        invert_layout.add_widget(self.invert_check)
        
        # Кнопки
        buttons_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, 0.2))
        
        btn_back = Button(
            text='НАЗАД',
            font_size=30,
            background_color=(0.8, 0.2, 0.2, 1),
            background_normal=''
        )
        btn_back.bind(on_press=self.go_back)
        
        btn_save = Button(
            text='СОХРАНИТЬ',
            font_size=30,
            background_color=(0.2, 0.8, 0.2, 1),
            background_normal=''
        )
        btn_save.bind(on_press=self.save_settings)
        
        btn_default = Button(
            text='ПО УМОЛЧАНИЮ',
            font_size=30,
            background_color=(0.2, 0.5, 0.8, 1),
            background_normal=''
        )
        btn_default.bind(on_press=self.default_settings)
        
        buttons_layout.add_widget(btn_back)
        buttons_layout.add_widget(btn_default)
        buttons_layout.add_widget(btn_save)
        
        # Добавляем все виджеты
        content.add_widget(graphics_label)
        content.add_widget(rays_layout)
        content.add_widget(fps_layout)
        content.add_widget(control_label)
        content.add_widget(sens_layout)
        content.add_widget(invert_layout)
        
        layout.add_widget(title)
        layout.add_widget(content)
        layout.add_widget(buttons_layout)
        
        self.add_widget(layout)
        
        # Загружаем сохраненные настройки
        self.load_settings()
    
    def update_rays_label(self, instance, value):
        self.rays_value.text = str(int(value))
    
    def update_fps_label(self, instance, value):
        self.fps_value.text = str(int(value))
    
    def update_sens_label(self, instance, value):
        self.sens_value.text = f'{value:.1f}'
    
    def load_settings(self):
        try:
            app = App.get_running_app()
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.rays_slider.value = settings.get('rays', 120)
                    self.fps_slider.value = settings.get('fps', 60)
                    self.sens_slider.value = settings.get('sensitivity', 1.5)
                    self.invert_check.active = settings.get('invert_y', False)
        except:
            pass
    
    def save_settings(self, instance):
        settings = {
            'rays': int(self.rays_slider.value),
            'fps': int(self.fps_slider.value),
            'sensitivity': self.sens_slider.value,
            'invert_y': self.invert_check.active
        }
        
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        
        app = App.get_running_app()
        app.apply_settings(settings)
        
        popup = Popup(
            title='Успешно',
            content=Label(text='Настройки сохранены!'),
            size_hint=(0.6, 0.4)
        )
        popup.open()
    
    def default_settings(self, instance):
        self.rays_slider.value = 120
        self.fps_slider.value = 60
        self.sens_slider.value = 1.5
        self.invert_check.active = False
    
    def go_back(self, instance):
        app = App.get_running_app()
        app.sm.current = 'menu'

class MapsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'maps'
        
        layout = BoxLayout(orientation='vertical', spacing=20, padding=30)
        
        title = Label(
            text='ВЫБОР КАРТЫ',
            font_size=50,
            color=(0.2, 0.6, 1, 1)
        )
        
        # Контейнер для карт
        maps_layout = BoxLayout(orientation='vertical', spacing=15)
        
        maps = [
            ('Маленький лабиринт', 'small'),
            ('Средний лабиринт', 'medium'),
            ('Большой лабиринт', 'large'),
            ('Рандомная карта', 'random'),
            ('Прямые коридоры', 'corridors')
        ]
        
        for map_name, map_id in maps:
            btn = Button(
                text=map_name,
                font_size=35,
                size_hint=(1, 0.2),
                background_color=(0.3, 0.3, 0.5, 1),
                background_normal=''
            )
            btn.bind(on_press=lambda x, mid=map_id: self.select_map(mid))
            maps_layout.add_widget(btn)
        
        # Кнопка назад
        btn_back = Button(
            text='НАЗАД',
            font_size=40,
            size_hint=(1, 0.2),
            background_color=(0.8, 0.2, 0.2, 1),
            background_normal=''
        )
        btn_back.bind(on_press=self.go_back)
        
        layout.add_widget(title)
        layout.add_widget(maps_layout)
        layout.add_widget(btn_back)
        
        self.add_widget(layout)
    
    def select_map(self, map_id):
        app = App.get_running_app()
        app.selected_map = map_id
        
        popup = Popup(
            title='Карта выбрана',
            content=Label(text=f'Выбрана карта: {map_id}'),
            size_hint=(0.6, 0.4)
        )
        popup.open()
        
        # Возвращаемся в игру
        Clock.schedule_once(lambda dt: app.sm.current == 'game' or app.sm.current == 'menu', 1)
        Clock.schedule_once(lambda dt: app.game_screen.start_game(), 1.1)
    
    def go_back(self, instance):
        app = App.get_running_app()
        app.sm.current = 'menu'

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'game'
        
        self.game_widget = RaycasterGame()
        self.add_widget(self.game_widget)
    
    def start_game(self):
        self.game_widget.reset_game()
        self.game_widget.is_paused = False

class PauseMenu(BoxLayout):
    def __init__(self, game_widget, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 20
        self.padding = 50
        self.game_widget = game_widget
        
        title = Label(
            text='ПАУЗА',
            font_size=60,
            color=(1, 0.5, 0, 1)
        )
        
        btn_resume = Button(
            text='ПРОДОЛЖИТЬ',
            font_size=40,
            size_hint=(1, 0.2),
            background_color=(0.2, 0.8, 0.2, 1),
            background_normal=''
        )
        btn_resume.bind(on_press=self.resume_game)
        
        btn_restart = Button(
            text='ЗАНОВО',
            font_size=40,
            size_hint=(1, 0.2),
            background_color=(0.2, 0.5, 0.8, 1),
            background_normal=''
        )
        btn_restart.bind(on_press=self.restart_game)
        
        btn_settings = Button(
            text='НАСТРОЙКИ',
            font_size=40,
            size_hint=(1, 0.2),
            background_color=(0.8, 0.5, 0.2, 1),
            background_normal=''
        )
        btn_settings.bind(on_press=self.open_settings)
        
        btn_menu = Button(
            text='В МЕНЮ',
            font_size=40,
            size_hint=(1, 0.2),
            background_color=(0.8, 0.2, 0.2, 1),
            background_normal=''
        )
        btn_menu.bind(on_press=self.go_to_menu)
        
        self.add_widget(title)
        self.add_widget(btn_resume)
        self.add_widget(btn_restart)
        self.add_widget(btn_settings)
        self.add_widget(btn_menu)
    
    def resume_game(self, instance):
        self.game_widget.is_paused = False
        self.parent.parent.dismiss()
    
    def restart_game(self, instance):
        self.game_widget.reset_game()
        self.game_widget.is_paused = False
        self.parent.parent.dismiss()
    
    def open_settings(self, instance):
        app = App.get_running_app()
        self.parent.parent.dismiss()
        app.sm.current = 'settings'
    
    def go_to_menu(self, instance):
        app = App.get_running_app()
        self.parent.parent.dismiss()
        app.sm.current = 'menu'

class RaycasterGame(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.is_paused = False
        self.pause_popup = None
        self.game_time = 0
        self.score = 0
        
        # Настройки по умолчанию
        self.settings = {
            'rays': 120,
            'fps': 60,
            'sensitivity': 1.5,
            'invert_y': False
        }
        
        # Загружаем сохраненные настройки
        self.load_settings()
        
        # Создаем элементы управления
        self.create_controls()
        
        # Инициализируем карту и игрока
        self.reset_game()
        
        # Настройка клавиатуры для ПК
        self.keys_pressed = set()
        self.setup_keyboard()
    
    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except:
            pass
    
    def reset_game(self):
        # Выбираем карту в зависимости от выбора
        app = App.get_running_app()
        map_id = getattr(app, 'selected_map', 'small')
        
        if map_id == 'small':
            self.map = [
                [1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,1],
                [1,0,1,1,0,1,0,1],
                [1,0,1,0,0,1,0,1],
                [1,0,0,0,0,0,0,1],
                [1,0,1,0,1,1,0,1],
                [1,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1]
            ]
            self.player_pos = [1.5, 1.5]
        elif map_id == 'medium':
            self.map = [
                [1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,1,1,0,1,1,1,0,1],
                [1,0,1,0,0,0,0,1,0,1],
                [1,0,1,0,1,1,0,1,0,1],
                [1,0,0,0,1,0,0,0,0,1],
                [1,0,1,0,1,0,1,1,0,1],
                [1,0,1,0,0,0,1,0,0,1],
                [1,0,0,0,1,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1]
            ]
            self.player_pos = [1.5, 1.5]
        elif map_id == 'large':
            self.map = [
                [1,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,1,1,1,1,0,1,1,1,0,1],
                [1,0,1,0,0,0,0,0,0,1,0,1],
                [1,0,1,0,1,1,1,1,0,1,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,1,0,1,0,1,1,1,1,0,1],
                [1,0,1,0,1,0,0,0,0,1,0,1],
                [1,0,1,0,1,1,1,1,0,1,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1]
            ]
            self.player_pos = [1.5, 1.5]
        elif map_id == 'random':
            self.generate_random_map(10)
            self.player_pos = [1.5, 1.5]
        else:  # corridors
            self.map = [
                [1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,1,1,1,1,1,1,0,1],
                [1,0,1,0,0,0,0,1,0,1],
                [1,0,1,0,1,1,0,1,0,1],
                [1,0,1,0,1,1,0,1,0,1],
                [1,0,1,0,0,0,0,1,0,1],
                [1,0,1,1,1,1,1,1,0,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1]
            ]
            self.player_pos = [1.5, 1.5]
        
        self.player_angle = 0
        self.fov = math.pi / 3
        self.rays = self.settings['rays']
        self.move_speed = 2.5 * self.settings['sensitivity']
        self.rot_speed = 2.5 * self.settings['sensitivity']
        
        # Сброс статистики
        self.game_time = 0
        self.score = 0
        
        # Запускаем игровой цикл
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, 1/self.settings['fps'])
    
    def generate_random_map(self, size):
        # Генерация случайного лабиринта
        self.map = [[1] * size for _ in range(size)]
        
        # Создаем проходы
        for i in range(1, size-1):
            for j in range(1, size-1):
                if random.random() > 0.3:  # 70% шанс прохода
                    self.map[i][j] = 0
        
        # Гарантируем, что стартовая позиция свободна
        self.map[1][1] = 0
        self.map[1][2] = 0
        self.map[2][1] = 0
    
    def setup_keyboard(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
    
    def _keyboard_closed(self):
        self._keyboard.unbind()
        self._keyboard = None
    
    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.keys_pressed.add(keycode[1])
        
        # Escape для паузы
        if keycode[1] == 'escape':
            self.toggle_pause()
        
        return True
    
    def _on_key_up(self, keyboard, keycode):
        if keycode[1] in self.keys_pressed:
            self.keys_pressed.remove(keycode[1])
        return True
    
    def create_controls(self):
        # Левый джойстик для движения
        self.move_joystick = VirtualJoystick()
        self.move_joystick.size_hint = (None, None)
        self.move_joystick.size = (200, 200)
        self.move_joystick.pos = (50, 50)
        self.add_widget(self.move_joystick)
        
        # Правый джойстик для поворота
        self.rotate_joystick = VirtualJoystick()
        self.rotate_joystick.size_hint = (None, None)
        self.rotate_joystick.size = (150, 150)
        self.rotate_joystick.pos = (Window.width - 200, 50)
        self.add_widget(self.rotate_joystick)
        
        # Кнопка паузы
        self.pause_button = Button(
            text='II',
            size_hint=(None, None),
            size=(60, 60),
            pos=(Window.width - 70, Window.height - 70),
            font_size=30,
            background_color=(0.3, 0.3, 0.3, 0.7),
            background_normal=''
        )
        self.pause_button.bind(on_press=lambda x: self.toggle_pause())
        self.add_widget(self.pause_button)
        
        # Кнопка сброса
        self.reset_button = Button(
            text='↻',
            size_hint=(None, None),
            size=(60, 60),
            pos=(10, Window.height - 70),
            font_size=30,
            background_color=(0.3, 0.3, 0.3, 0.7),
            background_normal=''
        )
        self.reset_button.bind(on_press=lambda x: self.reset_game())
        self.add_widget(self.reset_button)
        
        # Панель статистики
        self.stats_label = Label(
            text='Время: 0:00\nОчки: 0',
            size_hint=(None, None),
            size=(200, 60),
            pos=(Window.width/2 - 100, Window.height - 80),
            color=(1, 1, 1, 0.8),
            halign='center',
            valign='middle'
        )
        self.stats_label.bind(size=self.stats_label.setter('text_size'))
        self.add_widget(self.stats_label)
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.show_pause_menu()
        elif self.pause_popup:
            self.pause_popup.dismiss()
            self.pause_popup = None
    
    def show_pause_menu(self):
        if not self.pause_popup:
            pause_content = PauseMenu(self)
            self.pause_popup = Popup(
                title='',
                content=pause_content,
                size_hint=(0.8, 0.8),
                auto_dismiss=False,
                background=''
            )
            self.pause_popup.open()
    
    def cast_ray(self, angle):
        x, y = self.player_pos
        dir_x = math.cos(angle)
        dir_y = math.sin(angle)
        
        distance = 0
        max_depth = 20
        hit = False
        
        while not hit and distance < max_depth:
            distance += 0.1
            test_x = int(x + dir_x * distance)
            test_y = int(y + dir_y * distance)
            
            if test_x < 0 or test_x >= len(self.map[0]) or test_y < 0 or test_y >= len(self.map):
                hit = True
                distance = max_depth
            elif self.map[test_y][test_x] == 1:
                hit = True
        
        return distance
    
    def update(self, dt):
        if self.is_paused:
            return
        
        # Обновляем статистику
        self.game_time += dt
        minutes = int(self.game_time // 60)
        seconds = int(self.game_time % 60)
        self.stats_label.text = f'Время: {minutes}:{seconds:02d}\nОчки: {self.score}'
        
        # Управление с клавиатуры (для ПК)
        if self._keyboard:
            speed = self.move_speed * dt
            rot_speed = self.rot_speed * dt
            
            if 'w' in self.keys_pressed:
                self.player_pos[0] += math.cos(self.player_angle) * speed
                self.player_pos[1] += math.sin(self.player_angle) * speed
            if 's' in self.keys_pressed:
                self.player_pos[0] -= math.cos(self.player_angle) * speed
                self.player_pos[1] -= math.sin(self.player_angle) * speed
            if 'a' in self.keys_pressed:
                self.player_angle -= rot_speed
            if 'd' in self.keys_pressed:
                self.player_angle += rot_speed
        
        # Управление с джойстиков
        if hasattr(self, 'move_joystick') and hasattr(self, 'rotate_joystick'):
            move_x, move_y = self.move_joystick.stick_pos
            rotate_x, rotate_y = self.rotate_joystick.stick_pos
            
            # Инвертирование оси Y если нужно
            if self.settings['invert_y']:
                move_y = -move_y
            
            # Движение
            move_forward = move_y * self.move_speed * dt
            move_sideways = move_x * self.move_speed * dt
            
            # Обновление позиции игрока
            self.player_pos[0] += math.cos(self.player_angle) * move_forward
            self.player_pos[1] += math.sin(self.player_angle) * move_forward
            
            # Боковое движение
            self.player_pos[0] += math.cos(self.player_angle + math.pi/2) * move_sideways
            self.player_pos[1] += math.sin(self.player_angle + math.pi/2) * move_sideways
            
            # Вращение
            rotation = rotate_x * self.rot_speed * dt
            self.player_angle += rotation
        
        # Проверка столкновений
        self.check_collisions()
        
        # Отрисовка
        self.canvas.clear()
        with self.canvas:
            # Небо и пол
            Color(0.2, 0.2, 0.8)
            Rectangle(pos=(0, self.height/2), size=(self.width, self.height/2))
            Color(0.3, 0.2, 0.1)
            Rectangle(pos=(0, 0), size=(self.width, self.height/2))
            
            # Стены
            for ray in range(self.rays):
                ray_angle = (self.player_angle - self.fov/2) + (ray/self.rays) * self.fov
                distance = self.cast_ray(ray_angle)
                
                distance *= math.cos(self.player_angle - ray_angle)
                wall_height = min(self.height / (distance + 0.0001), self.height)
                
                intensity = max(0.3, 1 - distance/15)
                Color(intensity, intensity/2, intensity/2)
                
                x_pos = (ray/self.rays) * self.width
                wall_width = self.width / self.rays
                Rectangle(
                    pos=(x_pos, (self.height - wall_height)/2),
                    size=(wall_width, wall_height)
                )
            
            # Мини-карта
            self.draw_minimap()
    
    def check_collisions(self):
        player_x, player_y = self.player_pos
        
        check_points = [
            (int(player_x + 0.1), int(player_y)),
            (int(player_x - 0.1), int(player_y)),
            (int(player_x), int(player_y + 0.1)),
            (int(player_x), int(player_y - 0.1))
        ]
        
        for x, y in check_points:
            if (0 <= y < len(self.map) and 
                0 <= x < len(self.map[0]) and 
                self.map[y][x] == 1):
                if x == int(player_x):
                    if player_y > y:
                        self.player_pos[1] = y + 1.1
                    else:
                        self.player_pos[1] = y - 0.1
                if y == int(player_y):
                    if player_x > x:
                        self.player_pos[0] = x + 1.1
                    else:
                        self.player_pos[0] = x - 0.1
    
    def draw_minimap(self):
        minimap_size = 150
        cell_size = minimap_size / len(self.map)
        
        Color(0, 0, 0, 0.7)
        Rectangle(
            pos=(self.width - minimap_size - 10, 10),
            size=(minimap_size, minimap_size)
        )
        
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                if self.map[y][x] == 1:
                    Color(1, 1, 1, 0.8)
                    Rectangle(
                        pos=(self.width - minimap_size - 10 + x * cell_size,
                             10 + y * cell_size),
                        size=(cell_size - 1, cell_size - 1)
                    )
        
        player_x = self.player_pos[0] * cell_size
        player_y = self.player_pos[1] * cell_size
        
        Color(0, 1, 0, 0.8)
        Rectangle(
            pos=(self.width - minimap_size - 10 + player_x - 3,
                 10 + player_y - 3),
            size=(6, 6)
        )
        
        Color(1, 0, 0, 0.8)
        Line(
            points=[
                self.width - minimap_size - 10 + player_x,
                10 + player_y,
                self.width - minimap_size - 10 + player_x + math.cos(self.player_angle) * 10,
                10 + player_y + math.sin(self.player_angle) * 10
            ],
            width=2
        )

class RaycasterApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_map = 'small'
        self.sm = ScreenManager(transition=SlideTransition())
    
    def build(self):
        Window.fullscreen = 'auto'
        Window.size = (800, 600)
        
        # Создаем экраны
        self.sm.add_widget(MenuScreen())
        self.sm.add_widget(SettingsScreen())
        self.sm.add_widget(MapsScreen())
        
        # Создаем игровой экран
        self.game_screen = GameScreen()
        self.sm.add_widget(self.game_screen)
        
        return self.sm
    
    def apply_settings(self, settings):
        # Применяем настройки к игре
        if hasattr(self.game_screen, 'game_widget'):
            self.game_screen.game_widget.settings = settings
            self.game_screen.game_widget.rays = settings['rays']
            self.game_screen.game_widget.move_speed = 2.5 * settings['sensitivity']
            self.game_screen.game_widget.rot_speed = 2.5 * settings['sensitivity']
            
            # Обновляем игровой цикл с новым FPS
            Clock.unschedule(self.game_screen.game_widget.update)
            Clock.schedule_interval(self.game_screen.game_widget.update, 1/settings['fps'])

if __name__ == '__main__':
    RaycasterApp().run()
