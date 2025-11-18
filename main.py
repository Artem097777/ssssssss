from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        title = Label(text='Red Square Game', font_size=40)
        start_button = Button(text='Start Game', size_hint=(0.5, 0.2), pos_hint={'center_x': 0.5})
        start_button.bind(on_press=self.start_game)
        exit_button = Button(text='Exit', size_hint=(0.5, 0.2), pos_hint={'center_x': 0.5})
        exit_button.bind(on_press=self.exit_game)
        
        layout.add_widget(title)
        layout.add_widget(start_button)
        layout.add_widget(exit_button)
        self.add_widget(layout)
    
    def start_game(self, instance):
        self.manager.current = 'game'
    
    def exit_game(self, instance):
        App.get_running_app().stop()

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Устанавливаем размер квадрата
        self.size_hint = (None, None)
        self.size = (50, 50)
        # Начальная позиция квадрата (центр экрана)
        self.pos = (Window.width / 2 - self.width / 2, Window.height / 2 - self.height / 2)
        
        # Скорость движения
        self.speed = 5
        
        # Направление движения
        self.keys_pressed = set()
        
        # Рисуем красный квадрат
        with self.canvas:
            Color(1, 0, 0, 1)  # Красный цвет
            self.rect = Rectangle(size=self.size, pos=self.pos)
        
        # Привязываем события клавиш
        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)
        
        # Запускаем обновление каждый кадр
        Clock.schedule_interval(self.update, 1.0 / 60.0)  # 60 FPS
        
        # Кнопка для возврата в меню
        back_button = Button(text='Back to Menu', size_hint=(0.2, 0.1), pos_hint={'x': 0, 'top': 1})
        back_button.bind(on_press=self.back_to_menu)
        self.add_widget(back_button)
    
    def back_to_menu(self, instance):
        self.parent.manager.current = 'menu'
    
    def on_key_down(self, window, key, *args):
        self.keys_pressed.add(key)
    
    def on_key_up(self, window, key, *args):
        self.keys_pressed.discard(key)
    
    def update(self, dt):
        # Обновляем позицию на основе нажатых клавиш
        if 273 in self.keys_pressed:  # Вверх
            self.pos = (self.pos[0], min(self.pos[1] + self.speed, Window.height - self.height))
        if 274 in self.keys_pressed:  # Вниз
            self.pos = (self.pos[0], max(self.pos[1] - self.speed, 0))
        if 275 in self.keys_pressed:  # Вправо
            self.pos = (min(self.pos[0] + self.speed, Window.width - self.width), self.pos[1])
        if 276 in self.keys_pressed:  # Влево
            self.pos = (max(self.pos[0] - self.speed, 0), self.pos[1])
        
        # Обновляем позицию прямоугольника
        self.rect.pos = self.pos

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(GameWidget())

class RedSquareGameApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    RedSquareGameApp().run()
