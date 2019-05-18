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

# Класс ГГ
class hero(character):
    is_event_handler = True

    def __init__(self, name, fraction, seacil, stats, pos):
        super().__init__(name, fraction, seacil, hero_mover(), pos)

        self.hp = stats[0]
        self.stamina = stats[1]
        self.sp_stamina = stats[2]

        self.expirience = 0
        self.level = 0
        self.next_level = 1000

        self.lpressed = False
        self.rpressed = False

    # Закончить игру из-за смерти ГГ
    def die(self):
        pass

    # Получить новый уровень
    def get_level(self):
        pass

    # Поворот взгляда
    def on_mouse_motion(self, x, y, dx, dy):
        global mouse_x, mouse_y
        mouse_x = x
        mouse_y = y

        scroller = self.skin.scroller

        mid_x, mid_y = scroller.world_to_screen(scroller.fx, scroller.fy)

        x -= mid_x
        y -= mid_y

        if x:
            angle = degrees(atan(y / x))
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

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy)
        if buttons & mouse.LEFT:
            self.attack('r')
        elif buttons & mouse.RIGHT:
            self.attack('l')
        elif buttons & mouse.LEFT and buttons & mouse.RIGHT:
            self.attack('r')
            self.attack('l')

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.lpressed = True
        if button == mouse.RIGHT:
            self.rpressed = True

        self.on_mouse_drag(x, y, 0, 0, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.lpressed = False
        if button == mouse.RIGHT:
            self.rpressed = False

    def on_key_press(self, symbol, modifiers):
        if symbol == key.R and self.lpressed:
            self.reload('r')
        elif symbol == key.R and self.rpressed:
            self.reload('l')
        elif symbol == key.R and modifiers & key.MOD_SHIFT:
            self.switch_weapon()
        elif symbol == key.R:
            self.reload('r')
            self.reload('l')

        if symbol == key.LCTRL or symbol == key.RCTRL:
            self.skin.seat()

    def on_key_release(self, symbol, modifiers):
        if symbol == key.LCTRL or symbol == key.RCTRL:
            self.skin.seat()

    def set_scroller(self, scr):
        self.skin.scroller = scr

    def set_collision(self, manager):
        self.skin.collider = manager


class hero_mover(cocos.actions.Move):
    def step(self, dt):
        keyboard = self.target.keyboard
        vel_x = (keyboard[key.D] - keyboard[key.A]) * 50
        vel_y = (keyboard[key.W] - keyboard[key.S]) * 50

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

        self.target.velocity = (vel_x, vel_y)
        self.target.position = new.cshape.center
        self.target.scroller.set_focus(*new.cshape.center)

        self.target.scroller.set_focus(self.target.x, self.target.y)

        if self.target.pause_counter == 0:
            if self.target.velocity[0] or self.target.velocity[1] and not self.target.seating:
                mixer._channels[0].play(self.target.step_sound)         #поискать исправление
        self.target.pause_counter = (self.target.pause_counter + 1) % 20

        global mouse_x, mouse_y
        if self.target.velocity[0] or self.target.velocity[1]:
            mouse_x, mouse_y = self.target.scroller.world_to_screen(self.target.scroller.fx, self.target.scroller.fy)
            mouse_x += vector[0]
            mouse_y += vector[1]
            director.window.set_mouse_position(mouse_x, mouse_y)
