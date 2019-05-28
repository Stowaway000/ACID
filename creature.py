import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse
import cocos.audio.pygame.mixer as mixer
from cocos.actions import *
from cocos import mapcolliders
from math import sqrt, sin, cos, radians, atan, degrees

from item import *
from physics import *

# Параметры мыши
mouse_x = 10
mouse_y = 10
vector = [0, 0]

# Класс персонажа
class character(cocos.layer.ScrollableLayer):
    characters = []

    def __init__(self, name, fraction, seacil, mover, pos):
        super().__init__()

        self.photo = cocos.sprite.Sprite('res/img/portraits/' + name + '.png')

        self.SEACIL = seacil

        self.inventory = inventory()

        self.weapon_left = -1
        self.weapon_right = -1

        self.armor = -1

        self.skin = skin(name, mover, pos)

        self.add(self.skin)

        self.stand = 'normal'

        self.fraction = fraction

        self.overweight = False

    @staticmethod
    def get_in_sector(me, angle, r, look):
        chars = []

        angle = radians(angle) / 2
        vector = (look[0] * srqt(r), look[1] * srqt(r))
        r_vector = (vector[0] * cos(angle) - vector[1] * sin(angle), \
                    vector[0] * sin(angle) + vector[1] * cos(angle))
        s = abs(vector[0] * r_vector[1] - vector[1] * r_vector[0]) / 2

        for i in character.characters:
            vect = [me[0] - i.skin.x, me[1] - i.skin.y]
            dist = sqrt(vect[0] * vect[0] + vect[1] * vect[1])
            vect[0] *= sqrt(r / dist)
            vect[1] *= sqrt(r / dist)
            if dist <= r:
                if abs(vect[0] * vector[1] - vect[1] * vector[0]) / 2 <= s:
                    chars.append(i.get_info())

        return chars

    # Получить информацию о персонаже
    def get_info(self):
        # TODO
        return (fraction, self.skin.position)

    # Увеличить характеристику
    def set(self, attr, add):
        if attr == 'hp':
            self.hp += add
        elif attr == 'stamina':
            self.stamina += add

    # Получение урона
    def take_damage(self, dmg, k):
        if self.armor != -1:
            dmg -= self.inventory.get_armor(armor).statusAC(dmg, k)

        if dmg > 0:
            self.hp -= dmg

    # Специальная способность
    def use_ability(self):
        pass

    # Достать\спрятать оружие
    def switch_weapon(self):
        if self.skin.hidden:
            self.skin.show_weapon()
        else:
            self.skin.hide_weapon()

    # Атаковать оружием
    def attack(self, hand):
        if hand == 'r' and self.weapon_right != -1:
            self.inventory.get_weapon(self.weapon_right).shoot()
        elif self.weapon_left != -1:
            self.inventory.get_weapon(self.weapon_left).shoot()

    def calm(self, hand):
        if hand == 'r' and self.weapon_right != -1:

            self.inventory.get_weapon(self.weapon_right).refresh()
        elif self.weapon_left != -1:
            self.inventory.get_weapon(self.weapon_left).refresh()
    
    # Перезарядить оружие
    def reload(self, hand):
        if hand == 'r' and self.weapon_right != -1:
            ammo, ammo_type = self.inventory.get_weapon(self.weapon_right) \
                .get_max_cartridge()
            ammo = self.inventory.take(ammo_type, ammo)
            change = self.inventory.get_weapon(self.weapon_right).recharge(ammo)
            self.inventory.add(ammo_type, change)
        elif self.weapon_left != -1:
            ammo, ammo_type = self.inventory.get_weapon(self.weapon_left) \
                .get_max_cartridge()
            ammo = self.inventory.take(ammo_type, ammo)
            change = self.inventory.get_weapon(self.weapon_left).recharge(ammo)
            self.inventory.add(ammo_type, change)

    # Использовать бафф
    def use_item(self, item):
        self.inventory.get_usable(item).use(self)
        self.inventory.take(item, 1)

    def equip_weapon(self, index, hand):
        wp = self.inventory.get_weapon(index)
        if hand == 'r':
            self.weapon_right = index
            
            if get_global(wp.weapon_name).two_handed:
                self.unequip_weapon(self.weapon_left)
                
            self.skin.add_weapon(wp.weapon_name, wp, 'r')
        else:
            right = self.inventory.get_weapon(self.weapon_right)
            if get_global(right.weapon_name).two_handed:
                self.unequip_weapon(self.weapon_right)

            self.weapon_left = index
            self.skin.add_weapon(wp.weapon_name, wp, 'l')
            
    def unequip_weapon(self, index):
        if index == self.weapon_left:
            self.weapon_left = -1
            self.skin.remove_weapon('l')
        
        if index == self.weapon_right:
            self.weapon_right = -1
            self.skin.remove_weapon('r')

    def equip_armor(self, index):
        self.armor = index
        self.skin.add_armor(self.inventory.get_armor(index))

    def unequip_armor(self, index):
        if index == self.armor:
            self.armor = -1
            self.skin.remove_armor()
    
    # Положить вещь в инвентарь
    def take_item(self, item, count, adds=[]):
        self.inventory.add(item, count, adds)
        if self.inventory.weight > 4 * self.SEACIL[0]:
            self.overweight = True
        
        if get_type(item) == 'weapon' and self.weapon_left == -1 and\
                self.weapon_right == -1:
            self.equip_weapon(len(self.inventory.weapons) - 1, 'r')
            if self.skin.hidden:
                self.switch_weapon()
    
    # Выбросить педмет из инвентаря
    def drop_item(self, item, ind=0, count='all'):
        tp = get_type(item)
        adds = []
        
        if tp == 'item':
            count = self.inventory.take(item, count)
        elif tp == 'weapon':
            adds.append(self.inventory.weapons[ind].cartridge)
            
            self.unequip_weapon(ind)
            
            if self.weapon_left == len(self.inventory.weapons) - 1:
                self.weapon_left = ind
            
            if self.weapon_right == len(self.inventory.weapons) - 1:
                self.weapon_right = ind
            
            count = self.inventory.take(item, index=ind)
        elif tp == 'armor':
            adds.append(self.inventory.armors[ind].ac)
            
            self.unequip_armor(ind)
            
            if self.armor == len(self.inventory.armors) - 1:
                self.weapon_left = ind
            
            count = self.inventory.take(item, index=ind)

        PickableObject(item, self.skin.position, count, adds).place(self.skin.scroller)

    # Выложить предмет в ящик
    def store_item(self, item, ind=0, count='all'):
        tp = get_type(item)
        adds = []
        
        if tp == 'item':
            count = self.inventory.take(item, count)
            self.partner.take_item(item, count)
        elif tp == 'weapon':
            adds.append(self.inventory.weapons[ind].cartridge)
            
            self.unequip_weapon(ind)
            
            if self.weapon_left == len(self.inventory.weapons) - 1:
                self.weapon_left = ind
            
            if self.weapon_right == len(self.inventory.weapons) - 1:
                self.weapon_right = ind
            
            count = self.inventory.take(item, index=ind)
            self.partner.take_item(item, count, adds)
        elif tp == 'armor':
            adds.append(self.inventory.armors[ind].ac)
            
            self.unequip_armor(ind)
            
            if self.armor == len(self.inventory.armors) - 1:
                self.weapon_left = ind
            
            count = self.inventory.take(item, index=ind)
            self.partner.take_item(item, count, adds)
        
        self.interface.update_both()


class skin(cocos.sprite.Sprite):
    def __init__(self, name, mover, pos):
        stat = pyglet.image.load("res/img/skins/init.png")
        w_img = pyglet.image.load("res/img/skins/" + name + "/" + name + "_walk.png")
        w_img_grid = pyglet.image.ImageGrid(w_img, 1, 9, item_width=29, item_height=14)
        anim = pyglet.image.Animation.from_image_sequence(w_img_grid[:], 0.05, loop=True)

        super().__init__(stat)

        self.scroller = None
        self.keyboard = key.KeyStateHandler()
        director.window.push_handlers(self.keyboard)

        self.body = cocos.sprite.Sprite("res/img/skins/" + name + "/" + name + "_body.png")
        self.body_seat = cocos.sprite.Sprite("res/img/skins/" + name + "/" + name + "_body_seat.png")
        self.lhand = cocos.sprite.Sprite("res/img/skins/" + name + "/" + name + "_lhand.png")
        self.rhand = cocos.sprite.Sprite("res/img/skins/" + name + "/" + name + "_rhand.png")
        self.head = cocos.sprite.Sprite("res/img/skins/" + name + "/" + name + "_head.png")
        self.animation = cocos.sprite.Sprite(anim)

        self.body.position = 0, 0
        self.body_seat.position = 0, 0
        self.head.position = 0, 0
        self.lhand.position = -10, 7
        self.rhand.position = 10, 7

        self.add(self.body, name="body", z=1)
        self.add(self.head, name="head", z=3)

        self.armor = None
        self.lweapon = None
        self.rweapon = None
        self.both = False

        self.seating = False
        self.walking = False

        self.hidden = True

        self.position = pos
        self.velocity = (0, 0)

        self.step_sound = mixer.Sound("res/sound/step.wav")
        self.pause_counter = 0

        self.cshape = collision_unit([eu.Vector2(*self.position), self.body.width / 2], "circle")
        self.do(mover)

        self.near_objects = []
        self.near_stashes = []

    def walker(self, new_state):
        if self.walking != new_state:
            self.walking = new_state
            if not self.seating:
                self.remove("body")                
                if self.walking:
                    if self.armor:
                        self.add(self.armor.walk_sprite, name="body", z=1)
                    else:
                        self.add(self.animation, name="body", z=1)
                else:
                    if self.armor:
                        self.add(self.armor, name="body", z=1)
                    else:
                        self.add(self.body, name="body", z=1)

    def seat(self):
        self.seating = not self.seating
        if self.seating:
            self.remove("body")
            self.add(self.body_seat, name="body_seat", z=1)
        if not self.seating:
            self.remove("body_seat")

            if self.armor:
                self.add(self.armor, name="body", z=1)
            else:
                self.add(self.body, name="body", z=1)

    def add_weapon(self, name, handler, hand):
        if Weapon.weapons[name].two_handed:
            if self.lweapon:
                self.remove_weapon('l')
            if self.rweapon:
                self.remove_weapon('r')
            self.rweapon = handler
            self.rweapon.position = 10, 15
            self.body.rotation = 20
            self.rhand.position = 10, 4
            self.both = True
        else:
            if hand == 'l':
                self.remove_weapon('l')
                self.lweapon = handler
                self.lweapon.position = -10, 20
                self.body.rotation = 0
                self.rhand.position = 10, 7
            if hand == 'r':
                self.remove_weapon('r')
                self.rweapon = handler
                self.rweapon.position = 10, 20
                self.body.rotation = 0
                self.rhand.position = 10, 7
            self.both = False

        if not self.hidden:
            self.show_weapon()

    def remove_weapon(self, hand):
        if hand == "l":
            if self.lweapon:
                self.lweapon = None
                if not self.hidden:
                    self.remove("lhand")
                    if not self.both:
                        self.remove("lweapon")
        else:
            if self.rweapon:
                self.rweapon = None
                if not self.hidden:
                    self.remove("rhand")
                    if self.both:
                        self.remove("lhand")
                        self.remove("both")
                        self.both = False
                    else:
                        self.remove("rweapon")

    def add_armor(self, sprite):
        self.armor = sprite
        self.remove("body")
        self.add(self.armor, name="body", z=1)

    def remove_armor(self):
        self.armor = None
        self.remove("body")
        self.add(self.body, name="body", z=1)

    def show_weapon(self):
        self.hidden = False
        
        if self.both:
            self.add(self.lhand, name="lhand", z=0)
            self.add(self.rhand, name="rhand", z=0)
            self.add(self.rweapon, name="both", z=2)
            self.body.rotation = 20
            self.rhand.position = 10, 4
        else:
            if self.lweapon:
                if 'lhand' not in self.children_names:
                    self.add(self.lhand, name="lhand", z=0)
                    self.add(self.lweapon, name="lweapon", z=2)
            if self.rweapon:
                if 'rhand' not in self.children_names:
                    self.add(self.rhand, name="rhand", z=0)
                    self.add(self.rweapon, name="rweapon", z=2)

    def hide_weapon(self):
        self.hidden = True
        
        self.body.rotation = 0
        self.rhand.position = 10, 7
        if self.both:
            self.remove("lhand")
            self.remove("rhand")
            self.remove("both")
        else:
            if self.lweapon:
                self.remove("lhand")
                self.remove("lweapon")
            if self.rweapon:
                self.remove("rhand")
                self.remove("rweapon")
