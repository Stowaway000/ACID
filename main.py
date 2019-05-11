import cocos
import pyglet
from cocos.director import director
from cocos.scene import Scene
from cocos.actions import RotateBy, Repeat
from pyglet import font
from cocos.menu import LEFT, RIGHT, BOTTOM, TOP, CENTER
from polygon import *
from models import *
from physics import *


version = '0.002'  # Версия игры
# Ширина и высота окна
width = 1280
height = 720

# Убираем настройки по-умолчанию
def set_menu_style(menu, size=32):
    menu.font_item_selected['font_size'] = size
    menu.font_item_selected['font_name'] = 'Calibri'
    menu.font_item['font_name'] = 'Calibri'
    menu.font_item_selected['color'] = (229, 43, 80, 240)
    menu.font_item['color'] = (192, 192, 192, 200)


def load_map(name, hero):
    map_layer = MapLayer(name)
    map_collider = circle_map_collider(map_layer)
    hero.set_collision(map_collider)

    scroller = cocos.layer.ScrollingManager()
    scroller.scale = 2
    
    scroller.add(hero, 1)
    scroller.add(map_layer.layer_floor, -1)
    scroller.add(map_layer.layer_vertical, 1)
    scroller.add(map_layer.layer_objects, 1)
    scroller.add(map_layer.layer_above, 2)

    return scroller


def previous():
    director.pop()


def enter():
    cur_i = pyglet.image.load("res/img/cursor.png")
    cursor = pyglet.window.ImageMouseCursor(cur_i, 10, 10)
    director.window.set_mouse_cursor(cursor)
    
    main_hero = hero('hero', 'rebel', (5, 5, 5, 5, 5, 5), (100, 100, 100), (100, 80))
    
    scroller = load_map("map_test", main_hero)
    main_hero.set_scroller(scroller)
    
    scene = cocos.scene.Scene(scroller)

    weapon('rifle')
    main_hero.take_item('rifle', 1)
    
    director.push(scene)


def quit_game():
    director.window.close()


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
    items.append(cocos.menu.MenuItem("Настройки", enter))
    items.append(cocos.menu.MenuItem("Об игре", about_game))
    items.append(cocos.menu.MenuItem("Выйти", quit_game))

    menu.create_menu(items)
    menu_host.add(menu)

    return menu_host


if __name__ == '__main__':
    director.init(width=width, height=height, caption='Game')
    director.window.pop_handlers()
    
    mainMenu = create_menu()

    director.run(mainMenu)
