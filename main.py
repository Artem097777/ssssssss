from ursina import *
from kivy.core.window import Window

app = Ursina()

# Настройка окна для мобильных
window.borderless = False
window.color = color.black
window.exit_button.enabled = False

# Игрок (куб как временный аватар)
player = Entity(
    model='cube',
    color=color.orange,
    scale=(1, 2, 1),
    position=(0, 0.5, 0)
)

# Камера следует за игроком
camera.parent = player
camera.position = (0, 2, -5)
camera.rotation = (15, 0, 0)

# Управление (ПК-версия для тестирования)
def update():
    # Передвижение WASD
    if held_keys['w']: player.z += time.dt * 5
    if held_keys['s']: player.z -= time.dt * 5
    if held_keys['a']: player.x -= time.dt * 5
    if held_keys['d']: player.x += time.dt * 5

    # Поворот камеры мышью (на ПК)
    camera.rotation_y += mouse.velocity[0] * 20
    camera.rotation_x -= mouse.velocity[1] * 20

app.run()
