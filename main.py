import pygame
import sys

# Инициализация Pygame
pygame.init()

# Размеры экрана (под Android лучше использовать относительные значения)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Android Pygame")

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Позиция квадрата
x, y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
square_size = 100

# Основной цикл
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # При касании перемещаем квадрат в точку касания
            x, y = event.pos
            # Корректируем позицию, чтобы квадрат был по центру касания
            x -= square_size // 2
            y -= square_size // 2

    # Ограничиваем позицию квадрата границами экрана
    x = max(0, min(x, SCREEN_WIDTH - square_size))
    y = max(0, min(y, SCREEN_HEIGHT - square_size))

    # Рисуем фон и квадрат
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, (x, y, square_size, square_size))

    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
sys.exit()
