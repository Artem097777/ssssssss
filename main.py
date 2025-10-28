from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.image import Image
from kivy.properties import NumericProperty
import random
import math

# Устанавливаем полноэкранный режим для планшета
Window.fullscreen = 'auto'  # Автоматический полноэкранный режим
# Или можно использовать: Window.fullscreen = True

class FadeTransitionWidget(Widget):
    """Виджет для плавного перехода с затемнением"""
    alpha = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.complete_callback = None
        self.duration = 0.5  # длительность перехода в секундах
        self.elapsed_time = 0
        
    def start_fade_in(self, callback=None):
        """Начать плавное затемнение"""
        self.complete_callback = callback
        self.alpha = 0
        self.elapsed_time = 0
        Clock.schedule_interval(self._update_fade_in, 1/60)
    
    def _update_fade_in(self, dt):
        """Обновление анимации затемнения"""
        self.elapsed_time += dt
        progress = min(self.elapsed_time / self.duration, 1.0)
        self.alpha = progress
        
        if progress >= 1.0:
            Clock.unschedule(self._update_fade_in)
            if self.complete_callback:
                self.complete_callback()
    
    def start_fade_out(self, callback=None):
        """Начать плавное осветление"""
        self.complete_callback = callback
        self.alpha = 1
        self.elapsed_time = 0
        Clock.schedule_interval(self._update_fade_out, 1/60)
    
    def _update_fade_out(self, dt):
        """Обновление анимации осветления"""
        self.elapsed_time += dt
        progress = min(self.elapsed_time / self.duration, 1.0)
        self.alpha = 1 - progress
        
        if progress >= 1.0:
            Clock.unschedule(self._update_fade_out)
            if self.complete_callback:
                self.complete_callback()

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
        # Обновляем размер при изменении окна
        Window.bind(on_resize=self.on_window_resize)
    
    def on_window_resize(self, window, width, height):
        """Обновление UI при изменении размера окна"""
        self.bg_rect.size = Window.size
        self.update_fade_color(None, self.fade_transition.alpha)
    
    def setup_ui(self):
        # Фоновое изображение
        with self.canvas:
            Color(0.1, 0.1, 0.2, 1)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
        
        # Основной layout
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # Заголовок (увеличиваем шрифт для планшета)
        title_label = Label(
            text='NPC Симулятор',
            font_size='48sp',  # Увеличили для планшета
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.3)
        )
        
        # Кнопки меню (увеличиваем размеры для планшета)
        buttons_layout = BoxLayout(orientation='vertical', spacing=25, size_hint=(1, 0.6))
        
        self.start_button = Button(
            text='Начать игру',
            font_size='32sp',  # Увеличили для планшета
            background_color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.2)
        )
        self.start_button.bind(on_press=self.start_game)
        
        self.settings_button = Button(
            text='Настройки',
            font_size='32sp',  # Увеличили для планшета
            background_color=(0.2, 0.5, 0.8, 1),
            size_hint=(1, 0.2)
        )
        self.settings_button.bind(on_press=self.show_settings)
        
        self.about_button = Button(
            text='Об игре',
            font_size='32sp',  # Увеличили для планшета
            background_color=(0.8, 0.5, 0.2, 1),
            size_hint=(1, 0.2)
        )
        self.about_button.bind(on_press=self.show_about)
        
        self.exit_button = Button(
            text='Выход',
            font_size='32sp',  # Увеличили для планшета
            background_color=(0.8, 0.2, 0.2, 1),
            size_hint=(1, 0.2)
        )
        self.exit_button.bind(on_press=self.exit_game)
        
        buttons_layout.add_widget(self.start_button)
        buttons_layout.add_widget(self.settings_button)
        buttons_layout.add_widget(self.about_button)
        buttons_layout.add_widget(self.exit_button)
        
        # Информация внизу (увеличиваем шрифт)
        info_label = Label(
            text='Управление: WASD/Стрелки - движение, E - взаимодействие с NPC, ESC/P - меню',
            font_size='18sp',  # Увеличили для планшета
            color=(0.7, 0.7, 0.7, 1),
            size_hint=(1, 0.1)
        )
        
        layout.add_widget(title_label)
        layout.add_widget(buttons_layout)
        layout.add_widget(info_label)
        
        self.add_widget(layout)
        
        # Добавляем виджет перехода (изначально невидимый)
        self.fade_transition = FadeTransitionWidget()
        self.add_widget(self.fade_transition)
        
        # Отрисовка затемнения
        with self.fade_transition.canvas:
            Color(0, 0, 0, self.fade_transition.alpha)
            self.fade_rect = Rectangle(pos=(0, 0), size=Window.size)
        
        # Связываем свойство alpha с обновлением цвета
        self.fade_transition.bind(alpha=self.update_fade_color)
    
    def update_fade_color(self, instance, value):
        """Обновление цвета затемнения"""
        with self.fade_transition.canvas:
            self.fade_transition.canvas.clear()
            Color(0, 0, 0, value)
            Rectangle(pos=(0, 0), size=Window.size)
    
    def start_game(self, instance):
        # Запускаем плавное затемнение
        self.fade_transition.start_fade_in(self.switch_to_game)
    
    def switch_to_game(self):
        # Переключаемся на игровой экран после завершения затемнения
        self.manager.current = 'game'
        # Запускаем осветление на игровом экране
        game_screen = self.manager.get_screen('game')
        game_screen.fade_transition.alpha = 1
        game_screen.fade_transition.start_fade_out()
    
    def show_settings(self, instance):
        """Показать настройки"""
        settings_popup = SettingsPopup()
        settings_popup.open()
    
    def show_about(self, instance):
        """Показать информацию об игре"""
        about_text = """
NPC Симулятор

Игра с интеллектуальными NPC, обладающими разным поведением:

- Блуждающие NPC: Просто гуляют по карте
- Патрульные NPC: Охраняют территорию
- Следящие NPC: Идут за игроком
- Убегающие NPC: Избегают игрока

Управление:
- WASD/Стрелки - движение
- E - взаимодействие с NPC
- ESC/P - меню паузы

Нажмите E для взаимодействия с NPC!
        """
        about_popup = Popup(
            title='Об игре',
            content=Label(text=about_text, font_size='20sp'),  # Увеличили шрифт
            size_hint=(0.8, 0.7)  # Увеличили попап для планшета
        )
        about_popup.open()
    
    def exit_game(self, instance):
        App.get_running_app().stop()

class SettingsPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Настройки'
        self.size_hint = (0.8, 0.6)  # Увеличили для планшета
        
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)  # Увеличили отступы
        
        # Настройка количества NPC
        npc_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        npc_layout.add_widget(Label(text='Количество NPC:', font_size='24sp'))  # Увеличили шрифт
        self.npc_slider_label = Label(text='6', font_size='24sp')  # Увеличили шрифт
        npc_layout.add_widget(self.npc_slider_label)
        layout.add_widget(npc_layout)
        
        # Настройка сложности
        difficulty_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        difficulty_layout.add_widget(Label(text='Сложность:', font_size='24sp'))  # Увеличили шрифт
        self.difficulty_label = Label(text='Нормальная', font_size='24sp')  # Увеличили шрифт
        difficulty_layout.add_widget(self.difficulty_label)
        layout.add_widget(difficulty_layout)
        
        # Кнопки
        buttons_layout = BoxLayout(orientation='horizontal', spacing=15, size_hint=(1, 0.4))
        
        save_button = Button(
            text='Сохранить',
            font_size='24sp',  # Увеличили шрифт
            background_color=(0.2, 0.6, 0.2, 1)
        )
        save_button.bind(on_press=self.save_settings)
        
        cancel_button = Button(
            text='Отмена',
            font_size='24sp',  # Увеличили шрифт
            background_color=(0.8, 0.2, 0.2, 1)
        )
        cancel_button.bind(on_press=self.dismiss)
        
        buttons_layout.add_widget(save_button)
        buttons_layout.add_widget(cancel_button)
        
        layout.add_widget(buttons_layout)
        
        self.content = layout
    
    def save_settings(self, instance):
        # Здесь можно сохранить настройки
        self.dismiss()

class PauseMenu(BoxLayout):
    def __init__(self, game_screen, **kwargs):
        super().__init__(**kwargs)
        self.game_screen = game_screen
        self.orientation = 'vertical'
        self.padding = 60  # Увеличили отступы
        self.spacing = 25  # Увеличили промежутки
        self.size_hint = (0.7, 0.8)  # Увеличили для планшета
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        # Заголовок
        title = Label(
            text='Пауза',
            font_size='40sp',  # Увеличили шрифт
            bold=True,
            size_hint=(1, 0.2)
        )
        
        # Кнопки
        resume_button = Button(
            text='Продолжить',
            font_size='28sp',  # Увеличили шрифт
            background_color=(0.2, 0.6, 0.2, 1),
            size_hint=(1, 0.2)
        )
        resume_button.bind(on_press=self.resume_game)
        
        restart_button = Button(
            text='Начать заново',
            font_size='28sp',  # Увеличили шрифт
            background_color=(0.2, 0.5, 0.8, 1),
            size_hint=(1, 0.2)
        )
        restart_button.bind(on_press=self.restart_game)
        
        menu_button = Button(
            text='В главное меню',
            font_size='28sp',  # Увеличили шрифт
            background_color=(0.8, 0.5, 0.2, 1),
            size_hint=(1, 0.2)
        )
        menu_button.bind(on_press=self.to_main_menu)
        
        # Кнопка Назад
        back_button = Button(
            text='Назад',
            font_size='28sp',  # Увеличили шрифт
            background_color=(0.5, 0.5, 0.5, 1),
            size_hint=(1, 0.2)
        )
        back_button.bind(on_press=self.back_to_game)
        
        exit_button = Button(
            text='Выход',
            font_size='28sp',  # Увеличили шрифт
            background_color=(0.8, 0.2, 0.2, 1),
            size_hint=(1, 0.2)
        )
        exit_button.bind(on_press=self.exit_game)
        
        self.add_widget(title)
        self.add_widget(resume_button)
        self.add_widget(restart_button)
        self.add_widget(menu_button)
        self.add_widget(back_button)
        self.add_widget(exit_button)
    
    def resume_game(self, instance):
        self.game_screen.hide_pause_menu()
    
    def restart_game(self, instance):
        self.game_screen.restart_game()
    
    def to_main_menu(self, instance):
        self.game_screen.to_main_menu()
    
    def back_to_game(self, instance):
        """Вернуться в игру (альтернатива кнопке Продолжить)"""
        self.game_screen.hide_pause_menu()
    
    def exit_game(self, instance):
        App.get_running_app().stop()

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_widget = GameWidget()
        self.game_widget.game_screen = self
        self.add_widget(self.game_widget)
        
        # Добавляем виджет перехода
        self.fade_transition = FadeTransitionWidget()
        self.add_widget(self.fade_transition)
        
        # Отрисовка затемнения
        with self.fade_transition.canvas:
            Color(0, 0, 0, self.fade_transition.alpha)
            self.fade_rect = Rectangle(pos=(0, 0), size=Window.size)
        
        # Связываем свойство alpha с обновлением цвета
        self.fade_transition.bind(alpha=self.update_fade_color)
        
        self.pause_menu = None
        self.is_paused = False
        
        # Обновляем размер при изменении окна
        Window.bind(on_resize=self.on_window_resize)
    
    def on_window_resize(self, window, width, height):
        """Обновление UI при изменении размера окна"""
        self.update_fade_color(None, self.fade_transition.alpha)
    
    def update_fade_color(self, instance, value):
        """Обновление цвета затемнения"""
        with self.fade_transition.canvas:
            self.fade_transition.canvas.clear()
            Color(0, 0, 0, value)
            Rectangle(pos=(0, 0), size=Window.size)
    
    def show_pause_menu(self):
        if not self.is_paused:
            self.is_paused = True
            self.pause_menu = PauseMenu(self)
            self.add_widget(self.pause_menu)
            self.game_widget.pause_game()
    
    def hide_pause_menu(self):
        if self.is_paused:
            self.is_paused = False
            if self.pause_menu:
                self.remove_widget(self.pause_menu)
                self.pause_menu = None
            self.game_widget.resume_game()
    
    def restart_game(self):
        self.hide_pause_menu()
        self.remove_widget(self.game_widget)
        self.game_widget = GameWidget()
        self.game_widget.game_screen = self
        self.add_widget(self.game_widget)
    
    def to_main_menu(self):
        self.hide_pause_menu()
        # Запускаем затемнение перед переходом в меню
        self.fade_transition.start_fade_in(self.switch_to_menu)
    
    def switch_to_menu(self):
        # Переключаемся на меню после завершения затемнения
        self.manager.current = 'menu'
        # Запускаем осветление на экране меню
        menu_screen = self.manager.get_screen('menu')
        menu_screen.fade_transition.alpha = 1
        menu_screen.fade_transition.start_fade_out()

# Остальной код остается без изменений
class DialogueSystem:
    def __init__(self):
        # Более разнообразные диалоги для каждого типа поведения
        self.dialogues = {
            "wander": [
                "Привет! Как дела?",
                "Прекрасный день для прогулки!",
                "Вы не видели моего кота?",
                "Здесь так красиво...",
                "Интересно, что там впереди?",
                "Я заблудился? Нет, наверное...",
                "Какой чудесный ветерок!",
                "Надо бы найти место для отдыха",
                "Куда же все спешат?",
                "О, смотрите-ка, бабочка!",
                "Как хорошо здесь пахнет!",
                "Интересно, сколько времени?",
                "Надеюсь, не заблудиться...",
                "Какие красивые облака!",
                "Хочу найти что-нибудь интересное",
                "Здесь так тихо и спокойно",
                "Интересно, что за история у этого места?",
                "Надо бы пообщаться с кем-нибудь",
                "Какой прекрасный пейзаж!",
                "Хорошо бы найти источник воды"
            ],
            "patrol": [
                "Все спокойно на моем участке",
                "Патруль идет по плану",
                "Ничего подозрительного не вижу",
                "Доложите обстановку!",
                "Следую контрольной точке",
                "Оставаться настороже!",
                "Проверяю периметр",
                "Все в порядке, продолжаю обход",
                "Вижу нарушителя! Ой, это птица...",
                "Смена скоро подойдет",
                "Проверяю восточный сектор",
                "Западный сектор чист",
                "Южная зона под контролем",
                "Докладываю: все нормально",
                "Проверяю темные уголки",
                "Никаких нарушений не обнаружено",
                "Продолжаю наблюдение",
                "Все входы и выходы под контролем",
                "Отмечаюсь на контрольной точке",
                "Перехожу к следующему участку"
            ],
            "follow": [
                "Эй, подожди меня!",
                "Куда ты идешь?",
                "Можно я с тобой?",
                "Ты выглядишь интересным человеком",
                "Расскажешь что-нибудь?",
                "Я последую за тобой",
                "Не уходи так быстро!",
                "У тебя есть планы на сегодня?",
                "Мне скучно одному...",
                "Давай будем друзьями!",
                "Ты кажешься таким интересным!",
                "Можно я составлю тебе компанию?",
                "Куда мы идем?",
                "Расскажи о себе!",
                "У тебя есть интересные истории?",
                "Я всегда ищу новых друзей",
                "Твоя походка такая уверенная!",
                "Мне нравится твой стиль",
                "Давай вместе исследуем это место!",
                "Ты выглядишь как приключение!"
            ],
            "flee": [
                "Ой, не подходи!",
                "Помогите! Кто-нибудь!",
                "Я просто проходил мимо!",
                "Не трогай меня!",
                "Убирайся отсюда!",
                "Сейчас позову помощь!",
                "Отстань!",
                "Я никому не нужен!",
                "Лучше я пойду...",
                "Ой-ой-ой, беда!",
                "Не приближайся!",
                "Я вызову стражу!",
                "Помогите, нападают!",
                "Я ничего плохого не сделал!",
                "Отойди, пожалуйста!",
                "Мне страшно!",
                "Я просто маленький NPC!",
                "Не ешь меня!",
                "У меня нет денег!",
                "Я сообщу властям!"
            ]
        }
        
        # Уникальные имена для NPC
        self.npc_names = {
            "wander": ["Странник", "Путник", "Мечтатель", "Философ", "Наблюдатель", 
                      "Искатель", "Скиталец", "Путешественник", "Прогульщик", "Фланирующий"],
            "patrol": ["Стражник", "Охранник", "Дозорный", "Патроль", "Караульный",
                      "Часовой", "Инспектор", "Надзиратель", "Контролер", "Обходчик"],
            "follow": ["Любопытный", "Общительный", "Дружелюбный", "Приставучий", "Компанейский",
                      "Общительный", "Привязчивый", "Социальный", "Коммуникабельный", "Дружеский"],
            "flee": ["Трусишка", "Пуганый", "Осторожный", "Робкий", "Боязливый",
                    "Испуганный", "Несмелый", "Опасливый", "Пугливый", "Тревожный"]
        }
        
        self.greetings = [
            "Здравствуйте!", "Приветствую!", "Добрый день!", "Привет!", 
            "Рад вас видеть!", "Здорово!", "Приветик!", "Салют!", 
            "Доброго времени суток!", "Мое почтение!"
        ]
        
        self.farewells = [
            "До свидания!", "Удачи!", "Будьте здоровы!", "Всего хорошего!", 
            "Пока!", "До встречи!", "Счастливо!", "Прощайте!", 
            "Всего доброго!", "Берегите себя!"
        ]
        
        # История уже использованных фраз для каждого NPC
        self.used_phrases = {}
    
    def get_random_dialogue(self, behavior_type, npc_id):
        """Получить случайную фразу, стараясь не повторяться"""
        if behavior_type not in self.dialogues:
            return "..."
        
        if npc_id not in self.used_phrases:
            self.used_phrases[npc_id] = []
        
        available_phrases = [p for p in self.dialogues[behavior_type] if p not in self.used_phrases[npc_id]]
        
        # Если все фразы использованы, очищаем историю
        if not available_phrases:
            self.used_phrases[npc_id] = []
            available_phrases = self.dialogues[behavior_type]
        
        chosen_phrase = random.choice(available_phrases)
        self.used_phrases[npc_id].append(chosen_phrase)
        
        # Ограничиваем историю последними 5 фразами
        if len(self.used_phrases[npc_id]) > 5:
            self.used_phrases[npc_id] = self.used_phrases[npc_id][-5:]
        
        return chosen_phrase
    
    def get_random_name(self, behavior_type):
        """Получить случайное имя для NPC"""
        if behavior_type in self.npc_names:
            return random.choice(self.npc_names[behavior_type])
        return "NPC"

class NPC:
    def __init__(self, x, y, size, behavior_type="wander", color=(0, 1, 0), name=None):
        self.x = x
        self.y = y
        self.size = size
        self.speed = random.uniform(1.5, 2.5)
        self.behavior_type = behavior_type
        self.color = color
        
        # Диалоговая система
        self.dialogue_system = DialogueSystem()
        self.npc_id = f"{behavior_type}_{random.randint(1000, 9999)}"
        
        # Если имя не указано, генерируем случайное
        if name is None:
            self.name = self.dialogue_system.get_random_name(behavior_type)
        else:
            self.name = name
            
        self.direction_timer = 0
        self.direction = random.uniform(0, 2 * math.pi)
        self.target_x = x
        self.target_y = y
        self.change_direction_interval = random.randint(90, 180)
        self.rect = None
        
        self.speech_timer = 0
        self.speech_cooldown = random.randint(300, 600)
        self.current_speech = ""
        self.speech_duration = 0
        self.can_speak = True
        
        # Взаимодействие с игроком
        self.near_player = False
        self.interaction_cooldown = 0
        
        # Плавное изменение направления
        self.target_direction = self.direction
        self.turn_speed = 0.1
        
        # Для патрулирования
        self.waypoints = []
        self.current_waypoint = 0
        self.waypoint_reach_distance = 15
        
        # Для следования за игроком
        self.follow_distance = 120
        self.follow_cooldown = 0
        
        # Для убегания
        self.flee_distance = 180
        self.flee_cooldown = 0
        
        # Переменные для плавного движения
        self.velocity_x = 0
        self.velocity_y = 0
        self.max_velocity = self.speed
        self.acceleration = 0.1
        self.friction = 0.15
        
        # Состояния
        self.is_moving = True
        self.pause_timer = 0
        self.pause_duration = 0
        
    def update(self, player_x, player_y, obstacles, npcs, dt):
        # Проверка расстояния до игрока
        distance_to_player = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)
        self.near_player = distance_to_player < 150
        
        # Обновляем таймеры
        self.direction_timer += 1
        if self.follow_cooldown > 0:
            self.follow_cooldown -= 1
        if self.flee_cooldown > 0:
            self.flee_cooldown -= 1
        if self.interaction_cooldown > 0:
            self.interaction_cooldown -= 1
        
        # Обработка речи - более частая для следящих NPC
        if self.can_speak:
            self.speech_timer += 1
            speak_chance = 0.01  # Базовая вероятность
            if self.behavior_type == "follow":
                speak_chance = 0.02  # Следящие NPC говорят чаще
            elif self.behavior_type == "flee":
                speak_chance = 0.015  # Убегающие тоже чаще
            
            if self.speech_timer >= self.speech_cooldown and random.random() < speak_chance:
                self.speak_random()
            
            if self.current_speech and self.speech_duration > 0:
                self.speech_duration -= 1
                if self.speech_duration <= 0:
                    self.current_speech = ""
        
        # Обработка пауз в движении
        if self.pause_timer > 0:
            self.pause_timer -= 1
            self.is_moving = False
            if self.pause_timer <= 0:
                self.is_moving = True
                self.pause_duration = random.randint(30, 120)
        else:
            if random.random() < 0.002 and self.is_moving:
                self.pause_timer = random.randint(60, 180)
                self.is_moving = False
        
        if self.is_moving:
            if self.behavior_type == "wander":
                self.wander_behavior()
            elif self.behavior_type == "patrol":
                self.patrol_behavior()
            elif self.behavior_type == "follow":
                self.follow_behavior(player_x, player_y)
            elif self.behavior_type == "flee":
                self.flee_behavior(player_x, player_y)
            
            # Плавное изменение направления
            angle_diff = (self.target_direction - self.direction) % (2 * math.pi)
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            
            self.direction += angle_diff * self.turn_speed
            
            # Плавное ускорение и замедление
            target_vx = math.cos(self.direction) * self.speed
            target_vy = math.sin(self.direction) * self.speed
            
            self.velocity_x += (target_vx - self.velocity_x) * self.acceleration
            self.velocity_y += (target_vy - self.velocity_y) * self.acceleration
            
            # Применение трения при резких поворотах
            speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            if speed > self.max_velocity:
                self.velocity_x *= 0.95
                self.velocity_y *= 0.95
        
        else:
            # Плавная остановка во время паузы
            self.velocity_x *= 0.8
            self.velocity_y *= 0.8
        
        # Сохраняем старую позицию для отката при столкновения
        old_x, old_y = self.x, self.y
        
        # Двигаем NPC с плавной скоростью
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Проверка границ карты
        self.x = max(self.size/2, min(self.x, 2000 - self.size/2))
        self.y = max(self.size/2, min(self.y, 2000 - self.size/2))
        
        # Проверка столкновений с препятствиями
        npc_rect = {'x': self.x - self.size/2, 'y': self.y - self.size/2, 'width': self.size, 'height': self.size}
        collision_occurred = False
        
        for obstacle in obstacles:
            if self.check_collision(npc_rect, obstacle, min_distance=5):  # Добавляем минимальную дистанцию
                collision_occurred = True
                break
        
        # Проверка столкновений с другими NPC
        for other_npc in npcs:
            if other_npc != self:
                distance = math.sqrt((self.x - other_npc.x)**2 + (self.y - other_npc.y)**2)
                min_distance = (self.size + other_npc.size) / 2 + 10  # Минимальная дистанция между NPC
                if distance < min_distance:
                    # Отталкиваемся от другого NPC
                    angle = math.atan2(self.y - other_npc.y, self.x - other_npc.x)
                    push_force = (min_distance - distance) / min_distance
                    self.velocity_x += math.cos(angle) * push_force * 2
                    self.velocity_y += math.sin(angle) * push_force * 2
                    collision_occurred = True
        
        if collision_occurred:
            self.x, self.y = old_x, old_y
            self.target_direction = random.uniform(0, 2 * math.pi)
            self.velocity_x *= -0.5
            self.velocity_y *= -0.5
    
    def speak_random(self):
        """Произнести случайную фразу"""
        if not self.current_speech:
            self.current_speech = self.dialogue_system.get_random_dialogue(self.behavior_type, self.npc_id)
            self.speech_duration = random.randint(150, 250)  # Разная длительность
            self.speech_timer = 0
            self.speech_cooldown = random.randint(200, 500)  # Разный коолдаун
    
    def interact(self):
        """Взаимодействие с игроком"""
        if self.interaction_cooldown <= 0:
            greeting = random.choice(self.dialogue_system.greetings)
            dialogue = self.dialogue_system.get_random_dialogue(self.behavior_type, self.npc_id)
            self.current_speech = f"{greeting} {dialogue}"
            self.speech_duration = 300
            self.interaction_cooldown = 600
            return True
        return False

    def wander_behavior(self):
        if self.direction_timer >= self.change_direction_interval:
            self.target_direction = random.uniform(0, 2 * math.pi)
            self.direction_timer = 0
            self.change_direction_interval = random.randint(120, 300)
            
            if random.random() < 0.3:
                self.target_direction += random.uniform(-0.5, 0.5)

    def patrol_behavior(self):
        if not self.waypoints:
            start_x, start_y = self.x, self.y
            for _ in range(4):
                self.waypoints.append((
                    start_x + random.uniform(-200, 200),
                    start_y + random.uniform(-200, 200)
                ))
        
        target_x, target_y = self.waypoints[self.current_waypoint]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.waypoint_reach_distance:
            self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)
            self.pause_timer = random.randint(30, 90)
        else:
            self.target_direction = math.atan2(dy, dx)
            
            if random.random() < 0.05:
                self.target_direction += random.uniform(-0.3, 0.3)

    def follow_behavior(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > self.follow_distance + 50:
            self.target_direction = math.atan2(dy, dx)
            self.speed = 2.5
        elif distance > self.follow_distance:
            self.target_direction = math.atan2(dy, dx)
            self.speed = 1.5
            if random.random() < 0.1:
                self.target_direction += random.uniform(-0.4, 0.4)
        else:
            self.speed = 0.8
            if random.random() < 0.02:
                self.target_direction = random.uniform(0, 2 * math.pi)

    def flee_behavior(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.flee_distance:
            self.target_direction = math.atan2(-dy, -dx)
            self.speed = 3.0
            
            if random.random() < 0.2:
                self.target_direction += random.uniform(-0.8, 0.8)
        else:
            self.speed = 2.0
            self.wander_behavior()
    
    def check_collision(self, rect1, rect2, min_distance=0):
        """Проверка столкновения с минимальной дистанцией"""
        return (rect1['x'] - min_distance < rect2['x'] + rect2['width'] and
                rect1['x'] + rect1['width'] + min_distance > rect2['x'] and
                rect1['y'] - min_distance < rect2['y'] + rect2['height'] and
                rect1['y'] + rect1['height'] + min_distance > rect2['y'])

class SpeechBubble:
    def __init__(self, npc, text):
        self.npc = npc
        self.text = text
        self.duration = 180
        self.bg_rect = None
        self.text_label = None
        
    def create_graphics(self, parent_widget, camera_x, camera_y):
        # Создаем фон диалога на canvas
        with parent_widget.canvas:
            Color(0, 0, 0, 0.8)
            self.bg_rect = Rectangle(
                pos=(self.npc.x - camera_x - 120, self.npc.y - camera_y + 40),
                size=(240, 40)
            )
        
        # Создаем текстовую метку как виджет
        self.text_label = Label(
            text=self.text,
            size=(230, 30),
            size_hint=(None, None),
            color=(1, 1, 1, 1),
            bold=True
        )
        parent_widget.add_widget(self.text_label)
    
    def update_position(self, camera_x, camera_y):
        if self.bg_rect:
            self.bg_rect.pos = (self.npc.x - camera_x - 120, self.npc.y - camera_y + 40)
        
        if self.text_label:
            self.text_label.pos = (self.npc.x - camera_x - 115, self.npc.y - camera_y + 45)
            self.text_label.text_size = (230, 30)
    
    def remove(self, parent_widget):
        if self.bg_rect:
            parent_widget.canvas.remove(self.bg_rect)
        
        if self.text_label and self.text_label in parent_widget.children:
            parent_widget.remove_widget(self.text_label)

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Параметры игрока
        self.player_size = 50
        self.player_x = 400
        self.player_y = 300
        self.player_speed = 5
        
        # Параметры карты
        self.map_width, self.map_height = 2000, 2000
        
        # Камера
        self.camera_x, self.camera_y = 0, 0
        
        # NPC
        self.npcs = []
        
        # Текстура пола
        self.floor_texture = None
        self.floor_tile_size = 256  # Размер тайла текстуры пола
        self.floor_rects = []  # Список прямоугольников пола
        
        # Генерация карты
        self.obstacles = []
        self.generate_map()
        
        # Генерация NPC после карты, чтобы избежать пересечений
        self.generate_npcs()
        
        # Нажатые клавиши
        self.keys_pressed = set()
        
        # Система диалогов
        self.active_speech_bubble = None
        
        # Ссылка на игровой экран
        self.game_screen = None
        
        # Создание графических элементов
        self.create_graphics()
        
        # Обновление игры
        self.game_clock = Clock.schedule_interval(self.update, 1.0/60.0)
        
        # Обработка клавиатуры
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)
    
    def pause_game(self):
        """Приостановить игру"""
        self.game_clock.cancel()
    
    def resume_game(self):
        """Возобновить игру"""
        self.game_clock = Clock.schedule_interval(self.update, 1.0/60.0)
    
    def is_position_valid(self, x, y, width, height, object_type="obstacle"):
        """Проверяет, можно ли разместить объект в данной позиции"""
        # Проверка границ карты
        if x < 0 or y < 0 or x + width > self.map_width or y + height > self.map_height:
            return False
        
        # Проверка расстояния до игрока
        player_distance = math.sqrt((x - self.player_x)**2 + (y - self.player_y)**2)
        if player_distance < 200:  # Минимальная дистанция от игрока
            return False
        
        # Проверка столкновений с существующими препятствиями
        new_rect = {'x': x, 'y': y, 'width': width, 'height': height}
        for obstacle in self.obstacles:
            if self.check_rect_collision(new_rect, obstacle, min_distance=20):  # Исправлено на check_rect_collision
                return False
        
        # Для NPC дополнительно проверяем расстояние до других NPC
        if object_type == "npc":
            for npc in self.npcs:
                distance = math.sqrt((x - npc.x)**2 + (y - npc.y)**2)
                if distance < 80:  # Минимальная дистанция между NPC
                    return False
        
        return True
    
    def generate_npcs(self):
        """Генерация NPC с разным поведением и уникальными именами"""
        behaviors = [
            ("wander", (0.2, 0.8, 0.2)),
            ("patrol", (0.9, 0.8, 0.1)),
            ("follow", (0.9, 0.5, 0.1)),
            ("flee", (0.6, 0.2, 0.8)),
            ("wander", (0.2, 0.7, 0.8)),
            ("patrol", (0.8, 0.3, 0.8)),
        ]
        
        for behavior, color in behaviors:
            # Пытаемся найти валидную позицию для NPC
            attempts = 0
            while attempts < 100:  # Ограничиваем количество попыток
                x = random.randint(100, self.map_width - 100)
                y = random.randint(100, self.map_height - 100)
                size = random.randint(25, 35)
                
                if self.is_position_valid(x - size/2, y - size/2, size, size, "npc"):
                    npc = NPC(x, y, size, behavior, color)
                    self.npcs.append(npc)
                    break
                attempts += 1
    
    def generate_map(self):
        """Генерация процедурной карты с препятствиями, которые не пересекаются"""
        self.obstacles = []
        
        # 1. Случайные прямоугольные препятствия
        for _ in range(25):
            attempts = 0
            while attempts < 50:  # Ограничиваем попытки генерации
                width = random.randint(40, 120)
                height = random.randint(40, 120)
                x = random.randint(0, self.map_width - width)
                y = random.randint(0, self.map_height - height)
                
                if self.is_position_valid(x, y, width, height):
                    self.obstacles.append({
                        'x': x, 'y': y, 'width': width, 'height': height,
                        'type': 'rectangle', 'color': (0.2, 0.4, 0.8)
                    })
                    break
                attempts += 1
        
        # 2. Более естественные стены
        for _ in range(8):
            attempts = 0
            while attempts < 50:
                if random.random() > 0.5:
                    width = random.randint(150, 400)
                    height = random.randint(15, 30)
                    x = random.randint(0, self.map_width - width)
                    y = random.randint(0, self.map_height - height)
                else:
                    width = random.randint(15, 30)
                    height = random.randint(150, 400)
                    x = random.randint(0, self.map_width - width)
                    y = random.randint(0, self.map_height - height)
                
                if self.is_position_valid(x, y, width, height):
                    self.obstacles.append({
                        'x': x, 'y': y, 'width': width, 'height': height,
                        'type': 'wall', 'color': (0.4, 0.4, 0.4)
                    })
                    break
                attempts += 1
        
        # 3. Круги
        for _ in range(12):
            attempts = 0
            while attempts < 50:
                size = random.randint(35, 80)
                x = random.randint(0, self.map_width - size)
                y = random.randint(0, self.map_height - size)
                
                if self.is_position_valid(x, y, size, size):
                    self.obstacles.append({
                        'x': x, 'y': y, 'width': size, 'height': size,
                        'type': 'circle', 'color': (0.8, 0.2, 0.2),
                        'radius': size / 2
                    })
                    break
                attempts += 1
        
        # 4. Комнаты с проходами
        self.create_rooms(3)

    def create_rooms(self, num_rooms):
        for _ in range(num_rooms):
            attempts = 0
            while attempts < 30:
                room_width = random.randint(250, 500)
                room_height = random.randint(250, 500)
                room_x = random.randint(100, self.map_width - room_width - 100)
                room_y = random.randint(100, self.map_height - room_height - 100)
                
                # Проверяем, можно ли разместить комнату
                room_valid = True
                room_rect = {'x': room_x, 'y': room_y, 'width': room_width, 'height': room_height}
                
                for obstacle in self.obstacles:
                    if self.check_rect_collision(room_rect, obstacle, min_distance=30):  # Исправлено на check_rect_collision
                        room_valid = False
                        break
                
                if room_valid:
                    wall_thickness = 15
                    
                    # Создаем стены комнаты только если они не пересекаются с другими объектами
                    walls = []
                    
                    # Верхняя стена
                    top_wall = {'x': room_x, 'y': room_y + room_height - wall_thickness, 
                               'width': room_width, 'height': wall_thickness}
                    if random.random() > 0.3 and self.is_position_valid(**top_wall):
                        walls.append({**top_wall, 'type': 'wall', 'color': (0.5, 0.3, 0.1)})
                    
                    # Нижняя стена
                    bottom_wall = {'x': room_x, 'y': room_y, 
                                  'width': room_width, 'height': wall_thickness}
                    if random.random() > 0.3 and self.is_position_valid(**bottom_wall):
                        walls.append({**bottom_wall, 'type': 'wall', 'color': (0.5, 0.3, 0.1)})
                    
                    # Левая стена
                    left_wall = {'x': room_x, 'y': room_y, 
                                'width': wall_thickness, 'height': room_height}
                    if random.random() > 0.3 and self.is_position_valid(**left_wall):
                        walls.append({**left_wall, 'type': 'wall', 'color': (0.5, 0.3, 0.1)})
                    
                    # Правая стена
                    right_wall = {'x': room_x + room_width - wall_thickness, 'y': room_y, 
                                 'width': wall_thickness, 'height': room_height}
                    if random.random() > 0.3 and self.is_position_valid(**right_wall):
                        walls.append({**right_wall, 'type': 'wall', 'color': (0.5, 0.3, 0.1)})
                    
                    # Добавляем стены комнаты
                    self.obstacles.extend(walls)
                    break
                
                attempts += 1

    def create_graphics(self):
        with self.canvas:
            # Сначала рисуем пол
            self.create_floor()
            
            # Затем препятствия
            self.obstacle_rects = []
            for obstacle in self.obstacles:
                Color(*obstacle['color'])
                if obstacle['type'] == 'circle':
                    rect = Ellipse(
                        pos=(obstacle['x'] - self.camera_x, obstacle['y'] - self.camera_y),
                        size=(obstacle['width'], obstacle['height'])
                    )
                else:
                    rect = Rectangle(
                        pos=(obstacle['x'] - self.camera_x, obstacle['y'] - self.camera_y),
                        size=(obstacle['width'], obstacle['height'])
                    )
                self.obstacle_rects.append(rect)
            
            # Затем NPC
            self.npc_rects = []
            for npc in self.npcs:
                Color(*npc.color)
                rect = Ellipse(
                    pos=(npc.x - self.camera_x - npc.size/2, 
                         npc.y - self.camera_y - npc.size/2),
                    size=(npc.size, npc.size)
                )
                npc.rect = rect
                self.npc_rects.append(rect)
            
            # Игрок рисуется поверх всего
            Color(1, 0, 0)
            self.player_rect = Ellipse(
                pos=(self.player_x - self.camera_x - self.player_size/2, 
                     self.player_y - self.camera_y - self.player_size/2),
                size=(self.player_size, self.player_size)
            )

    def create_floor(self):
        """Создание текстуры пола"""
        try:
            # Пытаемся загрузить текстуру пола
            from kivy.core.image import Image as CoreImage
            self.floor_texture = CoreImage("floor.png").texture
            self.floor_texture.wrap = 'repeat'
        except:
            # Если текстура не найдена, используем простой цвет
            self.floor_texture = None
            print("Текстура floor.png не найдена. Используется цветной пол.")
        
        # Создаем тайлы пола
        self.floor_rects = []
        tile_size = self.floor_tile_size
        
        # Вычисляем количество тайлов по горизонтали и вертикали
        num_tiles_x = math.ceil(self.map_width / tile_size)
        num_tiles_y = math.ceil(self.map_height / tile_size)
        
        with self.canvas:
            if self.floor_texture:
                # Используем текстуру
                for x in range(num_tiles_x):
                    for y in range(num_tiles_y):
                        rect = Rectangle(
                            texture=self.floor_texture,
                            pos=(x * tile_size - self.camera_x, y * tile_size - self.camera_y),
                            size=(tile_size, tile_size)
                        )
                        self.floor_rects.append(rect)
            else:
                # Используем цветной пол
                Color(0.3, 0.3, 0.3, 1)
                for x in range(num_tiles_x):
                    for y in range(num_tiles_y):
                        # Чередуем цвета для создания шахматного паттерна
                        if (x + y) % 2 == 0:
                            Color(0.4, 0.4, 0.4, 1)
                        else:
                            Color(0.35, 0.35, 0.35, 1)
                        
                        rect = Rectangle(
                            pos=(x * tile_size - self.camera_x, y * tile_size - self.camera_y),
                            size=(tile_size, tile_size)
                        )
                        self.floor_rects.append(rect)

    def show_speech_bubble(self, npc, text):
        """Показать диалог над NPC"""
        if self.active_speech_bubble:
            self.active_speech_bubble.remove(self)
        
        speech_bubble = SpeechBubble(npc, text)
        speech_bubble.create_graphics(self, self.camera_x, self.camera_y)
        self.active_speech_bubble = speech_bubble

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.keys_pressed.add(keycode[1])
        
        if keycode[1] == 'e':
            self.interact_with_npc()
        
        # Пауза по клавише ESC или P
        if keycode[1] in ['escape', 'p']:
            if self.game_screen:
                self.game_screen.show_pause_menu()
        
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        if keycode[1] in self.keys_pressed:
            self.keys_pressed.remove(keycode[1])
        return True

    def interact_with_npc(self):
        """Взаимодействие с ближайшим NPC"""
        closest_npc = None
        min_distance = float('inf')
        
        for npc in self.npcs:
            distance = math.sqrt((npc.x - self.player_x)**2 + (npc.y - self.player_y)**2)
            if distance < 100 and distance < min_distance:
                closest_npc = npc
                min_distance = distance
        
        if closest_npc:
            closest_npc.interact()
            self.show_speech_bubble(closest_npc, f"{closest_npc.name}: {closest_npc.current_speech}")

    def update(self, dt):
        # Движение игрока
        new_x, new_y = self.player_x, self.player_y
        
        if 'w' in self.keys_pressed or 'up' in self.keys_pressed:
            new_y += self.player_speed
        if 's' in self.keys_pressed or 'down' in self.keys_pressed:
            new_y -= self.player_speed
        if 'a' in self.keys_pressed or 'left' in self.keys_pressed:
            new_x -= self.player_speed
        if 'd' in self.keys_pressed or 'right' in self.keys_pressed:
            new_x += self.player_speed
        
        # Проверка границ и столкновений для игрока
        if 0 <= new_x <= self.map_width - self.player_size and 0 <= new_y <= self.map_height - self.player_size:
            collision = False
            player_rect = {
                'x': new_x - self.player_size/2, 
                'y': new_y - self.player_size/2, 
                'width': self.player_size, 
                'height': self.player_size
            }
            
            for obstacle in self.obstacles:
                if obstacle['type'] == 'circle':
                    if self.check_circle_collision(player_rect, obstacle, min_distance=5):
                        collision = True
                        break
                else:
                    if self.check_rect_collision(player_rect, obstacle, min_distance=5):
                        collision = True
                        break
            
            if not collision:
                self.player_x, self.player_y = new_x, new_y
        
        # Обновление NPC
        for npc in self.npcs:
            npc.update(self.player_x, self.player_y, self.obstacles, self.npcs, dt)
            
            # Показ диалогов при случайной речи
            if npc.current_speech and npc.speech_duration > 0 and not self.active_speech_bubble:
                self.show_speech_bubble(npc, f"{npc.name}: {npc.current_speech}")
        
        # Обновление камеры
        self.camera_x = self.player_x - Window.width // 2
        self.camera_y = self.player_y - Window.height // 2
        
        self.camera_x = max(0, min(self.camera_x, self.map_width - Window.width))
        self.camera_y = max(0, min(self.camera_y, self.map_height - Window.height))
        
        # Обновление позиций графических элементов
        # Сначала обновляем пол
        self.update_floor()
        
        # Затем препятствия
        for i, obstacle in enumerate(self.obstacles):
            self.obstacle_rects[i].pos = (obstacle['x'] - self.camera_x, obstacle['y'] - self.camera_y)
        
        # Затем NPC
        for npc in self.npcs:
            if npc.rect:
                npc.rect.pos = (npc.x - self.camera_x - npc.size/2, 
                               npc.y - self.camera_y - npc.size/2)
        
        # Игрок
        self.player_rect.pos = (self.player_x - self.camera_x - self.player_size/2, 
                               self.player_y - self.camera_y - self.player_size/2)
        
        # Обновление позиции диалога
        if self.active_speech_bubble:
            self.active_speech_bubble.update_position(self.camera_x, self.camera_y)
            
            self.active_speech_bubble.duration -= 1
            if self.active_speech_bubble.duration <= 0:
                self.active_speech_bubble.remove(self)
                self.active_speech_bubble = None

    def update_floor(self):
        """Обновление позиции тайлов пола"""
        tile_size = self.floor_tile_size
        
        # Вычисляем количество тайлов по горизонтали и вертикали
        num_tiles_x = math.ceil(self.map_width / tile_size)
        num_tiles_y = math.ceil(self.map_height / tile_size)
        
        # Обновляем позиции всех тайлов пола
        for i, rect in enumerate(self.floor_rects):
            x_index = i % num_tiles_x
            y_index = i // num_tiles_x
            
            rect.pos = (x_index * tile_size - self.camera_x, 
                       y_index * tile_size - self.camera_y)

    def check_rect_collision(self, rect1, rect2, min_distance=0):
        """Проверка столкновения с минимальной дистанцией"""
        return (rect1['x'] - min_distance < rect2['x'] + rect2['width'] and
                rect1['x'] + rect1['width'] + min_distance > rect2['x'] and
                rect1['y'] - min_distance < rect2['y'] + rect2['height'] and
                rect1['y'] + rect1['height'] + min_distance > rect2['y'])

    def check_circle_collision(self, rect, circle, min_distance=0):
        """Проверка столкновения круга с прямоугольником с минимальной дистанцией"""
        closest_x = max(rect['x'], min(circle['x'] + circle['width']/2, rect['x'] + rect['width']))
        closest_y = max(rect['y'], min(circle['y'] + circle['height']/2, rect['y'] + rect['height']))
        
        distance_x = circle['x'] + circle['width']/2 - closest_x
        distance_y = circle['y'] + circle['height']/2 - closest_y
        
        collision_distance = circle['radius'] + min_distance
        return (distance_x * distance_x + distance_y * distance_y) <= (collision_distance * collision_distance)

class GameApp(App):
    def build(self):
        # Создаем менеджер экранов с плавным переходом
        sm = ScreenManager(transition=FadeTransition(duration=0.3))
        
        # Создаем экраны
        menu_screen = MenuScreen(name='menu')
        game_screen = GameScreen(name='game')
        
        # Добавляем экраны в менеджер
        sm.add_widget(menu_screen)
        sm.add_widget(game_screen)
        
        # Устанавливаем начальный экран
        sm.current = 'menu'
        
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        return sm

if __name__ == '__main__':
    GameApp().run()
