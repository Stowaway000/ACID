import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse
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
        self.weapon_l_equip = -1
        self.weapon_r_equip = -1

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
        if self.weapon_left == -1 and self.weapon_right == -1:
            self.weapon_left = self.weapon_l_equip
            self.weapon_right = self.weapon_r_equip
            self.skin.show_weapon()
        else:
            self.weapon_left = -1
            self.weapon_right = -1
            self.skin.hide_weapon()

    # Атаковать оружием
    def attack(self, hand):
        if hand == 'r' and self.weapon_right != -1:
            self.inventory.get_weapon(self.weapon_right).shoot()
        elif self.weapon_left != -1:
            self.inventory.get_weapon(self.weapon_left).shoot()

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

    # Положить вещь в инвентарь
    def take_item(self, item, count):
        if get_type(item) == 'weapon' and self.weapon_l_equip * \
                self.weapon_r_equip > 0:
            self.weapon_r_equip = len(self.inventory.weapons)
            self.inventory.add(item, count)
            if self.inventory.weight > 4 * self.SEACIL[0]:
                self.overweight = True

            self.skin.add_weapon(item, self.inventory.get_weapon(self.weapon_r_equip), 'r')
            self.switch_weapon()

    # Выбросить педмет из инвентаря
    def drop_item(self):
        pass

    # Выложить предмет в ящик
    def store_item(self):
        pass


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

        self.position = pos
        self.velocity = (0, 0)

        self.cshape = collision_unit([eu.Vector2(*self.position), self.body.width / 2], "circle")
        self.do(mover)

    def walker(self, new_state):
        if self.walking != new_state:
            self.walking = new_state
            if not self.seating:
                if self.walking:
                    self.remove("body")
                    self.add(self.animation, name="body", z=1)
                else:
                    self.remove("body")
                    self.add(self.body, name="body", z=1)

    def seat(self):
        self.seating = not self.seating
        if self.seating:
            self.remove("body")
            self.add(self.body_seat, name="body_seat", z=1)
        if not self.seating:
            self.remove("body_seat")
            self.add(self.body, name="body", z=1)

    def add_weapon(self, name, handler, hand):
        if weapon.weapons[name].two_handed:
            if self.lweapon:
                self.remove("lhand")
                self.remove("lweapon")
            if self.rweapon:
                self.remove("rhand")
                self.remove("rweapon")
            self.lweapon = False
            self.rweapon = handler
            self.rweapon.position = 10, 15
            self.body.rotation = 20
            self.rhand.position = 10, 4
            self.both = True
        else:
            self.both = False
            if hand == 'l':
                self.lweapon = handler
                self.lweapon.position = -10, 20
                self.body.rotation = 0
                self.rhand.position = 10, 7
            if hand == 'r':
                self.rweapon = handler
                self.rweapon.position = 10, 20
                self.body.rotation = 0
                self.rhand.position = 10, 7

    def remove_weapon(self, hand):
        if hand == "both":
            self.rweapon = None
            self.remove("rhand")
            self.remove("both")
        elif hand == "l":
            self.lweapon = None
            self.remove("lhand")
            self.remove("lweapon")
        else:
            self.rweapon = None
            self.remove("rhand")
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
        if self.both:
            self.add(self.rhand, name="rhand", z=0)
            self.add(self.rweapon, name="both", z=2)
            self.body.rotation = 20
            self.rhand.position = 10, 4
        else:
            if self.lweapon:
                self.add(self.lhand, name="lhand", z=0)
                self.add(self.lweapon, name="lweapon", z=2)
            if self.rweapon:
                self.add(self.rhand, name="rhand", z=0)
                self.add(self.rweapon, name="rweapon", z=2)

    def hide_weapon(self):
        self.body.rotation = 0
        self.rhand.position = 10, 7
        if self.both:
            self.remove("rhand")
            self.remove("both")
        else:
            if self.lweapon:
                self.remove("lhand")
                self.remove("lweapon")
            if self.rweapon:
                self.remove("rhand")
                self.remove("rweapon")