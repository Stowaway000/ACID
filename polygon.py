import cocos
from cocos.director import director
import pyglet
from pyglet.window import key, mouse
from cocos import mapcolliders
from cocos.actions import *
from math import atan, degrees
import os
from physics import *
from models import weapon

mouse_x = 10
mouse_y = 10
vector = [0, 0]

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
