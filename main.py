from kivy.config import Config

# Настраиваем конфигурацию для предотвращения предупреждений
Config.set('kivy', 'log_level', 'error')  # Уменьшаем уровень логов
Config.set('graphics', 'maxfps', '120')  # Ограничиваем FPS

# Для Windows отключаем проблемные провайдеры
import platform
if platform.system() == 'Windows':
    Config.set('input', 'wm_pen', '')
    Config.set('input', 'wm_touch', '')
    Config.set('input', 'wm_touch', '')
    Config.set('input', 'pen', '')
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Config.set('kivy', 'desktop', 1)
    
# Для Android/сенсорных устройств
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.graphics import *
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty, StringProperty, DictProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.logger import Logger
import math
import json
import os
import random
import time

# Настраиваем логгер для фильтрации предупреждений
import logging
logging.getLogger('kivy').setLevel(logging.ERROR)

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
            text='Версия 1.1 (с NPC)',
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
        
        # Настройки NPC
        npc_label = Label(text='NPC:', font_size=30, color=(1, 1, 1, 1))
        
        # Количество NPC
        npc_count_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        npc_count_label = Label(text='Количество NPC:', font_size=25)
        self.npc_count_slider = Slider(min=1, max=10, value=3, step=1)
        self.npc_count_value = Label(text='3', font_size=25)
        self.npc_count_slider.bind(value=self.update_npc_count_label)
        npc_count_layout.add_widget(npc_count_label)
        npc_count_layout.add_widget(self.npc_count_slider)
        npc_count_layout.add_widget(self.npc_count_value)
        
        # Сложность NPC
        npc_diff_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        npc_diff_label = Label(text='Сложность NPC:', font_size=25)
        self.npc_diff_slider = Slider(min=1, max=3, value=2, step=1)
        self.npc_diff_value = Label(text='Средняя', font_size=25)
        self.npc_diff_slider.bind(value=self.update_npc_diff_label)
        npc_diff_layout.add_widget(npc_diff_label)
        npc_diff_layout.add_widget(self.npc_diff_slider)
        npc_diff_layout.add_widget(self.npc_diff_value)
        
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
        
        # Тип управления
        control_type_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        control_type_label = Label(text='Тип управления:', font_size=25)
        self.control_type_slider = Slider(min=0, max=2, value=0, step=1)
        self.control_type_value = Label(text='Джойстики', font_size=25)
        self.control_type_slider.bind(value=self.update_control_type_label)
        control_type_layout.add_widget(control_type_label)
        control_type_layout.add_widget(self.control_type_slider)
        control_type_layout.add_widget(self.control_type_value)
        
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
        content.add_widget(npc_label)
        content.add_widget(npc_count_layout)
        content.add_widget(npc_diff_layout)
        content.add_widget(control_label)
        content.add_widget(sens_layout)
        content.add_widget(invert_layout)
        content.add_widget(control_type_layout)
        
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
    
    def update_npc_count_label(self, instance, value):
        self.npc_count_value.text = str(int(value))
    
    def update_npc_diff_label(self, instance, value):
        diff = int(value)
        if diff == 1:
            self.npc_diff_value.text = 'Легкая'
        elif diff == 2:
            self.npc_diff_value.text = 'Средняя'
        else:
            self.npc_diff_value.text = 'Сложная'
    
    def update_sens_label(self, instance, value):
        self.sens_value.text = f'{value:.1f}'
    
    def update_control_type_label(self, instance, value):
        types = ['Джойстики', 'Клавиатура', 'Оба']
        self.control_type_value.text = types[int(value)]
    
    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.rays_slider.value = settings.get('rays', 120)
                    self.fps_slider.value = settings.get('fps', 60)
                    self.npc_count_slider.value = settings.get('npc_count', 3)
                    self.npc_diff_slider.value = settings.get('npc_difficulty', 2)
                    self.sens_slider.value = settings.get('sensitivity', 1.5)
                    self.invert_check.active = settings.get('invert_y', False)
                    self.control_type_slider.value = settings.get('control_type', 0)
        except:
            pass
    
    def save_settings(self, instance):
        settings = {
            'rays': int(self.rays_slider.value),
            'fps': int(self.fps_slider.value),
            'npc_count': int(self.npc_count_slider.value),
            'npc_difficulty': int(self.npc_diff_slider.value),
            'sensitivity': self.sens_slider.value,
            'invert_y': self.invert_check.active,
            'control_type': int(self.control_type_slider.value)
        }
        
        try:
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f)
        except:
            pass
        
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
        self.npc_count_slider.value = 3
        self.npc_diff_slider.value = 2
        self.sens_slider.value = 1.5
        self.invert_check.active = False
        self.control_type_slider.value = 0
    
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
            ('Прямые коридоры', 'corridors'),
            ('Арена с NPC', 'arena')
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
        Clock.schedule_once(lambda dt: self.go_to_game(), 1)
    
    def go_to_game(self):
        app = App.get_running_app()
        app.sm.current = 'game'
        app.game_screen.start_game()
    
    def go_back(self, instance):
        app = App.get_running_app()
        app.sm.current = 'menu'

class NPC:
    def __init__(self, x, y, difficulty=2):
        self.x = x
        self.y = y
        self.difficulty = difficulty  # 1 - легкий, 2 - средний, 3 - сложный
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = 0.8 + (difficulty * 0.3)  # От 1.1 до 1.9
        self.health = 3
        self.detection_range = 5 + difficulty * 2  # От 7 до 11
        self.color = (
            1.0,  # R
            0.2 + (3 - difficulty) * 0.2,  # G (легкие зеленее)
            0.2 + (difficulty - 1) * 0.2   # B (сложные краснее)
        )
        self.last_move_time = time.time()
        self.move_change_interval = 2.0 / difficulty  # Чаще меняют направление на сложном уровне
        self.state = "patrol"  # patrol, chase, attack
        self.attack_range = 1.5
        self.attack_damage = 1
        self.attack_cooldown = 0
        self.size = 0.4
        
    def update(self, player_x, player_y, dt, map_data):
        # Обновляем кулдаун атаки
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Проверяем расстояние до игрока
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Определяем состояние
        if distance < self.attack_range:
            self.state = "attack"
        elif distance < self.detection_range:
            self.state = "chase"
        else:
            self.state = "patrol"
        
        # Действия в зависимости от состояния
        if self.state == "attack":
            # Атакуем игрока
            if self.attack_cooldown <= 0:
                self.attack_cooldown = 1.0  # 1 секунда между атаками
                return "damage"  # Сигнал о нанесении урона
            # Стоим на месте при атаке
            return None
            
        elif self.state == "chase":
            # Преследуем игрока
            if distance > 0:
                self.angle = math.atan2(dy, dx)
                move_x = math.cos(self.angle) * self.speed * dt
                move_y = math.sin(self.angle) * self.speed * dt
                
                # Проверяем столкновения со стенами
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                if self.can_move_to(new_x, new_y, map_data):
                    self.x = new_x
                    self.y = new_y
                    
        else:  # patrol
            # Патрулируем случайным образом
            current_time = time.time()
            if current_time - self.last_move_time > self.move_change_interval:
                self.angle = random.uniform(0, 2 * math.pi)
                self.last_move_time = current_time
            
            move_x = math.cos(self.angle) * self.speed * 0.5 * dt  # Медленнее при патрулировании
            move_y = math.sin(self.angle) * self.speed * 0.5 * dt
            
            # Проверяем столкновения со стенами
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            if self.can_move_to(new_x, new_y, map_data):
                self.x = new_x
                self.y = new_y
            else:
                # Если уперлись в стену, меняем направление
                self.angle = random.uniform(0, 2 * math.pi)
        
        return None
    
    def can_move_to(self, x, y, map_data):
        # Проверяем, можно ли переместиться в данную позицию
        map_x = int(x)
        map_y = int(y)
        
        if (0 <= map_y < len(map_data) and 
            0 <= map_x < len(map_data[0]) and 
            map_data[map_y][map_x] == 0):
            return True
        return False
    
    def take_damage(self, damage=1):
        self.health -= damage
        return self.health <= 0

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
    def __init__(self, game_widget, popup_instance, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 20
        self.padding = 50
        self.game_widget = game_widget
        self.popup_instance = popup_instance
        
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
        self.popup_instance.dismiss()
    
    def restart_game(self, instance):
        self.game_widget.reset_game()
        self.game_widget.is_paused = False
        self.popup_instance.dismiss()
    
    def open_settings(self, instance):
        self.popup_instance.dismiss()
        app = App.get_running_app()
        app.sm.current = 'settings'
    
    def go_to_menu(self, instance):
        self.popup_instance.dismiss()
        app = App.get_running_app()
        app.sm.current = 'menu'

class RaycasterGame(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.is_paused = False
        self.pause_popup = None
        self.player_health = 100
        self.score = 0
        self.npcs = []
        self.game_over = False
        
        # Состояние клавиш клавиатуры
        self.keyboard_state = {
            'w': False,  # Вперед
            's': False,  # Назад
            'a': False,  # Влево
            'd': False,  # Вправо
            'left': False,  # Поворот влево
            'right': False,  # Поворот вправо
            'up': False,  # Вперед (альтернатива)
            'down': False,  # Назад (альтернатива)
            'space': False,  # Атака
        }
        
        # Настройки по умолчанию
        self.settings = {
            'rays': 120,
            'fps': 60,
            'npc_count': 3,
            'npc_difficulty': 2,
            'sensitivity': 1.5,
            'invert_y': False,
            'control_type': 0  # 0 - джойстики, 1 - клавиатура, 2 - оба
        }
        
        # Загружаем сохраненные настройки
        self.load_settings()
        
        # Инициализируем карту и игрока
        self.reset_game()
        
        # Создаем отдельный виджет для 3D графики
        self.graphics_widget = Widget()
        self.add_widget(self.graphics_widget)
        
        # Создаем элементы управления (поверх графики)
        self.create_controls()
        
        # Запускаем игровой цикл
        Clock.schedule_interval(self.update, 1/self.settings['fps'])
        
        # Привязываем обработчики клавиатуры
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)
        
        # Таймер для мигания при получении урона
        self.damage_flash = 0
        self.last_shot_time = 0
    
    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except:
            pass
    
    def reset_game(self):
        # Сбрасываем состояние игры
        self.player_health = 100
        self.score = 0
        self.npcs = []
        self.game_over = False
        
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
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,1,1,1,0,1,1,1,1,0,1,1,1,1,0,1,1,0,1],
                [1,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
                [1,0,1,0,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1],
                [1,0,1,0,1,0,0,1,0,1,0,1,0,0,0,1,0,1,0,1],
                [1,0,1,0,1,0,1,1,0,1,0,1,0,1,0,1,0,1,0,1],
                [1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
                [1,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1],
                [1,0,1,0,0,0,0,1,0,1,0,0,0,0,0,1,0,0,0,1],
                [1,0,1,0,1,1,0,1,0,1,0,1,1,1,0,1,1,1,0,1],
                [1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
                [1,0,1,0,1,0,1,1,0,1,0,1,0,1,1,1,0,1,0,1],
                [1,0,1,0,0,0,1,0,0,1,0,0,0,1,0,0,0,1,0,1],
                [1,0,1,1,1,0,1,1,0,1,1,1,0,1,1,1,1,1,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,1,0,1,0,1,1,0,1,1,1,0,1,1,0,1,1,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
            ]
            self.player_pos = [3.0, 3.0]  # Центр стартовой позиции
            
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
            
        elif map_id == 'corridors':
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
            
        else:  # arena
            self.map = [
                [1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1]
            ]
            self.player_pos = [4.0, 4.0]
        
        self.player_angle = 0
        self.fov = math.pi / 3
        self.rays = self.settings['rays']
        self.move_speed = 2.5 * self.settings['sensitivity']
        self.rot_speed = 2.5 * self.settings['sensitivity']
        
        # Создаем NPC
        self.create_npcs()
    
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
    
    def create_npcs(self):
        self.npcs = []
        npc_count = self.settings.get('npc_count', 3)
        difficulty = self.settings.get('npc_difficulty', 2)
        
        for _ in range(npc_count):
            # Находим случайную свободную позицию для NPC
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                x = random.randint(1, len(self.map[0]) - 2)
                y = random.randint(1, len(self.map) - 2)
                
                # Проверяем, что клетка свободна и не слишком близко к игроку
                if (self.map[y][x] == 0 and 
                    abs(x - self.player_pos[0]) > 3 and 
                    abs(y - self.player_pos[1]) > 3):
                    self.npcs.append(NPC(x + 0.5, y + 0.5, difficulty))
                    placed = True
                attempts += 1
    
    def create_controls(self):
        # Удаляем старые элементы управления
        if hasattr(self, 'move_joystick'):
            self.remove_widget(self.move_joystick)
        if hasattr(self, 'rotate_joystick'):
            self.remove_widget(self.rotate_joystick)
        
        # Создаем только джойстики если они нужны
        control_type = self.settings.get('control_type', 0)
        if control_type == 0 or control_type == 2:  # Джойстики или оба
            self.create_joystick_controls()
        
        # Общие элементы управления
        self.create_common_controls()
    
    def create_joystick_controls(self):
        # Левый джойстик для движения (больше и ярче)
        self.move_joystick = VirtualJoystick()
        self.move_joystick.size_hint = (None, None)
        self.move_joystick.size = (250, 250)  # Увеличенный размер
        self.move_joystick.pos = (50, 50)
        # Добавляем яркий цвет для видимости
        with self.move_joystick.canvas:
            Color(0.2, 0.8, 0.2, 0.3)  # Яркий зеленый
            Ellipse(pos=self.move_joystick.pos, size=self.move_joystick.size)
        self.add_widget(self.move_joystick)
        
        # Правый джойстик для поворота (больше и ярче)
        self.rotate_joystick = VirtualJoystick()
        self.rotate_joystick.size_hint = (None, None)
        self.rotate_joystick.size = (200, 200)  # Увеличенный размер
        self.rotate_joystick.pos = (Window.width - 250, 50)
        # Добавляем яркий цвет для видимости
        with self.rotate_joystick.canvas:
            Color(0.8, 0.5, 0.2, 0.3)  # Яркий оранжевый
            Ellipse(pos=self.rotate_joystick.pos, size=self.rotate_joystick.size)
        self.add_widget(self.rotate_joystick)
    
    def create_common_controls(self):
        # Кнопка паузы
        self.pause_button = Button(
            text='II',
            size_hint=(None, None),
            size=(80, 80),
            pos=(Window.width - 90, Window.height - 90),
            font_size=40,
            background_color=(0.8, 0.8, 0.2, 0.9),
            color=(1, 1, 1, 1),
            background_normal='',
            border=(3, 3, 3, 3)
        )
        self.pause_button.bind(on_press=lambda x: self.toggle_pause())
        self.add_widget(self.pause_button)
        
        # Кнопка сброса
        self.reset_button = Button(
            text='↻',
            size_hint=(None, None),
            size=(80, 80),
            pos=(10, Window.height - 90),
            font_size=40,
            background_color=(0.2, 0.8, 0.8, 0.9),
            color=(1, 1, 1, 1),
            background_normal='',
            border=(3, 3, 3, 3)
        )
        self.reset_button.bind(on_press=lambda x: self.reset_game())
        self.add_widget(self.reset_button)
        
        # Кнопка атаки
        self.attack_button = Button(
            text='⚔',
            size_hint=(None, None),
            size=(100, 100),
            pos=(Window.width - 110, 100),
            font_size=50,
            background_color=(0.8, 0.2, 0.2, 0.9),
            color=(1, 1, 1, 1),
            background_normal='',
            border=(3, 3, 3, 3)
        )
        self.attack_button.bind(on_press=lambda x: self.player_attack())
        self.add_widget(self.attack_button)
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.show_pause_menu()
        elif self.pause_popup:
            self.pause_popup.dismiss()
            self.pause_popup = None
    
    def show_pause_menu(self):
        if not self.pause_popup:
            pause_content = PauseMenu(self, None)
            self.pause_popup = Popup(
                title='',
                content=pause_content,
                size_hint=(0.8, 0.8),
                auto_dismiss=False,
                background=''
            )
            pause_content.popup_instance = self.pause_popup
            self.pause_popup.open()
    
    def cast_ray(self, angle, max_depth=20):
        x, y = self.player_pos
        dir_x = math.cos(angle)
        dir_y = math.sin(angle)
        
        distance = 0
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
    
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Обработка нажатия клавиш
        key = keycode[1]  # Получаем символ клавиши
        
        if key in self.keyboard_state:
            self.keyboard_state[key] = True
        
        # ESC для паузы
        if key == 'escape':
            self.toggle_pause()
        
        # Enter для перезапуска
        if key == 'enter' or key == 'return':
            self.reset_game()
        
        # Пробел для атаки
        if key == 'spacebar':
            self.player_attack()
        
        return True
    
    def _on_keyboard_up(self, keyboard, keycode):
        # Обработка отпускания клавиш
        key = keycode[1]
        
        if key in self.keyboard_state:
            self.keyboard_state[key] = False
        
        return True
    
    def update_keyboard_controls(self, dt):
        # Движение вперед/назад
        move_forward = 0
        if self.keyboard_state['w'] or self.keyboard_state['up']:
            move_forward += 1
        if self.keyboard_state['s'] or self.keyboard_state['down']:
            move_forward -= 1
        
        # Боковое движение
        move_sideways = 0
        if self.keyboard_state['a']:
            move_sideways -= 1
        if self.keyboard_state['d']:
            move_sideways += 1
        
        # Поворот
        rotation = 0
        if self.keyboard_state['left']:
            rotation -= 1
        if self.keyboard_state['right']:
            rotation += 1
        
        # Применяем движение
        if move_forward != 0:
            self.player_pos[0] += math.cos(self.player_angle) * move_forward * self.move_speed * dt
            self.player_pos[1] += math.sin(self.player_angle) * move_forward * self.move_speed * dt
        
        if move_sideways != 0:
            self.player_pos[0] += math.cos(self.player_angle + math.pi/2) * move_sideways * self.move_speed * dt
            self.player_pos[1] += math.sin(self.player_angle + math.pi/2) * move_sideways * self.move_speed * dt
        
        if rotation != 0:
            self.player_angle += rotation * self.rot_speed * dt
    
    def player_attack(self):
        current_time = time.time()
        if current_time - self.last_shot_time < 0.5:  # Ограничение 2 выстрела в секунду
            return
        
        self.last_shot_time = current_time
        
        # Проверяем попадание в NPC
        attack_range = 3.0
        attack_angle = self.player_angle
        attack_fov = math.pi / 6  # 30 градусов
        
        npc_to_remove = []
        
        for i, npc in enumerate(self.npcs):
            # Вычисляем вектор к NPC
            dx = npc.x - self.player_pos[0]
            dy = npc.y - self.player_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > attack_range:
                continue
            
            # Вычисляем угол к NPC
            angle_to_npc = math.atan2(dy, dx)
            angle_diff = abs(angle_to_npc - attack_angle)
            
            # Нормализуем разницу углов
            if angle_diff > math.pi:
                angle_diff = 2 * math.pi - angle_diff
            
            # Проверяем, находится ли NPC в поле атаки
            if angle_diff < attack_fov / 2:
                # Проверяем, нет ли стены между игроком и NPC
                hit_wall = False
                test_distance = 0
                step = 0.1
                while test_distance < distance and not hit_wall:
                    test_distance += step
                    test_x = int(self.player_pos[0] + math.cos(angle_to_npc) * test_distance)
                    test_y = int(self.player_pos[1] + math.sin(angle_to_npc) * test_distance)
                    
                    if (test_x < 0 or test_x >= len(self.map[0]) or 
                        test_y < 0 or test_y >= len(self.map)):
                        break
                    
                    if self.map[test_y][test_x] == 1:
                        hit_wall = True
                        break
                
                if not hit_wall:
                    # Попадание!
                    if npc.take_damage():
                        npc_to_remove.append(i)
                        self.score += 100
                    else:
                        self.score += 10
        
        # Удаляем уничтоженных NPC
        for i in sorted(npc_to_remove, reverse=True):
            self.npcs.pop(i)
    
    def update(self, dt):
        if self.is_paused or self.game_over:
            return
        
        # Обновляем позиции элементов управления при изменении размера окна
        if hasattr(self, 'pause_button'):
            self.pause_button.pos = (self.width - 90, self.height - 90)
        if hasattr(self, 'reset_button'):
            self.reset_button.pos = (10, self.height - 90)
        if hasattr(self, 'attack_button'):
            self.attack_button.pos = (self.width - 110, 100)
        
        # Обновляем джойстики
        if hasattr(self, 'move_joystick'):
            self.move_joystick.pos = (50, 50)
        if hasattr(self, 'rotate_joystick'):
            self.rotate_joystick.pos = (self.width - 250, 50)
        
        # Уменьшаем мигание при получении урона
        if self.damage_flash > 0:
            self.damage_flash = max(0, self.damage_flash - dt * 2)
        
        # Обновление управления в зависимости от типа
        control_type = self.settings.get('control_type', 0)
        
        if control_type == 0:  # Только джойстики
            if hasattr(self, 'move_joystick') and hasattr(self, 'rotate_joystick'):
                move_x, move_y = self.move_joystick.stick_pos
                rotate_x, rotate_y = self.rotate_joystick.stick_pos
                
                # Инвертирование оси Y если нужно
                if self.settings.get('invert_y', False):
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
                
                # Вращение от джойстика
                rotation = rotate_x * self.rot_speed * dt
                self.player_angle += rotation
        
        elif control_type == 1:  # Только клавиатура
            self.update_keyboard_controls(dt)
        
        else:  # Оба типа управления
            # Сначала обновляем клавиатуру
            self.update_keyboard_controls(dt)
            
            # Затем добавляем управление джойстиками
            if hasattr(self, 'move_joystick') and hasattr(self, 'rotate_joystick'):
                move_x, move_y = self.move_joystick.stick_pos
                rotate_x, rotate_y = self.rotate_joystick.stick_pos
                
                # Инвертирование оси Y если нужно
                if self.settings.get('invert_y', False):
                    move_y = -move_y
                
                # Движение от джойстика
                move_forward = move_y * self.move_speed * dt
                move_sideways = move_x * self.move_speed * dt
                
                # Обновление позиции игрока
                self.player_pos[0] += math.cos(self.player_angle) * move_forward
                self.player_pos[1] += math.sin(self.player_angle) * move_forward
                
                # Боковое движение
                self.player_pos[0] += math.cos(self.player_angle + math.pi/2) * move_sideways
                self.player_pos[1] += math.sin(self.player_angle + math.pi/2) * move_sideways
                
                # Вращение от джойстика
                rotation = rotate_x * self.rot_speed * dt
                self.player_angle += rotation
        
        # Обновляем NPC
        npcs_to_remove = []
        for i, npc in enumerate(self.npcs):
            result = npc.update(self.player_pos[0], self.player_pos[1], dt, self.map)
            if result == "damage":
                # Игрок получает урон
                self.player_health -= npc.attack_damage
                self.damage_flash = 1.0
                
                if self.player_health <= 0:
                    self.game_over = True
                    self.show_game_over()
                    return
        
        # Проверка столкновений с игроком
        self.check_collisions()
        
        # Отрисовка только в graphics_widget
        self.graphics_widget.canvas.clear()
        with self.graphics_widget.canvas:
            # Эффект мигания при получении урона
            if self.damage_flash > 0:
                Color(1.0, 0.0, 0.0, self.damage_flash * 0.3)
                Rectangle(pos=(0, 0), size=(self.width, self.height))
            
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
            
            # Отрисовка NPC
            for npc in self.npcs:
                self.draw_npc(npc)
            
            # Отрисовка HUD поверх всего
            self.draw_hud()
    
    def draw_npc(self, npc):
        # Вычисляем относительную позицию NPC
        dx = npc.x - self.player_pos[0]
        dy = npc.y - self.player_pos[1]
        
        # Расстояние до NPC
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 15:  # Не рисуем далеких NPC
            return
        
        # Угол к NPC
        npc_angle = math.atan2(dy, dx)
        
        # Разница между направлением игрока и NPC
        angle_diff = npc_angle - self.player_angle
        
        # Нормализуем разницу углов
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        elif angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        # Проверяем, находится ли NPC в поле зрения
        if abs(angle_diff) < self.fov / 2:
            # Вычисляем позицию по горизонтали на экране
            screen_x = (angle_diff + self.fov/2) / self.fov * self.width
            
            # Размер NPC на экране (чем дальше, тем меньше)
            npc_height = self.height / (distance + 0.5) * 1.5
            npc_width = npc_height * 0.8
            
            # Проверяем, не закрыт ли NPC стеной
            ray_distance = self.cast_ray(npc_angle, distance)
            if ray_distance < distance - 0.5:
                return  # NPC закрыт стеной
            
            # Рисуем NPC
            Color(*npc.color)
            Rectangle(
                pos=(screen_x - npc_width/2, (self.height - npc_height)/2),
                size=(npc_width, npc_height)
            )
            
            # Индикатор здоровья над NPC
            health_width = npc_width
            health_height = 5
            health_ratio = npc.health / 3.0
            
            # Фон индикатора здоровья
            Color(0.2, 0.2, 0.2, 0.8)
            Rectangle(
                pos=(screen_x - health_width/2, (self.height - npc_height)/2 + npc_height),
                size=(health_width, health_height)
            )
            
            # Сам индикатор здоровья
            Color(0.2, 0.8, 0.2, 0.8)
            Rectangle(
                pos=(screen_x - health_width/2, (self.height - npc_height)/2 + npc_height),
                size=(health_width * health_ratio, health_height)
            )
    
    def draw_hud(self):
        # Панель здоровья
        health_width = 200
        health_height = 20
        health_x = 20
        health_y = self.height - 40
        
        # Фон здоровья
        Color(0.2, 0.2, 0.2, 0.8)
        Rectangle(
            pos=(health_x, health_y),
            size=(health_width, health_height)
        )
        
        # Индикатор здоровья
        health_ratio = self.player_health / 100.0
        if health_ratio > 0.6:
            health_color = (0.2, 0.8, 0.2, 0.8)
        elif health_ratio > 0.3:
            health_color = (0.8, 0.8, 0.2, 0.8)
        else:
            health_color = (0.8, 0.2, 0.2, 0.8)
        
        Color(*health_color)
        Rectangle(
            pos=(health_x, health_y),
            size=(health_width * health_ratio, health_height)
        )
        
        # Текст здоровья
        Color(1, 1, 1, 1)
        health_text = f"Здоровье: {int(self.player_health)}"
        self.draw_text(health_text, health_x + health_width + 10, health_y, 20)
        
        # Счет
        score_x = 20
        score_y = health_y - 30
        Color(1, 1, 1, 1)
        score_text = f"Счет: {self.score}"
        self.draw_text(score_text, score_x, score_y, 20)
        
        # Количество NPC
        npc_x = 20
        npc_y = score_y - 30
        npc_text = f"NPC осталось: {len(self.npcs)}"
        self.draw_text(npc_text, npc_x, npc_y, 20)
        
        
        
        # Сообщение о победе
        if len(self.npcs) == 0 and not self.game_over:
            Color(0.2, 0.8, 0.2, 0.8)
            Rectangle(
                pos=(self.width/2 - 150, self.height/2 - 50),
                size=(300, 100)
            )
            Color(1, 1, 1, 1)
            self.draw_text("ПОБЕДА!", self.width/2 - 50, self.height/2, 40)
            self.draw_text(f"Счет: {self.score}", self.width/2 - 60, self.height/2 - 30, 30)
    
    def draw_text(self, text, x, y, font_size):
        # Простая функция для рисования текста
        from kivy.core.text import Label as CoreLabel
        label = CoreLabel(text=text, font_size=font_size)
        label.refresh()
        texture = label.texture
        
        Color(1, 1, 1, 1)
        Rectangle(pos=(x, y), size=texture.size, texture=texture)
    
    def show_game_over(self):
        # Создаем popup с сообщением о конце игры
        content = BoxLayout(orientation='vertical', spacing=20, padding=30)
        
        title = Label(
            text='ИГРА ОКОНЧЕНА',
            font_size=50,
            color=(1, 0.2, 0.2, 1)
        )
        
        score_label = Label(
            text=f'Ваш счет: {self.score}',
            font_size=40,
            color=(1, 1, 1, 1)
        )
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=20)
        
        btn_restart = Button(
            text='ЗАНОВО',
            font_size=30,
            background_color=(0.2, 0.8, 0.2, 1),
            background_normal=''
        )
        btn_restart.bind(on_press=lambda x: self.restart_game())
        
        btn_menu = Button(
            text='В МЕНЮ',
            font_size=30,
            background_color=(0.8, 0.2, 0.2, 1),
            background_normal=''
        )
        btn_menu.bind(on_press=lambda x: self.go_to_menu())
        
        buttons_layout.add_widget(btn_restart)
        buttons_layout.add_widget(btn_menu)
        
        content.add_widget(title)
        content.add_widget(score_label)
        content.add_widget(buttons_layout)
        
        self.game_over_popup = Popup(
            title='',
            content=content,
            size_hint=(0.7, 0.5),
            auto_dismiss=False,
            background=''
        )
        self.game_over_popup.open()
    
    def restart_game(self):
        if hasattr(self, 'game_over_popup'):
            self.game_over_popup.dismiss()
        self.reset_game()
        self.game_over = False
    
    def go_to_menu(self):
        if hasattr(self, 'game_over_popup'):
            self.game_over_popup.dismiss()
        app = App.get_running_app()
        app.sm.current = 'menu'
    
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

class RaycasterApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_map = 'small'
        self.sm = ScreenManager(transition=SlideTransition())
    
    def build(self):
        # Устанавливаем размер окна
        Window.size = (1024, 768)
        
        # Для мобильных устройств делаем полноэкранный режим
        try:
            from kivy.utils import platform
            if platform in ('android', 'ios'):
                Window.fullscreen = 'auto'
                Config.set('graphics', 'fullscreen', 'auto')
        except:
            pass
        
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
            
            # Пересоздаем элементы управления с новыми настройками
            self.game_screen.game_widget.create_controls()
            
            # Пересоздаем NPC с новыми настройками
            if hasattr(self.game_screen.game_widget, 'create_npcs'):
                self.game_screen.game_widget.create_npcs()

if __name__ == '__main__':
    # Отключаем лишние логи
    import os
    os.environ['KIVY_NO_CONSOLELOG'] = '1'
    
    RaycasterApp().run()
