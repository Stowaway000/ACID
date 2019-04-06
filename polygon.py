import cocos
from cocos.director import director
import pyglet
from pyglet.window import key, mouse
from cocos import mapcolliders
from cocos.actions import *
from math import atan, degrees
import os

img1 = pyglet.image.load("res/img/hero.png")
img = pyglet.image.load("res/img/walk.png")
img_grid = pyglet.image.ImageGrid(img, 1, 9, item_width=29, item_height=14)
anim = pyglet.image.Animation.from_image_sequence(img_grid[:], 0.05, loop=True)

mouse_x = 10
mouse_y = 10
vector = [0, 0]

class Mover(cocos.actions.Move):
    def get_walls(self):
        last = self.target.rect()
        radius = abs(last.width - last.height) // 3

        new = last.copy()
        new.y += radius
        new.x += radius
        vel_x, vel_y = self.target.collide_map(last, new, radius, radius)
        if vel_y < 0 and 'up' not in self.target.walls:
            self.target.walls = self.target.walls + 'up'
        elif vel_y > 0:
            self.target.walls = self.target.walls.replace('up', '')

        new = last.copy()
        new.x += radius
        new.y += radius
        vel_x, vel_y = self.target.collide_map(last, new, radius, radius)
        if vel_x < 0 and 'right' not in self.target.walls:
            self.target.walls = self.target.walls + 'right'
        elif vel_x > 0:
            self.target.walls = self.target.walls.replace('right', '')

        new = last.copy()
        new.y -= radius
        new.x += radius
        vel_x, vel_y = self.target.collide_map(last, new, radius, -radius)
        if vel_y > 0 and 'down' not in self.target.walls:
            self.target.walls = self.target.walls + 'down'
        elif vel_y < 0:
            self.target.walls = self.target.walls.replace('down', '')

        new = last.copy()
        new.x -= radius
        new.y += radius
        vel_x, vel_y = self.target.collide_map(last, new, -radius, radius)
        if vel_x > 0 and 'left' not in self.target.walls:
            self.target.walls = self.target.walls + 'left'
        elif vel_x < 0:
            self.target.walls = self.target.walls.replace('left', '')

    def step(self, dt):
        vel_x = (keyboard[key.D] - keyboard[key.A]) * 75
        vel_y = (keyboard[key.W] - keyboard[key.S]) * 75

        if (self.target.velocity[0] or self.target.velocity[1]) and not(type(self.target.image) is pyglet.image.Animation):
            self.target.image = anim
        elif not (self.target.velocity[0] or self.target.velocity[1]):
            self.target.image = img1

        dx = vel_x * dt
        dy = vel_y * dt
        last = self.target.rect()

        new = last.copy()
        new.x += dx
        new.y += dy

        self.target.velocity = self.target.collide_map(last, new, vel_x, vel_y)
        self.target.position = new.center
        scroller.set_focus(*new.center)

        scroller.set_focus(self.target.x, self.target.y)

        global mouse_x, mouse_y
        if self.target.velocity[0] or self.target.velocity[1]:
            mouse_x, mouse_y = scroller.world_to_screen(scroller.fx, scroller.fy)
            mouse_x += vector[0]
            mouse_y += vector[1]
            director.window.set_mouse_position(mouse_x, mouse_y)

            self.get_walls()


class Skin(cocos.sprite.Sprite):
    def __init__(self):
        super().__init__(img1)

        self.position = 100, 80
        self.velocity = (0, 0)
        self.rect_img = cocos.sprite.Sprite('res/img/coll_b.png')
        self.rect_img_a = cocos.sprite.Sprite('res/img/coll.png')
        self.rect_img_d = cocos.sprite.Sprite('res/img/coll_d.png')
        self.collision = 'h'
        self.walls = ''

        self.do(Mover())

    def rect(self):
        x, y = self.position
        x -= self.rect_img.image_anchor_x
        y -= self.rect_img.image_anchor_y
        return cocos.rect.Rect(x, y, self.rect_img.width, self.rect_img.height)

    def switch_coll(self):
        self.rect_img, self.rect_img_a = self.rect_img_a, self.rect_img
        if self.collision == 'h':
            self.collision = 'v'
            if 'up' in self.walls:
                self.do(MoveBy((0, -8), 0))
                self.walls = self.walls.replace('up', '')
            if 'down' in self.walls:
                self.do(MoveBy((0, 8), 0))
                self.walls = self.walls.replace('down', '')
        else:
            self.collision = 'h'
            if 'left' in self.walls:
                self.do(MoveBy((8, 0), 0))
                self.walls = self.walls.replace('left', '')
            if 'right' in self.walls:
                self.do(MoveBy((-8, 0), 0))
                self.walls = self.walls.replace('right', '')


class HeroLayer(cocos.layer.ScrollableLayer):
    is_event_handler = True

    def __init__(self):
        super().__init__()

        self.skin = Skin()

        self.color = (0, 0, 0, 0)

        self.add(self.skin)

    def on_mouse_motion(self, x, y, dx, dy):
        global mouse_x, mouse_y
        mouse_x = x
        mouse_y = y
        
        mid_x, mid_y = scroller.world_to_screen(scroller.fx, scroller.fy)

        x -= mid_x
        y -= mid_y

        if x:
            angle = degrees(atan(y/x))
        else:
            angle = 90

        if x < 0 and y < 0:
            angle -= 180
        elif x < 0:
            angle += 180

        if not y and x < 0:
            angle = 180

        angle = -angle + 90

        if ('up' not in self.skin.walls or 'down' not in self.skin.walls) and\
           ('left' not in self.skin.walls or 'right' not in self.skin.walls):
            if self.skin.rotation != angle:
                h_x, h_y = scroller.world_to_screen(scroller.fx, scroller.fy)
                vector[0] = int(mouse_x - h_x)
                vector[1] = int(mouse_y - h_y)
                if 70 < abs(angle) < 110 or 250 < angle or angle < -70:
                    if self.skin.collision == 'h':
                        self.skin.switch_coll()
                elif self.skin.collision == 'v':
                    self.skin.switch_coll()

            self.skin.rotation = angle

    def set_collision(self, layer):
        mapcollider = mapcolliders.TmxObjectMapCollider()
        mapcollider.on_bump_handler = mapcollider.on_bump_bounce
        collision_handler = mapcolliders.make_collision_handler(mapcollider, layer)

        self.skin.collide_map = collision_handler


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


def load_map(name, hero):
    map_layer = MapLayer(name)

    hero.set_collision(map_layer.layer_collision)

    scroller = cocos.layer.ScrollingManager()
    scroller.scale = 2
    
    scroller.add(hero, 1)
    scroller.add(map_layer.layer_floor, -1)
    scroller.add(map_layer.layer_vertical, 1)
    scroller.add(map_layer.layer_objects, 1)
    scroller.add(map_layer.layer_above, 2)

    return scroller


if __name__ == "__main__":
    director.init(width=1280, height=720, caption="SuperGame")
    director.window.pop_handlers()

    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)
    
    cur_i = pyglet.image.load("res/img/cursor.png")
    cursor = pyglet.window.ImageMouseCursor(cur_i, 10, 10)
    director.window.set_mouse_cursor(cursor)

    hero_layer = HeroLayer()

    scroller = load_map("map_test", hero_layer)
    scene = cocos.scene.Scene(scroller)
    
    director.run(scene)
