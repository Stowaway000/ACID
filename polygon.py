import cocos
from cocos.director import director
import pyglet
from pyglet.window import key, mouse
from cocos import mapcolliders
from cocos.actions import *
from math import atan, degrees
import os 


working_dir = os.path.dirname(os.path.realpath(__file__))


img1 = pyglet.image.load("res/img/hero.png")
img = pyglet.image.load("res/img/walk.png")
img_grid = pyglet.image.ImageGrid(img, 1, 9, item_width=29, item_height=14)
anim = pyglet.image.Animation.from_image_sequence(img_grid[:], 0.05, loop=True)
mouse_x = 10
mouse_y = 10
curt = 0
vector =[0, 0]

class Mover(cocos.actions.Move):
    def step(self, dt):
        vel_x = (keyboard[key.D] - keyboard[key.A]) * 100
        vel_y = (keyboard[key.W] - keyboard[key.S]) * 100

        if (self.target.velocity[0] or self.target.velocity[1]) and not(type(self.target.image) is pyglet.image.Animation):
            self.target.image = anim
        elif not (self.target.velocity[0] or self.target.velocity[1]):
            self.target.image = img1

        old_pos = self.target.position

        dx = vel_x * dt
        dy = vel_y * dt
        last = self.target.rect()

        new = last.copy()
        new.x += int(dx)
        new.y += int(dy)

        self.target.velocity = self.target.collide_map(last, new, vel_x, vel_y)
        self.target.position = new.center
        scroller.set_focus(*new.center)

        if self.target.velocity[0] == 0 and self.target.velocity[1] == 0 and (vel_x or vel_y):
            self.target.stuck = 1

        self.target.velocity = (vel_x, vel_y)
        scroller.set_focus(self.target.x, self.target.y)

        global mouse_x, mouse_y
        if self.target.velocity[0] or self.target.velocity[1]:
            mouse_x, mouse_y = scroller.world_to_screen(scroller.fx, scroller.fy)
            mouse_x += vector[0]
            mouse_y += vector[1]
            director.window.set_mouse_position(mouse_x, mouse_y)


class Skin(cocos.sprite.Sprite):
    def __init__(self, collision_handler):
        super().__init__(anim)

        self.collide_map = collision_handler
        self.position = 100, 100
        self.velocity = (0, 0)
        self.rect_img = cocos.sprite.Sprite('res/img/coll_b.png')
        self.rect_img_a = cocos.sprite.Sprite('res/img/coll.png')
        self.rect_img_d = cocos.sprite.Sprite('res/img/coll_d.png')
        self.collision = 'h'

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
            self.do(MoveBy((0, -9), 0))
        else:
            self.collision = 'h'


class HeroLayer(cocos.layer.ScrollableLayer):
    is_event_handler = True

    def __init__(self, collision_handler):
        super().__init__()
        '''
        self.hero_spr = cocos.sprite.Sprite(anim)
        self.hero_spr.position = 100, 100
        self.hero_spr.velocity = (0, 0)
        self.hero_spr.image = anim
        '''
        self.skin = Skin(collision_handler)

        self.add(self.skin)

    def on_mouse_motion(self, x, y, dx, dy):
        global mouse_x, mouse_y
        mouse_x = x
        mouse_y = y
        #print(x, y)
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


class MapLayer(cocos.layer.ScrollableLayer):
    def __init__(self):
        super().__init__()
        floor = cocos.tiles.load("maps/map_test/floor.tmx")
        map = cocos.tiles.load("maps/map_test/objects.tmx")

        self.layer_floor = floor["floor"]

        self.layer_room1 = map["mid"]

        self.layer_room2 = map["objs"]

        self.layer_obj = map["collision"]


if __name__ == "__main__":
    director.init(width=1280, height=720, caption="SuperGame")
    director.window.pop_handlers()

    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)
    map_layer = MapLayer()

    mapcollider = mapcolliders.TmxObjectMapCollider()
    mapcollider.on_bump_handler = mapcollider.on_bump_bounce
    collision_handler = mapcolliders.make_collision_handler(mapcollider, map_layer.layer_obj)

    cur_i = pyglet.image.load("res/img/cursor.png")
    cursor = pyglet.window.ImageMouseCursor(cur_i, 10, 10)
    director.window.set_mouse_cursor(cursor)

    hero_layer = HeroLayer(collision_handler)

    scroller = cocos.layer.ScrollingManager()
    scroller.scale = 2
    scroller.add(map_layer.layer_floor, -1)
    scroller.add(map_layer.layer_room1, 1)
    scroller.add(map_layer.layer_room2, 1)
    scroller.add(hero_layer)

    my_scene = cocos.scene.Scene()
    my_scene.add(scroller)

    director.run(my_scene)
