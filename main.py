from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
import socket
import threading


class ServerApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.server_socket = None
        self.is_running = False
        
        # Элементы управления
        self.control_layout = BoxLayout(size_hint_y=0.1)
        self.start_btn = Button(text='Запустить сервер')
        self.stop_btn = Button(text='Остановить сервер', disabled=True)
        self.control_layout.add_widget(self.start_btn)
        self.control_layout.add_widget(self.stop_btn)
        
        # Лог сообщений
        self.log_label = Label(text='Лог сервера:', size_hint_y=0.1)
        self.log = TextInput(readonly=True, size_hint_y=0.8)
        
        self.add_widget(self.control_layout)
        self.add_widget(self.log_label)
        self.add_widget(self.log)
        
        # Привязка событий
        self.start_btn.bind(on_press=self.start_server)
        self.stop_btn.bind(on_press=self.stop_server)

    def start_server(self, instance):
        self.is_running = True
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.log.text += 'Сервер запущен...\n'
        
        # Запуск сервера в отдельном потоке
        threading.Thread(target=self.run_server, daemon=True).start()

    def stop_server(self, instance):
        self.is_running = False
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        if self.server_socket:
            self.server_socket.close()
        self.log.text += 'Сервер остановлен.\n'

    def run_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('0.0.0.0', 9090))
            self.server_socket.listen(5)
            
            while self.is_running:
                client_socket, addr = self.server_socket.accept()
                self.add_log(f'Подключен клиент: {addr}')
                
                # Обработка клиента в отдельном потоке
                threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, addr),
                    daemon=True
                ).start()
                
        except Exception as e:
            if self.is_running:
                self.add_log(f'Ошибка: {str(e)}')

    def handle_client(self, client_socket, addr):
        try:
            while self.is_running:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                self.add_log(f'От {addr}: {data}')
        except Exception as e:
            self.add_log(f'Ошибка с клиентом {addr}: {str(e)}')
        finally:
            client_socket.close()
            self.add_log(f'Клиент {addr} отключен')

    def add_log(self, message):
        # Потокобезопасное обновление UI
        Clock.schedule_once(lambda dt: setattr(self.log, 'text', self.log.text + message + '\n'))


class ServerAppKivy(App):
    def build(self):
        return ServerApp()


if __name__ == '__main__':
    ServerAppKivy().run()
