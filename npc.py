import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse
from cocos.actions import *
from cocos import mapcolliders
from math import sqrt, sin, cos, radians, atan, degrees, hypot

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
        for i in range(2):
            for j in range(2):
                self.rad_patrol[i][j] = stats[3 + i + j]

        super().__init__(name, fraction, stats[3:-1], npc_mover(), stats[-1])

        self.angle_velocity = 0

    # AI
    def think(self):
        pass

    # Создать труп и прочее
    def die(self):
        pass


class AI:
    def __init__(self, rad_patrol):
        self.mover = npc_mover()
        self.state = "patrol"
        self.rad_patrol = rad_patrol

    def change_state(self):
        if self.state == "patrol":
            self.state = "fight"
        else:
            self.state = "patrol"

    def get_way(self, x, y):
        self.mover.update(x, y)

    def think(self):
        if self.state == "patrol":
            pass
            # x, y = ...
            # self.get_way(x, y)
        else:
            pass


class patroling(AI):
    def choose_point(self):
        pass

    def trade(self):
        pass

    def think(self):
        pass


class fight(AI):
    def choose_enemy(self):
        pass

    def choose_cover(self):
        pass

    def danger(self):
        pass

    def attack(self):
        pass

    def think(self):
        pass


class npc_mover(cocos.actions.Move):
    def __init__(self):
        super().__init__()
        self.x = self.target.position[0]
        self.y = self.target.position[1]

    def step(self, dt):
        if self.target.position[0] != self.x and self.target.position[1] != self.y:
            vel_x = (self.x / hypot(self.x, self.y)) * 50
            vel_y = (self.y / hypot(self.x, self.y)) * 50
        else:
            vel_x = 0
            vel_y = 0

        if self.target.velocity[0] or self.target.velocity[1]:
            self.target.walk(True)
        elif not (self.target.velocity[0] or self.target.velocity[1]):
            self.target.walk(False)

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

    def update(self, x, y):
        self.x = x
        self.y = y
