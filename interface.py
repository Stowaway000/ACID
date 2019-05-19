import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.text import Label, HTMLLabel
from cocos.layer import Layer, ColorLayer, MultiplexLayer, ScrollingManager, ScrollableLayer
from cocos.scenes import pause
from cocos.scene import Scene
from cocos.menu import LEFT, RIGHT, BOTTOM, TOP, CENTER
from cocos.actions import FadeIn, FadeOut, MoveBy, RotateBy, CallFunc
import pyglet
from pyglet.window import key, mouse
from menu import set_menu_style, go_back, quit_game
from item import get_global, get_type


def add_label(txt, point, anchor='center', size=14):
    return Label(txt, point, font_name='Calibri', font_size=size,\
                 anchor_x=anchor, anchor_y='center')


def add_text(txt, point, anchor='center', size=14, padding=10):
    point = (point[0]+padding, point[1]-padding)
    txt = '<font face="Calibri" size="' + str(size) + '" color="white">'\
          + txt + '</font>'
    return HTMLLabel(txt, point, anchor_x=anchor, anchor_y='top',\
                     multiline=True, width=200-padding*2)


class Button(ColorLayer):
    def __init__(self, txt, x, y, w, h):
        super().__init__(100, 50, 0, 255)
        self.position = (x, y)
        self.width = w
        self.height = h

        self.label = add_label(txt, (w/2, h/2))
        self.add(self.label)

        self.rect = cocos.rect.Rect(x, y, w, h)

        self.visible = False

    def click(self, x, y):
        return self.rect.contains(x, y) and self.visible


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


class visual_inventory(ColorLayer):
    is_event_handler = True
    
    def __init__(self, hero):
        super().__init__(31, 38, 0, 255)

        w = director.window.width
        h = director.window.height
        self.position = (w/6, h/6)
        self.width = int(2*w/3)
        self.height = int(2*h/3)

        self.on_one = self.height/64

        self.item_window = ScrollingManager(cocos.rect.Rect(w/6, h/6, 200, int(2*h/3)))
        self.item_window.position = (w/6, h/6)
        self.item_window.scale = 2
        
        self.item_stack = ScrollableLayer()

        self.viewpoint = (w/6+50, h/6+self.height/4+16)

        self.scrollbar = ColorLayer(255, 200, 100, 255)
        self.scrollbar.width = 15
        
        self.up = h/6+self.height/4+16
        self.down = 0

        self.item_window.add(self.item_stack)
        self.add(self.scrollbar, name='sb')
        self.add(self.item_window)

        self.pixel_rel = 1

        self.hero_ref = hero

        self.buttons = []
        self.buttons.append(Button('Drop', 230, self.height-200, 100, 30))
        self.buttons.append(Button('Equip Right', 230, self.height-250, 100, 30))
        self.buttons.append(Button('Equip Left', 230, self.height-300, 100, 30))
        self.buttons.append(Button('Unequip', 230, self.height-250, 100, 30))

        self.items = []
        self.active_btn = []

        self.weapon_place = ColorLayer(255, 200, 100, 255, 100, 79)
        self.weapon_place.scale = 2
        self.weapon_place.anchor = (0, 0)
        self.weapon_place.position = (520, self.height-200)
        self.add(self.weapon_place, name='active')

        self.add(add_label('Right hand', (530, self.height-50), 'left'), 1)
        self.add(add_label('Left hand', (530, self.height-128), 'left'), 1,\
                 'lbl_left')
        
        self.selected = ''

    def refresh(self, pos):
        self.mouse_pos = pos
        invent = self.hero_ref.inventory

        total = len(invent.items) + len(invent.weapons) + len(invent.armors)
        if self.hero_ref.weapon_left != -1:
            total -= 1
        if self.hero_ref.weapon_right != -1:
            total -= 1
        
        self.remove('sb')
        self.scrollbar.height = int(self.height*min(self.on_one/total, 1))
        self.scrollbar.position = (200, self.height-self.scrollbar.height)
        self.add(self.scrollbar, name='sb')

        self.pixel_rel = self.scrollbar.height / self.height

        self.down = self.up - 32*(total-self.on_one)
        if self.down > self.up:
            self.down = self.up

        self.viewpoint = (self.viewpoint[0], self.up)
        self.item_window.set_focus(*self.viewpoint)

        for i in self.items:
            self.item_stack.remove(i)
        self.items.clear()

        if self.selected:
            self.btn_refresh('')
            self.selected = ''
            self.item_stack.remove('select')
            self.remove('naming')

        if 'w_right' in self.weapon_place.children_names:
            self.weapon_place.remove('w_right')
        if 'w_left' in self.weapon_place.children_names:
            self.weapon_place.remove('w_left')

        self.remove('active')
        if self.weapon_place.height < 79:
             self.add(add_label('Left hand', (530, self.height-128), 'left'), 1,\
                 'lbl_left')
        self.weapon_place.height = 79
        self.weapon_place.position = (520, self.height-200)
        self.add(self.weapon_place, name='active')
    
    def update(self, pos):
        self.refresh(pos)

        invent = self.hero_ref.inventory
        
        h = 0
        for key, val in invent.items.items():
            item = invent.get(key)
            spr = item.item_inv_sprite
            spr.position = (50, self.height/2-h*32)

            count = add_label(str(val), (40, 0))
            count.scale = 0.5
            spr.add(count, 1)
            self.item_stack.add(spr, 1, item.name+' i')
            self.items.append(item.name+' i')
            
            h += 1

        wps = invent.weapons
        for i in range(len(wps)):
            spr = wps[i].item_inv_sprite
            if i != self.hero_ref.weapon_left and i != self.hero_ref.\
               weapon_right:
                spr.position = (50, self.height/2-h*32)

                self.item_stack.add(spr, 1, wps[i].weapon_name+' '+str(i))
                self.items.append(wps[i].weapon_name+' '+str(i))
                
                h += 1
            elif i == self.hero_ref.weapon_left:
                spr.position = (50, 16)
                self.weapon_place.add(spr, 1, 'w_left')
            elif i == self.hero_ref.weapon_right:
                spr.position = (50, 55)
                if get_global(wps[i].weapon_name).two_handed:
                    self.remove('active')
                    self.weapon_place.height = 39
                    self.weapon_place.position = (520, self.height-121)
                    self.add(self.weapon_place, name='active')
                    self.remove('lbl_left')
                    
                    spr.position = (50, 16)
                self.weapon_place.add(spr, 1, 'w_right')
    
    def on_exit(self):
        director.window.set_mouse_position(*self.mouse_pos)
        super().on_exit()

    def move_view(self, dy):
        if self.viewpoint[1]+dy/2 > self.up:
            dy = 2*(self.up - self.viewpoint[1])
        elif self.viewpoint[1]+dy/2 < self.down:
            dy = 2*(self.down-self.viewpoint[1])

        self.scrollbar.position = (200, self.scrollbar.position[1]\
                                    +dy*self.pixel_rel)
                
        self.viewpoint = (self.viewpoint[0], self.viewpoint[1]+dy/2)
        self.item_window.set_focus(*self.viewpoint)
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x -= self.position[0]
        y -= self.position[1]

        if 195 < x < 220 and 0 < y < self.height:
            self.move_view(dy)

    def btn_set(self, key, index=''):
        st = []
        if key:
            st.append(0)
            tp = get_type(key.split()[0])
            if tp == 'weapon':
                index = int(index)
                if index != self.hero_ref.weapon_left and\
                   index != self.hero_ref.weapon_right:
                    st.append(1)
                    if not get_global(key.split()[0]).two_handed:
                        st.append(2)
                else:
                    st.append(3)

        return st

    def btn_refresh(self, key, index=''):
        need = self.btn_set(key, index)
        
        for i in self.active_btn:
            self.remove('btn'+str(i))
            self.buttons[i].visible = False

        for i in need:
            self.add(self.buttons[i], name='btn'+str(i))
            self.buttons[i].visible = True

        self.active_btn = need

    def on_item_click(self, key, val, index=''):
        if self.selected:
            self.item_stack.remove('select')
            self.remove('naming')
        
        self.btn_refresh(key, index)
                            
        selection = ColorLayer(100, 50, 0, 140)
        selection.width = 100
        selection.height = 32
        selection.position = (val.position[0]-50, val.position[1]-16)
        self.item_stack.add(selection, z=0, name='select')

        text = '<b>' + key.capitalize() + '</b><br>' + get_global(key)\
               .get_info()
        naming = add_text(text, (230, self.height)\
                          , 'left')
        self.add(naming, name='naming')

        self.selected = [key]
        if index != 'i':
            self.selected.append(int(index))

    def handle_btns(self, x, y):
        if self.buttons[0].click(x, y):
            self.hero_ref.drop_item(*self.selected)
            self.update(self.mouse_pos)
        
        if self.buttons[1].click(x, y):
            self.hero_ref.equip_weapon(self.selected[1], 'r')
            self.update(self.mouse_pos)

        if self.buttons[2].click(x, y):
            self.hero_ref.equip_weapon(self.selected[1], 'l')
            self.update(self.mouse_pos)
        
        if self.buttons[3].click(x, y):
            self.hero_ref.unequip_weapon(self.selected[1])
            self.update(self.mouse_pos)
    
    def on_mouse_press(self, x, y, button, modifiers):
        x -= self.position[0]
        y -= self.position[1]
        
        if button == mouse.LEFT:
            if 195 < x < 220 and (self.scrollbar.position[1] > y or\
               y > self.scrollbar.position[1]+self.scrollbar.height):
                dy = y - self.scrollbar.position[1] - self.scrollbar.height/2
                dy /= self.pixel_rel

                self.move_view(dy)
            elif 0 < x < 195 and 0 < y < self.height:
                y /= 2
                y += self.viewpoint[1] - self.up + 32
                names = self.item_stack.children_names
                for key, val in names.items():
                    if val.position[1] < y < val.position[1] + val.height and key != 'select':
                        self.on_item_click(key.split()[0], val, key.split()[1])
                        break
            else:
                self.handle_btns(x, y)
                
                cld = self.weapon_place.children_names
                if 'w_left' in cld:
                    if 520 < x < 720 and self.height-200 < y < self.height-136:
                        wp = self.hero_ref.inventory.get_weapon\
                             (self.hero_ref.weapon_left)
                        self.on_item_click(wp.weapon_name, cld['w_left'],\
                                           self.hero_ref.weapon_left)
                if 'w_right' in cld:
                    if 520 < x < 720 and self.height-121 < y < self.height-57:
                        wp = self.hero_ref.inventory.get_weapon\
                             (self.hero_ref.weapon_right)
                        self.on_item_click(wp.weapon_name, cld['w_right'],\
                                           self.hero_ref.weapon_right)


class stat_interface(Layer):
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


class interface(MultiplexLayer):
    is_event_handler = True
    
    def __init__(self, stats, host):
        self.stats = stat_interface(stats)
        self.invent = visual_inventory(host)
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
                self.invent.update(self.mouse_pos)
                self.switch_to(1)
            else:
                self.host.lurking = False
                self.switch_to(0)
        
        if symbol == key.ESCAPE:
            pause_sc = pause.get_pause_scene()
            
            pause_sc.remove(pause_sc.get_children()[1])

            pause_sc.add(game_menu(self.mouse_pos))
            
            director.push(pause_sc)
    
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
