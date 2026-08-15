from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'window_state', 'visible')
from kivy.core.window import Window
Window.softinput_mode = 'pan'

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Ellipse
from kivy.clock import Clock
from kivy.uix.button import Button
from math import sqrt
from kivy.utils import platform

# ---------- КНОПКА УПРАВЛЕНИЯ ----------
class KeyButton(Button):
    def __init__(self, key_name, keys_dict, size, **kwargs):
        super().__init__(**kwargs)
        self.key_name = key_name
        self.keys = keys_dict
        self.background_color = (0.3, 0.3, 0.3, 0.6)
        self.color = (1, 1, 1, 0.9)
        self.font_size = size * 0.4
        self.size_hint = (None, None)
        self.size = (size, size)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.keys[self.key_name] = True
            self.background_color = (0, 0.8, 0.8, 0.8)
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.keys[self.key_name] = False
            self.background_color = (0.3, 0.3, 0.3, 0.6)
            return True
        if self.keys.get(self.key_name, False):
            self.keys[self.key_name] = False
            self.background_color = (0.3, 0.3, 0.3, 0.6)
        return super().on_touch_up(touch)


# ---------- ДЖОЙСТИК ----------
class Joystick(Widget):
    def __init__(self, size, pos, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = size
        self.pos = pos
        self.radius = self.width / 2
        self.center_pos = (self.x + self.radius, self.y + self.radius)
        self.dx = 0.0
        self.dy = 0.0
        self.active = False
        with self.canvas:
            Color(0.2, 0.2, 0.2, 0.5)
            self.bg_circle = Ellipse(pos=self.pos, size=self.size)
            Color(0, 0.8, 0.8, 0.9)
            self.knob = Ellipse(pos=(self.center_pos[0] - 20, self.center_pos[1] - 20),
                                size=(40, 40))
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.radius = self.width / 2
        self.center_pos = (self.x + self.radius, self.y + self.radius)
        self.bg_circle.pos = self.pos
        self.bg_circle.size = self.size
        self._update_knob_pos()

    def _update_knob_pos(self):
        if not self.active:
            kx = self.center_pos[0] - 20
            ky = self.center_pos[1] - 20
        else:
            max_offset = self.radius * 0.8
            kx = self.center_pos[0] + self.dx * max_offset - 20
            ky = self.center_pos[1] + self.dy * max_offset - 20
        self.knob.pos = (kx, ky)
        self.canvas.ask_update()  # принудительная перерисовка

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.active = True
            self._update_vector(touch.pos)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.active:
            self._update_vector(touch.pos)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.active:
            self.active = False
            self.dx = 0.0
            self.dy = 0.0
            self._update_knob_pos()
            return True
        return super().on_touch_up(touch)

    def _update_vector(self, touch_pos):
        dx = touch_pos[0] - self.center_pos[0]
        dy = touch_pos[1] - self.center_pos[1]
        distance = sqrt(dx*dx + dy*dy)
        max_dist = self.radius * 0.8

        # Мёртвая зона (10 пикселей)
        dead_zone = 10
        if distance < dead_zone:
            self.dx = 0.0
            self.dy = 0.0
            self._update_knob_pos()
            return

        if distance > max_dist:
            dx = dx / distance * max_dist
            dy = dy / distance * max_dist
            distance = max_dist
        if distance > 0:
            self.dx = dx / max_dist
            self.dy = dy / max_dist
        else:
            self.dx = 0.0
            self.dy = 0.0
        self._update_knob_pos()

    def get_vector(self):
        return self.dx, self.dy


# ---------- КВАДРАТ ----------
class AdaptiveSquare(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (100, 100)
        self.pos = (0, 0)
        with self.canvas:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.speed = 300
        self.keys = {
            'w': False, 'up': False,
            's': False, 'down': False,
            'a': False, 'left': False,
            'd': False, 'right': False
        }

        # Поддержка клавиатуры (физической) на всех платформах
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

        Window.bind(on_resize=self.on_window_resize)

    def _keyboard_closed(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
            self._keyboard = None

    def on_window_resize(self, window, width, height):
        self.update_size_and_position()

    def update_size_and_position(self):
        w, h = Window.width, Window.height
        new_size = max(40, min(150, min(w, h) * 0.1))
        self.size = (new_size, new_size)
        self.pos = (w/2 - new_size/2, h/2 - new_size/2)
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if isinstance(keycode, (list, tuple)) and len(keycode) > 1:
            key_name = keycode[1].lower()
        else:
            key_name = str(keycode).lower()
        if key_name in self.keys:
            self.keys[key_name] = True
        return True

    def _on_key_up(self, keyboard, keycode):
        if isinstance(keycode, (list, tuple)) and len(keycode) > 1:
            key_name = keycode[1].lower()
        else:
            key_name = str(keycode).lower()
        if key_name in self.keys:
            self.keys[key_name] = False
        return True

    def move_to(self, x, y):
        w, h = Window.width, Window.height
        x = max(0, min(x, w - self.width))
        y = max(0, min(y, h - self.height))
        self.pos = (x, y)
        self.rect.pos = self.pos

    def move_by_vector(self, dx, dy, dt):
        x = self.pos[0] + dx * self.speed * dt
        y = self.pos[1] + dy * self.speed * dt
        self.move_to(x, y)

    # Сброс всех клавиш (вызывается при сворачивании)
    def reset_keys(self):
        for key in self.keys:
            self.keys[key] = False


# ---------- ИГРОВОЙ ВИДЖЕТ ----------
class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.square = AdaptiveSquare()
        self.add_widget(self.square)

        # Адаптивные размеры
        w, h = Window.width, Window.height
        btn_size = min(w, h) * 0.08
        joystick_size = min(w, h) * 0.2

        # Джойстик (слева внизу)
        joystick_pos = (20, 20)
        self.joystick = Joystick((joystick_size, joystick_size), joystick_pos)
        self.add_widget(self.joystick)

        self.keys = self.square.keys

        # WASD (слева сверху)
        wasd_positions = {
            'w': (btn_size * 0.7, h - btn_size * 5.5),
            'a': (btn_size * 0.2, h - btn_size * 4.8),
            's': (btn_size * 0.7, h - btn_size * 4.8),
            'd': (btn_size * 1.2, h - btn_size * 4.8),
        }
        self.wasd_buttons = []
        for key, pos in wasd_positions.items():
            btn = KeyButton(key, self.keys, btn_size, text=key.upper())
            btn.pos = pos
            self.add_widget(btn)
            self.wasd_buttons.append(btn)

        # Стрелки (справа внизу)
        arrow_positions = {
            'up': (w - btn_size * 2.6, btn_size * 1.5),
            'left': (w - btn_size * 3.2, btn_size * 0.8),
            'down': (w - btn_size * 2.6, btn_size * 0.8),
            'right': (w - btn_size * 2.0, btn_size * 0.8),
        }
        self.arrow_buttons = []
        labels = {'up': '↑', 'down': '↓', 'left': '←', 'right': '→'}
        for key, pos in arrow_positions.items():
            btn = KeyButton(key, self.keys, btn_size, text=labels[key])
            btn.pos = pos
            self.add_widget(btn)
            self.arrow_buttons.append(btn)

        Window.bind(on_resize=self.on_window_resize)

    def on_window_resize(self, window, width, height):
        pass  # можно пересчитать позиции кнопок, если нужно


# ---------- ПРИЛОЖЕНИЕ ----------
class GameApp(App):
    def build(self):
        root = GameWidget()
        Clock.schedule_once(lambda dt: root.square.update_size_and_position(), 0)
        Clock.schedule_interval(self.update, 1/60)
        return root

    def update(self, dt):
        keys = self.root.square.keys
        joystick_dx, joystick_dy = self.root.joystick.get_vector()

        dx = joystick_dx
        dy = joystick_dy

        # WASD – теперь ключи возвращают False по умолчанию!
        if keys.get('a', False):
            dx -= 1
        if keys.get('d', False):
            dx += 1
        if keys.get('w', False):
            dy += 1
        if keys.get('s', False):
            dy -= 1

        # Стрелки
        if keys.get('left', False):
            dx -= 1
        if keys.get('right', False):
            dx += 1
        if keys.get('up', False):
            dy += 1
        if keys.get('down', False):
            dy -= 1

        # Нормализация вектора
        length = sqrt(dx*dx + dy*dy)
        if length > 0:
            dx /= length
            dy /= length
            self.root.square.move_by_vector(dx, dy, dt)

    # Корректная обработка сворачивания (клавиши не залипают)
    def on_pause(self):
        self.root.square.reset_keys()
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    GameApp().run()
