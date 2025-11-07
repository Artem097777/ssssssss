import pygame
import sys

# Инициализация
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Игрок
player_x, player_y = 400, 300
player_speed = 5

# Основной цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Управление (клавиатура)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed

    # Отрисовка
    screen.fill((0, 0, 0))
    pygame.draw.circle(screen, (255, 0, 0), (player_x, player_y), 20)
    pygame.display.flip()
    clock.tick(60)
