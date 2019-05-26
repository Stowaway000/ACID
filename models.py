import cocos
from cocos.director import director
import pyglet
from pyglet.window import key, mouse
from cocos import mapcolliders
from cocos.actions import *
from math import atan, degrees
import cocos.euclid as eu
import cocos.collision_model as cm
import os


class MapLayer(cocos.layer.ScrollableLayer):
    def __init__(self, name):
        super().__init__()
        level = cocos.tiles.load("maps/" + name + "/map.tmx")
        self.layer_floor = level["floor"]
        self.layer_vertical = level["wall"]
        self.layer_above = level["up"]
        self.layer_objects = level["obj"]
        self.layer_decoration = level["decorations"]
        self.layer_collision = level["collision"]
        self.layer_collision.objects += self.layer_objects.objects

        self.layer_anim_up = cocos.layer.ScrollableLayer()

        anims = open("maps/" + name + "/anim_up.txt", 'r')
        s = anims.readline()
        while s:
            args = s.split()
            img = pyglet.image.load("res/img/map_anims/" + args[0] + ".png")
            img_grid = pyglet.image.ImageGrid(img, int(args[1]), int(args[2]),\
                                              item_width=int(args[3]),\
                                              item_height=int(args[4]))
            anim = pyglet.image.Animation.from_image_sequence(img_grid[:],\
                                                              float((args[5])), loop=True)
            anim = Sprite(anim)
            anim.position = (int(args[6]), int(args[7]))
            
            self.layer_anim_up.add(anim)
            
            s = anims.readline()

            
class Port(cocos.sprite.Sprite):
    def __init__(name, number, cur_x, cur_y, new_x, new_y):
        self.next_map = MapLayer(name)
        self.number = number
        self.position = cur_x,cur_y
        self.new_position = new_x, nex_y
        img = pyglet.image.load("res/img/port.png")
        super().__init__(img, cur_x,cur_y)
        self.cshape = cm. AARectShape(eu.Vector2(*self.position), self.width/2, self.height/2)
    def change_map(self):
        pass
