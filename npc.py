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

EPS = 1e-3

# Класс NPC
class NPC(character):
    def __init__(self, name, fraction, *pos):
        pos = int(pos[0]), int(pos[1])
        info = open('res/stats/chars/' + name + '.txt', 'r')
        stats = list(map(int, info.readline().split()))

        self.hp = stats[0]
        self.stamina = stats[1]
        self.sp_stamina = stats[2]
        self.rad_patrol = [[0] * 2 for i in range(2)]
        self.rad_patrol[0][0] = stats[3] + pos[0]
        self.rad_patrol[0][1] = stats[4] + pos[1]
        self.rad_patrol[1][0] = stats[5] + pos[0]
        self.rad_patrol[1][1] = stats[6] + pos[1]
        self.next_x = pos[0]
        self.next_y = pos[1]
        self.hash = str(hash(self))

        super().__init__(name, fraction, stats[7:], npc_mover(), pos)

        self.angle_velocity = 0
        self.state = "patrol"
        self.patrol = patroling(self.rad_patrol)
        self.fight = fight()
        self.info = []

        s = info.readline()
        while s:
            s = s.split()
            self.take_item(s[0], int(s[1]))
            s = info.readline()
        info.close()

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
        lr = cocos.layer.ScrollableLayer()
        spr = Sprite('res/img/corpse.png')
        spr.position = self.skin.position
        spr.rotation = self.skin.rotation
        lr.add(spr)
        self.parent.add(lr)

        self.parent.add(Stash(self.inventory, 'stash', self.skin.position))

        self.skin.collider.collision_manager.remove_tricky(self.skin.cshape)
        self.parent.remove(self.hash)


class patroling:
    def __init__(self, rad_patrol):
        self.rad_patrol = rad_patrol

    def choose_point(self):
        x = randint(self.rad_patrol[0][0], self.rad_patrol[1][0])
        y = randint(self.rad_patrol[0][1], self.rad_patrol[1][1])

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
        if (abs(self.target.position[0] - self.target.parent.next_x) > EPS) and (abs(self.target.position[1] - self.target.parent.next_y) > EPS):
            dist = hypot(self.target.parent.next_x-self.target.position[0], self.target.parent.next_y-self.target.position[1])
            vel_x = ((self.target.parent.next_x-self.target.position[0]) / dist) * 50
            vel_y = ((self.target.parent.next_y-self.target.position[1]) / dist) * 50
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
