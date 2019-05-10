import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.text import Label
from cocos.layer import Layer, ColorLayer, MultiplexLayer, ScrollingManager, ScrollableLayer
from cocos.scenes import pause
from cocos.scene import Scene
from cocos.menu import LEFT, RIGHT, BOTTOM, TOP, CENTER
from cocos.actions import FadeIn, FadeOut, MoveBy, RotateBy, CallFunc
import pyglet
from pyglet.window import key, mouse
from menu import set_menu_style, go_back, quit_game


def add_label(txt, point, anchor='center'):
    return Label(txt, point, font_name='Calibri',\
                 anchor_x=anchor,\
                 anchor_y='center')


class game_menu(Layer):
    is_event_handler = True
    
    def __init__(self, pos):
        super().__init__()

        menu = cocos.menu.Menu()
        menu.menu_halign = CENTER
        menu.menu_valign = CENTER
        set_menu_style(menu)

        items = list()
        items.append(cocos.menu.MenuItem("Продолжить", lambda:go_back(1)))
        items.append(cocos.menu.MenuItem("Главное меню", lambda:go_back(2)))
        items.append(cocos.menu.MenuItem("Выйти", quit_game))

        menu.create_menu(items)
        self.add(menu)

        self.mouse_pos = pos

    def on_exit(self):
        director.window.set_mouse_position(*self.mouse_pos)
        
        super().on_exit()
    
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            director.pop()


class visual_inventory(Layer):
    is_event_handler = True
    
    def __init__(self):
        super().__init__()

        w = director.window.width
        h = director.window.height
        self.position = (w/6, h/6)
        self.width = int(2*w/3)
        self.height = int(2*h/3)
        
        bg = ColorLayer(31, 38, 0, 255)
        bg.width = int(2*w/3)
        bg.height = int(2*h/3)
        bg.position = (0, 0)

        self.on_one = h/96

        self.item_window = ScrollingManager(cocos.rect.Rect(w/6, h/6, 200, int(2*h/3)))
        self.item_window.anchor = (0, 0)
        self.item_window.position = (w/6, h/6)
        
        self.item_stack = ScrollableLayer()
        self.item_stack.position = (0, 0)

        self.viewpoint = (w/6+50, h/6+self.height/4+16)
        
        self.item_window.set_focus(*self.viewpoint)
        self.item_window.scale = 2

        self.scrollbar = ColorLayer(255, 200, 100, 255)
        self.scrollbar.width = 15
        self.scrollbar.position = (200, 0)

        self.up = h/6+self.height/4+16
        self.down = 0

        self.item_window.add(self.item_stack)
        self.add(bg)
        self.add(self.scrollbar)
        self.add(self.item_window)

        self.pixel_rel = 1

    def update(self, pos, hero):
        self.mouse_pos = pos
        invent = hero.inventory
        
        h = 0

        total = len(invent.items) + len(invent.weapons) + len(invent.armors)
        self.scrollbar.height = int(self.height*min(self.on_one/total, 1))
        self.scrollbar.position = (200, self.height-self.scrollbar.height)

        self.pixel_rel = self.scrollbar.height / self.height

        self.down = self.up - 32*(total-self.on_one)

        self.viewpoint = (self.viewpoint[0], self.up)
        self.item_window.set_focus(*self.viewpoint)
        
        for key, val in invent.items.items():
            item = invent.get(key)
            spr = item.item_inv_sprite
            spr.position = (50, self.height/2-h*32)

            count = add_label(str(val), (80, self.height/2-h*32))
            self.item_stack.add(spr)
            self.item_stack.add(count)
            
            h += 1
    
    def on_exit(self):
        director.window.set_mouse_position(*self.mouse_pos)
        super().on_exit()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_press(x, y, buttons, modifiers)
        
        x -= self.position[0]
        y -= self.position[1]

        if 195 < x < 220 and 0 < y < self.height:
            if self.viewpoint[1]+dy/2 > self.up:
                dy = 2*(self.up - self.viewpoint[1])
            if self.viewpoint[1]+dy/2 < self.down:
                dy = 2*(self.down-self.viewpoint[1])
            
            self.viewpoint = (self.viewpoint[0], self.viewpoint[1]+dy/2)
            self.item_window.set_focus(*self.viewpoint)

            self.scrollbar.position = (200, self.scrollbar.position[1]+dy*self.pixel_rel)

    def on_mouse_press(self, x, y, button, modifiers):
        x -= self.position[0]
        y -= self.position[1]
        
        if button == mouse.LEFT:
            if 195 < x < 220 and (self.scrollbar.position[1] > y or\
               y > self.scrollbar.position[1]+self.scrollbar.height):
                dy = y - self.scrollbar.position[1] - self.scrollbar.height/2
                dy /= self.pixel_rel

                if self.viewpoint[1]+dy/2 > self.up:
                    dy = 2*(self.up - self.viewpoint[1])
                if self.viewpoint[1]+dy/2 < self.down:
                    dy = 2*(self.down-self.viewpoint[1])

                self.scrollbar.position = (200, self.scrollbar.position[1]\
                                           +dy*self.pixel_rel)
                
                self.viewpoint = (self.viewpoint[0], self.viewpoint[1]+dy/2)
                self.item_window.set_focus(*self.viewpoint)


class stat_interface(Layer):
    is_event_handler = True
    
    def __init__(self, stats):
        self.bars = {}

        super().__init__()

        for key, val in stats.items():
            self.bars[key] = add_label(str(val[0]), val[1])
            spr = Sprite('res/img/interface/' + key + '.png')
            spr.position = val[1]
            self.add(spr)

        for key, val in self.bars.items():
            self.add(val, name=key)

    def update(self, stats):
        for key, val in stats.items():
            self.change(key, val)

    def change(self, stat, new):
        self.remove(stat)

        old_pos = self.bars[stat].position
        self.bars[stat] = add_label(str(new), old_pos)

        self.add(self.bars[stat], name=stat)


    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            pause_sc = pause.get_pause_scene()
            
            pause_sc.remove(pause_sc.get_children()[1])

            pause_sc.add(game_menu(self.parent.mouse_pos))
            
            director.push(pause_sc)


class interface(MultiplexLayer):
    is_event_handler = True
    
    def __init__(self, stats, host):
        self.stats = stat_interface(stats)
        self.invent = visual_inventory()
        super().__init__(self.stats, self.invent)

        self.mouse_pos = (0, 0)
        
        self.host = host

        self.announcer = cocos.layer.ColorLayer(18, 22, 0, 0)
        self.announcer.position = (director.window.width/2,\
                                   director.window.height-100)
        self.add(self.announcer)

        self.queue = []

    def on_key_press(self, symbol, modifiers):
        if symbol == key.Q:
            if self.enabled_layer != 1:
                self.host.lurking = True
                self.invent.update(self.mouse_pos, self.host)
                self.switch_to(1)
            else:
                self.host.lurking = False
                self.switch_to(0)

    def change(self, stat, new):
        self.stats.change(stat, new)

    def update(self, stats):
        self.stats.update(stats)
    
    def next(self, title):
        self.queue.remove(title)
        if len(self.queue):
            self.make_announce(self.queue[0])
    
    def make_announce(self, title):
        names = self.announcer.children_names.copy()
        for i in names:
            self.announcer.remove(i)
        
        star = Sprite('res/img/interface/done.png', anchor = (0, 0))
        star.position = (0, 0)
        star.opacity = 0

        header = add_label('Выполнено!', (star.width + 10, star.height-15),\
                           'left')
        text = add_label(title, (star.width + 10, 30), 'left')

        
        self.announcer.height = star.height
        
        self.announcer.add(header, name='header')
        self.announcer.add(text, name='text')
        self.announcer.add(star, name='star')

        self.announcer.width = star.width + 20 + max(len(title), 10)*10

        fade_time = 1
        self.announcer.do((MoveBy((0, -50), fade_time)|FadeIn(fade_time)) +\
                   RotateBy(0, fade_time*2) + (MoveBy((0, 50), fade_time)\
                                               |FadeOut(fade_time))+CallFunc(lambda :self.next(title)))
        for i in self.announcer.get_children():
            i.do(FadeIn(fade_time)+ RotateBy(0, fade_time*2) + FadeOut(fade_time))
        
    def quest_done(self, title):
        self.queue.append(title)
        if len(self.queue) == 1:
            self.make_announce(title)
