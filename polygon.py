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

mouse_x = 10
mouse_y = 10
vector = [0, 0]

class Mover(cocos.actions.Move):
    def step(self, dt):
        keyboard = self.target.keyboard
        vel_x = (keyboard[key.D] - keyboard[key.A]) * 50
        vel_y = (keyboard[key.W] - keyboard[key.S]) * 50

        if (self.target.velocity[0] or self.target.velocity[1]) and not(type(self.target.image) is pyglet.image.Animation):
            self.target.image = self.target.walk
        elif not (self.target.velocity[0] or self.target.velocity[1]):
            self.target.image = self.target.static

        dx = vel_x * dt
        dy = vel_y * dt
        new = self.target.cshape

        new.cshape.center = eu.Vector2(new.cshape.center.x + dx, new.cshape.center.y)
        if self.target.collider.collision_manager.any_near(new, 0):
            vel_x = 0
            new.cshape.center.x -= dx
#            print(self.target.position)
        new.cshape.center = eu.Vector2(new.cshape.center.x, new.cshape.center.y + dy)
        if self.target.collider.collision_manager.any_near(new, 0):
            vel_y = 0
            new.cshape.center.y -= dy
#           print(self.target.position)
        self.target.velocity = (vel_x, vel_y)
        self.target.position = new.cshape.center
        self.target.scroller.set_focus(*new.cshape.center)

        self.target.scroller.set_focus(self.target.x, self.target.y)

        global mouse_x, mouse_y
        if self.target.velocity[0] or self.target.velocity[1]:
            mouse_x, mouse_y = self.target.scroller.world_to_screen(self.target.scroller.fx, self.target.scroller.fy)
            mouse_x += vector[0]
            mouse_y += vector[1]
            director.window.set_mouse_position(mouse_x, mouse_y)


class Skin(cocos.sprite.Sprite):
    def __init__(self, static, walk, kb):
        stat = pyglet.image.load("res/img/" + static + ".png")
        w_img = pyglet.image.load("res/img/" + walk + ".png")
        w_img_grid = pyglet.image.ImageGrid(w_img, 1, 9, item_width=29, item_height=14)
        anim = pyglet.image.Animation.from_image_sequence(w_img_grid[:], 0.05, loop=True)
        
        super().__init__(stat)

        self.scroller = None
        self.keyboard = kb

        self.static = stat
        self.walk = anim
        
        self.position = 100, 80
        self.velocity = (0, 0)
        
        self.rect_img = cocos.sprite.Sprite('res/img/coll_h.png')
        self.rect_img_cur = self.rect_img
        self.cshape = CollisionUnit([eu.Vector2(*self.position), 14], "circle")
        self.do(Mover())



class Hero(cocos.layer.ScrollableLayer):
    is_event_handler = True

    def __init__(self, kb):
        super().__init__()

        self.skin = Skin("hero", "walk", kb)

        self.color = (0, 0, 0, 0)

        self.add(self.skin)

    def on_mouse_motion(self, x, y, dx, dy):
        global mouse_x, mouse_y
        mouse_x = x
        mouse_y = y

        scroller = self.skin.scroller
        
        mid_x, mid_y = scroller.world_to_screen(scroller.fx, scroller.fy)

        x -= mid_x
        y -= mid_y

        if x:
            angle = degrees(atan(y/x))
        elif y > 0:
            angle = 90
        else:
            angle = -90        

        if x < 0 and y < 0:
            angle -= 180
        elif x < 0:
            angle += 180

        if not y and x < 0:
            angle = 180
        angle = -angle + 90

        if self.skin.rotation != angle:

            h_x, h_y = scroller.world_to_screen(scroller.fx, scroller.fy)
                
            vector[0] = int(mouse_x - h_x)
                
            vector[1] = int(mouse_y - h_y)

        self.skin.rotation = angle

    def set_scroller(self, scr):
        self.skin.scroller = scr

    def set_collision(self, manager):
        self.skin.collider = manager

class CollisionUnit():
    def __init__(self, obj, type):
        if type == "rect":
            center = (obj.position[0]+obj.size[0]/2, obj.position[1]+obj.size[1]/2)
            self.cshape = cm.AARectShape(center, obj.size[0]/2, obj.size[1]/2)
            print(obj.position, obj.size)
        elif type == "circle":
            self.cshape = cm.CircleShape(obj[0], obj[1])

class CircleMapCollider():
    def __init__(self, maplayer):
        self.collision_manager = cm.CollisionManagerBruteForce()
        for obj in maplayer.layer_collision.objects:
            block = CollisionUnit(obj, "rect")
            self.collision_manager.add(block)


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
