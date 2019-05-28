from cocos.scene import Scene
from cocos.actions import RotateBy, Repeat
from pyglet import font
import cocos.audio.pygame.mixer as mixer
from cocos.menu import LEFT, RIGHT, BOTTOM, TOP, CENTER, MultipleMenuItem
from hero import hero
from item import *
from physics import *
from interface import interface
from map import *
from menu import set_menu_style, previous, quit_game
from npc import NPC
from pyglet.window import key, mouse


version = '0.01'  # Версия игры


# Ширина и высота окна
width = 1280
height = 720


def on_key_press(symbol, modifiers):
    if symbol == key.ESCAPE:
        return True


def create_interface(hero):
    stats = hero.get_stats()

    stats['hp'].append((100, 100))
    stats['armor'].append((200, 100))
    stats['stamina'].append((width-100, 100))
    stats['weapon_r'].append((width/2+110, 100))
    stats['weapon_l'].append((width/2-110, 100))

    inter = interface(stats, hero)
    hero.interface = inter


def enter():
    cur_i = pyglet.image.load("res/img/cursor.png")
    cursor = pyglet.window.ImageMouseCursor(cur_i, 10, 10)
    director.window.set_mouse_cursor(cursor)
    
    main_hero = hero('hero', 'rebel', (5, 5, 5, 5, 5, 5), (100, 100, 100), (400, 30), NPC.npcs)
    create_interface(main_hero)

    Item('bul', 1, 1)
    Weapon('colt')
    #Weapon('pgun')
    Weapon('rifle')
    Armor('armor')

    scene = map_manager("map_outdoors", main_hero, 0)

    director.push(scene)
    main_theme.stop()

    main_hero.interface.quest_done('Родиться')
    main_hero.interface.quest_done('Умереть')

    main_hero.take_item('colt', 2)
    #main_hero.take_item('rifle', 1)
    #main_hero.take_item('pgun', 1)
    main_hero.take_item('bul', 30)


# Сцена "Об игре"
def about_game():
    about = Scene()
    
    bg = cocos.layer.ColorLayer(255, 255, 255, 255)
    
    info = cocos.text.Label("Версия игры: " + version, font_name='Verdana', font_size=32,\
                            anchor_x='center', anchor_y='center', color=(192, 192, 192, 200))
    info.position = (width//2, height//2)
                            
    back = cocos.menu.Menu()
    set_menu_style(back, 28)
    item = [cocos.menu.MenuItem('Назад', previous)]
    back.menu_valign = TOP
    back.menu_halign = LEFT
    back.menu_hmargin = 10
    back.create_menu(item)
                            
    bg.add(info)
    bg.add(back)
                            
    about.add(bg)
                            
    director.push(about)


def volume_sounds(arg):
    step_ch.set_volume(arg/10)
    shoot_ch.set_volume(arg/10)

def volume_music(arg):
    music_ch.set_volume(arg/10)


def settings():
    about = Scene()

    bg = cocos.layer.ColorLayer(255, 255, 255, 255)

    back = cocos.menu.Menu()
    set_menu_style(back, 28)
    item = [cocos.menu.MenuItem('Назад', previous)]
    back.menu_valign = TOP
    back.menu_halign = LEFT
    back.menu_hmargin = 10
    back.create_menu(item)

    sound = cocos.menu.Menu()
    set_menu_style(sound)
    items = []
    volumes = ['Mute','10','20','30','40','50','60','70','80','90','100']
    items.append(MultipleMenuItem('Sounds volume: ', volume_sounds,\
                                   volumes, 10))
    items.append(MultipleMenuItem('Music volume: ', volume_music,\
                                   volumes, 10))
    sound.create_menu(items)

    bg.add(sound)
    bg.add(back)

    about.add(bg)

    director.push(about)


# Создание фона для главного меню
def create_bg():
    bg = cocos.layer.Layer()
    space = cocos.sprite.Sprite('res/img/space.jpg')
    space.do(Repeat(RotateBy(360, 300)))
    
    ground = cocos.layer.ColorLayer(255, 255, 255, 255, height=height//2)
    ground.position = (-width//2, -height//2)
    
    game_title = cocos.text.Label("GAME", font_name='Verdana Bold', font_size=92,\
                                anchor_x='center')
    game_title.y = height // 4
                                  
    bg.add(space, 0)
    bg.add(ground, 1)
    bg.add(game_title, 2)
                                  
    return bg


# Создание главного меню
def create_menu():
    menu_host = Scene()
    
    bg = create_bg()
    bg.position = (width//2, height//2)
    menu_host.add(bg)
    
    menu = cocos.menu.Menu()
    menu.menu_halign = LEFT
    menu.menu_valign = BOTTOM
    menu.menu_hmargin = 50
    menu.menu_vmargin = 90
    set_menu_style(menu)
    
    items = list()
    items.append(cocos.menu.MenuItem("Новая игра", enter))
    items.append(cocos.menu.MenuItem("Загрузить игру", enter))
    items.append(cocos.menu.MenuItem("Настройки", settings))
    items.append(cocos.menu.MenuItem("Об игре", about_game))
    items.append(cocos.menu.MenuItem("Выйти", quit_game))
    
    menu.create_menu(items)
    menu_host.add(menu)
    
    return menu_host


if __name__ == '__main__':
    #director.init(width=width, height=height, caption='Game', fullscreen=True)
    director.init(width=width, height=height, caption='Game')
    director.window.pop_handlers()

    my_mixer = mixer.init()
    music_ch = mixer.Channel(0)
    step_ch = mixer.Channel(1)
    shoot_ch = mixer.Channel(2)
    main_theme = mixer.Sound("res/sound/main.wav")
    music_ch.play(main_theme, -1)

    director.window.push_handlers(on_key_press)
    
    mainMenu = create_menu()
    
    director.run(mainMenu)
