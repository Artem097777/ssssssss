import sys
import os
import math
import random
import datetime
import platform
import socket
import threading
import json
import hashlib
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.config import Config

# Настройка темной темы
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '700')
Window.clearcolor = (0.1, 0.1, 0.1, 1)

class UserManager:
    def __init__(self):
        self.users_file = "users.json"
        self.current_user = None
        self.users = self.load_users()
        
    def load_users(self):
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Ошибка загрузки пользователей: {e}")
            return {}
            
    def save_users(self):
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения пользователей: {e}")
            return False
            
    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
        
    def register_user(self, username, password, email=""):
        if username in self.users:
            return False, "Пользователь с таким именем уже существует"
            
        if len(username) < 3:
            return False, "Имя пользователя должно быть не менее 3 символов"
            
        if len(password) < 4:
            return False, "Пароль должен быть не менее 4 символов"
            
        user_id = len(self.users) + 1
        registration_date = datetime.datetime.now().isoformat()
        
        self.users[username] = {
            'id': user_id,
            'password_hash': self.hash_password(password),
            'email': email,
            'registration_date': registration_date,
            'last_login': None,
            'is_online': False,
            'profile': {
                'level': 1,
                'experience': 0,
                'messages_sent': 0,
                'commands_used': 0
            }
        }
        
        if self.save_users():
            return True, "Пользователь успешно зарегистрирован"
        else:
            return False, "Ошибка сохранения данных"
            
    def login_user(self, username, password):
        if username not in self.users:
            return False, "Пользователь не найден"
            
        stored_hash = self.users[username]['password_hash']
        input_hash = self.hash_password(password)
        
        if stored_hash == input_hash:
            self.current_user = username
            self.users[username]['last_login'] = datetime.datetime.now().isoformat()
            self.users[username]['is_online'] = True
            self.save_users()
            return True, f"Добро пожаловать, {username}!"
        else:
            return False, "Неверный пароль"
            
    def logout_user(self):
        if self.current_user and self.current_user in self.users:
            self.users[self.current_user]['is_online'] = False
        self.current_user = None
        self.save_users()
        
    def update_user_profile(self, field, value):
        if self.current_user and self.current_user in self.users:
            if field in self.users[self.current_user]['profile']:
                self.users[self.current_user]['profile'][field] = value
                self.save_users()
                return True
        return False
        
    def get_user_profile(self, username=None):
        if username is None:
            username = self.current_user
            
        if username and username in self.users:
            return self.users[username]
        return None
        
    def get_online_users(self):
        online_users = []
        for username, data in self.users.items():
            if data.get('is_online', False):
                online_users.append(username)
        return online_users

class LoginPopup(Popup):
    def __init__(self, console_app, **kwargs):
        super().__init__(**kwargs)
        self.console_app = console_app
        self.title = 'Вход / Регистрация'
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False
        
        self.create_ui()
        
    def create_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Вкладки
        self.tabs = TabbedPanel()
        
        # Вкладка входа
        login_tab = TabbedPanelItem(text='Вход')
        login_layout = BoxLayout(orientation='vertical', spacing=10)
        
        login_layout.add_widget(Label(text='Имя пользователя:', size_hint_y=None, height=30))
        self.login_username = TextInput(multiline=False, size_hint_y=None, height=40)
        login_layout.add_widget(self.login_username)
        
        login_layout.add_widget(Label(text='Пароль:', size_hint_y=None, height=30))
        self.login_password = TextInput(multiline=False, password=True, size_hint_y=None, height=40)
        login_layout.add_widget(self.login_password)
        
        self.login_btn = Button(text='Войти', size_hint_y=None, height=50)
        self.login_btn.bind(on_press=self.handle_login)
        login_layout.add_widget(self.login_btn)
        
        login_tab.add_widget(login_layout)
        
        # Вкладка регистрации
        register_tab = TabbedPanelItem(text='Регистрация')
        register_layout = BoxLayout(orientation='vertical', spacing=10)
        
        register_layout.add_widget(Label(text='Имя пользователя:', size_hint_y=None, height=30))
        self.reg_username = TextInput(multiline=False, size_hint_y=None, height=40)
        register_layout.add_widget(self.reg_username)
        
        register_layout.add_widget(Label(text='Пароль:', size_hint_y=None, height=30))
        self.reg_password = TextInput(multiline=False, password=True, size_hint_y=None, height=40)
        register_layout.add_widget(self.reg_password)
        
        register_layout.add_widget(Label(text='Email (необязательно):', size_hint_y=None, height=30))
        self.reg_email = TextInput(multiline=False, size_hint_y=None, height=40)
        register_layout.add_widget(self.reg_email)
        
        self.register_btn = Button(text='Зарегистрироваться', size_hint_y=None, height=50)
        self.register_btn.bind(on_press=self.handle_register)
        register_layout.add_widget(self.register_btn)
        
        register_tab.add_widget(register_layout)
        
        self.tabs.add_widget(login_tab)
        self.tabs.add_widget(register_tab)
        
        layout.add_widget(self.tabs)
        
        # Кнопка отмены
        cancel_btn = Button(text='Отмена', size_hint_y=None, height=50)
        cancel_btn.bind(on_press=self.dismiss)
        layout.add_widget(cancel_btn)
        
        self.content = layout
        
    def handle_login(self, instance):
        username = self.login_username.text.strip()
        password = self.login_password.text
        
        if not username or not password:
            self.show_error("Заполните все поля")
            return
            
        success, message = self.console_app.user_manager.login_user(username, password)
        if success:
            self.show_success(message)
            self.console_app.update_header()
            Clock.schedule_once(lambda dt: self.dismiss(), 1)
        else:
            self.show_error(message)
            
    def handle_register(self, instance):
        username = self.reg_username.text.strip()
        password = self.reg_password.text
        email = self.reg_email.text.strip()
        
        if not username or not password:
            self.show_error("Заполните обязательные поля")
            return
            
        success, message = self.console_app.user_manager.register_user(username, password, email)
        if success:
            self.show_success(message)
            # Автоматический вход после регистрации
            self.console_app.user_manager.login_user(username, password)
            self.console_app.update_header()
            Clock.schedule_once(lambda dt: self.dismiss(), 1)
        else:
            self.show_error(message)
            
    def show_error(self, message):
        popup = Popup(title='Ошибка', content=Label(text=message),
                     size_hint=(0.6, 0.4))
        popup.open()
        
    def show_success(self, message):
        popup = Popup(title='Успех', content=Label(text=message),
                     size_hint=(0.6, 0.4))
        popup.open()

class ProfilePopup(Popup):
    def __init__(self, console_app, **kwargs):
        super().__init__(**kwargs)
        self.console_app = console_app
        self.title = 'Профиль пользователя'
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = True
        
        self.create_ui()
        
    def create_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        user_info = self.console_app.user_manager.get_user_profile()
        if not user_info:
            layout.add_widget(Label(text="Ошибка загрузки профиля"))
            return
            
        # Основная информация
        info_text = f"""👤 Информация о профиле:

📛 Имя пользователя: {self.console_app.user_manager.current_user}
📧 Email: {user_info.get('email', 'Не указан')}
📅 Дата регистрации: {user_info.get('registration_date', 'Неизвестно')}
🕐 Последний вход: {user_info.get('last_login', 'Никогда')}

🎮 Статистика:
   🎯 Уровень: {user_info['profile']['level']}
   ⭐ Опыт: {user_info['profile']['experience']}
   📤 Сообщений отправлено: {user_info['profile']['messages_sent']}
   ⌨️ Команд использовано: {user_info['profile']['commands_used']}"""
        
        info_label = Label(text=info_text, size_hint_y=None, height=200,
                          text_size=(None, None), halign='left', valign='top')
        info_label.bind(size=lambda *x: setattr(info_label, 'text_size', (info_label.width, None)))
        layout.add_widget(info_label)
        
        # Список онлайн пользователей
        layout.add_widget(Label(text="👥 Пользователи онлайн:", size_hint_y=None, height=30))
        
        online_scroll = ScrollView()
        online_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        online_layout.bind(minimum_height=online_layout.setter('height'))
        
        online_users = self.console_app.user_manager.get_online_users()
        for user in online_users:
            online_layout.add_widget(Label(text=f"🟢 {user}", size_hint_y=None, height=30))
            
        if not online_users:
            online_layout.add_widget(Label(text="Нет пользователей онлайн", size_hint_y=None, height=30))
            
        online_scroll.add_widget(online_layout)
        layout.add_widget(online_scroll)
        
        # Кнопки
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        ok_btn = Button(text='OK')
        ok_btn.bind(on_press=lambda x: self.dismiss())
        
        logout_btn = Button(text='Выйти')
        logout_btn.bind(on_press=self.handle_logout)
        
        btn_layout.add_widget(ok_btn)
        btn_layout.add_widget(logout_btn)
        
        layout.add_widget(btn_layout)
        self.content = layout
        
    def handle_logout(self, instance):
        self.console_app.user_manager.logout_user()
        self.console_app.update_header()
        self.dismiss()

class ChatClient:
    def __init__(self, console_ref):
        self.console = console_ref
        self.socket = None
        self.connected = False
        self.receiving = False
        self.username = f"User{random.randint(1000, 9999)}"
        
    def connect_to_server(self, host, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            
            if self.console.user_manager.current_user:
                self.username = self.console.user_manager.current_user
            else:
                self.username = f"User{random.randint(1000, 9999)}"
                
            self.console.append_output(f"✅ Подключено к чат-серверу {host}:{port}\n", [0, 1, 0])
            self.console.append_output(f"💬 Ваш ник: {self.username}\n", [0, 1, 0])
            self.console.append_output("💡 Используйте 'send <сообщение>' для отправки или 'chat help' для помощи\n", [1, 1, 0])
            
            self.receiving = True
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            self.console.append_output(f"❌ Ошибка подключения: {e}\n", [1, 0, 0])
            return False
            
    def disconnect(self):
        self.connected = False
        self.receiving = False
        if self.socket:
            self.socket.close()
        self.console.append_output("🔌 Отключено от чат-сервера\n", [1, 0.65, 0])
        
    def send_message(self, message):
        if self.connected and self.socket:
            try:
                if self.console.user_manager.current_user:
                    current_stats = self.console.user_manager.get_user_profile()['profile']
                    self.console.user_manager.update_user_profile('messages_sent', current_stats['messages_sent'] + 1)
                
                full_message = f"{self.username}: {message}"
                self.socket.send(full_message.encode('utf-8'))
                self.console.append_output(f"📤 Вы: {message}\n", [0.53, 0.81, 0.92])
                return True
            except Exception as e:
                self.console.append_output(f"❌ Ошибка отправки: {e}\n", [1, 0, 0])
                return False
        else:
            self.console.append_output("❌ Не подключено к серверу. Используйте 'connect <ip> <port>'\n", [1, 0, 0])
            return False
        
    def receive_messages(self):
        while self.receiving and self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if data:
                    if not data.startswith(f"{self.username}:"):
                        # Используем Clock для безопасного обновления UI из другого потока
                        Clock.schedule_once(lambda dt: self.console.append_output(f"💬 {data}\n", [0.56, 0.93, 0.56]))
                else:
                    break
            except:
                if self.receiving:
                    Clock.schedule_once(lambda dt: self.console.append_output("❌ Соединение с сервером разорвано\n", [1, 0, 0]))
                break

class ConsoleApp(App):
    def __init__(self):
        super().__init__()
        self.command_history = []
        self.history_index = -1
        self.current_dir = os.getcwd()
        self.variables = {}
        self.user_manager = UserManager()
        self.chat_client = ChatClient(self)
        
    def build(self):
        self.title = 'Умная Консоль Kivy + Чат-команды + Система пользователей'
        
        # Основной layout
        main_layout = BoxLayout(orientation='vertical')
        
        # Заголовок
        self.header_label = Label(
            text='🚀 Умная Консоль | 🔓 Гостевой режим - используйте "login" для входа',
            size_hint_y=None,
            height=40,
            color=[0, 1, 0, 1],
            bold=True
        )
        main_layout.add_widget(self.header_label)
        
        # Область вывода с прокруткой
        output_scroll = ScrollView()
        self.output_text = TextInput(
            readonly=True,
            background_color=[0.12, 0.12, 0.12, 1],
            foreground_color=[1, 1, 1, 1],
            font_size=14,
            size_hint_y=None
        )
        # Убираем привязку высоты, которая может вызывать проблемы
        self.output_text.height = 400
        output_scroll.add_widget(self.output_text)
        main_layout.add_widget(output_scroll)
        
        # Панель ввода
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        
        input_label = Label(text='>>>', size_hint_x=None, width=40, color=[1, 1, 0, 1])
        self.input_field = TextInput(
            multiline=False,
            background_color=[0.18, 0.18, 0.18, 1],
            foreground_color=[1, 1, 1, 1],
            font_size=14
        )
        self.input_field.bind(on_text_validate=self.execute_command)
        
        run_btn = Button(
            text='Выполнить',
            size_hint_x=None,
            width=100,
            background_color=[0, 0.48, 0.8, 1]
        )
        run_btn.bind(on_press=lambda x: self.execute_command())
        
        input_layout.add_widget(input_label)
        input_layout.add_widget(self.input_field)
        input_layout.add_widget(run_btn)
        
        main_layout.add_widget(input_layout)
        
        # Показываем приветствие
        Clock.schedule_once(lambda dt: self.show_welcome(), 0.1)
        
        return main_layout
        
    def update_header(self):
        if self.user_manager.current_user:
            user_info = self.user_manager.get_user_profile()
            level = user_info['profile']['level']
            exp = user_info['profile']['experience']
            header_text = f"🚀 Умная Консоль | 👤 {self.user_manager.current_user} | 🎯 Уровень {level} | ⭐ {exp} опыта"
        else:
            header_text = "🚀 Умная Консоль | 🔓 Гостевой режим - используйте 'login' для входа"
        self.header_label.text = header_text
        
    def show_welcome(self):
        welcome_text = """╔══════════════════════════════════════════════════════════════════╗
║               🚀 УМНАЯ КОНСОЛЬ Kivy + ЧАТ + USERS              ║
║                  Добро пожаловать! v3.0                        ║
╚══════════════════════════════════════════════════════════════════╝

👤 **Система пользователей:**
  • login - вход в систему
  • register - регистрация нового пользователя  
  • profile - просмотр профиля
  • logout - выход из системы
  • users - список онлайн пользователей

📋 Основные команды:
  • help - показать все команды
  • clear - очистить экран
  • time - текущее время
  • date - текущая дата

💬 ЧАТ-команды:
  • chat help - справка по чату
  • connect [ip] [port] - подключиться к чат-серверу
  • send [сообщение] - отправить сообщение
  • disconnect - отключиться от сервера

"""
        self.append_output(welcome_text, [0, 1, 0])
        
    def append_output(self, text, color=None):
        if color is None:
            color = [1, 1, 1, 1]
            
        # Просто добавляем текст без сложной логики прокрутки
        original_color = self.output_text.foreground_color
        self.output_text.foreground_color = color
        self.output_text.text += text
        self.output_text.foreground_color = original_color
        
        # Прокручиваем вниз
        self.output_text.cursor = (0, len(self.output_text.text))
        
    def execute_command(self, instance=None):
        command = self.input_field.text.strip()
        if not command:
            return
            
        # Добавляем в историю
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Обновляем статистику команд
        if self.user_manager.current_user:
            current_stats = self.user_manager.get_user_profile()['profile']
            self.user_manager.update_user_profile('commands_used', current_stats['commands_used'] + 1)
            self.user_manager.update_user_profile('experience', current_stats['experience'] + 1)
            
            if current_stats['commands_used'] + 1 >= current_stats['level'] * 10:
                self.user_manager.update_user_profile('level', current_stats['level'] + 1)
                self.append_output(f"🎉 Поздравляем! Вы достигли уровня {current_stats['level'] + 1}!\n", [1, 0.84, 0])
        
        self.append_output(f"> {command}\n", [1, 1, 0])
        self.input_field.text = ''
        
        # Обрабатываем встроенные команды
        if self.handle_builtin_commands(command):
            return
            
        # Для системных команд в Kivy используем os.system или subprocess
        import subprocess
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.stdout:
                self.append_output(result.stdout + '\n')
            if result.stderr:
                self.append_output(result.stderr + '\n', [1, 0, 0])
        except Exception as e:
            self.append_output(f"Ошибка выполнения команды: {e}\n", [1, 0, 0])
            
    def handle_builtin_commands(self, command):
        parts = command.split()
        if not parts:
            return False
            
        cmd = parts[0].lower()
        
        builtin_commands = {
            'help': self.cmd_help,
            'clear': self.cmd_clear,
            'time': self.cmd_time,
            'date': self.cmd_date,
            'calc': self.cmd_calc,
            'weather': self.cmd_weather,
            'joke': self.cmd_joke,
            'quote': self.cmd_quote,
            'dice': self.cmd_dice,
            'coin': self.cmd_coin,
            'todo': self.cmd_todo,
            'pwd': self.cmd_pwd,
            'sysinfo': self.cmd_sysinfo,
            'matrix': self.cmd_matrix,
            'game': self.cmd_game,
            'chat': self.cmd_chat,
            'connect': self.cmd_connect,
            'send': self.cmd_send,
            'disconnect': self.cmd_disconnect,
            'exit': self.cmd_exit,
            'login': self.cmd_login,
            'register': self.cmd_register,
            'profile': self.cmd_profile,
            'logout': self.cmd_logout,
            'users': self.cmd_users
        }
        
        if cmd in builtin_commands:
            builtin_commands[cmd](parts[1:] if len(parts) > 1 else [])
            return True
        return False
    
    def cmd_help(self, args):
        help_text = """
🎯 **СПРАВОЧНИК КОМАНД v3.0**

👤 **Система пользователей:**
  • login - вход в систему
  • register - регистрация нового пользователя
  • profile - просмотр профиля и статистики
  • logout - выход из системы
  • users - список онлайн пользователей

📊 **Основные команды:**
  • help - показать эту справку
  • clear - очистить экран
  • exit - выйти из программы

💬 **Чат-команды:**
  • chat help - справка по чату
  • connect [ip] [port] - подключиться к серверу
  • send [сообщение] - отправить сообщение
  • disconnect - отключиться от сервера
  • chat status - статус подключения

🕐 **Время и дата:**
  • time - текущее время
  • date - текущая дата

🧮 **Калькулятор:**
  • calc 2+2 - простые вычисления
  • calc sin(30) - тригонометрия

🎲 **Развлечения:**
  • joke - случайная шутка
  • quote - вдохновляющая цитата
  • dice - бросить игральные кости
  • coin - подбросить монетку

📝 **Полезности:**
  • todo - управление списком дел
  • weather - пример прогноза погоды
  • pwd - текущая рабочая директория
  • sysinfo - информация о системе

🎮 **Игры:**
  • game - меню мини-игр
"""
        self.append_output(help_text, [0, 1, 1])
    
    def cmd_login(self, args):
        LoginPopup(self).open()
    
    def cmd_register(self, args):
        popup = LoginPopup(self)
        if hasattr(popup.tabs, 'tab_list') and len(popup.tabs.tab_list) > 1:
            popup.tabs.switch_to(popup.tabs.tab_list[1])
        popup.open()
    
    def cmd_profile(self, args):
        if not self.user_manager.current_user:
            self.append_output("❌ Вы не вошли в систему. Используйте 'login' для входа\n", [1, 0, 0])
            return
            
        ProfilePopup(self).open()
    
    def cmd_logout(self, args):
        if self.user_manager.current_user:
            username = self.user_manager.current_user
            self.user_manager.logout_user()
            self.update_header()
            self.append_output(f"✅ Вы вышли из системы ({username})\n", [0, 1, 0])
        else:
            self.append_output("ℹ️ Вы и так не в системе\n", [1, 1, 0])
    
    def cmd_users(self, args):
        online_users = self.user_manager.get_online_users()
        if online_users:
            self.append_output("👥 Пользователи онлайн:\n", [0, 1, 0])
            for user in online_users:
                user_info = self.user_manager.get_user_profile(user)
                level = user_info['profile']['level']
                self.append_output(f"   🟢 {user} (Уровень {level})\n", [0.56, 0.93, 0.56])
        else:
            self.append_output("👥 Нет пользователей онлайн\n", [1, 1, 0])
    
    def cmd_chat(self, args):
        if not args:
            self.append_output("❌ Использование: chat [команда]\n", [1, 0, 0])
            self.append_output("💡 Доступные команды: help, status, users\n", [1, 1, 0])
            return
            
        subcommand = args[0].lower()
        
        if subcommand == 'help':
            chat_help = """
💬 **СПРАВКА ПО ЧАТ-КОМАНДАМ**

🔗 **Подключение:**
  • connect [ip] [port] - подключиться к серверу
    Пример: connect 127.0.0.1 8080

📤 **Отправка сообщений:**
  • send [текст] - отправить сообщение
    Пример: send Привет всем!

🔌 **Управление подключения:**
  • disconnect - отключиться от сервера
  • chat status - показать статус подключения

📊 **Информация:**
  • chat users - список пользователей (если поддерживается сервером)

💡 **Особенности с системой пользователей:**
  • При входе в систему ваш ник в чате изменится на имя пользователя
  • В гостевом режиме используется случайный ник
  • Статистика сообщений сохраняется в профиле
"""
            self.append_output(chat_help, [1, 0.41, 0.71])
            
        elif subcommand == 'status':
            status = "✅ Подключено" if self.chat_client.connected else "❌ Не подключено"
            color = [0, 1, 0] if self.chat_client.connected else [1, 0, 0]
            self.append_output(f"📊 Статус чата: {status}\n", color)
            if self.chat_client.connected:
                username = self.user_manager.current_user if self.user_manager.current_user else self.chat_client.username
                self.append_output(f"👤 Ваш ник: {username}\n", [0, 1, 0])
                
        elif subcommand == 'users':
            if self.chat_client.connected:
                self.append_output("📊 Список пользователей: (функция требует поддержки сервером)\n", [1, 1, 0])
            else:
                self.append_output("❌ Не подключено к серверу\n", [1, 0, 0])
        else:
            self.append_output(f"❌ Неизвестная команда чата: {subcommand}\n", [1, 0, 0])
    
    def cmd_connect(self, args):
        if len(args) < 2:
            self.append_output("❌ Использование: connect [IP] [PORT]\n", [1, 0, 0])
            self.append_output("💡 Пример: connect 127.0.0.1 8080\n", [1, 1, 0])
            return
            
        ip = args[0]
        try:
            port = int(args[1])
        except ValueError:
            self.append_output("❌ Порт должен быть числом\n", [1, 0, 0])
            return
        
        if self.chat_client.connect_to_server(ip, port):
            self.append_output(f"✅ Успешное подключение к {ip}:{port}\n", [0, 1, 0])
        else:
            self.append_output(f"❌ Не удалось подключиться к {ip}:{port}\n", [1, 0, 0])
    
    def cmd_send(self, args):
        if not args:
            self.append_output("❌ Использование: send [сообщение]\n", [1, 0, 0])
            return
            
        message = " ".join(args)
        if not self.chat_client.send_message(message):
            self.append_output("❌ Не удалось отправить сообщение\n", [1, 0, 0])
    
    def cmd_disconnect(self, args):
        if self.chat_client.connected:
            self.chat_client.disconnect()
            self.append_output("🔌 Отключено от чат-сервера\n", [1, 0.65, 0])
        else:
            self.append_output("ℹ️ Не было активного подключения\n", [1, 1, 0])
    
    def cmd_clear(self, args):
        self.output_text.text = ''
        self.show_welcome()
    
    def cmd_time(self, args):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.append_output(f"🕐 Текущее время: {current_time}\n", [0, 1, 0])
    
    def cmd_date(self, args):
        current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        day_of_week = days[datetime.datetime.now().weekday()]
        self.append_output(f"📅 Сегодня: {current_date} ({day_of_week})\n", [0, 1, 0])
    
    def cmd_calc(self, args):
        if not args:
            self.append_output("❌ Использование: calc <выражение>\n", [1, 0, 0])
            return
            
        expression = " ".join(args)
        try:
            result = eval(expression, {"__builtins__": None}, 
                         {"sin": math.sin, "cos": math.cos, "tan": math.tan,
                          "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
                          "log": math.log, "log10": math.log10})
            self.append_output(f"🧮 Результат: {result}\n", [0, 1, 0])
        except Exception as e:
            self.append_output(f"❌ Ошибка вычисления: {e}\n", [1, 0, 0])
    
    def cmd_weather(self, args):
        cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург"]
        city = random.choice(cities)
        temps = random.randint(-20, 35)
        conditions = ["☀️ Солнечно", "🌧️ Дождь", "❄️ Снег", "☁️ Облачно", "🌤️ Переменная облачность"]
        condition = random.choice(conditions)
        
        weather_text = f"""
🌍 Прогноз погоды для {city}:
   Температура: {temps}°C
   Состояние: {condition}
   Влажность: {random.randint(30, 90)}%
   Ветер: {random.randint(0, 15)} м/с
"""
        self.append_output(weather_text, [0.53, 0.81, 0.92])
    
    def cmd_joke(self, args):
        jokes = [
            "Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25!",
            "Какой у программиста любимый напиток? Java!",
            "Почему Python стал таким популярным? Потому что у него нет лишних скобок!",
        ]
        joke = random.choice(jokes)
        self.append_output(f"😂 Шутка: {joke}\n\n", [1, 0.65, 0])
    
    def cmd_quote(self, args):
        quotes = [
            ("Код — это поэзия.", "Неизвестный программист"),
            ("Преждевременная оптимизация — корень всех зол.", "Дональд Кнут"),
            ("Единственный способ делать великие дела — любить то, что ты делаешь.", "Стив Джобс"),
        ]
        quote, author = random.choice(quotes)
        self.append_output(f"💬 \"{quote}\"\n   — {author}\n\n", [1, 0.84, 0])
    
    def cmd_dice(self, args):
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2
        
        dice_chars = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        
        result = f"""
🎲 Бросок игральных костей:
   Первая кость: {dice1} {dice_chars[dice1-1]}
   Вторая кость: {dice2} {dice_chars[dice2-1]}
   Сумма: {total}
"""
        if dice1 == dice2:
            result += "   🎉 Дубль!"
        
        self.append_output(result + "\n", [1, 0.41, 0.71])
    
    def cmd_coin(self, args):
        result = random.choice(["Орёл", "Решка"])
        symbol = "🦅" if result == "Орёл" else "🪙"
        self.append_output(f"{symbol} Монетка показывает: {result}\n\n", [1, 0.84, 0])
    
    def cmd_todo(self, args):
        if not hasattr(self, 'todo_list'):
            self.todo_list = []
            
        if not args:
            if not self.todo_list:
                self.append_output("📝 Список дел пуст. Используйте: todo add <задача>\n", [0, 1, 0])
            else:
                todo_text = "📝 Ваш список дел:\n"
                for i, task in enumerate(self.todo_list, 1):
                    status = "✅" if task['done'] else "⏳"
                    todo_text += f"   {i}. {status} {task['text']}\n"
                self.append_output(todo_text + "\n")
        elif args[0] == 'add' and len(args) > 1:
            task = ' '.join(args[1:])
            self.todo_list.append({'text': task, 'done': False})
            self.append_output(f"✅ Добавлено: {task}\n", [0, 1, 0])
        elif args[0] == 'done' and len(args) > 1:
            try:
                index = int(args[1]) - 1
                if 0 <= index < len(self.todo_list):
                    self.todo_list[index]['done'] = True
                    self.append_output(f"✅ Задача {index+1} выполнена!\n", [0, 1, 0])
                else:
                    self.append_output("❌ Неверный номер задачи\n", [1, 0, 0])
            except ValueError:
                self.append_output("❌ Использование: todo done <номер>\n", [1, 0, 0])
    
    def cmd_pwd(self, args):
        self.append_output(f"📁 Текущая директория: {self.current_dir}\n", [0, 1, 0])
    
    def cmd_sysinfo(self, args):
        info = f"""
💻 Информация о системе:
   ОС: {platform.system()} {platform.release()}
   Процессор: {platform.processor()}
   Архитектура: {platform.architecture()[0]}
   Python: {platform.python_version()}
   Пользователь: {os.getenv('USERNAME', 'Неизвестно')}
"""
        self.append_output(info, [0, 1, 1])
    
    def cmd_matrix(self, args):
        matrix_chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノ"
        lines = []
        for i in range(10):
            line = ''.join(random.choice(matrix_chars) for _ in range(40))
            lines.append(line)
        
        matrix_text = "🌐 Матричный эффект:\n" + "\n".join(lines) + "\n"
        self.append_output(matrix_text, [0, 1, 0])
    
    def cmd_game(self, args):
        games_text = """
🎮 ДОСТУПНЫЕ МИНИ-ИГРЫ:

1. Угадай число (game guess)
   Компьютер загадывает число от 1 до 100

2. Камень-Ножницы-Бумага (game rps)
   Классическая игра против компьютера

💡 Введите 'game guess' или 'game rps' для начала игры
"""
        self.append_output(games_text, [1, 0.41, 0.71])
        
        if args and args[0] == 'guess':
            self.start_guess_game()
        elif args and args[0] == 'rps':
            self.start_rps_game()
    
    def start_guess_game(self):
        self.guess_number = random.randint(1, 100)
        self.guess_attempts = 0
        self.append_output("\n🎯 Игра 'Угадай число' началась!\n", [0, 1, 0])
        self.append_output("Я загадал число от 1 до 100. Попробуй угадать!\n", [0, 1, 0])
    
    def start_rps_game(self):
        self.append_output("\n✂️ Игра 'Камень-Ножницы-Бумага' началась!\n", [0, 1, 0])
        self.append_output("Выбери: камень, ножницы или бумага\n", [0, 1, 0])
    
    def cmd_exit(self, args):
        if self.chat_client.connected:
            self.chat_client.disconnect()
        self.user_manager.logout_user()
        App.get_running_app().stop()

if __name__ == '__main__':
    ConsoleApp().run()
