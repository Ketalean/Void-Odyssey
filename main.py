import os
import sqlite3
import sys
from random import randint, choice

import pygame
from pygame import draw, Color

FPS = 60

pygame.init()

WIDTH = 960
HEIGHT = 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
# sipg

k_right = 'd'
k_left = 'a'
k_up = 'w'
k_down = 's'
k_shoot = 'l'
k_jump = ' '
k_dash = 'p'


def load_image(name, colorkey=None):
    """
    Функция загружает изображение по имени файла, в котором оно хранится.
    Возвращает готовое для использования в классах изображение.
    :param name: str имя файла (формат png, jpg и т. п.)
    :param colorkey: если указан -1, убирает фон
    :return: image
    """
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


def load_level(filename):
    """
    Функция загружает лвл по карте файла.
    Возвращает список с картой уровня
    :param filename: str имя файла карты
    :return: список с элементами карты
    """
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Electro_Ball(pygame.sprite.Sprite):
    """
    Класс снаряда игрока.
    """

    # набросок снаряда
    def __init__(self, sheet, columns, rows, x, y, direction):
        super().__init__(ball_group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.k = 0
        self.x = x
        self.y = y
        self.direction = direction

    def cut_sheet(self, sheet, columns, rows):
        """
        Разрезает полученное изображение на равные части.
        :param sheet: str имя файла, хранящее изображение
        :param columns: int кол-во колонок, на которое нужно разбить изображение
        :param rows: int кол-во рядов, на которое нужно разбить изображение
        :return: Nothing
        """
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        """
        Функция отвечает за анимацию и перемещение снаряда
        :return: Nothing
        """
        screen_rect = (0, 0, WIDTH, HEIGHT)
        self.cur_frame = (self.cur_frame + 1) % 6
        self.image = self.frames[self.cur_frame]
        SPEED = 10
        if self.direction == 'right':
            self.x += SPEED
            self.rect = self.rect.move(SPEED, 0)
        else:
            self.x -= SPEED
            self.rect = self.rect.move(-SPEED, 0)
        if not self.rect.colliderect(screen_rect):
            self.kill()


player_image = load_image('hero.png')

tile_images = {
    'wall': load_image('stones.png'),
    'empty': load_image('grass.png'),
    'ground2': load_image('ground.png'),
    'dirt': load_image('dirt.png')
}

tile_width = tile_height = 64


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Portal(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, id):
        super().__init__(portals_group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.id = id
        self.k = 0

    def cut_sheet(self, sheet, columns, rows):
        """
        Разрезает полученное изображение на равные части.
        :param sheet: str имя файла, хранящее изображение
        :param columns: int кол-во колонок, на которое нужно разбить изображение
        :param rows: int кол-во рядов, на которое нужно разбить изображение
        :return: Nothing
        """
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        """
        Анимация портала.
        :return: Nothing
        """
        if self.k == 10:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.k = 0


class Coin(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(coin_group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.k = 0

    def cut_sheet(self, sheet, columns, rows):
        """
        Разрезает полученное изображение на равные части.
        :param sheet: str имя файла, хранящее изображение
        :param columns: int кол-во колонок, на которое нужно разбить изображение
        :param rows: int кол-во рядов, на которое нужно разбить изображение
        :return: Nothing
        """
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        """
        Анимация монетки.
        :return: Nothing
        """
        if self.k == 10:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.k = 0


class Player(pygame.sprite.Sprite):
    """
    Класс игрока, который передвигается по основному миру (где выбирается уровень).
    """

    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(player_group)
        self.pos = [x, y]
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.k = 0
        self.x = x
        self.y = y

    def cut_sheet(self, sheet, columns, rows):
        """
        Разрезает полученное изображение на равные части.
        :param sheet: str имя файла, хранящее изображение
        :param columns: int кол-во колонок, на которое нужно разбить изображение
        :param rows: int кол-во рядов, на которое нужно разбить изображение
        :return: Nothing
        """
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, direction):
        """
        Анимация персонажа, в зависимости от направления движения изменяется.
        :param direction: str направление движения персонажа
        :return: Nothing
        """
        if self.k == 3:
            if direction == 'u':
                self.cur_frame = (self.cur_frame + 1) % 3
            elif direction == 'r':
                if 2 < self.cur_frame <= 4:
                    self.cur_frame += 1
                else:
                    self.cur_frame = 3
            elif direction == 'd':
                if 5 < self.cur_frame <= 6:
                    self.cur_frame += 1
                else:
                    self.cur_frame = 6
            elif direction == 'l':
                if 8 < self.cur_frame <= 9:
                    self.cur_frame += 1
                else:
                    self.cur_frame = 9
            self.image = self.frames[self.cur_frame]
            self.k = 0

    def move(self, direction):
        """
        Перемещение персонажа по карте.
        :param direction: str направление движения персонажа
        :return: Nothing
        """
        SPEED = 5
        if direction == 'r':
            if self.x < WIDTH:
                self.x += SPEED
                self.rect = self.rect.move(SPEED, 0)
            else:
                self.rect = self.rect.move(-WIDTH, 0)
                self.x = 0
        elif direction == 'l':
            if self.x > 0:
                self.x -= SPEED
                self.rect = self.rect.move(-SPEED, 0)
            else:
                self.rect = self.rect.move(WIDTH, 0)
                self.x = WIDTH
        elif direction == 'u':
            if self.y > 0:
                self.y -= SPEED
                self.rect = self.rect.move(0, -SPEED)
            else:
                self.rect = self.rect.move(0, HEIGHT)
                self.y = HEIGHT
        elif direction == 'd':
            if self.y < HEIGHT:
                self.y += SPEED
                self.rect = self.rect.move(0, SPEED)
            else:
                self.rect = self.rect.move(0, -HEIGHT)
                self.y = 0
        elif direction == 'ur' or direction == 'ru':
            self.move('u')
            self.move('r')
        elif direction == 'ul' or direction == 'lu':
            self.move('u')
            self.move('l')
        elif direction == 'dr' or direction == 'rd':
            self.move('d')
            self.move('r')
        elif direction == 'dl' or direction == 'ld':
            self.move('d')
            self.move('l')


class RealPlayer(Player):
    """
    Класс игрока, который непосредственно сражается в уровнях.
    """

    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(sheet, columns, rows, x, y)
        self.look = 'right'
        self.y0 = self.y
        self.v0 = 50
        self.t = 0
        self.G = 7
        self.vy = 0
        self.need_jump = False
        self.hit_points = 3

    def jump(self):
        """
        Функция отвечает за прыжок персонажа.
        :return: Nothing
        """
        if self.need_jump:
            if self.v0:
                self.y = self.y0 - self.v0 * self.t + self.G * self.t ** 2 / 2
                self.vy = self.v0 - self.G * self.t
                self.t += 0.4
            if self.y > self.y0:
                self.v0 = 50
                self.t = 0
                self.y = self.y0
                self.need_jump = False
            self.rect.y = self.y

    def move(self, direction, speed=7):
        """
        Перемещение персонажа во время битв.
        :param direction: str направление движения
        :param speed: int скорость перемещения
        :return: Nothing
        """
        if direction == 'r':
            if self.x < WIDTH - 60:
                self.x += speed
                self.rect = self.rect.move(speed, 0)
        elif direction == 'l':
            if self.x > 0:
                self.x -= speed
                self.rect = self.rect.move(-speed, 0)


class DarkLord(pygame.sprite.Sprite):
    """
    Класс босса первого уровня, Тёмного Лорда.
    """

    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(enemy_group)
        self.hit_points = 1000
        self.pos = [x, y]
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.x = x
        self.y = y
        self.width = self.rect.width
        self.height = self.rect.height
        self.k = 0
        self.state = 'spawn'

    def cut_sheet(self, sheet, columns, rows):
        """
        Разрезает полученное изображение на равные части.
        :param sheet: str имя файла, хранящее изображение
        :param columns: int кол-во колонок, на которое нужно разбить изображение
        :param rows: int кол-во рядов, на которое нужно разбить изображение
        :return: Nothing
        """
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        """
        Функция отвечает за анимацию Лорда, в зависимости от его состояния (появляется или стоит)
        изменяется анимация.
        :return: Nothing
        """
        if self.k == 6:
            if self.state == 'spawn':
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
                if self.cur_frame == 16:
                    self.state = 'stay'
            elif self.state == 'stay':
                if self.cur_frame < 19:
                    self.cur_frame = self.cur_frame + 1
                else:
                    self.cur_frame = 16
            elif self.state == 'death':
                pass
            self.image = self.frames[self.cur_frame]
            self.k = 0

    def move(self):
        """
        Функция отвечает за случайное перемещение босса по локации, где происходит сражение.
        :return: Nothing
        """
        self.state = 'spawn'
        old_x = self.x
        self.x = randint(50, 650)
        if old_x > self.x:
            self.rect = self.rect.move(-(old_x - self.x), 0)
        else:
            self.rect = self.rect.move(self.x - old_x, 0)
        self.update()


class Tentacl(pygame.sprite.Sprite):
    """
    Класс щупальца, которым атакует Тёмный Лорд.
    """

    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(enemy_attack_group)
        self.hit_points = 40
        self.pos = [x, y]
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.x = x
        self.y = y
        self.width = self.rect.width
        self.height = self.rect.height
        self.k = 0
        self.state = 'spawn'

    def cut_sheet(self, sheet, columns, rows):
        """
        Разрезает полученное изображение на равные части.
        :param sheet: str имя файла, хранящее изображение
        :param columns: int кол-во колонок, на которое нужно разбить изображение
        :param rows: int кол-во рядов, на которое нужно разбить изображение
        :return: Nothing
        """
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        """
        Функция отвечает за анимацию щупальца, в зависимости от его состояния (спавнится или стоит)
        изменяется анимация.
        :return: Nothing
        """
        if self.k == 6:
            if self.state == 'spawn':
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
                if self.cur_frame == 8:
                    self.state = 'stay'
            elif self.state == 'stay':
                if self.cur_frame < 15:
                    self.cur_frame = self.cur_frame + 1
                else:
                    self.cur_frame = 8
            elif self.state == 'death':
                pass
            self.image = self.frames[self.cur_frame]
            self.k = 0


class Flame_Ball(pygame.sprite.Sprite):
    """
    Класс огненного снаряда, которым атакует Тёмный Лорд.
    """

    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(enemy_attack_group)
        self.pos = [x, y]
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.x = x
        self.y = y
        self.width = self.rect.width
        self.height = self.rect.height
        self.k = 0

    def cut_sheet(self, sheet, columns, rows):
        """
        Разрезает полученное изображение на равные части.
        :param sheet: str имя файла, хранящее изображение
        :param columns: int кол-во колонок, на которое нужно разбить изображение
        :param rows: int кол-во рядов, на которое нужно разбить изображение
        :return: Nothing
        """
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        """
        Анимация снаряда.
        :return: Nothing
        """
        if self.k == 6:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.image = self.frames[self.cur_frame]
            self.k = 0

    def spawn(self, x, y):
        """
        Функция отвечает за появление и перемещение снаряда.
        :param x: int координата x, к которой движется снаряд
        :param y: int координата y, к которой движется снаряд
        :return: Nothing
        """
        pos = (x, y)
        SPEED = 1
        if self.x == x and self.y == y:
            return
        if pos[0] == self.x:
            if self.y < pos[1]:
                self.y += SPEED
                self.rect = self.rect.move(0, SPEED)
            else:
                self.y -= SPEED
                self.rect = self.rect.move(0, -SPEED)
        elif pos[1] == self.y:
            if self.x < pos[0]:
                self.x += SPEED
                self.rect = self.rect.move(SPEED, 0)
            else:
                self.x -= SPEED
                self.rect = self.rect.move(-SPEED, 0)
        else:
            if self.x < pos[0]:
                self.x += SPEED
                self.rect = self.rect.move(SPEED, 0)
            else:
                self.x -= SPEED
                self.rect = self.rect.move(-SPEED, 0)
            if self.y < pos[1]:
                self.y += 1
                self.rect = self.rect.move(0, SPEED)
            else:
                self.y -= SPEED
                self.rect = self.rect.move(0, -SPEED)


class Hole(Tentacl):
    """
    Класс дыры, которая свидетельствует о скором появлении щупальца Тёмного Лорда.
    """

    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(sheet, columns, rows, x, y)

    def update(self):
        """
        Функция отвечает за анимацию дыры, в зависимости от состояния (появление или пребывание) анимация различна
        :return: Nothing
        """
        if self.k == 16:
            if self.state == 'spawn':
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
                if self.cur_frame == 4:
                    self.state = 'stay'
            elif self.state == 'stay':
                self.cur_frame = 4
            self.image = self.frames[self.cur_frame]
            self.k = 0


class Andromalius(DarkLord):
    """
    Класс босса второго уровня, Андромалиуса.
    """

    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(sheet, columns, rows, x, y)
        self.state = 'stay'
        self.speed = 10
        self.second_move = False

    def update(self):
        """
        Функция отвечает за анимацию Андромалиуса.
        :return: Nothing
        """
        if self.k == 8:
            if self.state == 'stay':
                if self.cur_frame < 23:
                    self.cur_frame = self.cur_frame + 1
                else:
                    self.cur_frame = 20
            elif self.state == 'death':
                pass
            self.image = self.frames[self.cur_frame]
            self.k = 0

    def move(self):
        """
        Функция отвечает за перемещение Андромалиуса от одного края арены до противоположного
        (босс опускается вниз, проносится и поднимается наверх).
        :return: Nothing
        """
        if self.state == 'go_right':
            if self.x < 750:
                self.x += self.speed
                self.rect = self.rect.move(self.speed, 0)
            else:
                self.state = 'up'
        elif self.state == 'go_left':
            if self.x > 50:
                self.x -= self.speed
                self.rect = self.rect.move(-self.speed, 0)
            else:
                self.state = 'up'
        elif self.state == 'down':
            if self.y < 365:
                self.y += self.speed
                self.rect = self.rect.move(0, self.speed)
            else:
                if self.x == 750:
                    self.state = 'go_left'
                else:
                    self.state = 'go_right'
        elif self.state == 'up':
            if self.y > 190:
                self.y -= self.speed
                self.rect = self.rect.move(0, -self.speed)
            else:
                self.state = 'stay'

    def fake_move(self):
        """
        Функция отвечает за фальшивое перемещение Андромалиуса (босс опускается вниз и сразу поднимается вверх).
        :return: Nothing
        """
        if self.state == 'down':
            if self.y < 365:
                self.y += self.speed
                self.rect = self.rect.move(0, self.speed)
            else:
                self.state = 'up'
        elif self.state == 'up':
            if self.y > 190:
                self.y -= self.speed
                self.rect = self.rect.move(0, -self.speed)
            else:
                self.state = 'stay'

    def high_move(self):
        """
        Функция отвечает за перемещение Андромалиуса, при котором он почти не изменяет высоту полёта
        (проносится сверху над игроком).
        :return: Nothing
        """
        if self.state == 'go_right':
            if self.x < 750:
                self.x += self.speed
                self.rect = self.rect.move(self.speed, 0)
            else:
                self.state = 'up'
        elif self.state == 'go_left':
            if self.x > 50:
                self.x -= self.speed
                self.rect = self.rect.move(-self.speed, 0)
            else:
                self.state = 'up'
        elif self.state == 'down':
            if self.y < 240:
                self.y += self.speed
                self.rect = self.rect.move(0, self.speed)
            else:
                if self.x == 750:
                    self.state = 'go_left'
                else:
                    self.state = 'go_right'
        elif self.state == 'up':
            if self.y > 190:
                self.y -= self.speed
                self.rect = self.rect.move(0, -self.speed)
            else:
                self.state = 'stay'

    def cool_move(self):
        """
        Функция отвечает за коронную атаку Андромалиуса: босс опускается вниз, перемещается к противоположному
        краю арены, возвращается назад и поднимается наверх.
        :return: Nothing
        """
        if self.state == 'go_right':
            if self.x < 750:
                self.x += self.speed
                self.rect = self.rect.move(self.speed, 0)
            elif not self.second_move:
                self.state = 'go_left'
                self.second_move = True
            else:
                self.state = 'up'
        elif self.state == 'go_left':
            if self.x > 50:
                self.x -= self.speed
                self.rect = self.rect.move(-self.speed, 0)
            elif not self.second_move:
                self.state = 'go_right'
                self.second_move = True
            else:
                self.state = 'up'
        elif self.state == 'down':
            if self.y < 365:
                self.y += self.speed
                self.rect = self.rect.move(0, self.speed)
            else:
                if self.x == 750:
                    self.state = 'go_left'
                else:
                    self.state = 'go_right'
        elif self.state == 'up':
            if self.y > 190:
                self.y -= self.speed
                self.rect = self.rect.move(0, -self.speed)
            else:
                self.state = 'stay'
                self.second_move = False


# основной персонаж
player = None
darklord = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
ball_group = pygame.sprite.Group()
portals_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
enemy_attack_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()


def generate_level(level):
    """
    Функция загружает списку с элементами карты.
    Возвращает x и y уровня
    :param level: list список элементов карты
    :return x, y: x, y уровня
    """
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '$':
                Tile('ground2', x, y)
            elif level[y][x] == '*':
                Tile('dirt', x, y)
            elif level[y][x] == '@':
                pass
    # вернем игрока, а также размер поля в клетках
    return x, y


def terminate():
    """
    Прерывание игры
    """
    pygame.quit()
    sys.exit()


def game():
    """
    Функция отвечает за основной мир, где игрок выбирает уровень.
    Глобальные переменные:
    player - для правильной работы с созданным спрайтом, удалить предыдущий объект, создать новый
    finished_levels - для чтения списка пройденных уровней
    x, y - для курсора при финальном окне
    :return: Nothing
    """
    global player, finished_levels, x, y
    check_level()
    level_x, level_y = generate_level(load_level('map.txt'))
    level = load_level('map.txt')
    SHOOTEVENTTYPE = pygame.USEREVENT + 1
    pygame.time.set_timer(SHOOTEVENTTYPE, 200)
    player = Player(load_image("hero-move.png"), 3, 4, 385, 550)
    pygame.mouse.set_visible(False)
    running = True
    go_right = False
    go_left = False
    go_up = False
    go_down = False
    portal = Portal(load_image("portal.png"), 5, 1, 64, 54, 1)
    portal2 = Portal(load_image("portal.png"), 5, 1, 448, 54, 2)
    text_coords = {1: (140, 50), 2: (530, 50)}
    leave = False
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (419 <= x <= 530 and 365 <= y <= 410) and len(finished_levels) == 2:  # 425, 365, 125, 50
                    restart()
                    player.kill()
                    game()
            if event.type == pygame.KEYDOWN:
                if event.unicode == k_right:
                    go_right = True
                elif event.unicode == k_left:
                    go_left = True
                elif event.unicode == k_up:
                    go_up = True
                elif event.unicode == k_down:
                    go_down = True
                elif event.key == pygame.K_x:
                    leave = True
            if event.type == pygame.KEYUP:
                if event.unicode == k_right:
                    go_right = False
                elif event.unicode == k_left:
                    go_left = False
                elif event.unicode == k_up:
                    go_up = False
                elif event.unicode == k_down:
                    go_down = False
        # Painting
        screen.fill((0, 0, 0))
        tiles_group.draw(screen)
        portals_group.draw(screen)
        portal.update()
        portal2.update()
        if go_up and go_right:
            player_group.draw(screen)
            player.update('u')
            player.move('ur')
        elif go_up and go_left:
            player_group.draw(screen)
            player.update('u')
            player.move('ul')
        elif go_down and go_right:
            player_group.draw(screen)
            player.update('d')
            player.move('dr')
        elif go_down and go_left:
            player_group.draw(screen)
            player.update('d')
            player.move('dl')
        elif go_right:
            player_group.draw(screen)
            player.update('r')
            player.move('r')
        elif go_left:
            player_group.draw(screen)
            player.update('l')
            player.move('l')
        elif go_up:
            player_group.draw(screen)
            player.update('u')
            player.move('u')
        elif go_down:
            player_group.draw(screen)
            player.update('d')
            player.move('d')
        else:
            hero = load_image('hero.png')
            screen.blit(hero, (player.x, player.y))
        if pygame.sprite.spritecollideany(player, portals_group):
            i = pygame.sprite.spritecollideany(player, portals_group).id
            if i not in finished_levels:
                if leave and (i == 1 or (i == 2 and 1 in finished_levels)):
                    call_level(i)
                elif i == 2 and 1 not in finished_levels:
                    print_text('Недоступно', text_coords[i][0], text_coords[i][1], (0, 0, 0), 20)
                else:
                    print_text('Нажмите X', text_coords[i][0], text_coords[i][1], (0, 0, 0), 20)
            else:
                print_text('Уровень пройден', text_coords[i][0], text_coords[i][1], (0, 0, 0), 20)
        else:
            leave = False
        ball_group.update()
        ball_group.draw(screen)
        if len(finished_levels) == 2:
            pygame.draw.rect(screen, (187, 165, 61), (250, 150, 500, 300))
            print_text('**************************************************', 250, 150)
            print_text('**************************************************', 250, 440)
            for i in range(160, 440, 10):
                print_text('*', 250, i)
                print_text('*', 740, i)
            print_text('%%% Поздравляем! %%%', 300, 175)
            print_text(f'Вы прошли игру!', 270, 275, (0, 0, 0), 17)
            print_text('Чтобы пройти игру заново нажмите ДА', 270, 325, (0, 0, 0), 17)
            pygame.draw.rect(screen, (55, 67, 69), (425, 365, 125, 50))
            print_text('>ДА<', 440, 372, (192, 192, 192))
            if pygame.mouse.get_focused():
                arrow = load_image('Cursor.png')
                screen.blit(arrow, (x, y))
        # Time
        pygame.display.flip()
        if player.k < 3:
            player.k += 1
        if portal.k < 10:
            portal.k += 1
        if portal2.k < 10:
            portal2.k += 1
        clock.tick(FPS)
    pygame.quit()


def first_level():
    """
    Функция отвечает за первый уровень.
    Глобальные переменные:
    player - для правильной работы с созданным спрайтом, удалить предыдущий объект, создать новый
    x, y - также для курсора, + здесь чтобы pycharm не ругался
    :return: Nothing
    """
    global player, x, y
    # далее прописаны события игрока и босса, названия говорят какое событие описано
    SHOOTEVENTTYPE = pygame.USEREVENT + 1
    BOSSMOVEEVENTTYPE = pygame.USEREVENT + 2
    BOSSATTACKEVENTTIME = pygame.USEREVENT + 3
    SPAWNHOLESEVENTTYPE = pygame.USEREVENT + 4
    DASHAVAILABLEEVENTTYPE = pygame.USEREVENT + 5
    PLAYERRESISTANCEEVENTTYPE = pygame.USEREVENT + 6
    BOSSBALLATTACKEVENTTIME = pygame.USEREVENT + 7
    # установка кд, таймеров для кастомных событий
    pygame.time.set_timer(BOSSMOVEEVENTTYPE, 3500)
    pygame.time.set_timer(BOSSATTACKEVENTTIME, 4100)
    pygame.time.set_timer(SPAWNHOLESEVENTTYPE, 1500)
    pygame.time.set_timer(DASHAVAILABLEEVENTTYPE, 1000)
    pygame.time.set_timer(PLAYERRESISTANCEEVENTTYPE, 0)
    pygame.time.set_timer(BOSSBALLATTACKEVENTTIME, 0)
    pygame.display.set_caption('Void Odyssey')
    pygame.mouse.set_visible(False)
    player.kill()
    player = RealPlayer(load_image("hero-move.png"), 3, 4, 100, 400)
    darklord = DarkLord(load_image("shadow3.png"), 4, 5, 600, 340)
    hp_color = (200, 0, 0)
    killed_tntcls = 0
    # списки для спрайтов
    balls = []
    boss_balls = []
    coins = []
    holes = []
    tentacles = []
    # булевые переменные, из названий понятно, назначение некоторых поясню
    running = True
    first_lvl_victory = False
    go_right = False
    go_left = False
    shoot_time = False
    shoot = False
    check_coins = True  # для корректного создания монет при победе над боссом
    need_move_boss = False
    hole_spawn = False
    boss_attack = False
    boss_ball_attack = False
    dash_available = True
    player_resistance = False
    change_available = True
    right_pos = False
    stop = False  # остановка уровня при победе и поражении
    target_x = 0
    target_y = 0
    lvl_up = 2
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                pass
            if event.type == SHOOTEVENTTYPE and shoot:
                shoot_time = True
            else:
                shoot_time = False
            if event.type == BOSSMOVEEVENTTYPE and darklord.hit_points != 0:
                need_move_boss = True
            if event.type == BOSSATTACKEVENTTIME:
                boss_attack = True
            if event.type == BOSSBALLATTACKEVENTTIME:
                boss_ball_attack = True
                n = 450
                right_pos = False
            if event.type == SPAWNHOLESEVENTTYPE and darklord.state == 'stay':
                hole_spawn = True
            if event.type == DASHAVAILABLEEVENTTYPE:
                dash_available = True
            if event.type == PLAYERRESISTANCEEVENTTYPE:
                player_resistance = False
                change_available = True
                pygame.time.set_timer(PLAYERRESISTANCEEVENTTYPE, 0)
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if ((450 <= x <= 550 and 350 <= y <= 400 and stop) or
                        (425 <= x <= 550 and 350 <= y <= 400 and first_lvl_victory)):
                    game()
            if event.type == pygame.KEYDOWN:
                if event.unicode == k_right:
                    go_right = True
                    player.look = 'right'
                elif event.unicode == k_dash and dash_available:
                    dash_available = False
                    if player.look == 'right':
                        player.move('r', 100)
                    else:
                        player.move('l', 100)
                elif event.unicode == k_left:
                    go_left = True
                    player.look = 'left'
                elif event.unicode == k_shoot:
                    pygame.time.set_timer(SHOOTEVENTTYPE, 300)
                    shoot = True
                elif event.unicode == k_jump:
                    player.need_jump = True
            if event.type == pygame.KEYUP:
                if event.unicode == k_right:
                    go_right = False
                elif event.unicode == k_left:
                    go_left = False
                elif event.unicode == k_shoot:
                    pygame.time.set_timer(SHOOTEVENTTYPE, 0)
                    shoot = False
        if player_resistance and change_available:
            pygame.time.set_timer(PLAYERRESISTANCEEVENTTYPE, 3000)
            change_available = False
        # Painting
        screen.fill((0, 0, 0))
        fon = pygame.transform.scale(load_image('castleinthedark.gif'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        screen.blit(load_image('heart_space.png'), (20, 20))
        screen.blit(load_image('heart_space.png'), (80, 20))
        screen.blit(load_image('heart_space.png'), (140, 20))
        pygame.draw.rect(screen, hp_color, (200, 20, darklord.hit_points // 2, 20))
        pygame.draw.rect(screen, (200, 200, 200), (200, 20, 500, 20), 2)
        if player.hit_points >= 1:
            screen.blit(load_image('heart_full.png'), (20, 20))
            if player.hit_points >= 2:
                screen.blit(load_image('heart_full.png'), (80, 20))
                if player.hit_points == 3:
                    screen.blit(load_image('heart_full.png'), (140, 20))
        if darklord.hit_points <= 300 and lvl_up == 1:
            lvl_up -= 1
            pygame.time.set_timer(BOSSMOVEEVENTTYPE, 1750)
            pygame.time.set_timer(BOSSATTACKEVENTTIME, 2050)
            pygame.time.set_timer(SPAWNHOLESEVENTTYPE, 750)
            pygame.time.set_timer(BOSSBALLATTACKEVENTTIME, 6000)
            hp_color = (100, 0, 50)
        elif darklord.hit_points <= 600 and lvl_up == 2:
            lvl_up -= 1
            pygame.time.set_timer(BOSSMOVEEVENTTYPE, 2300)
            pygame.time.set_timer(BOSSATTACKEVENTTIME, 2700)
            pygame.time.set_timer(SPAWNHOLESEVENTTYPE, 1000)
            pygame.time.set_timer(BOSSBALLATTACKEVENTTIME, 10000)
            hp_color = (150, 0, 0)
        if need_move_boss:
            darklord.k = 6
            darklord.cur_frame = 0
            darklord.move()
            need_move_boss = False
        if hole_spawn and len(tentacles) < 8:
            hole = Hole(load_image('tntcl_spawn.png'), 5, 1, player.x, 470)
            holes.append(hole)
            enemy_attack_group.add(hole)
            hole_spawn = False
        if boss_ball_attack and darklord.state != 'death' and len(boss_balls) <= 4:
            for i in range(4):
                boss_ball = Flame_Ball(load_image('flameball.png'), 4, 1,
                                       darklord.x + 50, darklord.y + 50)
                boss_balls.append(boss_ball)
            boss_ball_attack = False
        if boss_balls:
            n = 450
            n_right_pos = 0
            if not right_pos:
                for b in boss_balls:
                    if b.k < 6:
                        b.k += 1
                    b.spawn(n, 300)
                    if b.x == n and b.y == 300:
                        n_right_pos += 1
                    if pygame.sprite.collide_mask(player, b):
                        player.hit_points -= 1
                        player_resistance = True
                        b.kill()
                        boss_balls.remove(b)
                    n += 50
            if n_right_pos >= 4:
                right_pos = True
                target_x = player.x
                target_y = player.y
                n_right_pos = 0
            if right_pos:
                for b in boss_balls:
                    if b.k < 6:
                        b.k += 1
                    b.spawn(target_x, target_y)
                    if b.x == int(target_x) and b.y == int(target_y):
                        b.kill()
                        boss_balls.remove(b)
                    if pygame.sprite.collide_mask(player, b):
                        player.hit_points -= 1
                        player_resistance = True
                        b.kill()
                        boss_balls.remove(b)

        if boss_attack and len(tentacles) < 8 and darklord.state != 'death':
            for h in holes:
                tentacle = Tentacl(load_image('tentacles.png'), 8, 2, h.x, 350)
                h.kill()
                holes.remove(h)
                tentacles.append(tentacle)
            boss_attack = False
        if darklord.state == 'death':
            for h in holes:
                h.kill()
                if h in holes:
                    holes.remove(h)
            for t in tentacles:
                t.kill()
                if t in tentacles:
                    tentacles.remove(t)
            for b in boss_balls:
                b.kill()
                if b in boss_balls:
                    boss_balls.remove(b)
        enemy_group.draw(screen)
        enemy_attack_group.update()
        enemy_attack_group.draw(screen)
        if go_right:
            player_group.draw(screen)
            player.update('r')
            player.move('r')
        elif go_left:
            player_group.draw(screen)
            player.update('l')
            player.move('l')
        else:
            hero = load_image('hero.png')
            screen.blit(hero, (player.x, player.y))
        ball_group.update()
        ball_group.draw(screen)

        if shoot_time:
            if player.look == 'right':
                ball = Electro_Ball(load_image("electro-ball-right.png"), 3,
                                    2, player.x, player.y, player.look)
            else:
                ball = Electro_Ball(load_image("electro-ball-left.png"), 3,
                                    2, player.x, player.y, player.look)
            balls.append(ball)
            shoot_time = False
        darklord.update()
        player.jump()
        coin_group.draw(screen)
        if balls:
            for b in balls:
                if ((pygame.sprite.collide_mask(b, darklord)) and (darklord.hit_points > 0) and
                        darklord.state == 'stay' and not stop):
                    b.kill()
                    balls.remove(b)
                    darklord.hit_points -= 20
                elif b.x < 0 or b.x > 900:
                    b.kill()
                    balls.remove(b)
                for t in tentacles:
                    if (pygame.sprite.collide_mask(b, t)) and (t.hit_points > 0) and not stop:
                        t.hit_points -= 10
                        b.kill()
                        if b in balls:
                            balls.remove(b)
                    if t.hit_points <= 0:
                        killed_tntcls += 1
                        t.kill()
                        tentacles.remove(t)
        if tentacles:
            for t in tentacles:
                if t.k < 6:
                    t.k += 1
                if pygame.sprite.collide_mask(player, t) and t.state == 'stay' and not player_resistance:
                    player.hit_points -= 1
                    player_resistance = True
                    t.kill()
                    tentacles.remove(t)
        if pygame.sprite.collide_mask(player, darklord) and darklord.state == 'stay' and not player_resistance:
            player_resistance = True
            player.hit_points -= 1
        if holes:
            for h in holes:
                if h.k < 16:
                    h.k += 1
        if darklord.hit_points <= 0:
            darklord.state = 'death'
            darklord.k = 6
            if darklord.cur_frame > 0:
                darklord.cur_frame -= 1
            darklord.update()
            if darklord.cur_frame == 0:
                darklord.kill()
                tentacles = []
                # print_text('Победа', WIDTH // 2 - 100, HEIGHT - 630, (255, 255, 255))
        if darklord.state == 'death':
            # для монеток
            player_resistance = True
            if check_coins is True:
                if not coins:
                    for i in range(3):
                        d = i * 45
                        coin = Coin(load_image("coins.png"), 6, 1, darklord.x + d, darklord.y + 64)
                        coins.append(coin)
                for c in coins:
                    c.update()
                    if c.k < 10:
                        c.k += 1
                    if pygame.sprite.collide_mask(player, c):
                        c.kill()
                        coins.remove(c)
                        if not coins:
                            check_coins = False
                            new_balance = get_balance() + 3
                            update_balance(new_balance)
                            player.kill()
                            finish_level(1)
                            first_lvl_victory = True
        if first_lvl_victory:
            fon = pygame.transform.scale(load_image('castleinthedark.gif'), (WIDTH, HEIGHT))
            screen.blit(fon, (0, 0))
            pygame.draw.rect(screen, (187, 165, 61), (250, 150, 500, 300))
            print_text('**************************************************', 250, 150)
            print_text('**************************************************', 250, 440)
            for i in range(160, 440, 10):
                print_text('*', 250, i)
                print_text('*', 740, i)
            print_text('%%% Победа %%%', 325, 175)
            if player.hit_points == 1:
                print_text(f'У Вас осталось {player.hit_points} очко здоровья', 270, 225,
                           (0, 0, 0), 17)
            else:
                print_text(f'У Вас осталось {player.hit_points} очка здоровья', 270, 225,
                           (0, 0, 0), 17)
            print_text(f'Вы убили {killed_tntcls} щупалец', 270, 275, (0, 0, 0), 17)
            print_text('Ранг:', 270, 325, (0, 0, 0), 17)
            if player.hit_points == 3 and killed_tntcls >= 20:
                print_text('S', 325, 325, (230, 0, 0), 17)
            elif player.hit_points == 3 and killed_tntcls >= 15:
                print_text('A', 325, 325, (255, 79, 0), 17)
            elif player.hit_points >= 2 and killed_tntcls >= 10:
                print_text('B', 325, 325, (1, 50, 32), 17)
            else:
                print_text('C', 325, 325, (75, 83, 32), 17)
            pygame.draw.rect(screen, (55, 67, 69), (425, 350, 125, 50))
            print_text('>Ура<', 430, 355, (192, 192, 192))
            if pygame.mouse.get_focused():
                arrow = load_image('Cursor.png')
                screen.blit(arrow, (x, y))
        if player.hit_points <= 0:
            stop = True
            darklord.kill()
            player.kill()
            enemy_attack_group.empty()
            coin_group.empty()
            fon = pygame.transform.scale(load_image('castleinthedark.gif'), (WIDTH, HEIGHT))
            screen.blit(fon, (0, 0))
            pygame.draw.rect(screen, (200, 25, 25), (250, 150, 500, 300))
            print_text('**************************************************', 250, 150)
            print_text('**************************************************', 250, 440)
            for i in range(160, 440, 10):
                print_text('*', 250, i)
                print_text('*', 740, i)
            print_text('%%% Поражение %%%', 300, 175)
            print_text(f'У босса осталось {darklord.hit_points} очков здоровья', 270, 225,
                       (0, 0, 0), 17)
            print_text(f'Вы убили {killed_tntcls} щупалец', 270, 275, (0, 0, 0), 17)
            pygame.draw.rect(screen, (0, 0, 0), (450, 350, 100, 50))
            print_text('>ОК<', 455, 355, (255, 255, 255))
            if pygame.mouse.get_focused():
                arrow = load_image('Cursor.png')
                screen.blit(arrow, (x, y))
        # Time
        pygame.display.flip()
        if player.k < 3:
            player.k += 1
        if darklord.k < 6:
            darklord.k += 1
        clock.tick(FPS)
    pygame.quit()


def second_level():
    """
    Функция отвечает за второй уровень.
    Глобальные переменные:
    player - для правильной работы с созданным спрайтом, удалить предыдущий объект, создать новый
    x, y - также для курсора, + здесь чтобы pycharm не ругался
    :return: Nothing
    """
    global player, x, y
    tiles_group.empty()
    # здесь снова использована отрисовка уровня, конкретно земля
    level_x, level_y = generate_level(load_level('map_lvl2.txt'))
    level = load_level('map_lvl2.txt')
    # кастомные ивенты также как в первом лвле
    SHOOTEVENTTYPE = pygame.USEREVENT + 1
    BOSSATTACKEVENTTIME = pygame.USEREVENT + 3
    DASHAVAILABLEEVENTTYPE = pygame.USEREVENT + 5
    PLAYERRESISTANCEEVENTTYPE = pygame.USEREVENT + 6
    pygame.time.set_timer(BOSSATTACKEVENTTIME, 4100)
    pygame.time.set_timer(DASHAVAILABLEEVENTTYPE, 1000)
    pygame.time.set_timer(PLAYERRESISTANCEEVENTTYPE, 0)
    pygame.display.set_caption('Void Odyssey')
    pygame.mouse.set_visible(False)
    player.kill()
    player = RealPlayer(load_image("hero-move.png"), 3, 4, 100, 440)
    andromalius = Andromalius(load_image('andromalius.png'), 8, 3, 750, 140)
    hp_color = (200, 0, 0)
    lvl_up = 2
    # списки для спрайтов
    balls = []
    coins = []
    # список с паттернами для атак андромалиуса
    patterns = [andromalius.move, andromalius.fake_move, andromalius.high_move, andromalius.cool_move]
    choose = andromalius.move
    rnd_rank = choice(['S', 'A'])  # о великий рандом
    # булевые переменые
    go_right = False
    go_left = False
    shoot_time = False
    shoot = False
    running = True
    dash_available = True
    player_resistance = False
    change_available = True
    boss_attack = False
    stop = False
    second_lvl_victory = False
    check_coins = True  # для корректного создания монеток
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                pass
            if event.type == SHOOTEVENTTYPE and shoot:
                shoot_time = True
            else:
                shoot_time = False
            if event.type == DASHAVAILABLEEVENTTYPE:
                dash_available = True
            if event.type == BOSSATTACKEVENTTIME and andromalius.state == 'stay':
                boss_attack = True
            if event.type == PLAYERRESISTANCEEVENTTYPE:
                player_resistance = False
                change_available = True
                pygame.time.set_timer(PLAYERRESISTANCEEVENTTYPE, 0)
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if ((450 <= x <= 550 and 350 <= y <= 400 and stop) or
                        (425 <= x <= 550 and 350 <= y <= 400 and second_lvl_victory)):
                    game()
            if event.type == pygame.KEYDOWN:
                if event.unicode == k_right:
                    go_right = True
                    player.look = 'right'
                elif event.unicode == k_dash and dash_available:
                    dash_available = False
                    if player.look == 'right':
                        player.move('r', 100)
                    else:
                        player.move('l', 100)
                elif event.unicode == k_left:
                    go_left = True
                    player.look = 'left'
                elif event.unicode == k_shoot:
                    pygame.time.set_timer(SHOOTEVENTTYPE, 300)
                    shoot = True
                elif event.unicode == k_jump:
                    player.need_jump = True
            if event.type == pygame.KEYUP:
                if event.unicode == k_right:
                    go_right = False
                elif event.unicode == k_left:
                    go_left = False
                elif event.unicode == k_shoot:
                    pygame.time.set_timer(SHOOTEVENTTYPE, 0)
                    shoot = False
        if andromalius.hit_points <= 300 and lvl_up == 1:
            lvl_up -= 1
            pygame.time.set_timer(BOSSATTACKEVENTTIME, 3700)
            andromalius.speed = 18
            hp_color = (100, 0, 50)
        elif andromalius.hit_points <= 600 and lvl_up == 2:
            lvl_up -= 1
            pygame.time.set_timer(BOSSATTACKEVENTTIME, 3300)
            andromalius.speed = 14
            hp_color = (150, 0, 0)
        if player_resistance and change_available:
            pygame.time.set_timer(PLAYERRESISTANCEEVENTTYPE, 3000)
            change_available = False
        if pygame.sprite.collide_mask(andromalius,
                                      player) and not player_resistance and not andromalius.state == 'death':
            player_resistance = True
            player.hit_points -= 1
        # Painting
        screen.fill((0, 0, 0))
        fon = pygame.transform.scale(load_image('boloto.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        tiles_group.draw(screen)
        screen.blit(load_image('heart_space.png'), (20, 20))
        screen.blit(load_image('heart_space.png'), (80, 20))
        screen.blit(load_image('heart_space.png'), (140, 20))
        pygame.draw.rect(screen, hp_color, (200, 20, andromalius.hit_points // 2, 20))
        pygame.draw.rect(screen, (200, 200, 200), (200, 20, 500, 20), 2)
        if player.hit_points >= 1:
            screen.blit(load_image('heart_full.png'), (20, 20))
            if player.hit_points >= 2:
                screen.blit(load_image('heart_full.png'), (80, 20))
                if player.hit_points == 3:
                    screen.blit(load_image('heart_full.png'), (140, 20))
        if go_right:
            player_group.draw(screen)
            player.update('r')
            player.move('r')
        elif go_left:
            player_group.draw(screen)
            player.update('l')
            player.move('l')
        else:
            hero = load_image('hero.png')
            screen.blit(hero, (player.x, player.y))
        ball_group.update()
        ball_group.draw(screen)
        enemy_group.draw(screen)
        enemy_group.update()
        choose()

        if shoot_time:
            if player.look == 'right':
                ball = Electro_Ball(load_image("electro-ball-right.png"), 3,
                                    2, player.x, player.y, player.look)
            else:
                ball = Electro_Ball(load_image("electro-ball-left.png"), 3,
                                    2, player.x, player.y, player.look)
            balls.append(ball)
            shoot_time = False
        if boss_attack:
            boss_attack = False
            andromalius.state = 'down'
            choose = choice(patterns)
        player.jump()
        coin_group.draw(screen)
        if balls:
            for b in balls:
                if (pygame.sprite.collide_mask(b, andromalius)) and (andromalius.hit_points > 0) and not stop:
                    b.kill()
                    balls.remove(b)
                    andromalius.hit_points -= 20
                elif b.x < 0 or b.x > 900:
                    b.kill()
                    balls.remove(b)
        if andromalius.hit_points <= 0:
            andromalius.state = 'death'
            andromalius.k = 8
            if andromalius.cur_frame > 0:
                andromalius.cur_frame -= 1
            andromalius.update()
            if andromalius.cur_frame == 0:
                andromalius.kill()
                # print_text('Победа', WIDTH // 2 - 100, HEIGHT - 630, (255, 255, 255))
        if andromalius.state == 'death':
            # для монеток
            player_resistance = True
            if check_coins is True:
                if not coins:
                    for i in range(3):
                        d = i * 45
                        coin = Coin(load_image("coins.png"), 6, 1, andromalius.x + d, 440)
                        coins.append(coin)
                for c in coins:
                    c.update()
                    if c.k < 10:
                        c.k += 1
                    if pygame.sprite.collide_mask(player, c):
                        c.kill()
                        coins.remove(c)
                        if not coins:
                            check_coins = False
                            new_balance = get_balance() + 3
                            update_balance(new_balance)
                            player.kill()
                            finish_level(2)
                            second_lvl_victory = True
        if second_lvl_victory:
            fon = pygame.transform.scale(load_image('boloto.png'), (WIDTH, HEIGHT))
            screen.blit(fon, (0, 0))
            pygame.draw.rect(screen, (187, 165, 61), (250, 150, 500, 300))
            print_text('**************************************************', 250, 150)
            print_text('**************************************************', 250, 440)
            for i in range(160, 440, 10):
                print_text('*', 250, i)
                print_text('*', 740, i)
            print_text('%%% Победа %%%', 325, 175)
            if player.hit_points == 1:
                print_text(f'У Вас осталось {player.hit_points} очко здоровья', 270, 225,
                           (0, 0, 0), 17)
            else:
                print_text(f'У Вас осталось {player.hit_points} очка здоровья', 270, 225,
                           (0, 0, 0), 17)
            print_text(f'Вы увернулись от всех атак Андромалиуса!', 270, 275, (0, 0, 0), 17)
            print_text('Ранг:', 270, 325, (0, 0, 0), 17)
            if player.hit_points == 3:
                print_text(f'{rnd_rank}', 325, 325, (230, 0, 0), 17)
            elif player.hit_points == 2:
                print_text('B', 325, 325, (1, 50, 32), 17)
            else:
                print_text('C', 325, 325, (75, 83, 32), 17)
            pygame.draw.rect(screen, (55, 67, 69), (425, 350, 125, 50))
            print_text('>Ура<', 430, 355, (192, 192, 192))
            if pygame.mouse.get_focused():
                arrow = load_image('Cursor.png')
                screen.blit(arrow, (x, y))
        if player.hit_points <= 0:
            stop = True
            andromalius.kill()
            player.kill()
            enemy_attack_group.empty()
            coin_group.empty()
            fon = pygame.transform.scale(load_image('boloto.png'), (WIDTH, HEIGHT))
            screen.blit(fon, (0, 0))
            pygame.draw.rect(screen, (200, 25, 25), (250, 150, 500, 300))
            print_text('**************************************************', 250, 150)
            print_text('**************************************************', 250, 440)
            for i in range(160, 440, 10):
                print_text('*', 250, i)
                print_text('*', 740, i)
            print_text('%%% Поражение %%%', 300, 175)
            print_text(f'У босса осталось {andromalius.hit_points} очков здоровья', 270, 225,
                       (0, 0, 0), 17)
            print_text('Андромалиус следит.', 270, 275, (0, 0, 0), 17)
            pygame.draw.rect(screen, (0, 0, 0), (450, 350, 100, 50))
            print_text('>ОК<', 455, 355, (255, 255, 255))
            if pygame.mouse.get_focused():
                arrow = load_image('Cursor.png')
                screen.blit(arrow, (x, y))
        pygame.display.flip()
        if player.k < 3:
            player.k += 1
        if andromalius.k < 8:
            andromalius.k += 1
        clock.tick(FPS)
    pygame.quit()


def start_screen():
    """
    Функция отвечает за начальное окно.
    Глобальные переменные:
    x, y - для расположения курсора в том же месте что и при выходе из настроек/для передачи в окно настроек
    :return: Nothing
    """
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
                    settings_screen()
                else:
                    game()
        # Painting
        screen.fill((0, 0, 0))
        fon = pygame.transform.scale(load_image('environment_forest_evening.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
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
    """
    Функция отвечает за окно настроек и сохранение выбранных пользователем настроек.
    Глобальные переменные:
    x, y - для расположения курсора в том же месте что и в меню
    k_right, k_left, k_up, k_down, k_shoot, k_jump, k_dash - запоминание клавиш выбранных пользователем для
    использования в самой игре
    :return: Nothing
    """
    global x, y, k_right, k_left, k_up, k_down, k_shoot, k_jump, k_dash
    error = False
    pygame.display.set_caption('Settings')
    color_right = (0, 0, 0)  # цвет надписи, отвечающий за кнопку "вправо". Далее по аналогии
    inp_right = False  # означает, надо ли изменять кнопку "вправо". Далее по аналогии
    color_left = (0, 0, 0)
    inp_left = False
    color_up = (0, 0, 0)
    inp_up = False
    color_down = (0, 0, 0)
    inp_down = False
    color_shoot = (0, 0, 0)
    inp_shoot = False
    color_jump = (0, 0, 0)
    inp_jump = False
    color_dash = (0, 0, 0)
    inp_dash = False
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
                    if (len(set(list([k_right, k_left, k_up, k_down, k_shoot, k_dash]))) ==
                            len([k_right, k_left, k_up, k_down, k_shoot, k_dash]) and
                            len([k_right, k_left, k_up, k_down, k_shoot, k_dash]) ==
                            len(''.join([k_right, k_left, k_up, k_down, k_shoot, k_dash]))):
                        return [k_right, k_left, k_up, k_down, k_shoot, k_dash]
                    else:
                        error = True
                if 337 <= x <= 412 and 350 <= y <= 390 and error:
                    error = False
                if 375 <= x <= 405 and 44 <= y <= 85:
                    color_right = (150, 150, 150)
                    inp_right = True
                else:
                    color_right = (0, 0, 0)
                    inp_right = False
                if 375 <= x <= 405 and 94 <= y <= 135:
                    color_left = (150, 150, 150)
                    inp_left = True
                else:
                    color_left = (0, 0, 0)
                    inp_left = False
                if 375 <= x <= 405 and 144 <= y <= 185:
                    color_up = (150, 150, 150)
                    inp_up = True
                else:
                    color_up = (0, 0, 0)
                    inp_up = False
                if 375 <= x <= 405 and 194 <= y <= 235:
                    color_down = (150, 150, 150)
                    inp_down = True
                else:
                    color_down = (0, 0, 0)
                    inp_down = False
                if 375 <= x <= 405 and 244 <= y <= 285:
                    color_shoot = (150, 150, 150)
                    inp_shoot = True
                else:
                    color_shoot = (0, 0, 0)
                    inp_shoot = False
                if 375 <= x <= 405 and 294 <= y <= 335:
                    color_jump = (150, 150, 150)
                    inp_jump = True
                else:
                    color_jump = (0, 0, 0)
                    inp_jump = False
                if 375 <= x <= 405 and 344 <= y <= 385:
                    color_dash = (150, 150, 150)
                    inp_dash = True
                else:
                    color_dash = (0, 0, 0)
                    inp_dash = False
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
                elif inp_jump:
                    if event.unicode in 'qwertyuiopasdfghjklzxcvbnm ':
                        k_jump = event.unicode
                    inp_jump = False
                    color_jump = (0, 0, 0)
                elif inp_dash:
                    if event.unicode in 'qwertyuiopasdfghjklzxcvbnm ':
                        k_dash = event.unicode
                    inp_dash = False
                    color_dash = (0, 0, 0)
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
        screen.blit(pergament, (394, 294))
        screen.blit(pergament, (394, 344))
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
        print_text('Прыжок', 50, 300)
        print_text(k_dash, 400, 350, color_dash)
        print_text('Рывок', 50, 350)
        if k_jump == ' ':
            print_text('''SPA
CE''', 400, 300, color_jump, 12)
        else:
            print_text(k_jump, 400, 300, color_jump)
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


def get_balance():
    """
    Функция для получения баланса игрока.
    :return: n монет на балансе игрока
    """
    filename = os.path.join('data', 'localgamedb.sql')
    con = sqlite3.connect(filename)
    cur = con.cursor()
    current_balance = cur.execute('''select balance
             from player where id=?''', (1,)).fetchone()[0]
    con.close()
    return current_balance


def update_balance(n):
    """
    Функция чтобы обновить баланс игрока в БД
    добавить n монет (в основном 3)
    !изменение БД!
    :param n: int кол-во монет
    :return: Nothing
    """
    filename = os.path.join('data', 'localgamedb.sql')
    con = sqlite3.connect(filename)
    cur = con.cursor()
    cur.execute('''UPDATE Player
                SET balance = ?
                WHERE id = 1''', (n,))
    con.commit()
    con.close()


def finish_level(level_id):
    """
    Функция для обавление пройденного уровня по level_id в БД
    !изменение БД!
    :param level_id: int айди лвла
    :return: Nothing
    """
    filename = os.path.join('data', 'localgamedb.sql')
    con = sqlite3.connect(filename)
    cur = con.cursor()
    cur.execute('''INSERT INTO Levels(user_id,level_id)
                             VALUES(?,?)''', (1, level_id))
    con.commit()
    con.close()


def check_level():
    """
    Получение списка пройденных уровней игрока.
    !чтение из БД!
    Изменение глобального списка finished_levels
    no params
    :return: Nothing
    """
    global finished_levels
    finished_levels = []
    filename = os.path.join('data', 'localgamedb.sql')
    con = sqlite3.connect(filename)
    cur = con.cursor()
    levels = cur.execute('''select level_id
             from Levels where user_id=?''', (1,)).fetchall()
    con.close()
    for el in levels:
        finished_levels.append(el[0])


def call_level(i):
    """
    Функция, чтобы запустить уровень.
    Вызов функции уровня
    :param i: int, айди уровня
    :return: Nothing
    """
    if i == 1:
        first_level()
    else:
        second_level()


def restart():
    """
    Сбросить все данные о прохождении игры. Начать заново.
    !Изменение БД!
    :return: Nothing
    """
    update_balance(0)
    filename = os.path.join('data', 'localgamedb.sql')
    con = sqlite3.connect(filename)
    cur = con.cursor()
    cur.execute('''DELETE from levels''')
    con.commit()
    con.close()


start_screen()
