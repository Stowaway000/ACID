import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse
from cocos.actions import *
from cocos import mapcolliders
from math import sqrt, sin, cos, radians, atan, degrees, hypot
from random import randint

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
        self.rad_patrol = [[0] * 2 for i in range(2)]
        self.rad_patrol[0][0] = stats[3]
        self.rad_patrol[0][1] = stats[4]
        self.rad_patrol[1][0] = stats[5]
        self.rad_patrol[1][1] = stats[6]
        self.next_x = stats[-2]
        self.next_y = stats[-1]

        super().__init__(name, fraction, stats[7:-2], npc_mover(), (stats[-1], stats[-2]))

        self.angle_velocity = 0
        self.state = "patrol"
        self.patrol = patroling(self.rad_patrol)
        self.fight = fight()
        self.info = []

    def change_state(self):
        if self.state == "patrol":
            self.state = "fight"
        else:
            self.state = "patrol"

    # AI
    def think(self):
        if self.state == "patrol":
            pass
            # x, y = ...
            # self.get_way(x, y)
        else:
            pass

    # Создать труп и прочее
    def die(self):
        pass


class patroling:
    def __init__(self, rad_patrol):
        self.rad_patrol = rad_patrol

    def choose_point(self):
        x = randint(self.rad_patrol[0][0], self.rad_patrol[1][0])
        y = randint(self.rad_patrol[1][1], self.rad_patrol[0][1])
        return x, y

    def trade(self):
        pass

    def think(self):
        pass


class fight():
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
    def step(self, dt):
        if self.target.position[0] != self.target.parent.next_x and self.target.position[1] != self.target.parent.next_y:
            vel_x = (self.target.parent.x / hypot(self.target.parent.x, self.target.parent.y)) * 50
            vel_y = (self.target.parent.y / hypot(self.target.parent.x, self.target.parent.y)) * 50
        else:
            vel_x = 0
            vel_y = 0

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
        print(new.cshape.center)
        self.target.parent.info = self.target.parent.get_in_sector(self.target.position,
                                                                   self.target.rotation,
                                                                   20,
                                                                   [cos(self.target.rotation),
                                                                    sin(self.target.rotation)])
        self.target.velocity = (vel_x, vel_y)
        self.target.position = new.cshape.center

        if vel_x == 0 and vel_y == 0:
            self.target.parent.next_x, self.target.parent.next_y = \
                self.target.parent.patrol.choose_point()
