import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse
from cocos.actions import *
from cocos import mapcolliders
from math import sqrt, sin, cos, radians, atan, degrees

from creature import *

# Параметры мыши
mouse_x = 10
mouse_y = 10
vector = [0, 0]


# Класс ГГ
class hero(character):
    is_event_handler = True
    
    def __init__(self, name, fraction, seacil, stats, pos):
        super().__init__(name, fraction, seacil, hero_mover(), pos)

        self.hp = stats[0]
        self.stamina = stats[1]
        self.sp_stamina = stats[2]
        
        self.expirience = 0
        self.level = 0
        self.next_level = 1000

        self.lpressed = False
        self.rpressed = False

        self.interface = None

        self.lurking = False

    def take_damage(self, dmg, k):
        super().take_damage(dmg, k)

        arm = self.inventory.get_armor(self.armor)
        ar_ac = 0
        if arm:
            ar_ac = arm.ac

        dct = {'hp': self.hp,
               'armor': ar_ac}
        self.interface.update(dct)

    def equip_weapon(self, index, hand):
        super().equip_weapon(index, hand)

        dct = {}
        if hand == 'r':
            self.get_wp_stats('r', dct)
        else:
            self.get_wp_stats('l', dct)
        
        self.interface.update(dct)

    def unequip_weapon(self, index):
        super().unequip_weapon(index)

        dct = {}
        self.get_wp_stats('r', dct)
        self.get_wp_stats('l', dct)
        
        self.interface.update(dct)
    
    def equip_armor(self, index):
        super().equip_armor(index)
        
        dct = {'armor': self.inventory.get_armor(self.armor).ac}
        self.interface.update(dct)

    def unequip_armor(self, index):
        super().unequip_armor(index)
        
        dct = {'armor': 0}
        self.interface.update(dct)

    def get_wp_stats(self, hand, dct):
        if hand == 'r':
            if self.weapon_right != -1:
                wp = self.inventory.get_weapon(self.weapon_right)
                dct['weapon_r'] = [str(wp.cartridge)+'/'+\
                                   str(wp.get_max_cartridge()[0])]
                dct['weapon_r'].append(wp.item_inv_sprite)
            else:
                dct['weapon_r'] = [0]
        else:
            if self.weapon_left != -1:
                wp = self.inventory.get_weapon(self.weapon_left)
                dct['weapon_l'] = [str(wp.cartridge)+'/'+\
                                   str(wp.get_max_cartridge()[0])]
                dct['weapon_l'].append(wp.item_inv_sprite)
            else:
                dct['weapon_l'] = [0]
    
    def get_stats(self):
        ar_ac = 0
        if self.armor != -1:
            armor = self.inventory.get_armor(self.armor)
            ar_ac = armor.ac

        dct = {'hp': [self.hp],
               'armor': [ar_ac],
               'stamina': [self.stamina]}

        self.get_wp_stats('r', dct)
        self.get_wp_stats('l', dct)
        
        return dct
    
    # Закончить игру из-за смерти ГГ   
    def die(self):
        pass

    # Получить новый уровень
    def get_level(self):
        pass

    # Поворот взгляда
    def on_mouse_motion(self, x, y, dx, dy):
        if not self.lurking:
            global mouse_x, mouse_y
            mouse_x = x
            mouse_y = y

            self.interface.mouse_pos = x, y

            scroller = self.skin.scroller
            
            mid_x, mid_y = scroller.world_to_screen(scroller.fx, scroller.fy)

            x -= mid_x
            y -= mid_y

            if x:
                angle = degrees(atan(y/x))
            elif y > 0:
                angle = 90
            else:
                angle = -90        

            if x < 0 and y < 0:
                angle -= 180
            elif x < 0:
                angle += 180

            if not y and x < 0:
                angle = 180

            angle = -angle + 90

            if self.skin.rotation != angle:

                h_x, h_y = scroller.world_to_screen(scroller.fx, scroller.fy)
                    
                vector[0] = int(mouse_x - h_x)
                    
                vector[1] = int(mouse_y - h_y)

            self.skin.rotation = angle
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.lurking:
            self.on_mouse_motion(x, y, dx, dy)
            if buttons & mouse.LEFT and not self.skin.hidden:
                self.attack('r')
            elif buttons & mouse.RIGHT and not self.skin.hidden:
                self.attack('l')
            elif buttons & mouse.LEFT and buttons & mouse.RIGHT and not self.skin.hidden:
                self.attack('r')
                self.attack('l')
    
    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            clicked = False

            if not self.lurking:
                X, Y = self.parent.screen_to_world(x, y)
                for i in self.skin.near_objects:
                    obj = PickableObject.pickables[i]
                    if obj.spr.get_rect().contains(X, Y):
                        self.take_item(obj.name, obj.count, obj.additional)
                        obj.destruct()
                        self.skin.near_objects.remove(i)

                        clicked = True
                        break
                
                for i in self.skin.near_stashes:
                    obj = Stash.stashes[i]
                    if obj.sprite.get_rect().contains(X, Y):
                        self.interface.exchange_with(obj)

                        clicked = True
                        break
            
            if not clicked:
                self.lpressed = True
            
        if button == mouse.RIGHT:
            self.rpressed = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.lpressed = False
        if button == mouse.RIGHT:
            self.rpressed = False
    
    def on_key_press(self, symbol, modifiers):
        if not self.lurking:
            if symbol == key.R and self.lpressed and not self.skin.hidden:
                self.reload('r')
            elif symbol == key.R and self.rpressed and not self.skin.hidden:
                self.reload('l')
            elif symbol == key.R and modifiers & key.MOD_SHIFT:
                self.switch_weapon()
            elif symbol == key.R and not self.skin.hidden:
                self.reload('r')
                self.reload('l')
            elif symbol == key.E and self.skin.near_objects:
                obj = PickableObject.pickables[self.skin.near_objects[0]]
                self.take_item(obj.name, obj.count, obj.additional)
                obj.destruct()
                self.skin.near_objects.pop(0)
            elif symbol == key.E and self.skin.near_stashes:
                obj = Stash.stashes[self.skin.near_stashes[0]]
                pass
            
            if symbol == key.LCTRL or symbol == key.RCTRL:
                self.skin.seat()

    def on_key_release(self, symbol, modifiers):
        if not self.lurking:
            if symbol == key.LCTRL or symbol == key.RCTRL:
                self.skin.seat()

    def set_scroller(self, scr):
        self.skin.scroller = scr

    def set_collision(self, manager):
        self.skin.collider = manager


class hero_mover(cocos.actions.Move):
    def step(self, dt):
        if not self.target.parent.lurking:
            keyboard = self.target.keyboard
            vel_x = (keyboard[key.D] - keyboard[key.A]) * 75
            vel_y = (keyboard[key.W] - keyboard[key.S]) * 75

            if self.target.velocity[0] or self.target.velocity[1]:
                self.target.walker(True)
            elif not (self.target.velocity[0] or self.target.velocity[1]):
                self.target.walker(False)

            dx = vel_x * dt
            dy = vel_y * dt
            new = self.target.cshape

            new.cshape.center = eu.Vector2(new.cshape.center.x + dx, new.cshape.center.y)
            if self.target.collider.collision_manager.any_near(new, 0):
                vel_x = 0
                new.cshape.center.x -= dx

            new.cshape.center = eu.Vector2(new.cshape.center.x, new.cshape.center.y + dy)
            if self.target.collider.collision_manager.any_near(new, 0):
                vel_y = 0
                new.cshape.center.y -= dy

            self.target.velocity = (vel_x, vel_y)
            self.target.position = new.cshape.center
            self.target.scroller.set_focus(*new.cshape.center)

            self.target.scroller.set_focus(self.target.x, self.target.y)

            for name, i in PickableObject.pickables.items():
                if self.target.collider.collision_manager.they_collide(i.cshape, self.target.cshape):
                    if name not in self.target.near_objects:
                        self.target.near_objects.append(name)
                        i.select()
                else:
                    if name in self.target.near_objects:
                        self.target.near_objects.remove(name)
                        i.deselect()

            for name, i in Stash.stashes.items():
                if self.target.collider.collision_manager.they_collide(i.cshape, self.target.cshape):
                    if name not in self.target.near_stashes:
                        self.target.near_stashes.append(name)
                        i.select()
                else:
                    if name in self.target.near_stashes:
                        self.target.near_stashes.remove(name)
                        i.deselect()

            global mouse_x, mouse_y
            if self.target.velocity[0] or self.target.velocity[1]:
                mouse_x, mouse_y = self.target.scroller.world_to_screen(self.target.scroller.fx, self.target.scroller.fy)
                mouse_x += vector[0]
                mouse_y += vector[1]
                director.window.set_mouse_position(mouse_x, mouse_y)
        else:
            self.target.walker(False)
