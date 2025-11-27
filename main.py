from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
import socket
import threading
import time
import json
from datetime import datetime

class AndroidServer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.server_socket = None
        self.is_running = False
        self.clients = []
        self.message_history = []

        self.setup_ui()

    def setup_ui(self):
        # Заголовок
        title = Label(
            text='📱 Android TCP Server',
            size_hint_y=None, height=60, 
            font_size='24sp', bold=True
        )
        self.add_widget(title)

        # Сетевой статус
        self.status_label = Label(
            text='🔴 Сервер остановлен',
            size_hint_y=None, height=40,
            font_size='16sp'
        )
        self.add_widget(self.status_label)

        # Панель управления
        control_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=80)
        
        self.control_btn = Button(
            text='🚀 Запустить сервер', 
            background_color=(0.2, 0.7, 0.3, 1),
            font_size='18sp'
        )
        self.control_btn.bind(on_press=self.toggle_server)
        control_layout.add_widget(self.control_btn)

        self.settings_btn = Button(
            text='⚙️ Настройки', 
            background_color=(0.3, 0.5, 0.8, 1),
            font_size='18sp', size_hint_x=0.4
        )
        self.settings_btn.bind(on_press=self.show_settings)
        control_layout.add_widget(self.settings_btn)

        self.add_widget(control_layout)

        # Информация о подключении
        self.connection_info = Label(
            text='IP: неизвестен | Порт: -- | Клиентов: 0',
            size_hint_y=None, height=40,
            font_size='14sp'
        )
        self.add_widget(self.connection_info)

        # Лог сообщений с прокруткой
        log_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        log_header.add_widget(Label(text='📨 Лог сообщений:', size_hint_x=0.7))
        
        clear_btn = Button(
            text='🧹 Очистить', 
            size_hint_x=0.3,
            background_color=(0.8, 0.6, 0.2, 1)
        )
        clear_btn.bind(on_press=self.clear_log)
        log_header.add_widget(clear_btn)
        
        self.add_widget(log_header)

        scroll_view = ScrollView()
        self.log_content = Label(
            text='Добро пожаловать! Запустите сервер для начала работы.\n',
            text_size=(None, None),
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.log_content.bind(texture_size=self.log_content.setter('size'))
        scroll_view.add_widget(self.log_content)
        self.add_widget(scroll_view)

        # Статистика
        self.stats_label = Label(
            text='Сообщений: 0 | Ошибок: 0',
            size_hint_y=None, height=30,
            font_size='12sp'
        )
        self.add_widget(self.stats_label)

        self.stats = {'messages': 0, 'errors': 0, 'connections': 0}

    def show_settings(self, instance):
        """Показать настройки подключения"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Порт
        port_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        port_layout.add_widget(Label(text='Порт:', size_hint_x=0.4))
        port_input = TextInput(
            text='8080', 
            multiline=False,
            input_filter='int'
        )
        port_layout.add_widget(port_input)
        content.add_widget(port_layout)

        # Кнопки
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        
        test_btn = Button(text='Тест порта', background_color=(0.2, 0.7, 0.3, 1))
        test_btn.bind(on_press=lambda x: self.test_port(port_input.text))
        btn_layout.add_widget(test_btn)

        ip_btn = Button(text='Показать IP', background_color=(0.3, 0.5, 0.8, 1))
        ip_btn.bind(on_press=self.show_ip_info)
        btn_layout.add_widget(ip_btn)

        content.add_widget(btn_layout)

        close_btn = Button(text='Закрыть', size_hint_y=None, height=50)
        content.add_widget(close_btn)

        popup = Popup(
            title='Настройки сервера',
            content=content,
            size_hint=(0.8, 0.6)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def test_port(self, port_str):
        """Проверить доступность порта"""
        try:
            port = int(port_str)
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_socket.bind(('0.0.0.0', port))
            test_socket.close()
            self.log_message(f"✅ Порт {port} доступен")
        except Exception as e:
            self.log_message(f"❌ Порт {port} занят: {e}")

    def show_ip_info(self, instance):
        """Показать подробную информацию об IP"""
        ips = self.get_all_ips()
        ip_text = "Доступные IP адреса:\n\n"
        for ip in ips:
            ip_text += f"• {ip}:8080\n"
        
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text=ip_text))
        
        copy_btn = Button(text='Копировать все IP', size_hint_y=None, height=50)
        content.add_widget(copy_btn)
        
        close_btn = Button(text='Закрыть', size_hint_y=None, height=50)
        content.add_widget(close_btn)
        
        popup = Popup(title='IP адреса', content=content, size_hint=(0.9, 0.7))
        
        def copy_ips(btn):
            ip_list = "\n".join([f"{ip}:8080" for ip in ips])
            Clipboard.copy(ip_list)
            self.log_message("📋 IP адреса скопированы в буфер")
            popup.dismiss()
        
        copy_btn.bind(on_press=copy_ips)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def get_all_ips(self):
        """Получить все IP адреса устройства"""
        ips = []
        try:
            hostname = socket.gethostname()
            all_ips = socket.getaddrinfo(hostname, None)
            for addr in all_ips:
                ip = addr[4][0]
                if ip not in ips and not ip.startswith('127.'):
                    ips.append(ip)
        except Exception as e:
            self.log_message(f"Ошибка получения IP: {e}")
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            if local_ip not in ips:
                ips.append(local_ip)
        except:
            pass
        
        return ips

    def toggle_server(self, instance):
        """Запуск/остановка сервера"""
        if not self.is_running:
            self.start_server()
        else:
            self.stop_server()

    def start_server(self):
        """Запуск TCP сервера"""
        port = 8080  # Фиксированный порт для простоты
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(1.0)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(5)
            
            self.is_running = True
            self.control_btn.text = '🛑 Остановить сервер'
            self.control_btn.background_color = (0.8, 0.2, 0.2, 1)
            self.status_label.text = '🟢 Сервер запущен'
            
            # Показываем информацию для подключения
            ips = self.get_all_ips()
            main_ip = ips[0] if ips else "неизвестен"
            self.connection_info.text = f"IP: {main_ip} | Порт: {port} | Клиентов: 0"
            
            self.log_message("=" * 50)
            self.log_message("🚀 СЕРВЕР ЗАПУЩЕН")
            self.log_message("📡 Адреса для подключения:")
            for ip in ips:
                self.log_message(f"   {ip}:{port}")
            self.log_message("=" * 50)

            # Запуск потока прослушивания
            self.server_thread = threading.Thread(target=self.listen_clients)
            self.server_thread.daemon = True
            self.server_thread.start()
            
        except Exception as e:
            self.log_message(f"❌ Ошибка запуска сервера: {e}")
            self.stats['errors'] += 1
            self.update_stats()

    def stop_server(self):
        """Остановка сервера"""
        if self.server_socket:
            self.is_running = False
            
            # Закрываем клиентские соединения
            for client_socket, addr in self.clients:
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear()
            
            try:
                self.server_socket.close()
            except:
                pass
            
            self.control_btn.text = '🚀 Запустить сервер'
            self.control_btn.background_color = (0.2, 0.7, 0.3, 1)
            self.status_label.text = '🔴 Сервер остановлен'
            self.connection_info.text = 'IP: неизвестен | Порт: -- | Клиентов: 0'
            self.log_message("🛑 СЕРВЕР ОСТАНОВЛЕН")

    def listen_clients(self):
        """Прослушивание входящих подключений"""
        while self.is_running:
            try:
                client_socket, addr = self.server_socket.accept()
                self.stats['connections'] += 1
                self.log_message(f"🔗 Новый клиент: {addr[0]}:{addr[1]}")
                
                self.clients.append((client_socket, addr))
                self.update_connection_info()
                
                # Запускаем обработчик клиента
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    self.log_message(f"⚠️ Ошибка подключения: {e}")
                    self.stats['errors'] += 1
                    self.update_stats()
                break

    def handle_client(self, client_socket, addr):
        """Обработка клиентского соединения"""
        client_ip = addr[0]
        try:
            client_socket.settimeout(1.0)
            while self.is_running:
                try:
                    data = client_socket.recv(1024).decode('utf-8').strip()
                    if not data:
                        break
                    
                    # Обработка команды
                    response = self.process_command(data, client_ip)
                    if response:
                        client_socket.send(response.encode('utf-8'))
                    
                    self.stats['messages'] += 1
                    self.update_stats()
                    
                except socket.timeout:
                    continue
                except:
                    break
                    
        except Exception as e:
            self.log_message(f"⚠️ Ошибка клиента {client_ip}: {e}")
            self.stats['errors'] += 1
            self.update_stats()
        finally:
            try:
                client_socket.close()
            except:
                pass
            
            # Удаляем клиента из списка
            self.clients = [c for c in self.clients if c[1] != addr]
            self.update_connection_info()
            self.log_message(f"🔌 Отключился: {client_ip}")

    def process_command(self, data, client_ip):
        """Обработка входящих команд"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Сохраняем сообщение в историю
        message_entry = {
            'time': timestamp,
            'ip': client_ip,
            'message': data,
            'type': 'incoming'
        }
        self.message_history.append(message_entry)
        
        # Логируем сообщение
        self.log_message(f"📨 [{timestamp}] {client_ip}: {data}")
        
        # Простые команды
        if data.lower() == 'ping':
            return 'pong'
        elif data.lower() == 'time':
            return f'Текущее время: {datetime.now().strftime("%H:%M:%S")}'
        elif data.lower() == 'stats':
            return f'Статистика: {len(self.clients)} клиентов, {self.stats["messages"]} сообщений'
        elif data.lower().startswith('echo '):
            return data[5:]
        else:
            return f'Эхо: {data}'

    def update_connection_info(self):
        """Обновление информации о подключениях"""
        ips = self.get_all_ips()
        main_ip = ips[0] if ips else "неизвестен"
        Clock.schedule_once(lambda dt: setattr(
            self.connection_info,
            'text',
            f'IP: {main_ip} | Порт: 8080 | Клиентов: {len(self.clients)}'
        ))

    def update_stats(self):
        """Обновление статистики"""
        Clock.schedule_once(lambda dt: setattr(
            self.stats_label,
            'text',
            f'Сообщений: {self.stats["messages"]} | Ошибок: {self.stats["errors"]} | Подключений: {self.stats["connections"]}'
        ))

    def log_message(self, message):
        """Добавление сообщения в лог"""
        Clock.schedule_once(lambda dt: self.update_log(message))

    def update_log(self, message):
        """Обновление лога в основном потоке"""
        self.log_content.text += f"{message}\n"
        # Автопрокрутка к последнему сообщению
        scroll_view = self.log_content.parent
        if scroll_view and hasattr(scroll_view, 'scroll_y'):
            scroll_view.scroll_y = 0

    def clear_log(self, instance):
        """Очистка лога сообщений"""
        self.log_content.text = 'Лог очищен\n'
        self.log_message("🧹 Лог сообщений очищен")

    def on_stop(self):
        """Остановка при закрытии приложения"""
        self.stop_server()

class AndroidServerApp(App):
    def build(self):
        self.title = 'Android TCP Server'
        return AndroidServer()

    def on_stop(self):
        self.root.on_stop()

if __name__ == '__main__':
    AndroidServerApp().run()
