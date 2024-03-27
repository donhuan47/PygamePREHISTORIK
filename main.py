import random
import sys
import pygame as pg

pg.init()
# pg.key.set_repeat(2, 70)

size = WIDTH, HEIGHT = 800, 600
sc = pg.display.set_mode(size)
pg.display.set_caption('Prehistoric True Story')
clock = pg.time.Clock()


# bg_music = pg.mixer.Sound('audio/music.wav')
# bg_music.play(loops = -1)


def start_screen():
    intro_text = [
        "Прехисторик 2", "",
        "Помоги выжить древнему человеку, ведь повсюду опасности ",
        "управляй стрелками ",
        "помоги ему избежать вымирания", '',
        'Нажми для старта']

    fon = pg.transform.scale(pg.image.load('start.jpg'), (WIDTH, HEIGHT))

    font = pg.font.Font(None, 30)

    while 1:  # Зацикливаем стартовый экран пока не нажмут эникей
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                return  # начинаем игру

        sc.blit(fon, (0, 0))
        text_coord = 50
        for line in intro_text:
            x = random.randrange(-1, 1)  # Строки будут немного подрагиваться
            string_rendered = font.render(line, True, pg.Color('red'))
            intro_rect = string_rendered.get_rect()

            text_coord += 10 + x
            intro_rect.top = text_coord
            # intro_rect.x = 10
            text_coord += intro_rect.height
            sc.blit(string_rendered, intro_rect)

        pg.display.flip()
        clock.tick(60)


def gameover_screen():
    image = pg.image.load("go.jpg")
    image = pg.transform.scale(image, size)  # Подгоняем размер картинки на весь экран
    rect = image.get_rect()
    rect.right = 0  # Будем выдвигать картинку из левой стороны окна. Начальное положение

    while 1:  # Зацикливаем  экран
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                global hero, start_time
                hero = Hero((WIDTH * 0.45, 150))
                hero.health = 3
                start_time = pg.time.get_ticks()

                hero.dead_sound.stop()
                return  # продолжаем
        sc.blit(image, rect)
        pg.display.flip()
        clock.tick(60)
        if rect.left < 0:
            rect.left += 8


class Background(pg.sprite.Sprite):
    def __init__(self, img_path, move_speed=1):
        super().__init__(background)  # Помещаем в группу background
        # self.image = pg.transform.scale(pg.image.load('sky.png'), (80, 80))
        self.image = pg.image.load(img_path)
        self.rect = self.image.get_rect()
        self.move_speed = move_speed


class Grass(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)  # Помещаем в группу all_sprites
        self.image = pg.transform.scale(pg.image.load('grass.png'), (80, 80))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        # self.rect.height = 20
        # self.mask = pg.mask.from_surface(self.image)


class Bone(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(bones_group)  # Помещаем в группу
        self.angle = 0  # начальный угол
        self.dangle = random.randrange(-30, 30)  # произвольное вращение разных костей
        self.x = pos[0]
        self.y = pos[1]
        self.dy_gravity = -random.randint(15, 45)
        self.dx = random.randint(5, 15)  # speed horizontal
        self.image_not_rotated = pg.image.load('bone.png')  # оригиналы не меняем
        self.rect_not_rotated = self.image_not_rotated.get_rect()

        self.image = pg.image.load('bone.png')  # эти будем поворачивать на нек угол
        self.rect = self.image.get_rect(center=(self.x, self.y))

        self.send_bone_sound = pg.mixer.Sound('snd_bone.mp3')
        self.send_bone_sound.set_volume(0.1)

        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        self.angle += self.dangle
        self.dy_gravity += 1
        self.x -= self.dx
        self.y += self.dy_gravity
        self.image = pg.transform.rotozoom(self.image_not_rotated, self.angle, 1)
        self.rect = self.image.get_rect(center=(self.x, self.y))

        if self.rect.x < 10 or self.rect.y > 580:
            self.kill()
        # for line in intro_text:
        #     string_rendered = font.render(line, 0, pg.Color('red'), pg.Color('green'))
        #     intro_rect = string_rendered.get_rect()


class Hero(pg.sprite.Sprite):
    Vy = 0

    def __init__(self, pos):
        super().__init__(hero_group)  # Помещаем в  группу
        self.facing_right = 1  # Флаг что чел лицом смотрит направо
        self.on_ground = 0
        self.dx = 0  # Сколько надо прибавить к текущей координате на каждом обновлении
        self.dy = 0
        self.speed = 8
        self.health = 3
        self.image = pg.transform.scale(pg.image.load('inair.png'), (80, 120))
        self.rect = self.image.get_rect(center=pos)

        self.walk_spr = []  # набор спрайтов при хождении
        self.walk_spr.append(pg.image.load('walk1.png'))
        self.walk_spr.append(pg.image.load('walk2.png'))
        self.walk_spr.append(pg.image.load('walk3.png'))
        self.idle_spr = []  # Набор спрайтов при стоянии на месте
        self.idle_spr.append(pg.image.load('idle1.png'))
        self.idle_spr.append(pg.image.load('idle2.png'))
        self.idle_spr.append(pg.image.load('idle3.png'))
        self.cur_sprite = 0  # Запоминаем Текущий спрайт ( общий счетчик для всех состояний действий)
        self.gravity = 0.1

        self.jump_sound = pg.mixer.Sound('jump.mp3')
        self.hit_sound = pg.mixer.Sound('hit.mp3')
        self.hit_sound2 = pg.mixer.Sound('hit2.mp3')
        self.fall_sound = pg.mixer.Sound('falling.mp3')
        self.dead_sound = pg.mixer.Sound('dye.mp3')
        self.jump_sound.set_volume(0.05)

    def get_keys_pressed(self):
        keys = pg.key.get_pressed()  # снимаем маску зажатых клавиш
        if (keys[pg.K_SPACE] or keys[pg.K_UP]) and (keys[pg.K_RIGHT] or keys[pg.K_LEFT]):
            hero.jump()
            if keys[pg.K_LEFT]:
                self.dx = -1 * self.speed
                self.facing_right = 0
                self.going_left_animate()
            elif keys[pg.K_RIGHT]:
                self.dx = 1 * self.speed
                self.facing_right = 1
                self.going_right_animate()

        elif keys[pg.K_SPACE] or keys[pg.K_UP]:
            self.jump()
            self.dy = - 1 * self.speed
        elif keys[pg.K_DOWN]:
            self.dy = 1 * self.speed
        elif keys[pg.K_RIGHT]:
            self.dx = 1 * self.speed
            self.facing_right = 1
            self.going_right_animate()
        elif keys[pg.K_LEFT]:
            self.dx = -1 * self.speed
            self.facing_right = 0
            self.going_left_animate()
        else:
            self.idle_animate()
            self.dx = 0
            self.dy = 0

    def update(self):
        self.get_keys_pressed()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()

        # pg.draw.rect(sc, (255, 255, 255), self.rect)
        if self.rect.top > HEIGHT:  # Упал ниже экрана Конец игры
            self.fall_sound.play()
            gameover_screen()

        # Проверка что в нас попал предмет
        if pg.sprite.spritecollide(hero_group.sprite, bones_group, True):
            bones_group.empty()
            self.health -= 1
            self.hit_sound.play()
            self.hit_sound2.play()
            if self.health == 0:
                self.dead_sound.play()
                gameover_screen()

        if not self.on_ground:
            if self.facing_right:
                self.image = pg.image.load('inair.png')
            else:
                self.image = pg.transform.flip(pg.image.load('inair.png'), 1, 0)  # Если стоял лицом влево то зеркалим

    def idle_animate(self):
        if self.on_ground:
            if self.facing_right:  # Если смотрит направо то спрайты не переворачиваем
                self.image = self.idle_spr[int(self.cur_sprite)]
            else:
                self.image = pg.transform.flip(self.idle_spr[int(self.cur_sprite)], 1, 0)  # Повернуть спрайт влево
            self.cur_sprite = (self.cur_sprite + 0.1) % 3  # три кадра поэтому перебор 0 1 2  0.1 -скорость смены

    def going_right_animate(self):
        # if self.on_ground:
        self.image = self.walk_spr[int(self.cur_sprite)]
        self.cur_sprite = (self.cur_sprite + 0.1) % 3  # три кадра поэтому перебор 0 1 2
        # else:
        #     self.image = pg.image.load('inair.png')

    def going_left_animate(self):
        if self.on_ground:
            self.image = pg.transform.flip(self.walk_spr[int(self.cur_sprite)], 1, 0)  # Поворот налево лицом
            self.cur_sprite = (self.cur_sprite + 0.1) % 3  # три кадра поэтому перебор 0 1 2
        else:
            self.image = pg.transform.flip(pg.image.load('inair.png'), 1, 0)

    def horizontal_movement_collision(self):
        self.rect.x += self.dx  # Смещаем
        for sprite in all_sprites.sprites():
            if sprite.rect.colliderect(self.rect):  # Если с кемто столкнулся
                if self.dx < 0:  # И при этом шел влево то значит столкнулся левым краем и
                    self.rect.left = sprite.rect.right  # задаем правильную позицию. Останавливаем.
                elif self.dx > 0:  # Если шел вправо
                    self.rect.right = sprite.rect.left  # то тоже задаем правильную позицию.
                self.dx = 0

    def vertical_movement_collision(self):
        # self.rect.y += self.dy  # Смещаем
        self.apply_gravity()
        # self.on_ground = 0
        for sprite in all_sprites.sprites():
            if sprite.rect.colliderect(self.rect):  # Если с кемто столкнулся
                if self.dy < 0:  # И при этом двигался вверх то значит столкнулся верхним краем и
                    self.rect.top = sprite.rect.bottom  # задаем правильную позицию. Останавливаем.
                    self.on_ground = 0
                    # self.rect.y += 5
                    self.dy = 0

                elif self.dy > 0:  # Если двигался вниз
                    self.rect.bottom = sprite.rect.top  # то тоже задаем правильную позицию.
                    self.on_ground = 1
                    self.gravity = 0.1
                self.dy = 0

    def jump(self):
        if self.on_ground:
            self.gravity = -25
            self.jump_sound.play()
            self.on_ground = 0

    def apply_gravity(self):

        self.gravity += 1
        print("gravity =", self.gravity, 'dy', self.dy)
        self.dy = self.gravity
        self.rect.y += self.dy


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj, coeff=1):  # Коэффициент смещения для фоновых картинок будет меньше 1
        if hero.rect.centerx > WIDTH * 0.6:  # сместить камеру если игрок прошел 60% экрана
            self.dx = - (hero.rect.centerx - WIDTH * 0.6)
        elif hero.rect.centerx < WIDTH * 0.4:  #
            self.dx = - (hero.rect.centerx - WIDTH * 0.4)  # Игрок идет налево. Все сдвишаем напарво dx > 0
        if hero.rect.top < HEIGHT * 0.1:  # Игрок оказался близко у верхней границы
            self.dy = HEIGHT * 0.1 - hero.rect.top
        elif hero.rect.bottom > HEIGHT * 0.95:  # Игрок оказался близко у нижней границы
            self.dy = -(hero.rect.bottom - HEIGHT * 0.95)

        obj.rect.x += self.dx * coeff  # само смещение объекта
        obj.rect.y += self.dy * coeff


background = pg.sprite.Group()
all_sprites = pg.sprite.Group()

# hero_group = pg.sprite.Group()
hero_group = pg.sprite.GroupSingle()

bones_group = pg.sprite.Group()

camera = Camera()
hero = Hero((WIDTH * 0.45, 100))

#  Создаем уровень
level_list = []
f = open('level1.txt')
for i in f:
    level_list.append(i.rstrip())
level_list = level_list[::-1]  # переворачиваем порядок строк тк отрисовку начинаем с нижней строки
for row_n, row in enumerate(level_list, start=1):
    for pos_n, elem in enumerate(row):
        if elem == "*":
            Grass((pos_n * 80, 600 - 80 * row_n))

bone_timer = pg.USEREVENT + 1  # Номер события
pg.time.set_timer(bone_timer, random.randint(1000, 10000))  # Которое будем добавлять в очередь каждые 1000 мс

# bg_img_sufr = pg.image.load('sky.png')  # фоновая картинка
# bg_img_rect = bg_img_sufr.get_rect()


sky = Background('sky.png', 0.1)


def update_world():
    sc.fill(pg.Color('white'))

    # sc.blit(bg_img_sufr, bg_img_rect)

    background.draw(sc)
    all_sprites.draw(sc)
    all_sprites.update()
    hero_group.draw(sc)
    hero_group.update()
    pg.display.update()
    bones_group.draw(sc)
    bones_group.update()
    display_score()

    pg.display.update()  # Если убрать то кость не будет рисаоватья. Почему


start_time = 0
test_font = pg.font.Font('font/Pixeltype.ttf', 50)


def display_score():
    current_time = int(pg.time.get_ticks() / 1000) - start_time
    score_surf = test_font.render(f'Score: {current_time} Health:{hero.health}', False, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(400, 50))
    sc.blit(score_surf, score_rect)
    return current_time


start_screen()
while 1:
    start_time = 0  # int(pygame.time.get_ticks() / 1000)
    for i in pg.event.get():
        if i.type == pg.QUIT:
            sys.exit()

        if i.type == bone_timer:
            bone = Bone((random.randint(600, 800), 550))
            bone.send_bone_sound.play()

    # for bg in background:
    #     camera.apply(bg)
    #
    for sprite in all_sprites:  # Двигаем все объекты при смещении камеры
        camera.apply(sprite)
    for sprite in hero_group:  # Двигаем персонажа при смещении камеры
        camera.apply(sprite)

    # for sprite in bones_group:  # удалить
    #     camera.apply(sprite)

    camera.dy = 0  # НУЖНО однократное смещение поэтому сдвиг обнуляем
    camera.dx = 0

    update_world()
    clock.tick(60)
