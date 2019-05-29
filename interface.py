import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.layer import Layer, ColorLayer, MultiplexLayer, ScrollingManager, ScrollableLayer
from cocos.scenes import pause
from cocos.scene import Scene
from cocos.menu import LEFT, RIGHT, BOTTOM, TOP, CENTER
from cocos.actions import FadeIn, FadeOut, MoveBy, RotateBy, CallFunc
import pyglet
from pyglet.window import key, mouse
from menu import set_menu_style, go_back, quit_game
from item import get_global, get_type
from utils import safe_remove, add_label, add_text


class Button(ColorLayer):
    def __init__(self, txt, x, y, w, h):
        super().__init__(120, 20, 8, 180)
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


class BasicVisualInventory(ColorLayer):
    is_event_handler = True

    def __init__(self, hero, pos, tp='hero', role='normal'):
        w = director.window.width
        h = director.window.height

        self.type = tp
        
        super().__init__(31, 38, 0, 200, 520, int(2*h/3))

        self.position = pos

        self.on_one = self.height/64

        self.item_window = ScrollingManager(cocos.rect.Rect(*pos, 200, int(2*h/3)))
        self.item_window.position = pos
        self.item_window.scale = 2
        
        self.item_stack = ScrollableLayer()

        self.viewpoint = (pos[0]+50, pos[1]+self.height/4+16)

        self.scrollbar = ColorLayer(120, 20, 8, 200, 15)
        
        self.up = pos[1]+self.height/4+16
        self.down = 0

        self.item_window.add(self.item_stack)
        self.add(self.scrollbar, name='sb')
        self.add(self.item_window)

        self.pixel_rel = 1

        self.hero_ref = hero

        self.items = []
        
        self.selected = ''

        description_bg = ColorLayer(31, 38, 0, 200, 280, 246)
        description_bg.position = (230, self.height-256)
        self.add(description_bg)

        self.role = role
        self.buttons = []
        self.active_btn = []
        if role == 'exchanger':
            self.buttons.append(Button('Shift', 230, self.height-296, 100, 30))

    def handle_btns(self, x, y):
        if self.role == 'exchanger':
            if self.buttons[0].click(x, y):
                self.hero_ref.store_item(*self.selected)
    
    def btn_set(self, key, index=''):
        st = []
        if key and self.role == 'exchanger':
            st.append(0)

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
    
    def refresh(self, pos):
        if self.selected:
            self.btn_refresh('')
        
        self.mouse_pos = pos
        invent = self.hero_ref.inventory

        total = len(invent.items) + len(invent.weapons) + len(invent.armors) + len(invent.usables)
        if self.type == 'hero':
            if self.hero_ref.weapon_left != -1:
                total -= 1
            if self.hero_ref.weapon_right != -1:
                total -= 1
            if self.hero_ref.armor != -1:
                total -= 1
        if not total:
            total = self.on_one
        
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
            self.selected = ''
            safe_remove(self.item_stack, 'select')
            self.remove('naming')

    def update(self, pos=-1):
        if pos == -1:
            pos = self.mouse_pos
        self.refresh(pos)

        invent = self.hero_ref.inventory
        
        h = 0
        for key, val in invent.items.items():
            item = invent.get(key)
            spr = Sprite(item.item_inv_sprite.image)
            spr.position = (50, self.height/2-h*32)

            count = add_label(str(val), (40, 0))
            count.scale = 0.5
            spr.add(count, 1)
            self.item_stack.add(spr, 1, item.name+' i')
            self.items.append(item.name+' i')
            
            h += 1

        for key, val in invent.usables.items():
            item = invent.get_usable(key)
            spr = Sprite(item.item_inv_sprite.image)
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
            if self.type == 'hero':
                if i != self.hero_ref.weapon_left and i != self.hero_ref.\
                   weapon_right:
                    spr.position = (50, self.height/2-h*32)

                    self.item_stack.add(spr, 1, wps[i].weapon_name+' '+str(i))
                    self.items.append(wps[i].weapon_name+' '+str(i))
                    
                    h += 1
            else:
                spr.position = (50, self.height/2-h*32)

                self.item_stack.add(spr, 1, wps[i].weapon_name+' '+str(i))
                self.items.append(wps[i].weapon_name+' '+str(i))
                    
                h += 1

        ars = invent.armors
        for i in range(len(ars)):
            spr = ars[i].item_inv_sprite
            if self.type == 'hero':
                if i != self.hero_ref.armor:
                    
                    spr.position = (50, self.height/2-h*32)

                    self.item_stack.add(spr, 1, ars[i].armor_name+' '+str(i))
                    self.items.append(ars[i].armor_name+' '+str(i))
                
                    h += 1
            else:
                spr.position = (50, self.height/2-h*32)

                self.item_stack.add(spr, 1, ars[i].armor_name+' '+str(i))
                self.items.append(ars[i].armor_name+' '+str(i))
                
                h += 1

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

    def on_item_click(self, key, val, index='', no_selection=False):
        safe_remove(self.item_stack, 'select')
        safe_remove(self, 'naming')

        if not no_selection:
            selection = ColorLayer(120, 20, 8, 140)
            selection.width = 100
            selection.height = 32
            selection.position = (val.position[0]-50, val.position[1]-16)
            self.item_stack.add(selection, z=0, name='select')

        text = '<b>' + key.capitalize() + '</b><br>' + get_global(key)\
               .get_info()
        naming = add_text(text, (230, self.height-10)\
                          , 'left', width=280)
        self.add(naming, name='naming')

        self.selected = [key]
        if index != 'i':
            self.selected.append(int(index))

        self.btn_refresh(key, index)

    def on_mouse_press(self, x, y, button, modifiers):
        x -= self.position[0]
        y -= self.position[1]

        self.handle_btns(x, y)
        
        if button == mouse.LEFT:
            if 195 < x < 220 and (self.scrollbar.position[1] +\
                                  self.scrollbar.height < y or\
                                  y < self.scrollbar.position[1]):
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

    def on_exit(self):
        director.window.set_mouse_position(*self.mouse_pos)
        super().on_exit()


class visual_inventory(BasicVisualInventory):
    is_event_handler = True
    
    def __init__(self, hero):
        w = director.window.width
        h = director.window.height
        
        super().__init__(hero, (w/2-365, h/6))
        
        self.width = 730

        self.buttons.append(Button('Drop', 230, self.height-296, 100, 30))
        self.buttons.append(Button('Equip Right', 340, self.height-296, 100, 30))
        self.buttons.append(Button('Equip Left', 450, self.height-296, 100, 30))
        self.buttons.append(Button('Unequip', 340, self.height-296, 100, 30))
        self.buttons.append(Button('Wear', 340, self.height-296, 100, 30))
        self.buttons.append(Button('Unwear', 340, self.height-296, 100, 30))
        self.buttons.append(Button('Use', 340, self.height-296, 100, 30))

        self.weapon_place = ColorLayer(31, 38, 0, 200, 100, 79)
        self.weapon_place.scale = 2
        self.weapon_place.anchor = (0, 0)
        self.weapon_place.position = (520, self.height-168)
        self.add(self.weapon_place, name='active')

        self.armor_place = ColorLayer(31, 38, 0, 200, 100, 39)
        self.armor_place.scale = 2
        self.armor_place.anchor = (0, 0)
        self.armor_place.position = (520, self.height-256)
        self.add(self.armor_place)

        self.add(add_label('Right hand', (self.weapon_place.position[0]+10,\
                                          self.weapon_place.position[1]+150),\
                           'left'), 1)
        self.add(add_label('Left hand', (self.weapon_place.position[0]+10,\
                                         self.weapon_place.position[1]+72),\
                           'left'), 1,\
                 'lbl_left')
        self.add(add_label('Armor', (self.armor_place.position[0]+10,\
                                     self.armor_place.position[1]+70),\
                           'left'), 1)

    def refresh(self, pos):
        safe_remove(self.weapon_place, 'w_right')
        safe_remove(self.weapon_place, 'w_left')
        safe_remove(self.armor_place, 'armor')
        
        super().refresh(pos)

        self.remove('active')
        if self.weapon_place.height < 79:
             self.add(add_label('Left hand', (self.weapon_place.position[0]+10,\
                                         self.weapon_place.position[1]+72),\
                           'left'), 1,\
                 'lbl_left')
        self.weapon_place.height = 79
        self.weapon_place.position = (520, self.height-168)
        self.add(self.weapon_place, name='active')
    
    def update(self, pos):
        super().update(pos)

        invent = self.hero_ref.inventory
        wps = invent.weapons
        if self.hero_ref.weapon_left != -1:
            spr = wps[self.hero_ref.weapon_left].item_inv_sprite
            spr.position = (50, 16)
            self.weapon_place.add(spr, 1, 'w_left')
        
        if self.hero_ref.weapon_right != -1:
            spr = wps[self.hero_ref.weapon_right].item_inv_sprite
            spr.position = (50, 55)
            if get_global(wps[self.hero_ref.weapon_right].weapon_name).two_handed:
                self.remove('active')
                self.weapon_place.height = 39
                self.weapon_place.position = (520, self.height-89)
                self.add(self.weapon_place, name='active')
                self.remove('lbl_left')
                    
                spr.position = (50, 16)
            self.weapon_place.add(spr, 1, 'w_right')
        
        if self.hero_ref.armor != -1:
            spr = invent.armors[self.hero_ref.armor].item_inv_sprite
            spr.position = (50, 16)
            self.armor_place.add(spr, 1, 'armor')

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
            elif tp == 'armor':
                index = int(index)
                if index != self.hero_ref.armor:
                    st.append(4)
                else:
                    st.append(5)
            elif tp == 'usable':
                st.append(6)

        return st

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

        if self.buttons[4].click(x, y):
            self.hero_ref.equip_armor(self.selected[1])
            self.update(self.mouse_pos)

        if self.buttons[5].click(x, y):
            self.hero_ref.unequip_armor(self.selected[1])
            self.update(self.mouse_pos)

        if self.buttons[6].click(x, y):
            self.hero_ref.use_item(self.selected[0])
            self.update(self.mouse_pos)
    
    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        x -= self.position[0]
        y -= self.position[1]

        cld = self.weapon_place.children_names
        cld_ar = self.armor_place.children_names
        wp_pl = self.weapon_place
        ar_pl = self.armor_place
        if 'w_left' in cld:
            if wp_pl.position[0] < x < wp_pl.position[0] + wp_pl.width*2\
               and wp_pl.position[1] < y < wp_pl.position[1]+wp_pl.height:
                
                wp = self.hero_ref.inventory.get_weapon\
                        (self.hero_ref.weapon_left)
                self.on_item_click(wp.weapon_name, cld['w_left'],\
                                           self.hero_ref.weapon_left,\
                                   no_selection=True)
        if 'w_right' in cld:
            if wp_pl.position[0] < x < wp_pl.position[0] + wp_pl.width*2\
               and wp_pl.position[1] + wp_pl.height< y < wp_pl.position[1]\
               + wp_pl.height*2:
                
                wp = self.hero_ref.inventory.get_weapon\
                        (self.hero_ref.weapon_right)
                self.on_item_click(wp.weapon_name, cld['w_right'],\
                                    self.hero_ref.weapon_right,\
                                   no_selection=True)
        if 'armor' in cld_ar:
            if ar_pl.position[0] < x < ar_pl.position[0] + ar_pl.width*2\
               and ar_pl.position[1]< y < ar_pl.position[1]\
               + ar_pl.height*2:
                
                wp = self.hero_ref.inventory.get_armor(self.hero_ref.armor)
                self.on_item_click(wp.armor_name, cld_ar['armor'],\
                                           self.hero_ref.armor,\
                                   no_selection=True)


class stat_interface(Layer):
    def __init__(self, stats):
        self.bars = {}

        super().__init__()

        for key, val in stats.items():
            self.bars[key] = add_label(str(val[0]), val[1])
            spr = Sprite('res/img/interface/' + key + '.png')
            spr.position = val[1]
            self.add(spr)

            if 'weapon' in key:
                spr.scale = 2
                spr.opacity = 0
                self.bars[key].opacity = 0
                
                if key[-1] == 'r':
                    self.r_wp = spr
                else:
                    self.l_wp = spr

                self.bars[key].position = (self.bars[key].position[0]+70,\
                                           self.bars[key].position[1]-32)

        for key, val in self.bars.items():
            self.add(val, name=key)

    def update(self, stats):
        for key, val in stats.items():
            self.change(key, val)

    def on_enter(self):
        if 'wp' in self.r_wp.children_names:
            self.r_wp.children_names['wp'].position = (0, 0)
        if 'wp' in self.l_wp.children_names:
            self.l_wp.children_names['wp'].position = (0, 0)
    
    def change(self, stat, new):
        self.remove(stat)

        old_pos = self.bars[stat].position
        self.bars[stat] = add_label(str(new), old_pos)

        if 'weapon' in stat:
            self.bars[stat].opacity = 0
            if len(new) > 1:
                self.bars[stat] = add_label(str(new[0]), old_pos)
                self.bars[stat].opacity = 255
                
                new[1].position = (0, 0)
                if stat[-1] == 'r':
                    self.r_wp.opacity = 255
                    safe_remove(self.r_wp, 'wp')
                    self.r_wp.add(new[1], name='wp')
                else:
                    self.l_wp.opacity = 255
                    safe_remove(self.l_wp, 'wp')
                    self.l_wp.add(new[1], name='wp')
            elif stat[-1] == 'r':
                safe_remove(self.r_wp, 'wp')
                self.r_wp.opacity = 0
            elif stat[-1] == 'l':
                safe_remove(self.l_wp, 'wp')
                self.l_wp.opacity = 0

        self.add(self.bars[stat], name=stat)


class interface(MultiplexLayer):
    is_event_handler = True
    
    def __init__(self, stats, host):
        self.stats = stat_interface(stats)
        self.invent = visual_inventory(host)

        w = director.window.width
        h = director.window.height
        self.exchange = Layer()
        self.mine = BasicVisualInventory(host, (w/6-60, h/6), role='exchanger')
        self.exchange.add(self.mine)
        super().__init__(self.stats, self.invent, self.exchange)

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
        
        if symbol == key.E:
            if self.enabled_layer != 2:
                his = self.host.get_partner()
                if his:
                    self.exchange_with(his)
            else:
                self.host.lurking = False
                self.switch_to(0)
        
        if symbol == key.ESCAPE:
            pause_sc = pause.get_pause_scene()
            
            pause_sc.remove(pause_sc.get_children()[1])

            pause_sc.add(game_menu(self.mouse_pos))
            
            director.push(pause_sc)

    def exchange_with(self, his):
        w = director.window.width
        h = director.window.height
        safe_remove(self.exchange, 'his')
        self.his = BasicVisualInventory(his, (w/6+480, h/6), 'stash', 'exchanger')
        his.set_partner(self.host)
        self.exchange.add(self.his, name='his')

        self.host.lurking = True
        self.mine.update(self.mouse_pos)
        self.his.update(self.mouse_pos)
        self.switch_to(2)

    def update_both(self):
        self.his.update()
        self.mine.update()
    
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
