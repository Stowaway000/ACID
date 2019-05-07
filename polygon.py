import cocos
from cocos.director import director
import pyglet
from pyglet.window import key, mouse
from cocos import mapcolliders
from cocos.actions import *
from math import atan, degrees
import os
from physics import *


mouse_x = 10
mouse_y = 10
vector = [0, 0]


class skin(cocos.sprite.Sprite):
    def __init__(self, name, mover, pos):
        stat = pyglet.image.load("res/img/skins/" + name + "/" + name + ".png")
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

        self.body.position = 0, 0
        self.body_seat.position = 0, 0
        self.head.position = 0, 0
        self.lhand.position = -10, 7
        self.rhand.position = 10, 7

        self.add(self.lhand, z=0)
        self.add(self.rhand, z=0)
        self.add(self.body, z=1)
        self.add(self.head, z=2)

        self.armor = None
        self.lweapon = None
        self.rweapon = None
        self.both = False

        self.static = stat
        self.walk = anim

        self.seating = False
        self.walking = False

        self.position = pos
        self.velocity = (0, 0)
        
        self.cshape = collision_unit([eu.Vector2(*self.position), self.static.width/2], "circle")
        self.do(mover)

    def draw(self):
        if self.both:
            self.remove(self.lhand)
            self.remove(self.rhand)
            self.add(self.rweapon, z=0)
        else:
            if self.lweapon:
                self.add(self.lhand, z=0)
            if self.rweapon:
                self.add(self.rhand, z=0)

        if self.seating:
            self.add(self.body_seat, z=1)
        else:

            if self.armor:
                self.add(self.armor, z=1)
            else:
                self.add(self.body, z=1)

        self.show_weapon()

    def walk(self):
        self.walking = not self.walking

    def seat(self):
        self.seating = not self.seating
        if not self.seating:
            self.remove(self.body_seat)

    def add_weapon(self, name, sprite, hand):
        if weapon.weapons[name].two_handed:
            self.remove(self.lhand)
            self.remove(self.rhand)
            self.lweapon = False
            self.rweapon = sprite
            self.rweapon.position = 10, 10
        else:
            if hand == 'l':
                self.lweapon = sprite
                self.lweapon.position = -10, 10
            if hand == 'r':
                self.rweapon = sprite
                self.rweapon.position = 10, 10

    def add_armor(self, sprite):
        self.armor = sprite

    def remove_armor(self):
        self.armor = None

    def show_weapon(self):
        if self.both:
            self.add(self.rweapon, z=0)
        else:
            if self.lweapon:
                self.add(self.lweapon, z=0)
            if self.rweapon:
                self.add(self.rweapon, z=0)

    def hide_weapon(self):
        self.remove(self.lweapon)
        self.remove(self.rweapon)


class MapLayer(cocos.layer.ScrollableLayer):
    def __init__(self, name):
        super().__init__()
        level = cocos.tiles.load("maps/" + name + "/map.tmx")
        self.layer_floor = level["floor"]
        self.layer_vertical = level["wall"]
        self.layer_above = level["up"]
        self.layer_objects = level["obj"]
        self.layer_collision = level["collision"]
        self.layer_collision.objects += self.layer_objects.objects
