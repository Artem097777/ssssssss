import pygame
import sys
import math

# Инициализация
pygame.init()
screen = pygame.display.set_mode((480, 320))  # Разрешение для телефона
clock = pygame.time.Clock()

# Параметры игрока
player_x, player_y = 2.0, 2.0
player_angle = 0
player_speed = 0.05

# Карта (1 — стена, 0 — проход)
map_grid = [
    [1,1,1,1,1],
    [1,0,0,0,1],
    [1,0,1,0,1],
    [1,0,0,0,1],
    [1,1,1,1,1]
]

def draw_wall(screen, x, y, height, color):
    pygame.draw.rect(screen, color, (x, 160 - height//2, 2, height))

def raycast(player_x, player_y, angle, map_grid):
    # Упрощённый рейкастинг
    distance = 0
    while distance < 20:
        test_x = int(player_x + distance * math.cos(angle))
        test_y = int(player_y + distance * math.sin(angle))
        if (test_x < 0 or test_x >= len(map_grid) or
            test_y < 0 or test_y >= len(map_grid[0]) or
            map_grid[test_x][test_y] == 1):
            return distance
        distance += 0.1
    return 20

# Основной цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Управление (виртуальные кнопки)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_angle -= 0.03
    if keys[pygame.K_RIGHT]:
        player_angle += 0.03
    if keys[pygame.K_UP]:
        player_x += player_speed * math.cos(player_angle)
        player_y += player_speed * math.sin(player_angle)
    if keys[pygame.K_DOWN]:
        player_x -= player_speed * math.cos(player_angle)
        player_y -= player_speed * math.sin(player_angle)

    # Отрисовка
    screen.fill((0, 0, 0))  # Чёрный фон

    # Рейкастинг для стен
    for x in range(0, 480, 2):
        angle = player_angle + (x - 240) * 0.002  # Угол луча
        distance = raycast(player_x, player_y, angle, map_grid)
        height = max(0, int(200 / distance))
        draw_wall(screen, x, 160, height, (100, 100, 100))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
