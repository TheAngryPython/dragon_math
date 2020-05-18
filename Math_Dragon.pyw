# обновление
import requests
import json
import time, threading
import os

update = True
version = '0.1.1'

versions = json.loads(requests.get('https://theangrypython.github.io/dm/versions.json').text)
if versions['stable'] != version and update:
    from tkinter import *
    import tkinter.ttk as ttk
    import zipfile
    import shutil
    root = Tk()
    text = Text(width=25, height=5, wrap=WORD)
    text.pack()

    def progress():
        text.insert(1.0, f'Downloading version {versions["stable"]}')
        f = open(f'update-{versions["stable"]}.zip', 'wb')
        f.write(requests.get(versions["path"]).content)
        f.close()
        text.insert(1.0, f'\nUnpacking')
        z = zipfile.ZipFile(f'update-{versions["stable"]}.zip', 'r')
        z.extractall('update')
        z.close()
        os.remove(f'update-{versions["stable"]}.zip')
        text.insert(1.0, f'\nApplying')
        folder = os.path.dirname(os.path.realpath('__file__'))
        zip = os.path.join(os.path.join(folder, 'update'), os.listdir(os.path.join(folder, 'update'))[0])
        def ld(l, folder=os.path.dirname(os.path.realpath('__file__'))):
            dir = os.listdir(l)
            for name in dir:
                if os.path.isdir(os.path.join(l, name)):
                    os.makedirs(os.path.join(folder, name))
                    ld(os.path.join(l, name), os.path.join(folder, name))
                else:
                    text.insert(1.0, '\n'+name)
                    try:
                        try:
                            os.remove(os.path.join(folder, name))
                        except:
                            pass
                        os.rename(os.path.join(l, name), os.path.join(folder, name))
                        os.remove(os.path.join(l, name))
                    except:
                        pass
        ld(zip)
        shutil.rmtree(os.path.join(os.path.join(folder, 'update')))
        text.insert(1.0, '\n\nDONE! restart program')
        time.sleep(9999999)
        quit()

    threading.Thread(target=progress).start()
    root.mainloop()
    quit()

import pygame
import pygame_menu
import random
from pygame.locals import *
from socket import gethostname
import pyAesCrypt
import io
import logging

# настройка сохранения конфига
appdata_folder = os.path.join(os.environ['LOCALAPPDATA'], 'EgTer')
app_folder = os.path.join(appdata_folder, 'Math Dragon')
config_file = os.path.join(app_folder, 'data')

if not os.path.exists(appdata_folder):
    os.makedirs(appdata_folder)
if not os.path.exists(app_folder):
    os.makedirs(app_folder)
if not os.path.exists(config_file):
    fIn = io.BytesIO(json.dumps({}).encode())
    fCiph = io.BytesIO()
    pyAesCrypt.encryptStream(fIn, fCiph, gethostname(), 64 * 1024)
    f = open(config_file, 'wb')
    f.write(fCiph.getvalue())
    f.close()

try:
    pyAesCrypt.decryptFile(config_file+".aes", config_file, gethostname(), 64 * 1024)
    f = open(config_file, 'r')
    config = json.loads(f.read())
    f.close()
    os.remove(config_file)
except:
    config = {}

def cfg_save():
    global config
    f = open(config_file, 'w')
    f.write(json.dumps(config))
    f.close()
    pyAesCrypt.encryptFile(config_file, config_file+".aes", gethostname(), 64 * 1024)
    os.remove(config_file)

def quit_game():
    cfg_save()
    pygame.quit()

try:
    config['record']
except:
    config['record'] = 0

try:
    config['games']
except:
    config['games'] = 0

try:
    config['record_name']
except:
    config['record_name'] = 'you'

# настройка логгинга
logging.basicConfig(filename=os.path.join(app_folder, 'log.txt'), level=logging.INFO)

# настройка разрешения
WIDTH = 600
HEIGHT = 400
FPS = 60

# переменные
difficulty = 'Easy'
nums = []
a_num = 0
mn = 0
mx = 9
score = 0
username = random.choice(['Drago', 'Math', 'pro', 'profi'])

# Создаем игру и окно
pygame.init()
pygame.mixer.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.init()
all_sprites = pygame.sprite.Group()

# настройка папки ассетов
# game_folder = os.path.dirname(__file__)
game_folder = os.path.dirname(os.path.realpath('__file__'))
assets_folder = os.path.join(game_folder, 'assets')
img_folder = os.path.join(assets_folder, 'img')
ex_img = {l: os.path.join(img_folder, 'ex_'+l+'.png') for l in '0123456789+'}
fonts_folder = os.path.join(assets_folder, 'fonts')
ex_font = os.path.join(fonts_folder, 'ex.ttf')
bg_folder = os.path.join(img_folder, 'bg')
sounds_folder = os.path.join(assets_folder, 'sounds')
music_folder = os.path.join(sounds_folder, 'music')

# иконка
pygame.display.set_icon(pygame.image.load("icon.ico"))

# настройка звуков
sounds = {}
sounds['true'] = [pygame.mixer.Sound(os.path.join(sounds_folder, 'true_answer_'+str(i)+'.wav')) for i in [1,2,3]]
sounds['false'] = [pygame.mixer.Sound(os.path.join(sounds_folder, 'false_answer_1.wav'))]
sounds['speed_up'] = [pygame.mixer.Sound(os.path.join(sounds_folder, 'speed_up_'+str(i)+'.wav')) for i in [1,2,3]]
sounds['record'] = [pygame.mixer.Sound(os.path.join(sounds_folder, 'new_record_'+str(i)+'.wav')) for i in [1]]
sounds['die'] = [pygame.mixer.Sound(os.path.join(sounds_folder, 'die_'+str(i)+'.wav')) for i in [1]]
sounds['menu_select'] = [pygame.mixer.Sound(os.path.join(sounds_folder, 'menu_select_'+str(i)+'.wav')) for i in [1]]

# настройка музыки
music = {name: os.path.join(music_folder, name) for name in os.listdir(music_folder)}

# Задаем цвета
WHITE = (255, 255, 255)
WHITE_GRAY = (225, 225, 225)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# скорость игры
SPEED_Y = 5
SPEED_EX = -1
SPEED_EX_NEXT = 0
SPEED_EX_NEXT_SCORE = 3
EX_ADD = 1
TIME = time.time()
NEXT_EX = 0

# прозрачная поверхность
class Foreground(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.Surface((WIDTH, HEIGHT))
        self.image.fill(RED)
        self.image.set_alpha(0)
        self.alpha = 0
        self.step = 0
        self.time = TIME
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = (0, 0)
        self.type = 'none'
        self.event = 'idle'
        self.alpha_to = 60

    def update(self):
        if self.event == 'warn' and self.step != 6:
            self.step += 1
            self.image.set_alpha(self.alpha)
        elif self.event == 'warn':
            self.type = 'none'
            self.step = 0
            self.alpha = 0
            self.image.set_alpha(self.alpha)

    def warn(self):
        self.alpha = self.alpha_to
        self.event = 'warn'

# фон
class Background(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load(os.path.join(bg_folder, random.choice(os.listdir(bg_folder)))).convert()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = (0, 0)

# игрок
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.level = 2
        self.time = TIME
        self.im = 1
        self.images = [pygame.image.load(os.path.join(img_folder, 'player-'+str(i)+'.png')).convert_alpha() for i in [1,2,3,4]]
        self.image = self.images[0]
        self.anim_speed = 0.1
        self.size = 50
        self.rot = 0
        self.rot_to = 0
        self.rect = self.image.get_rect()
        self.rect.center = (int(WIDTH / 8), int(HEIGHT / 2))
        self.rot = 0
        self.last_update = pygame.time.get_ticks()
        self.event = 'idle'

    def update(self):
        if self.event == 'idle':
            self.rot_to = 0
        self.event = 'idle'
        if self.rot_to > self.rot:
            self.rot += 1
            self.image = pygame.transform.rotate(self.images[self.im], self.rot)
        elif self.rot_to == self.rot:
            pass
        else:
            self.rot -= 1
            self.image = pygame.transform.rotate(self.images[self.im], self.rot)
        if self.time < (TIME - self.anim_speed):
            self.image = pygame.transform.rotate(self.images[self.im], self.rot)
            self.time = TIME
            self.im += 1
            if self.im > 3:
                self.im = 0
        self.anim_speed = 0.1

    def up(self):
        if self.rect.y - 10 > 0:
            self.rect.y -= SPEED_Y
            self.anim_speed = 0.06
            self.rot_to = 9
            self.event = 'up'
        else:
            self.event = 'idle'

    def down(self):
        if self.rect.y + 70 < (HEIGHT - self.size):
            self.rect.y += SPEED_Y
            self.anim_speed = 0.14
            self.rot_to = -9
            self.event = 'down'
        else:
            self.event = 'idle'

# ответы
class Ex(pygame.sprite.Sprite):
    def __init__(self, text, level, true):
        lvls = [75, 200, 325]
        width = 75
        height = 75
        width = 30 * len(text)
        pygame.sprite.Sprite.__init__(self)
        self.true = true
        self.temp = 0
        self.text = text
        self.level_y = level
        self.font = pygame.font.Font(ex_font, 50)
        self.textSurf = self.font.render(text, 1, WHITE)
        self.image = pygame.Surface([width, height], pygame.SRCALPHA, 32).convert_alpha()
        W = self.textSurf.get_width()
        H = self.textSurf.get_height()
        self.image.blit(self.textSurf, [width/2 - W/2, height/2 - H/2])
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH + self.image.get_width(), lvls[level])

    def update(self):
        self.rect.x += SPEED_EX

    def show(self):
        if self.true:
            self.textSurf = self.font.render(self.text, 1, GREEN)
        else:
            self.textSurf = self.font.render(self.text, 1, RED)
        width = 30 * len(self.text)
        self.image = pygame.Surface([width, 75], pygame.SRCALPHA, 32).convert_alpha()
        W = self.textSurf.get_width()
        H = self.textSurf.get_height()
        self.image.blit(self.textSurf, [width/2 - W/2, 75/2 - H/2])

def is_simple(num):
    nms = [(num / i, int(num / i), i) for i in range(mn + 2, mx + 1)]
    lst = []
    for nm in nms:
        if nm[0] == nm[1]:
            lst.append(nm[2])
    if len(lst) == 0:
        return (False, lst)
    else:
        return (True, lst)

# генерировать правильный ответ
def generate_true(num):
    if is_simple(num)[0] and difficulty != 'Easy':
        r = random.randint(1, 4)
    else:
        r = random.randint(1, 2)
    if r == 1:
        nm = random.randint(mn, num)
        nm = num - nm
        nm1 = num - nm
        sep = '+'
    elif r == 2:
        sep = '-'
        nm = random.randint(num, mx)
        nm1 = (num - nm) * -1
    elif r == 3:
        sep = '*'
        nm = random.choice(is_simple(num)[1])
        nm1 = int(num / nm)
    elif r == 4:
        sep = '/'
        nm1 = random.choice(is_simple(num)[1])
        nm = int(num * nm1)
    return (nm, nm1, sep, True)

# генерировать не правильный ответ
def generate_false(num):
    sep = random.choice(['-', '+', '/', '*'])
    while 1:
        nm = random.randint(mn, mx)
        nm1 = random.randint(mn, mx)

        if nm1 == 0 or nm == 0 and sep == '/':
            continue

        if nm + nm1 != num and nm - nm1 != num and nm / nm1 != num and nm * nm1 != num:
            break

    return (nm, nm1, sep, False)

ex = []
t_num = 0
record_played = False

# создать следующие варианты
def next_nums():
    global nums, a_num, ex, t_num, detect
    detect = True

    # создаём список
    a_num = random.randint(mn, mx)
    t_num = generate_true(a_num)
    nums = [t_num, generate_false(a_num), generate_false(a_num)]
    # мешаем список
    random.shuffle(nums)
    # ищем правильный вариант
    for i in range(len(nums)):
        if nums[i] == t_num:
            t_num = i

    while 1:
        try:
            ex[0].kill()
            ex.pop(0)
        except:
            break

    ex = []

    for i in range(3):
        ex.append(Ex(f'{nums[i][0]} {nums[i][2]} {nums[i][1]}', i, nums[i][3]))

    for e in ex:
        all_sprites.add(e)

    return (a_num, nums)

next_nums()

# ещё переменные
font = pygame.font.SysFont('arial', 25)
pygame.display.set_caption("Math Dragon")
clock = pygame.time.Clock()
player = Player()
warn = Foreground()
BackGround = Background()
all_sprites.add(player)
all_sprites.add(warn)
detect = True
LIFES = 3
LIFES_CONST = 3
sound_played = 0
QUIT_TEXT = 'Вы проиграли!'

def set_difficulty(c=None, val=None, name=None):
    lst = {
        'Hard': {'speed': -5, 'mx': 9999, 'ex': 10, 'ex_next': 100, 'lifes': 3},
        'Medium': {'speed': -3, 'mx': 999, 'ex': 4, 'ex_next': 20, 'lifes': 3},
        'Easy': {'speed': -1, 'mx': 9, 'ex': 1, 'ex_next': 3, 'lifes': 3},
        }

    global SPEED_EX, mx, SPEED_EX_NEXT_SCORE, EX_ADD, LIFES
    if name == None:
        SPEED_EX_NEXT_SCORE = lst[c[0]]['ex_next']
        EX_ADD = lst[c[0]]['ex']
        SPEED_EX = lst[c[0]]['speed']
        mx = lst[c[0]]['mx']
        difficulty = c[0]
    else:
        SPEED_EX_NEXT_SCORE = lst[name]['ex_next']
        EX_ADD = lst[name]['ex']
        SPEED_EX = lst[name]['speed']
        mx = lst[name]['mx']
        difficulty = name

# Цикл игры
running = True
def start():
    # exec(eval('global '+', '.join(make_global(*globals()))))
    global NEXT_EX, TIME, warn, sound_played, QUIT_TEXT, LIFES, record_played, difficulty, set_difficulty, username, pygame, pygame_menu, random, color, os, time, json, appdata_folder, app_folder, config_file, f, config, cfg_save, WIDTH, HEIGHT, FPS, nums, a_num, mn, mx, score, screen, all_sprites, game_folder, assets_folder, img_folder, ex_img, fonts_folder, ex_font, bg_folder, WHITE, BLACK, RED, GREEN, BLUE, SPEED_Y, SPEED_EX, SPEED_EX_NEXT, Background, Player, Ex, generate_true, generate_false, ex, t_num, next_nums, detect, font, clock, player, BackGround, running
    TIME = time.time()
    # bgtime = TIME
    config['games'] += 1
    next_nums()
    music_game = [music['game_1.ogg'], music['game_2.ogg'], music['game_3.ogg']]
    random.shuffle(music_game)
    pygame.mixer.music.queue(music_game[0])
    pygame.mixer.music.queue(music_game[1])
    pygame.mixer.music.load(music_game[2])
    pygame.mixer.music.play(-1)
    while running:
        sound_played = 0
        TIME = time.time()

        # # смена фона по таймеру
        # if bgtime < TIME - 90:
        #     BackGround.image = pygame.image.load(os.path.join(bg_folder, random.choice(os.listdir(bg_folder)))).convert()
        #     bgtime = TIME

        # Держим цикл на правильной скорости
        clock.tick(FPS)

        # Ввод процесса (события)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.type == pygame.K_ESCAPE:
                    quit_game()
                elif event.dict['key'] == 113: # q
                    running = False
                    QUIT_TEXT = 'Выход...'

        if pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_w]:
              player.up()
        if pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[pygame.K_s]:
              player.down()
        if pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_d]:
              for e in ex:
                  e.rect.x -= -SPEED_EX + 1
        for e in ex:
            if e.rect.x <= 0 - e.image.get_width():
                NEXT_EX += 1
                if NEXT_EX == len(ex):
                    next_nums()
                    break
            else:
                NEXT_EX = 0
            if e.rect.x + SPEED_EX <= player.rect.x <= e.rect.x - SPEED_EX and detect:
                detect = False
                if -SPEED_EX >= SPEED_Y:
                    SPEED_Y += 1
                if 0 < player.rect.y + 50 <= (HEIGHT / 3):
                    PLAYER_LEVEL = 0
                elif (HEIGHT / 3) < player.rect.y + 50 <= (HEIGHT / 3 * 2):
                    PLAYER_LEVEL = 1
                else:
                    PLAYER_LEVEL = 2
                for e in ex:
                    e.show()
                if PLAYER_LEVEL == t_num:
                    score += EX_ADD
                    if score > config['record']:
                        if record_played == False:
                            random.choice(sounds['record']).play()
                            record_played = True
                            sound_played = 1
                        config['record'] = score
                        config['record_name'] = username
                    SPEED_EX_NEXT += EX_ADD
                    if SPEED_EX_NEXT == SPEED_EX_NEXT_SCORE:
                        random.choice(sounds['speed_up']).play()
                        SPEED_EX -= 1
                        SPEED_EX_NEXT = 0
                        sound_played = 1
                    if sound_played == 0:
                        random.choice(sounds['true']).play()
                else:
                    if LIFES == 0:
                        random.choice(sounds['die']).play()
                        # raise SystemExit(100)
                        running = False
                    else:
                        warn.warn()
                        LIFES -= 1
                        random.choice(sounds['false']).play()
                break

        # Обновление
        all_sprites.update()
        screen.blit(BackGround.image, BackGround.rect)
        f1 = pygame.font.Font(ex_font, 30)
        score_text = f1.render('Счёт: '+str(score), 1, WHITE_GRAY)
        screen.blit(score_text, (10, 0))
        num_text = f1.render('Получится: '+str(a_num), 1, WHITE_GRAY)
        screen.blit(num_text, (10, 35))
        record_text = f1.render('Рекорд '+str(config['record_name'])+': '+str(config['record']), 1, WHITE_GRAY)
        screen.blit(record_text, (10, 70))
        record_text = f1.render('Всего игр: '+str(config['games']), 1, WHITE_GRAY)
        screen.blit(record_text, (10, 105))
        speed_text = f1.render('Скорость: '+str(-1 * SPEED_EX), 1, WHITE_GRAY)
        screen.blit(speed_text, (10, 140))
        lifes_text = f1.render('Ошибок осталось: '+str(LIFES), 1, WHITE_GRAY)
        screen.blit(lifes_text, (10, 175))

        # Рендеринг
        all_sprites.draw(screen)

        # После отрисовки всего, переворачиваем экран
        pygame.display.flip()

    die_text = f1.render(QUIT_TEXT, 1, WHITE)
    screen.blit(die_text, (WIDTH / 3, HEIGHT / 3))
    pygame.display.flip()
    pygame.mixer.music.stop()
    cfg_save()
    time.sleep(3)
    QUIT_TEXT = 'Вы проиграли!'
    running = True
    record_played = False
    score = 0
    SPEED_EX = -1
    BackGround.image = pygame.image.load(os.path.join(bg_folder, random.choice(os.listdir(bg_folder)))).convert()
    SPEED_Y = 5
    LIFES = LIFES_CONST
    player.rect.center = (int(WIDTH / 8), int(HEIGHT / 2))
    pygame.mixer.music.load(music['menu.ogg'])
    pygame.mixer.music.play(-1)
    set_difficulty(name=difficulty)

def set_name(name):
    global username
    username = name

def set_lifes(inp):
    global LIFES, LIFES_CONST
    try:
        LIFES = int(inp)
    except:
        LIFES = 3
    LIFES_CONST = LIFES

# музыка меню
pygame.mixer.music.load(music['menu.ogg'])
pygame.mixer.music.play(-1)

menu_theme = pygame_menu.themes.THEME_DARK
menu_theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_TITLE_ONLY_DIAGONAL

menu_bg = pygame_menu.baseimage.BaseImage(
    image_path=os.path.join(bg_folder, 'bg4.jpg'),
    drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY
)
menu_theme.background_color = menu_bg
# menu_theme.widget_selection_effect = pygame_menu.widgets.LeftArrowSelection1

menu = pygame_menu.Menu(400, 600, 'Math Dragon',
                        theme=menu_theme)
menu.add_text_input('Name: ', default=username, onchange=set_name)
menu.add_selector('Difficulty: ', [('Easy', 1), ('Medium', 2), ('Hard', 3)], onchange=set_difficulty)
menu.add_text_input('Lifes: ', default='3', onchange=set_lifes)
menu.add_button('Play', start)
menu.add_button('Quit', quit_game)

menu.mainloop(screen)

pygame.quit()
