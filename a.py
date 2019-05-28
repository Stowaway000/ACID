import cocos 
from cocos.director import director 
from cocos.scene import Scene 
from cocos.actions import RotateBy, Repeat 
from pyglet import font 
from cocos.menu import LEFT, RIGHT, BOTTOM, TOP, CENTER, MultipleMenuItem 

version = '0.001' # Версия игры 
# Ширина и высота окна 
width = 1280 
height = 720 


# Убираем настроки по-умолчанию 
def set_menu_style(menu, size=32): 
    menu.font_item_selected['font_size'] = size 
    menu.font_item_selected['font_name'] = 'Calibri' 
    menu.font_item['font_name'] = 'Calibri' 
    menu.font_item_selected['color'] = (229, 43, 80, 240) 
    menu.font_item['color'] = (192, 192, 192, 200) 


def previous(): 
    director.pop() 


def enter(): 
    director.push(Scene()) 


def quit_game(): 
    director.window.close() 


# Сцена "Об игре" 
def about_game(): 
    about = Scene() 

    bg = cocos.layer.ColorLayer(255, 255, 255, 255) 

    info = cocos.text.Label("Версия игры: " + version, font_name='Verdana', font_size=32, anchor_x='center', anchor_y='center', color=(192, 192, 192, 200)) 
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

    game_title = cocos.text.Label("GAME", font_name='Verdana Bold', font_size=92,anchor_x='center') 
    game_title.y = height // 4 

    bg.add(space, 0) 
    bg.add(ground, 1) 
    bg.add(game_title, 2) 

    return bg

def pic(a, b): 
    pass 

def menu_cast():
    about = Scene() 
    bg = cocos.layer.ColorLayer(255, 255, 255, 255) 
    back = cocos.menu.Menu() 
    set_menu_style(back, 28) 
    item = [cocos.menu.MenuItem('Назад', previous)] 
    back.menu_valign = TOP 
    back.menu_halign = LEFT 
    back.menu_hmargin = 10 
    back.create_menu(item) 
    evv = cocos.text.Label("Создание персонажа", font_name='Verdana', font_size=32,anchor_x='center', anchor_y='center', color=(75, 0, 135, 255)) 
    evv.position = (640, 700)

    shmot = ['chipsinka.png', 'classic.png', 'glamurniy.png', 'red.png','summerstyle.png', 'travka.png'] 
    faces = ['lichiko1.png', 'lichiko2.png', 'lichiko3.png'] 
    qubor = ['nar.png', 'shap.png', 'taksist.png', 'ushan.png', 'uzb.png'] 

    a = cocos.sprite.Sprite('res/img/outline.png') 
    a.position = (0,0) 

    s = cocos.menu.Menu() 
    set_menu_style(s) 
    items = [] 
    items.append(MultipleMenuItem('Shmot: ',lambda arg:pic(arg,shmot), shmot, 1)) 
    s.create_menu(items) 

    xakki = cocos.text.Label("Характеристики", font_name='Verdana', font_size=20,anchor_x='center', anchor_y='center', color=(75, 0, 135, 255)) 
    xakki.position = (600, 100) 

    print(13)
    bg.add(evv) 
    bg.add(s) 
    bg.add(back) 
    bg.add(xakki) 
    bg.add(a) 
    about.add(bg) 

    director.replace(about) 


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
    items.append(cocos.menu.MenuItem("Новая игра", menu_cast)) 
    items.append(cocos.menu.MenuItem("Загрузить игру", enter)) 
    items.append(cocos.menu.MenuItem("Настройки", enter)) 
    items.append(cocos.menu.MenuItem("Об игре", about_game)) 
    items.append(cocos.menu.MenuItem("Выйти", quit_game)) 

    menu.create_menu(items) 
    menu_host.add(menu) 

    return menu_host 


if __name__ == '__main__': 
    director.init(width=width, height=height, caption='Game') 

    mainMenu = create_menu()
    director.run(mainMenu)
