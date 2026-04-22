"""
3D DOOM-style Raycaster - ANIME NPC DIALOG SYSTEM
С сенсорным управлением для Android
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color, Line, Ellipse, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.modalview import ModalView
from kivy.uix.behaviors import ButtonBehavior
from math import cos, sin, sqrt, atan2
import math
from time import time

# Настройки
Window.size = (900, 600)
Window.show_cursor = True

TARGET_FPS = 120
FRAME_TIME = 1.0 / TARGET_FPS

class TouchJoystick(Widget):
    """Виртуальный джойстик для Android"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.2, 0.2)
        self.pos_hint = {'x': 0.02, 'y': 0.02}
        
        self.active = False
        self.touch_id = None
        self.value = (0, 0)  # x, y от -1 до 1
        
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.update_canvas()
        
    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Фон джойстика
            Color(0.2, 0.2, 0.3, 0.7)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.width/2])
            
            # Центр
            Color(0.5, 0.5, 0.7, 0.8)
            center_x = self.pos[0] + self.width/2
            center_y = self.pos[1] + self.height/2
            radius = self.width/3
            Ellipse(pos=(center_x - radius, center_y - radius), 
                   size=(radius*2, radius*2))
            
            # Ручка джойстика
            if self.active:
                joy_x = self.pos[0] + self.width/2 + self.value[0] * self.width/3
                joy_y = self.pos[1] + self.height/2 + self.value[1] * self.height/3
            else:
                joy_x = self.pos[0] + self.width/2
                joy_y = self.pos[1] + self.height/2
            
            Color(0.8, 0.8, 1, 0.9)
            handle_radius = self.width/4
            Ellipse(pos=(joy_x - handle_radius, joy_y - handle_radius), 
                   size=(handle_radius*2, handle_radius*2))
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.active = True
            self.touch_id = touch.uid
            self.update_joystick(touch.pos)
            return True
        return False
    
    def on_touch_move(self, touch):
        if self.active and touch.uid == self.touch_id:
            self.update_joystick(touch.pos)
            return True
        return False
    
    def on_touch_up(self, touch):
        if self.active and touch.uid == self.touch_id:
            self.active = False
            self.value = (0, 0)
            self.touch_id = None
            self.update_canvas()
            return True
        return False
    
    def update_joystick(self, touch_pos):
        center_x = self.pos[0] + self.width/2
        center_y = self.pos[1] + self.height/2
        
        dx = touch_pos[0] - center_x
        dy = touch_pos[1] - center_y
        
        max_dist = min(self.width/2, self.height/2)
        dist = min(1.0, sqrt(dx*dx + dy*dy) / max_dist)
        
        if dist > 0:
            angle = atan2(dy, dx)
            self.value = (math.cos(angle) * dist, math.sin(angle) * dist)
        else:
            self.value = (0, 0)
        
        self.update_canvas()

class TouchButton(ButtonBehavior, Widget):
    """Сенсорная кнопка действия"""
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.size_hint = (0.1, 0.1)
        self.background_color_normal = (0.3, 0.3, 0.5, 0.8)
        self.background_color_down = (0.5, 0.5, 0.8, 0.9)
        self.current_color = self.background_color_normal
        self.is_pressed = False
        self._label = None
        
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.update_canvas()
        
    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*self.current_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
            
            # Рисуем текст
            if self.text:
                from kivy.core.text import Label as CoreLabel
                label = CoreLabel(text=self.text, font_size=self.height*0.5, 
                                color=(1,1,1,1), bold=True)
                label.refresh()
                texture = label.texture
                text_size = texture.size
                Rectangle(texture=texture, 
                         pos=(self.pos[0] + self.width/2 - text_size[0]/2,
                              self.pos[1] + self.height/2 - text_size[1]/2),
                         size=text_size)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.is_pressed = True
            self.current_color = self.background_color_down
            self.update_canvas()
            self.dispatch('on_press')
            return True
        return False
    
    def on_touch_up(self, touch):
        if self.is_pressed:
            self.is_pressed = False
            self.current_color = self.background_color_normal
            self.update_canvas()
            self.dispatch('on_release')
            return True
        return False
    
    def on_press(self):
        pass
    
    def on_release(self):
        pass

class NPC:
    """Неигровой персонаж с аниме-портретом"""
    def __init__(self, x, y, name="Мико", sprite_color=(0.8, 0.4, 0.8)):
        self.x = x
        self.y = y
        self.name = name
        self.sprite_color = sprite_color
        
        # Диалоги с эмоциями
        self.dialogues = [
            {"text": f"Привет! Я {name}.", "emotion": "happy"},
            {"text": "Добро пожаловать в наше измерение!", "emotion": "happy"},
            {"text": "Здесь очень опасно... Будь осторожен.", "emotion": "worried"},
            {"text": "Если найдёшь красный ключ - принеси мне.", "emotion": "normal"},
            {"text": "Я верю в тебя! Удачи!", "emotion": "happy"}
        ]
        self.current_dialogue = 0
        self.is_talking = False
        
    def get_dialogue(self):
        if self.current_dialogue < len(self.dialogues):
            return self.dialogues[self.current_dialogue]
        return {"text": "У меня больше нет новостей.", "emotion": "normal"}
    
    def next_dialogue(self):
        if self.current_dialogue < len(self.dialogues) - 1:
            self.current_dialogue += 1
            return True
        return False
    
    def reset_dialogue(self):
        self.current_dialogue = 0

class AnimatedPortrait(RelativeLayout):
    """Анимированный портрет персонажа"""
    def __init__(self, npc, **kwargs):
        super().__init__(**kwargs)
        self.npc = npc
        self.size_hint = (0.35, 0.7)
        self.pos_hint = {'x': 0.02, 'y': 0.15}
        self.animation_time = 0
        
        Clock.schedule_interval(self.animate, 0.05)
        self.bind(pos=self.update_portrait, size=self.update_portrait)
        
    def animate(self, dt):
        self.animation_time += dt
        self.update_portrait()
    
    def update_portrait(self, *args):
        self.canvas.clear()
        
        with self.canvas:
            Color(0.1, 0.1, 0.15, 0.95)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            
            Color(0.8, 0.6, 0.9, 0.5 + math.sin(self.animation_time * 3) * 0.2)
            Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], 20), width=3)
            
            self.draw_anime_character()
    
    def draw_anime_character(self):
        w, h = self.size
        x, y = self.pos
        
        center_x = x + w // 2
        center_y = y + h // 2
        
        skin_color = (1, 0.9, 0.8, 1)
        hair_color = (0.6, 0.3, 0.8, 1)
        eye_color = (0.2, 0.5, 1, 1)
        dress_color = (0.9, 0.5, 0.5, 1)
        
        head_radius = min(w, h) * 0.2
        bob_offset = math.sin(self.animation_time * 2) * 2
        
        Color(*skin_color)
        Ellipse(pos=(center_x - head_radius, center_y + head_radius * 0.5 + bob_offset), 
                size=(head_radius * 2, head_radius * 2))
        
        Color(*hair_color)
        Ellipse(pos=(center_x - head_radius * 1.1, center_y + head_radius * 0.8 + bob_offset), 
                size=(head_radius * 2.2, head_radius * 1.8))
        Ellipse(pos=(center_x - head_radius * 0.8, center_y + head_radius * 1.2 + bob_offset), 
                size=(head_radius * 1.6, head_radius * 0.8))
        
        Ellipse(pos=(center_x - head_radius * 1.3, center_y + head_radius * 0.6 + bob_offset), 
                size=(head_radius * 0.8, head_radius * 1.2))
        Ellipse(pos=(center_x + head_radius * 0.5, center_y + head_radius * 0.6 + bob_offset), 
                size=(head_radius * 0.8, head_radius * 1.2))
        
        Color(1, 1, 1, 1)
        eye_size = head_radius * 0.35
        left_eye_pos = (center_x - head_radius * 0.5, center_y + head_radius * 0.8 + bob_offset)
        right_eye_pos = (center_x + head_radius * 0.15, center_y + head_radius * 0.8 + bob_offset)
        Ellipse(pos=left_eye_pos, size=(eye_size, eye_size * 1.2))
        Ellipse(pos=right_eye_pos, size=(eye_size, eye_size * 1.2))
        
        Color(*eye_color)
        iris_size = eye_size * 0.7
        Ellipse(pos=(left_eye_pos[0] + eye_size * 0.15, left_eye_pos[1] + eye_size * 0.1), 
                size=(iris_size, iris_size))
        Ellipse(pos=(right_eye_pos[0] + eye_size * 0.15, right_eye_pos[1] + eye_size * 0.1), 
                size=(iris_size, iris_size))
        
        Color(0, 0, 0, 1)
        pupil_size = iris_size * 0.5
        Ellipse(pos=(left_eye_pos[0] + eye_size * 0.25, left_eye_pos[1] + eye_size * 0.15), 
                size=(pupil_size, pupil_size))
        Ellipse(pos=(right_eye_pos[0] + eye_size * 0.25, right_eye_pos[1] + eye_size * 0.15), 
                size=(pupil_size, pupil_size))
        
        Color(1, 1, 1, 1)
        highlight_size = pupil_size * 0.4
        Ellipse(pos=(left_eye_pos[0] + eye_size * 0.3, left_eye_pos[1] + eye_size * 0.25), 
                size=(highlight_size, highlight_size))
        Ellipse(pos=(right_eye_pos[0] + eye_size * 0.3, right_eye_pos[1] + eye_size * 0.25), 
                size=(highlight_size, highlight_size))
        
        dialogue = self.npc.get_dialogue()
        emotion = dialogue.get("emotion", "normal")
        
        Color(1, 0.4, 0.4, 1)
        mouth_y = center_y + head_radius * 0.3 + bob_offset
        
        if emotion == "happy":
            Line(points=[
                center_x - head_radius * 0.3, mouth_y,
                center_x, mouth_y + head_radius * 0.15,
                center_x + head_radius * 0.3, mouth_y
            ], width=2, cap='round', joint='round')
        elif emotion == "worried":
            Line(points=[
                center_x - head_radius * 0.3, mouth_y - head_radius * 0.1,
                center_x, mouth_y,
                center_x + head_radius * 0.3, mouth_y - head_radius * 0.1
            ], width=2, cap='round', joint='round')
        else:
            Line(points=[
                center_x - head_radius * 0.2, mouth_y,
                center_x + head_radius * 0.2, mouth_y
            ], width=2, cap='round')
        
        blush_alpha = 0.4 + math.sin(self.animation_time * 2) * 0.2
        Color(1, 0.6, 0.6, blush_alpha)
        blush_size = head_radius * 0.3
        Ellipse(pos=(center_x - head_radius * 0.8, center_y + head_radius * 0.4 + bob_offset), 
                size=(blush_size, blush_size * 0.6))
        Ellipse(pos=(center_x + head_radius * 0.5, center_y + head_radius * 0.4 + bob_offset), 
                size=(blush_size, blush_size * 0.6))
        
        Color(*dress_color)
        body_width = head_radius * 1.5
        body_height = head_radius * 2
        RoundedRectangle(
            pos=(center_x - body_width // 2, center_y - body_height * 0.5),
            size=(body_width, body_height),
            radius=[10]
        )
        
        Color(1, 1, 1, 1)
        Line(points=[
            center_x - body_width // 3, center_y + body_height * 0.3,
            center_x, center_y + body_height * 0.1,
            center_x + body_width // 3, center_y + body_height * 0.3
        ], width=2, cap='round')

class DialogueBox(ModalView):
    """Стильное окно диалога с портретом"""
    def __init__(self, npc, on_close_callback, **kwargs):
        super().__init__(**kwargs)
        self.npc = npc
        self.on_close_callback = on_close_callback
        self.size_hint = (0.95, 0.38)
        self.pos_hint = {'center_x': 0.5, 'y': 0.01}
        self.auto_dismiss = False
        self.background = ''
        self.background_color = (0, 0, 0, 0)
        
        self.opacity = 0
        anim = Animation(opacity=1, duration=0.3, t='out_quad')
        anim.start(self)
        
        main_layout = FloatLayout()
        
        with main_layout.canvas.before:
            Color(0.05, 0.05, 0.1, 0.95)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[15]
            )
            Color(0.8, 0.6, 0.9, 1)
            Line(
                rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], 15),
                width=3
            )
        
        self.portrait = AnimatedPortrait(npc)
        self.add_widget(self.portrait)
        
        text_layout = BoxLayout(
            orientation='vertical',
            pos_hint={'x': 0.38, 'y': 0.1},
            size_hint=(0.58, 0.8),
            spacing=5
        )
        
        name_label = Label(
            text=f"[b]{npc.name}[/b]",
            markup=True,
            font_size='20sp',
            color=(0.9, 0.7, 1, 1),
            size_hint=(1, 0.2),
            halign='left',
            valign='middle'
        )
        name_label.bind(size=name_label.setter('text_size'))
        text_layout.add_widget(name_label)
        
        dialogue = npc.get_dialogue()
        self.dialogue_label = Label(
            text=dialogue["text"],
            font_size='16sp',
            color=(1, 1, 1, 1),
            size_hint=(1, 0.5),
            halign='left',
            valign='top'
        )
        self.dialogue_label.bind(size=self.dialogue_label.setter('text_size'))
        text_layout.add_widget(self.dialogue_label)
        
        button_layout = BoxLayout(
            size_hint=(1, 0.3),
            spacing=10
        )
        
        self.next_button = Button(
            text="Далее ▼",
            font_size='16sp',
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        self.next_button.bind(on_press=self.on_next)
        button_layout.add_widget(self.next_button)
        
        close_button = Button(
            text="Закрыть ✕",
            font_size='16sp',
            background_color=(0.7, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        close_button.bind(on_press=self.on_close)
        button_layout.add_widget(close_button)
        
        text_layout.add_widget(button_layout)
        main_layout.add_widget(text_layout)
        
        self.add_widget(main_layout)
        self.bind(pos=self.update_bg, size=self.update_bg)
    
    def update_bg(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
    
    def on_next(self, instance):
        if self.npc.next_dialogue():
            dialogue = self.npc.get_dialogue()
            anim = Animation(opacity=0, duration=0.1)
            anim.bind(on_complete=lambda *args: self.update_text(dialogue["text"]))
            anim.start(self.dialogue_label)
        else:
            self.next_button.disabled = True
            self.next_button.text = "Конец"
            self.next_button.background_color = (0.4, 0.4, 0.4, 1)
    
    def update_text(self, text):
        self.dialogue_label.text = text
        anim = Animation(opacity=1, duration=0.1)
        anim.start(self.dialogue_label)
        self.portrait.update_portrait()
    
    def on_close(self, instance):
        anim = Animation(opacity=0, duration=0.2)
        anim.bind(on_complete=lambda *args: self._dismiss())
        anim.start(self)
    
    def _dismiss(self):
        self.npc.is_talking = False
        self.npc.reset_dialogue()
        self.dismiss()
        if self.on_close_callback:
            self.on_close_callback()

class DoomRaycaster(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Игрок
        self.pos_x = 3.0
        self.pos_y = 3.0
        self.dir_x = 1.0
        self.dir_y = 0.0
        self.plane_x = 0.0
        self.plane_y = 0.66
        
        self.angle = 0.0
        self.move_speed = 0.1
        self.rot_speed = 0.05
        self.mouse_sensitivity = 0.0025
        
        # Состояние игры
        self.game_paused = False
        self.interaction_distance = 1.8
        
        # Карта
        self.map = [
            [1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,0,1,0,0,1,0,1],
            [1,0,0,0,1,0,0,0,0,1],
            [1,0,2,0,1,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,0,0,0,0,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1]
        ]
        
        self.map_width = len(self.map[0])
        self.map_height = len(self.map)
        
        # Создаём NPC
        self.npcs = []
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.map[y][x] == 2:
                    self.npcs.append(NPC(x + 0.5, y + 0.5, "Мико-тян"))
        
        # Управление с клавиатуры (для десктопа)
        self._keyboard = None
        self.keys_pressed = set()
        
        # Сенсорное управление
        self.setup_touch_controls()
        
        # Мышь (для десктопа)
        self.last_mouse_x = Window.mouse_pos[0]
        Window.bind(mouse_pos=self.on_mouse_move)
        
        # FPS
        self.last_frame_time = time()
        self.last_time = time()
        self.frame_count = 0
        self.fps = 0
        
        # Рендеринг
        self.render_scale = 2
        
        # UI
        self.setup_ui()
        
        # Запуск
        Clock.schedule_interval(self.update, 0)
        Clock.schedule_interval(self.update_ui, 0.1)
        
        # Клавиатура для десктопа
        self.init_keyboard()
    
    def init_keyboard(self):
        """Инициализация клавиатуры для десктопа"""
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        if self._keyboard:
            self._keyboard.bind(on_key_down=self._on_key_down)
            self._keyboard.bind(on_key_up=self._on_key_up)
    
    def setup_touch_controls(self):
        """Настройка сенсорных кнопок"""
        # Джойстик для движения
        self.joystick = TouchJoystick()
        self.add_widget(self.joystick)
        
        # Кнопка взаимодействия
        self.interact_btn = TouchButton(text="E")
        self.interact_btn.pos_hint = {'right': 0.98, 'y': 0.02}
        self.interact_btn.bind(on_release=self.on_interact_touch)
        self.add_widget(self.interact_btn)
        
        # Кнопка поворота налево
        self.rotate_left_btn = TouchButton(text="←")
        self.rotate_left_btn.pos_hint = {'x': 0.75, 'y': 0.02}
        self.rotate_left_btn.bind(on_press=self.start_rotate_left, on_release=self.stop_rotate)
        self.add_widget(self.rotate_left_btn)
        
        # Кнопка поворота направо
        self.rotate_right_btn = TouchButton(text="→")
        self.rotate_right_btn.pos_hint = {'x': 0.85, 'y': 0.02}
        self.rotate_right_btn.bind(on_press=self.start_rotate_right, on_release=self.stop_rotate)
        self.add_widget(self.rotate_right_btn)
        
        # Кнопка выхода
        self.exit_btn = TouchButton(text="✕")
        self.exit_btn.pos_hint = {'right': 0.98, 'top': 0.98}
        self.exit_btn.bind(on_release=self.on_exit_touch)
        self.add_widget(self.exit_btn)
        
        self.rotating_left = False
        self.rotating_right = False
    
    def setup_ui(self):
        """Настройка UI элементов"""
        self.fps_label = Label(
            text="FPS: 0",
            pos_hint={'right': 1, 'top': 1},
            size_hint=(None, None),
            font_size='14sp',
            color=(0,1,0,1)
        )
        self.add_widget(self.fps_label)
        
        self.hint_label = Label(
            text="WASD: Move | E: Talk | ESC: Quit",
            pos_hint={'center_x': 0.5, 'y': 10},
            size_hint=(None, None),
            font_size='14sp',
            color=(1,1,1,1)
        )
        self.add_widget(self.hint_label)
        
        self.interact_label = Label(
            text="",
            pos_hint={'center_x': 0.5, 'center_y': 0.25},
            size_hint=(None, None),
            font_size='18sp',
            color=(1, 0.8, 1, 1)
        )
        self.add_widget(self.interact_label)
    
    def _keyboard_closed(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
            self._keyboard = None
    
    def _on_key_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        
        if key == 'escape':
            App.get_running_app().stop()
        elif key == 'e' and not self.game_paused:
            self.check_interaction()
        else:
            self.keys_pressed.add(key)
        
        return True
    
    def _on_key_up(self, keyboard, keycode):
        if keycode[1] in self.keys_pressed:
            self.keys_pressed.remove(keycode[1])
        return True
    
    def on_interact_touch(self, instance):
        """Обработка касания кнопки взаимодействия"""
        if not self.game_paused:
            self.check_interaction()
    
    def start_rotate_left(self, instance):
        self.rotating_left = True
    
    def start_rotate_right(self, instance):
        self.rotating_right = True
    
    def stop_rotate(self, instance):
        self.rotating_left = False
        self.rotating_right = False
    
    def on_exit_touch(self, instance):
        App.get_running_app().stop()
    
    def check_interaction(self):
        """Проверка взаимодействия с NPC"""
        for npc in self.npcs:
            distance = sqrt((self.pos_x - npc.x)**2 + (self.pos_y - npc.y)**2)
            if distance < self.interaction_distance:
                self.start_dialogue(npc)
                break
    
    def start_dialogue(self, npc):
        """Начать диалог с аниме-персонажем"""
        self.game_paused = True
        npc.is_talking = True
        Window.show_cursor = True
        
        dialogue_box = DialogueBox(npc, self.end_dialogue)
        dialogue_box.open()
    
    def end_dialogue(self):
        """Завершить диалог"""
        self.game_paused = False
        Window.show_cursor = False
    
    def on_mouse_move(self, window, pos):
        if self.game_paused:
            return
        
        if not hasattr(self, 'last_mouse_x'):
            self.last_mouse_x = pos[0]
            return
            
        dx = pos[0] - self.last_mouse_x
        self.last_mouse_x = pos[0]
        
        if abs(dx) > 0:
            self.rotate_head(dx * self.mouse_sensitivity)
    
    def rotate_head(self, angle_delta):
        old_dir_x = self.dir_x
        self.dir_x = self.dir_x * cos(angle_delta) - self.dir_y * sin(angle_delta)
        self.dir_y = old_dir_x * sin(angle_delta) + self.dir_y * cos(angle_delta)
        
        old_plane_x = self.plane_x
        self.plane_x = self.plane_x * cos(angle_delta) - self.plane_y * sin(angle_delta)
        self.plane_y = old_plane_x * sin(angle_delta) + self.plane_y * cos(angle_delta)
        
        self.angle += angle_delta
    
    def update_ui(self, dt):
        # FPS
        self.fps_label.text = f"FPS: {self.fps}"
        
        # Проверка близости к NPC
        near_npc = False
        for npc in self.npcs:
            distance = sqrt((self.pos_x - npc.x)**2 + (self.pos_y - npc.y)**2)
            if distance < self.interaction_distance:
                near_npc = True
                self.interact_label.text = f"✨ Нажми E чтобы поговорить с {npc.name} ✨"
                break
        
        if not near_npc:
            self.interact_label.text = ""
        
        # Цвет FPS
        if self.fps >= TARGET_FPS * 0.9:
            self.fps_label.color = (0, 1, 0, 1)
        elif self.fps >= TARGET_FPS * 0.5:
            self.fps_label.color = (1, 1, 0, 1)
        else:
            self.fps_label.color = (1, 0, 0, 1)
    
    def update(self, dt):
        current_time = time()
        
        # FPS счётчик
        self.frame_count += 1
        if current_time - self.last_time >= 0.5:
            self.fps = self.frame_count * 2
            self.frame_count = 0
            self.last_time = current_time
        
        if self.game_paused:
            return
        
        if current_time - self.last_frame_time < FRAME_TIME:
            return
        
        self.last_frame_time = current_time
        
        # Получаем ввод с джойстика для движения
        move_x, move_y = 0.0, 0.0
        
        # Клавиатурное управление (десктоп)
        if 'w' in self.keys_pressed:
            move_x += self.dir_x * self.move_speed
            move_y += self.dir_y * self.move_speed
        if 's' in self.keys_pressed:
            move_x -= self.dir_x * self.move_speed
            move_y -= self.dir_y * self.move_speed
        if 'a' in self.keys_pressed:
            move_x += self.plane_x * self.move_speed
            move_y += self.plane_y * self.move_speed
        if 'd' in self.keys_pressed:
            move_x -= self.plane_x * self.move_speed
            move_y -= self.plane_y * self.move_speed
        
        # Сенсорное управление (джойстик)
        if hasattr(self, 'joystick') and self.joystick.active:
            joy_x, joy_y = self.joystick.value
            if abs(joy_x) > 0.1 or abs(joy_y) > 0.1:
                move_x += self.dir_x * joy_y * self.move_speed
                move_y += self.dir_y * joy_y * self.move_speed
                move_x += self.plane_x * joy_x * self.move_speed
                move_y += self.plane_y * joy_x * self.move_speed
        
        # Поворот с сенсорных кнопок
        if hasattr(self, 'rotating_left') and self.rotating_left:
            self.rotate_head(self.rot_speed)
        if hasattr(self, 'rotating_right') and self.rotating_right:
            self.rotate_head(-self.rot_speed)
        
        if move_x != 0 or move_y != 0:
            new_x = self.pos_x + move_x
            if 0 <= new_x < self.map_width and self.map[int(self.pos_y)][int(new_x)] in [0, 2]:
                self.pos_x = new_x
            
            new_y = self.pos_y + move_y
            if 0 <= new_y < self.map_height and self.map[int(new_y)][int(self.pos_x)] in [0, 2]:
                self.pos_y = new_y
        
        self.render_frame()
    
    def render_frame(self):
        self.canvas.clear()
        w, h = self.width, self.height
        
        with self.canvas:
            # Пол и потолок
            Color(0.15, 0.15, 0.25, 1)
            Rectangle(pos=(0, h//2), size=(w, h//2))
            Color(0.25, 0.2, 0.15, 1)
            Rectangle(pos=(0, 0), size=(w, h//2))
            
            dir_x = self.dir_x
            dir_y = self.dir_y
            plane_x = self.plane_x
            plane_y = self.plane_y
            pos_x = self.pos_x
            pos_y = self.pos_y
            map_ref = self.map
            step = self.render_scale
            
            for x in range(0, int(w), step):
                camera_x = 2 * x / w - 1
                ray_dir_x = dir_x + plane_x * camera_x
                ray_dir_y = dir_y + plane_y * camera_x
                
                map_x = int(pos_x)
                map_y = int(pos_y)
                
                delta_dist_x = abs(1.0 / ray_dir_x) if ray_dir_x != 0 else 1e30
                delta_dist_y = abs(1.0 / ray_dir_y) if ray_dir_y != 0 else 1e30
                
                if ray_dir_x < 0:
                    step_x = -1
                    side_dist_x = (pos_x - map_x) * delta_dist_x
                else:
                    step_x = 1
                    side_dist_x = (map_x + 1.0 - pos_x) * delta_dist_x
                    
                if ray_dir_y < 0:
                    step_y = -1
                    side_dist_y = (pos_y - map_y) * delta_dist_y
                else:
                    step_y = 1
                    side_dist_y = (map_y + 1.0 - pos_y) * delta_dist_y
                
                hit = 0
                side = 0
                
                for _ in range(20):
                    if side_dist_x < side_dist_y:
                        side_dist_x += delta_dist_x
                        map_x += step_x
                        side = 0
                    else:
                        side_dist_y += delta_dist_y
                        map_y += step_y
                        side = 1
                    
                    if map_x < 0 or map_x >= self.map_width or map_y < 0 or map_y >= self.map_height:
                        break
                    
                    if map_ref[map_y][map_x] == 1:
                        hit = 1
                        break
                
                if hit:
                    if side == 0:
                        perp_wall_dist = side_dist_x - delta_dist_x
                    else:
                        perp_wall_dist = side_dist_y - delta_dist_y
                    
                    if perp_wall_dist < 0.01:
                        perp_wall_dist = 0.01
                    
                    line_height = int(h / perp_wall_dist)
                    if line_height > h * 2:
                        line_height = h * 2
                    
                    draw_start = max(0, -line_height // 2 + h // 2)
                    draw_end = min(h, line_height // 2 + h // 2)
                    
                    shade = 1.0 / (1.0 + perp_wall_dist * 0.08)
                    
                    if side == 0:
                        r, g, b = 0.7 * shade, 0.2 * shade, 0.2 * shade
                    else:
                        r, g, b = 0.2 * shade, 0.2 * shade, 0.7 * shade
                    
                    Color(r, g, b, 1)
                    Rectangle(pos=(x, draw_start), size=(step, draw_end - draw_start))
            
            # Рендеринг NPC
            for npc in self.npcs:
                self.render_sprite(npc, w, h)
            
            # Прицел
            cx, cy = w // 2, h // 2
            cs = 10
            pulse = math.sin(time() * 10) * 0.5 + 0.5
            Color(0, 1, 0, 0.7 + pulse * 0.3)
            Line(points=[cx - cs, cy, cx + cs, cy], width=2)
            Line(points=[cx, cy - cs, cx, cy + cs], width=2)
            
            Color(1, 0, 0, 1)
            Ellipse(pos=(cx - 2, cy - 2), size=(4, 4))
    
    def render_sprite(self, npc, w, h):
        """Рендеринг спрайта NPC"""
        dx = npc.x - self.pos_x
        dy = npc.y - self.pos_y
        
        inv_det = 1.0 / (self.plane_x * self.dir_y - self.dir_x * self.plane_y)
        transform_x = inv_det * (self.dir_y * dx - self.dir_x * dy)
        transform_y = inv_det * (-self.plane_y * dx + self.plane_x * dy)
        
        if transform_y <= 0:
            return
        
        sprite_screen_x = int((w / 2) * (1 + transform_x / transform_y))
        sprite_height = abs(int(h / transform_y))
        sprite_width = abs(int(h / transform_y))
        
        sprite_height = min(sprite_height, h * 2)
        sprite_width = min(sprite_width, w // 4)
        
        draw_start_x = sprite_screen_x - sprite_width // 2
        draw_start_y = h // 2 - sprite_height // 2
        
        if 0 <= draw_start_x < w:
            with self.canvas:
                r, g, b = npc.sprite_color
                Color(r, g, b, 1)
                Rectangle(pos=(draw_start_x, draw_start_y), 
                         size=(sprite_width, sprite_height))
                
                Color(1, 1, 1, 1)
                eye_size = max(3, sprite_width // 6)
                Ellipse(pos=(draw_start_x + sprite_width//4 - eye_size//2, 
                           draw_start_y + sprite_height*2//3),
                       size=(eye_size, eye_size))
                Ellipse(pos=(draw_start_x + sprite_width*3//4 - eye_size//2, 
                           draw_start_y + sprite_height*2//3),
                       size=(eye_size, eye_size))
                
                Color(0, 0, 0, 1)
                pupil_size = eye_size // 2
                Ellipse(pos=(draw_start_x + sprite_width//4 - pupil_size//2, 
                           draw_start_y + sprite_height*2//3 + eye_size//4),
                       size=(pupil_size, pupil_size))
                Ellipse(pos=(draw_start_x + sprite_width*3//4 - pupil_size//2, 
                           draw_start_y + sprite_height*2//3 + eye_size//4),
                       size=(pupil_size, pupil_size))
                
                Color(1, 0.5, 0.5, 1)
                Line(points=[
                    draw_start_x + sprite_width//3, draw_start_y + sprite_height//2,
                    draw_start_x + sprite_width//2, draw_start_y + sprite_height//2 + sprite_height//6,
                    draw_start_x + sprite_width*2//3, draw_start_y + sprite_height//2
                ], width=2, cap='round')

class DoomGame(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.raycaster = DoomRaycaster()
        self.add_widget(self.raycaster)

class DoomApp(App):
    def build(self):
        return DoomGame()
    
    def on_stop(self):
        Window.show_cursor = True

if __name__ == '__main__':
    DoomApp().run()
