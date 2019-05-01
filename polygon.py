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
        stat = pyglet.image.load("res/img/" + name + ".png")
        w_img = pyglet.image.load("res/img/" + name + "_walk.png")
        w_img_grid = pyglet.image.ImageGrid(w_img, 1, 9, item_width=29, item_height=14)
        anim = pyglet.image.Animation.from_image_sequence(w_img_grid[:], 0.05, loop=True)
        
        super().__init__(stat)

        self.scroller = None
        self.keyboard = key.KeyStateHandler()
        director.window.push_handlers(self.keyboard)

        self.static = stat
        self.walk = anim
        
        self.position = 100, 80
        self.velocity = (0, 0)
        
        self.rect_img = cocos.sprite.Sprite('res/img/coll_h.png')
        self.rect_img_cur = self.rect_img

        self.cshape = collision_unit([eu.Vector2(*self.position), self.static.width/2], "circle")
        self.do(mover)


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
