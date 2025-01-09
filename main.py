import pygame
import os
import sys
from pygame import draw, Color

FPS = 30

pygame.init()

FPS = 50
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def start_screen():
    pygame.display.set_caption('Void Odyssey')
    x, y = 0, 0
    pygame.mouse.set_visible(False)
    running = True
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
        # Painting
        screen.fill((0, 0, 0))
        logo = load_image('logo.png')
        screen.blit(logo, (WIDTH // 2 - 150, 20))
        if pygame.mouse.get_focused():
            arrow = load_image('arrow.png')
            screen.blit(arrow, (x, y))

        pygame.display.flip()
        # Time
        clock.tick(FPS)
    pygame.quit()


start_screen()


