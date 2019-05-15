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

# Класс NPC
class NPC(character):
    def __init__(self, name, fraction):
        info = open('stats/chars/' + name + '.txt', 'r')
        stats = list(map(float, info.readline().split()))
        info.close()

        self.hp = stats[0]
        self.stamina = stats[1]
        self.sp_stamina = stats[2]

        super().__init__(name, fraction, stats[3:-1], npc_mover(), stats[-1])

        self.angle_velocity = 0

    # AI
    def think(self):
        pass

    # Создать труп и прочее
    def die(self):
        pass


class npc_mover(cocos.actions.Move):
    def step(self, dt):
        #TODO
        pass
