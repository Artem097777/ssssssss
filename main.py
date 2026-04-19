from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
from kivy.utils import platform


class ResponsiveGame(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Определяем тип устройства
        self.is_mobile = platform in ('android', 'ios')
        
        # Устанавливаем размеры в зависимости от устройства
        if self.is_mobile:
            # Для мобильных устройств
            self.player_size = min(Window.width, Window.height) * 0.12
            self.button_size = min(Window.width, Window.height) * 0.1
            self.button_font = min(Window.width, Window.height) * 0.06
            self.panel_width = 0.8
            self.panel_y = 0.03
        else:
            # Для планшетов и компьютеров
            self.player_size = 70
            self.button_size = 60
            self.button_font = 28
            self.panel_width = 0.4
            self.panel_y = 0.02
        
        self.create_player()
        self.create_controls()
        
        Clock.schedule_interval(self.update, 1/60)
    
    def create_player(self):
        self.player = Widget()
        self.player.size = (self.player_size, self.player_size)
        self.player.size_hint = (None, None)
        self.player.speed = 400
        self.player.move_x = 0
        self.player.move_y = 0
        
        with self.player.canvas:
            Color(0.2, 0.6, 1, 1)
            self.player.circle = Ellipse(pos=self.player.pos, size=self.player.size)
        
        self.player.bind(pos=self.update_player_graphics)
        self.player.pos = (Window.width//2 - self.player_size//2, 
                          Window.height//2 - self.player_size//2)
        self.add_widget(self.player)
    
    def update_player_graphics(self, *args):
        self.player.circle.pos = self.player.pos
    
    def move_player(self, dt):
        new_x = self.player.x + self.player.move_x * self.player.speed * dt
        new_y = self.player.y + self.player.move_y * self.player.speed * dt
        new_x = max(0, min(Window.width - self.player.width, new_x))
        new_y = max(0, min(Window.height - self.player.height, new_y))
        self.player.pos = (new_x, new_y)
    
    def create_controls(self):
        panel = BoxLayout(
            size_hint=(self.panel_width, 0.12),
            pos_hint={'x': (1-self.panel_width)/2, 'y': self.panel_y},
            spacing=10
        )
        
        def make_button(text, move_x, move_y):
            btn = Button(
                text=text,
                font_size=self.button_font,
                background_color=(0.3, 0.3, 0.5, 1),
                size_hint=(0.2, 1)
            )
            btn.bind(on_press=lambda x: self.set_movement(move_x, move_y))
            btn.bind(on_release=lambda x: self.stop_movement(move_x, move_y))
            return btn
        
        panel.add_widget(make_button("←", -1, 0))
        panel.add_widget(make_button("↑", 0, 1))
        panel.add_widget(make_button("↓", 0, -1))
        panel.add_widget(make_button("→", 1, 0))
        
        self.add_widget(panel)
    
    def set_movement(self, x, y):
        if x != 0:
            self.player.move_x = x
        if y != 0:
            self.player.move_y = y
    
    def stop_movement(self, x, y):
        if x != 0:
            self.player.move_x = 0
        if y != 0:
            self.player.move_y = 0
    
    def update(self, dt):
        self.move_player(dt)
    
    def on_size(self, *args):
        if hasattr(self, 'player'):
            self.player.pos = (
                max(0, min(Window.width - self.player.width, self.player.x)),
                max(0, min(Window.height - self.player.height, self.player.y))
            )


class ResponsiveApp(App):
    def build(self):
        if platform == 'android' or platform == 'ios':
            Window.fullscreen = True
        else:
            Window.size = (800, 600)
        return ResponsiveGame()


if __name__ == '__main__':
    ResponsiveApp().run()
