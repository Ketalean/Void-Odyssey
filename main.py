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

k_right = 'd'
k_left = 'a'
k_up = 'w'
k_down = 's'
k_shoot = 'l'


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


player_image = load_image('player.png')


class Player(pygame.sprite.Sprite):
    # набросок класса игрока с анимацией
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.k = 0
        self.x = x
        self.y = y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if self.k == 3:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.k = 0

    def move(self):
        if self.x < WIDTH:
            self.x += 10
            self.rect = self.rect.move(10, 0)
        else:
            self.rect = self.rect.move(-800, 0)
            self.x = 0


# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def terminate():
    """
    Прерывание игры
    """
    pygame.quit()
    sys.exit()


def game():
    # набросок первого уровня игры
    player = Player(load_image("player-move.png"), 8, 1, 100, 400)
    pygame.mouse.set_visible(False)
    running = True
    go = False
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                pass
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    go = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    go = False
        # Painting
        screen.fill((0, 0, 0))
        if go:
            all_sprites.draw(screen)
            player.update()
            player.move()
        else:
            hero = load_image('player.png')
            screen.blit(hero, (player.x, player.y))
        # Time
        pygame.display.flip()
        if player.k < 3:
            player.k += 1
        clock.tick(FPS)
    pygame.quit()


def start_screen():
    global x, y
    pygame.display.set_caption('Void Odyssey')
    pygame.mouse.set_visible(False)
    running = True
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if WIDTH // 2 - 75 <= x <= WIDTH // 2 + 75 and 290 <= y <= 349:
                    print(settings_screen())
                else:
                    game()
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
    global x, y, k_right, k_left, k_up, k_down, k_shoot
    error = False
    pygame.display.set_caption('Settings')
    color_right = (0, 0, 0)  # цвет надписи, отвечающий за кнопку "вправо". Далее по аналогии
    inp_right = False  # означает, надо ли изменять кнопку "вправо"
    color_left = (0, 0, 0)
    inp_left = False
    color_up = (0, 0, 0)
    inp_up = False
    color_down = (0, 0, 0)
    inp_down = False
    color_shoot = (0, 0, 0)
    inp_shoot = False
    pygame.mouse.set_visible(False)
    running = True
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 550 <= x <= 650 and 525 <= y <= 575:
                    #  проверяет, всё ли хорошо с настройками
                    if (len(set(list([k_right, k_left, k_up, k_down, k_shoot]))) ==
                            len([k_right, k_left, k_up, k_down, k_shoot]) and
                            len([k_right, k_left, k_up, k_down, k_shoot]) ==
                            ''.join([k_right, k_left, k_up, k_down, k_shoot])):
                        return [k_right, k_left, k_up, k_down, k_shoot]
                    else:
                        error = True
                if 337 <= x <= 412 and 350 <= y <= 390 and error:
                    error = False
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
                    print_text(k_left, 400, 50, color_left)
                else:
                    color_left = (0, 0, 0)
                    inp_left = False
                if 344 <= x <= 405 and 144 <= y <= 185:
                    color_up = (150, 150, 150)
                    inp_up = True
                    print_text(k_up, 400, 50, color_up)
                else:
                    color_up = (0, 0, 0)
                    inp_up = False
                if 344 <= x <= 405 and 194 <= y <= 235:
                    color_down = (150, 150, 150)
                    inp_down = True
                    print_text(k_down, 400, 50, color_down)
                else:
                    color_down = (0, 0, 0)
                    inp_down = False
                if 344 <= x <= 405 and 244 <= y <= 285:
                    color_shoot = (150, 150, 150)
                    inp_shoot = True
                    print_text(k_shoot, 400, 50, color_shoot)
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
                    color_shoot = (0, 0, 0)
                if event.key == pygame.K_ESCAPE:
                    start_screen()
                    # exit to main menu

        # Painting
        screen.fill((150, 150, 150))
        pergament = load_image('pergament.png', (255, 255, 255))
        screen.blit(pergament, (394, 44))
        screen.blit(pergament, (394, 94))
        screen.blit(pergament, (394, 144))
        screen.blit(pergament, (394, 194))
        screen.blit(pergament, (394, 244))
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
        print_text('OK', 580, 535)
        if error:
            draw.rect(screen, Color('yellow'), (250, 250, 250, 150))
            draw.rect(screen, Color('black'), (245, 245, 260, 160), 5)
            print_text('''Неправильный формат ввода:
1) Для управления использованы
клавиши НЕ английского алфавита
2) Одна и та же клавиша 
используется более 1 раза''', 255, 255, (200, 0, 0), 11)
            draw.rect(screen, Color('black'), (337, 350, 75, 40))
            print_text('OK', 353, 352, (250, 250, 250))
        if pygame.mouse.get_focused():
            arrow = load_image('Cursor.png')
            screen.blit(arrow, (x, y))
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
