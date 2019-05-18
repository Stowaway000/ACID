import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse
from cocos.actions import *
from cocos import mapcolliders
from math import sqrt, sin, cos, radians, atan, degrees


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

    def draw_on(self, scroller):
        scroller.add(self.layer_floor, -1)
        scroller.add(self.layer_vertical, 1)
        scroller.add(self.layer_objects, 1)
        scroller.add(self.layer_decoration, 0)
        scroller.add(self.layer_above, 2)
        scroller.add(self.layer_anim_up, 2)
