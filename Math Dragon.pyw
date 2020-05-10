import pygame
import pygame_menu
import random
from pygame.locals import *
import os
import time
import json
from socket import gethostname
import pyAesCrypt
import io

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

cfg_save()

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
game_folder = os.path.dirname(__file__)
assets_folder = os.path.join(game_folder, 'assets')
img_folder = os.path.join(assets_folder, 'img')
ex_img = {l: os.path.join(img_folder, 'ex_'+l+'.png') for l in '0123456789+'}
fonts_folder = os.path.join(assets_folder, 'fonts')
ex_font = os.path.join(fonts_folder, 'ex.ttf')
bg_folder = os.path.join(img_folder, 'bg')
sounds_folder = os.path.join(assets_folder, 'sounds')
music_folder = os.path.join(sounds_folder, 'music')

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
print(music)

# Задаем цвета
WHITE = (255, 255, 255)
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
        self.time = time.time()
        self.im = 1
        self.images = [pygame.image.load(os.path.join(img_folder, 'player-'+str(i)+'.png')).convert_alpha() for i in [1,2,3,4]]
        self.image = self.images[0]
        self.image_orig = self.image
        self.size = 50
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.rect = self.image.get_rect()
        self.rect.center = (int(WIDTH / 8), int(HEIGHT / 2))
        self.rot = 0
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rect.y = self.rect.y
        if self.time < (time.time() - 0.1):
            self.image = self.images[self.im]
            self.time = time.time()
            self.im += 1
            if self.im > 3:
                self.im = 0

    def up(self):
        if self.rect.y - 10 > 0:
            self.rect.y -= SPEED_Y

    def down(self):
        if self.rect.y + 70 < (HEIGHT - self.size):
            self.rect.y += SPEED_Y

# ответы
class Ex(pygame.sprite.Sprite):
    def __init__(self, text, level, width = 75, height = 75, true = False):
        lvls = [75, 200, 325]
        width = 30 * len(text)
        pygame.sprite.Sprite.__init__(self)
        self.true = true
        self.temp = 0
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

    def __str__(self):
        return 'ex'

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
    return (nm, nm1, sep)

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

    return (nm, nm1, sep)

ex = []
t_num = 0
record_played = False

# создать следующие варианты
def next_nums():
    global nums, a_num, ex, t_num, detect
    detect = True
    nums = [0,0,0]
    nums[random.randint(0,2)] = 1
    a_num = random.randint(mn, mx)
    for i in [0,1,2]:
        if nums[i]:
            nums[i] = (generate_true(a_num), 1)
            t_num = i
        else:
            nums[i] = (generate_false(a_num), 0)

    while 1:
        try:
            ex[0].kill()
            ex.pop(0)
        except:
            break

    ex = []

    for i in [0,1,2]:
        ex.append(Ex(f'{nums[i][0][0]} {nums[i][0][2]} {nums[i][0][1]}', i))

    for e in ex:
        all_sprites.add(e)

    return (a_num, nums)

next_nums()

# ещё переменные
font = pygame.font.SysFont('arial', 25)
pygame.display.set_caption("Math Dragon")
clock = pygame.time.Clock()
player = Player()
BackGround = Background()
all_sprites.add(player)
bgtime = time.time()
detect = True

def make_global(*ar):
    l = []
    for a in ar:
        l.append(a)
    return l

# Цикл игры
running = True
def start():
    # exec(eval('global '+', '.join(make_global(*globals()))))
    global __name__, username, __doc__, __package__, __loader__, __spec__, __annotations__, __builtins__, __file__, pygame, pygame_menu, random, LIL_ENDIAN, BIG_ENDIAN, YV12_OVERLAY, IYUV_OVERLAY, YUY2_OVERLAY, UYVY_OVERLAY, YVYU_OVERLAY, SWSURFACE, HWSURFACE, RESIZABLE, ASYNCBLIT, OPENGL, OPENGLBLIT, ANYFORMAT, HWPALETTE, DOUBLEBUF, FULLSCREEN, HWACCEL, SRCCOLORKEY, RLEACCELOK, RLEACCEL, SRCALPHA, PREALLOC, NOFRAME, GL_RED_SIZE, GL_GREEN_SIZE, GL_BLUE_SIZE, GL_ALPHA_SIZE, GL_BUFFER_SIZE, GL_DOUBLEBUFFER, GL_DEPTH_SIZE, GL_STENCIL_SIZE, GL_ACCUM_RED_SIZE, GL_ACCUM_GREEN_SIZE, GL_ACCUM_BLUE_SIZE, GL_ACCUM_ALPHA_SIZE, GL_STEREO, GL_MULTISAMPLEBUFFERS, GL_MULTISAMPLESAMPLES, GL_SWAP_CONTROL, GL_ACCELERATED_VISUAL, TIMER_RESOLUTION, AUDIO_U8, AUDIO_S8, AUDIO_U16LSB, AUDIO_S16LSB, AUDIO_U16MSB, AUDIO_S16MSB, AUDIO_U16, AUDIO_S16, AUDIO_U16SYS, AUDIO_S16SYS, SCRAP_TEXT, SCRAP_BMP, SCRAP_PPM, SCRAP_PBM, SCRAP_CLIPBOARD, SCRAP_SELECTION, BLEND_ADD, BLEND_SUB, BLEND_MULT, BLEND_MIN, BLEND_MAX, BLEND_RGB_ADD, BLEND_RGB_SUB, BLEND_RGB_MULT, BLEND_RGB_MIN, BLEND_RGB_MAX, BLEND_RGBA_ADD, BLEND_RGBA_SUB, BLEND_RGBA_MULT, BLEND_RGBA_MIN, BLEND_RGBA_MAX, BLEND_PREMULTIPLIED, NOEVENT, ACTIVEEVENT, KEYDOWN, KEYUP, MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP, JOYAXISMOTION, JOYBALLMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP, VIDEORESIZE, VIDEOEXPOSE, QUIT, SYSWMEVENT, USEREVENT, NUMEVENTS, HAT_CENTERED, HAT_UP, HAT_RIGHTUP, HAT_RIGHT, HAT_RIGHTDOWN, HAT_DOWN, HAT_LEFTDOWN, HAT_LEFT, HAT_LEFTUP, BUTTON_LEFT, BUTTON_MIDDLE, BUTTON_RIGHT, AUDIODEVICEADDED, AUDIODEVICEREMOVED, FINGERMOTION, FINGERDOWN, FINGERUP, MULTIGESTURE, MOUSEWHEEL, TEXTINPUT, TEXTEDITING, WINDOWEVENT, WINDOWEVENT_CLOSE, BUTTON_WHEELUP, BUTTON_WHEELDOWN, AUDIO_ALLOW_FREQUENCY_CHANGE, AUDIO_ALLOW_FORMAT_CHANGE, AUDIO_ALLOW_CHANNELS_CHANGE, AUDIO_ALLOW_ANY_CHANGE, DROPFILE, DROPTEXT, DROPBEGIN, DROPCOMPLETE, BUTTON_X1, BUTTON_X2, K_UNKNOWN, K_FIRST, K_BACKSPACE, K_TAB, K_CLEAR, K_RETURN, K_PAUSE, K_ESCAPE, K_SPACE, K_EXCLAIM, K_QUOTEDBL, K_HASH, K_DOLLAR, K_AMPERSAND, K_QUOTE, K_LEFTPAREN, K_RIGHTPAREN, K_ASTERISK, K_PLUS, K_COMMA, K_MINUS, K_PERIOD, K_SLASH, K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_COLON, K_SEMICOLON, K_LESS, K_EQUALS, K_GREATER, K_QUESTION, K_AT, K_LEFTBRACKET, K_BACKSLASH, K_RIGHTBRACKET, K_CARET, K_UNDERSCORE, K_BACKQUOTE, K_a, K_b, K_c, K_d, K_e, K_f, K_g, K_h, K_i, K_j, K_k, K_l, K_m, K_n, K_o, K_p, K_q, K_r, K_s, K_t, K_u, K_v, K_w, K_x, K_y, K_z, K_DELETE, K_KP0, K_KP1, K_KP2, K_KP3, K_KP4, K_KP5, K_KP6, K_KP7, K_KP8, K_KP9, K_KP_PERIOD, K_KP_DIVIDE, K_KP_MULTIPLY, K_KP_MINUS, K_KP_PLUS, K_KP_ENTER, K_KP_EQUALS, K_UP, K_DOWN, K_RIGHT, K_LEFT, K_INSERT, K_HOME, K_END, K_PAGEUP, K_PAGEDOWN, K_F1, K_F2, K_F3, K_F4, K_F5, K_F6, K_F7, K_F8, K_F9, K_F10, K_F11, K_F12, K_F13, K_F14, K_F15, K_NUMLOCK, K_CAPSLOCK, K_SCROLLOCK, K_RSHIFT, K_LSHIFT, K_RCTRL, K_LCTRL, K_RALT, K_LALT, K_RMETA, K_LMETA, K_LSUPER, K_RSUPER, K_MODE, K_HELP, K_PRINT, K_SYSREQ, K_BREAK, K_MENU, K_POWER, K_EURO, K_LAST, KMOD_NONE, KMOD_LSHIFT, KMOD_RSHIFT, KMOD_LCTRL, KMOD_RCTRL, KMOD_LALT, KMOD_RALT, KMOD_LMETA, KMOD_RMETA, KMOD_NUM, KMOD_CAPS, KMOD_MODE, KMOD_CTRL, KMOD_SHIFT, KMOD_ALT, KMOD_META, USEREVENT_DROPFILE, Rect, color, Color, os, time, json, appdata_folder, app_folder, config_file, f, config, cfg_save, WIDTH, HEIGHT, FPS, nums, a_num, mn, mx, score, screen, all_sprites, game_folder, assets_folder, img_folder, ex_img, fonts_folder, ex_font, bg_folder, WHITE, BLACK, RED, GREEN, BLUE, SPEED_Y, SPEED_EX, SPEED_EX_NEXT, Background, Player, Ex, generate_true, generate_false, ex, t_num, next_nums, detect, __warningregistry__, font, clock, player, BackGround, bgtime, make_global, running
    config['games'] += 1
    next_nums()
    volume = 0.9
    for i in range(10):
        pygame.mixer.music.set_volume(volume)
        volume -= 0.1
        time.sleep(0.1)
    pygame.mixer.music.stop()
    pygame.mixer.music.load(music['game_1.ogg'])
    pygame.mixer.music.play(-1)
    volume = 0.
    for i in range(10):
        pygame.mixer.music.set_volume(volume)
        volume += 0.1
        time.sleep(0.1)
    pygame.mixer.music.set_volume(1)
    while running:
        if bgtime < time.time() - 90:
            BackGround.image = pygame.image.load(os.path.join(bg_folder, random.choice(os.listdir(bg_folder)))).convert()
            bgtime = time.time()

        # Держим цикл на правильной скорости
        clock.tick(FPS)

        # Ввод процесса (события)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                cfg_save()
                pygame.quit()
            elif event.type == pygame.K_ESCAPE:
                running = False
                cfg_save()
                pygame.quit()

        if pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_w]:
              player.up()
        if pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[pygame.K_s]:
              player.down()
        for e in ex:
            if e.rect.x <= 0 - e.image.get_width():
                next_nums()
                break
            if e.rect.x + SPEED_EX <= player.rect.x <= e.rect.x - SPEED_EX and detect:
                detect = False
                if 0 < player.rect.y <= (HEIGHT / 3):
                    PLAYER_LEVEL = 0
                elif (HEIGHT / 3) < player.rect.y <= (HEIGHT / 3 * 2):
                    PLAYER_LEVEL = 1
                else:
                    PLAYER_LEVEL = 2
                if PLAYER_LEVEL == t_num:
                    random.choice(sounds['true']).play()
                    BackGround.image = pygame.image.load(os.path.join(bg_folder, random.choice(os.listdir(bg_folder)))).convert()
                    score += EX_ADD
                    if score > config['record']:
                        if record_played == False:
                            random.choice(sounds['record']).play()
                            record_played = True
                        config['record'] = score
                        config['record_name'] = username
                    SPEED_EX_NEXT += 1
                    if SPEED_EX_NEXT == SPEED_EX_NEXT_SCORE:
                        random.choice(sounds['speed_up']).play()
                        SPEED_EX -= 1
                        SPEED_EX_NEXT = 0
                else:
                    cfg_save()
                    raise SystemExit(100)
                    running = False
                break

        # Обновление
        all_sprites.update()
        screen.blit(BackGround.image, BackGround.rect)
        f1 = pygame.font.Font(ex_font, 30)
        score_text = f1.render('Счёт: '+str(score), 1, WHITE)
        screen.blit(score_text, (10, 0))
        num_text = f1.render('Получится: '+str(a_num), 1, WHITE)
        screen.blit(num_text, (10, 35))
        record_text = f1.render('Рекорд '+str(config['record_name'])+': '+str(config['record']), 1, WHITE)
        screen.blit(record_text, (10, 70))
        record_text = f1.render('Всего игр: '+str(config['games']), 1, WHITE)
        screen.blit(record_text, (10, 105))
        speed_text = f1.render('Скорость: '+str(-1 * SPEED_EX), 1, WHITE)
        screen.blit(speed_text, (10, 140))

        # Рендеринг
        all_sprites.draw(screen)

        # После отрисовки всего, переворачиваем экран
        pygame.display.flip()
    # running = True
    pygame.quit()

def set_difficulty(c, val):
    lst = {
        'Hard': {'speed': -5, 'mx': 9999, 'ex': 10, 'ex_next': 100},
        'Medium': {'speed': -3, 'mx': 999, 'ex': 4, 'ex_next': 20},
        'Easy': {'speed': -1, 'mx': 9, 'ex': 1, 'ex_next': 3},
        }

    global SPEED_EX, mx, SPEED_EX_NEXT_SCORE, EX_ADD
    SPEED_EX_NEXT_SCORE = lst[c[0]]['ex_next']
    EX_ADD = lst[c[0]]['ex']
    SPEED_EX = lst[c[0]]['speed']
    mx = lst[c[0]]['mx']
    difficulty = c[0]

def set_name(name):
    global username
    username = name

# музыка меню
pygame.mixer.music.load(music['menu.ogg'])
pygame.mixer.music.play()

menu = pygame_menu.Menu(400, 600, 'Math Dragon',
                        theme=pygame_menu.themes.THEME_DARK)
menu.add_text_input('Name: ', default=username, onchange=set_name)
menu.add_selector('Difficulty: ', [('Easy', 1), ('Medium', 2), ('Hard', 3)], onchange=set_difficulty)
menu.add_button('Play', start)
menu.add_button('Quit', pygame_menu.events.EXIT)

menu.mainloop(screen)

pygame.quit()
