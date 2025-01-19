import pygame
import os
import sys
from pygame import draw, Color

FPS = 60

pygame.init()

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
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if WIDTH // 2 - 75 <= x <= WIDTH // 2 + 75 and 290 <= y <= 349:
                    settings_screen()
        # Painting
        screen.fill((0, 0, 0))
        logo = load_image('logo.png')
        screen.blit(logo, (WIDTH // 2 - 150, 20))
        play = load_image('play.jpg')
        screen.blit(play, (WIDTH // 2 - 75, 200))
        settings = load_image('settings.jpg')
        screen.blit(settings, (WIDTH // 2 - 75, 290))
        draw.rect(screen, Color('white'), (WIDTH // 2 - 75, 200, 150, 69), 2)
        draw.rect(screen, Color('white'), (WIDTH // 2 - 75, 290, 150, 59), 2)
        if pygame.mouse.get_focused():
            arrow = load_image('Cursor.png')
            screen.blit(arrow, (x, y))

        pygame.display.flip()
        # Time
        clock.tick(FPS)
    pygame.quit()


def settings_screen():
    pygame.display.set_caption('Settings')
    x, y = 0, 0
    color_right = (0, 0, 0)  # цвет надписи, отвечающий за кнопку "вправо". Далее по аналогии
    inp_right = False  # означает, надо ли изменять кнопку "вправо"
    k_right = 'd'
    color_left = (0, 0, 0)
    inp_left = False
    k_left = 'a'
    color_up = (0, 0, 0)
    inp_up = False
    k_up = 'w'
    color_down = (0, 0, 0)
    inp_down = False
    k_down = 's'
    color_shoot = (0, 0, 0)
    inp_shoot = False
    k_shoot = 'l'
    pygame.mouse.set_visible(False)
    running = True
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 344 <= x <= 405 and 44 <= y <= 85:
                    color_right = (150, 150, 150)
                    inp_right = True
                    print_text(k_right, 400, 50, color_right)
                else:
                    color_right = (0, 0, 0)
                    inp_right = False
                if 344 <= x <= 405 and 94 <= y <= 135:
                    color_left = (150, 150, 150)
                    inp_left = True
                    print_text('a', 400, 50, color_left)
                else:
                    color_left = (0, 0, 0)
                    inp_left = False
                if 344 <= x <= 405 and 144 <= y <= 185:
                    color_up = (150, 150, 150)
                    inp_up = True
                    print_text('w', 400, 50, color_up)
                else:
                    color_up = (0, 0, 0)
                    inp_up = False
                if 344 <= x <= 405 and 194 <= y <= 235:
                    color_down = (150, 150, 150)
                    inp_down = True
                    print_text('s', 400, 50, color_down)
                else:
                    color_down = (0, 0, 0)
                    inp_down = False
                if 344 <= x <= 405 and 244 <= y <= 285:
                    color_shoot = (150, 150, 150)
                    inp_shoot = True
                    print_text('l', 400, 50, color_shoot)
                else:
                    color_shoot = (0, 0, 0)
                    inp_shoot = False
            elif event.type == pygame.KEYDOWN:
                if inp_right:
                    if event.unicode in 'qwertyuiopasdfghjklzxcvbnm':
                        k_right = event.unicode
                    inp_right = False
                    color_right = (0, 0, 0)
                elif inp_left:
                    if event.unicode in 'qwertyuiopasdfghjklzxcvbnm':
                        k_left = event.unicode
                    inp_left = False
                    color_left = (0, 0, 0)
                elif inp_up:
                    if event.unicode in 'qwertyuiopasdfghjklzxcvbnm':
                        k_up = event.unicode
                    inp_up = False
                    color_up = (0, 0, 0)
                elif inp_down:
                    if event.unicode in 'qwertyuiopasdfghjklzxcvbnm':
                        k_down = event.unicode
                    inp_down = False
                    color_down = (0, 0, 0)
                elif inp_shoot:
                    if event.unicode in 'qwertyuiopasdfghjklzxcvbnm':
                        k_shoot = event.unicode
                    inp_shoot = False
                    color_shoot= (0, 0, 0)

        # Painting
        screen.fill((150, 150, 150))
        pergament = load_image('pergament.png', (255, 255, 255))
        screen.blit(pergament, (394, 44))
        screen.blit(pergament, (394, 94))
        screen.blit(pergament, (394, 144))
        screen.blit(pergament, (394, 194))
        screen.blit(pergament, (394, 244))
        if pygame.mouse.get_focused():
            arrow = load_image('Cursor.png')
            screen.blit(arrow, (x, y))
        print_text('Движение вправо', 50, 50)
        print_text(k_right, 400, 50, color_right)
        print_text('Движение влево', 50, 100)
        print_text(k_left, 400, 100, color_left)
        print_text('Движение вверх', 50, 150)
        print_text(k_up, 400, 150, color_up)
        print_text('Движение вниз', 50, 200)
        print_text(k_down, 400, 200, color_down)
        print_text('Стрелять', 50, 250)
        print_text(k_shoot, 400, 250, color_shoot)
        draw.rect(screen, Color('white'), (550, 525, 100, 50))
        pygame.display.flip()
        # Time
        clock.tick(FPS)
    pygame.quit()


def print_text(message, x, y, color=(0, 0, 0), font_size=30, font_type='DreiFraktur.ttf'):
    """
    Функция выводит текст на экран
    :param message: (str) текст, который надо вывести
    :param x: (int) координаты по x
    :param y: (int) координаты по y
    :param color: (tuple) цвет текста
    :param font_size: размер шрифта
    :param font_type: тип шрифта, не стоит изменять
    :return: Nothing
    """

    fullname = os.path.join('data', font_type)
    font = pygame.font.Font(fullname, font_size)
    text = font.render(message, True, color)
    screen.blit(text, (x, y))


start_screen()
