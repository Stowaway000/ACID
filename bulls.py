import cocos
from cocos.actions import *
from physics import *
from cocos.sprite import Sprite
from math import *
from pyglet.image import load, ImageGrid, Animation

class bullet(cocos.layer.ScrollableLayer):
    bulls = []
    
    def __init__(self, name, pos, rot, man, speed, npc_ref):
        super().__init__()
        self.bul = cocos.sprite.Sprite("res/img/items/" + name + ".png")

        self.npc_ref = npc_ref
       #x = 11
       #y = 18
       #pos = (pos[0]+dx, pos[1]+dy)
        self.bul.position = pos
        self.add(self.bul, z=3)
        self.position = (10, 10)
        self.bul.rotation = rot
        self.speed = speed
        self.manager = man
        self.cshape = collision_unit((pos, 2), "bullet")
        self.name = str(hash(self))

        self.tracer = Sprite('res/img/items/tracer_' + name + '.png', anchor=(0, 0))
        self.tracer.rotation = rot - 90
        self.tracer.position = pos
        self.tracer.opacity = 75
        self.dot = pos
        self.tracer.do(FadeOut(0.05)+CallFunc(lambda:del_tracer(self.tracer)))
        self.tracer.scale_x = 0.01

        bullet.bulls.append(self)

        self.do(bullet_mover())

    def stop_move(self):
        self.stop()
        
        hole_l = tr_l = cocos.layer.ScrollableLayer()
        hole_img = load('res/img/hole.png')
        hole_grid = ImageGrid(hole_img, 1, 6, item_height=15, item_width=10)
        hole_anim = Sprite(Animation.from_image_sequence(hole_grid[:], 0.05, loop=False))
        hole_anim.rotation = self.bul.rotation + 180
        hole_anim.position = self.bul.position
        hole_l.add(hole_anim)
        self.parent.add(hole_l)
        hole_l.do(MoveBy((0, 0), 0.1)+CallFunc(lambda:del_tracer(hole_l)))
            
        self.parent.remove(self.name)
        bullet.bulls.remove(self)


class bullet_mover(Move):
    def step(self, dt):
        for i in range(20):
            if self.elem_step(dt/30):
                break

    def elem_step(self, dt):
        dist = sqrt((self.target.bul.position[0] - self.target.dot[0])**2 + (self.target.bul.position[1] - self.target.dot[1])**2)
        if dist:
            if self.target.tracer.scale_x <= 0.005:
                self.target.tracer.scale_x = 0.01
            
            self.target.tracer.scale_x = dist*self.target.tracer.scale_x / self.target.tracer.width
            
        
        old_pos = self.target.bul.position
        angle = self.target.bul.rotation
        dx = sin(radians(angle)) * self.target.speed * dt
        dy = cos(radians(angle)) * self.target.speed * dt
        new_pos = (old_pos[0] + dx, old_pos[1] + dy)
        self.target.bul.position = new_pos
        new = self.target.cshape

        for i in self.target.npc_ref:
            if self.target.manager.collision_manager.they_collide(i.skin.cshape, new):
                i.take_damage(20, 0.5)
                self.target.stop_move()
                return 1
        
        new.cshape.center = eu.Vector2(new.cshape.center[0] + dx, new.cshape.center[1])
        if self.target.manager.collision_manager.any_near(new, 0):
            self.target.stop_move()
            return 1

        new.cshape.center = eu.Vector2(new.cshape.center[0], new.cshape.center[1] + dy)
        if self.target.manager.collision_manager.any_near(new, 0):
            self.target.stop_move()
            return 1

        return 0

    
def del_tracer(tracer):
    tracer.parent.remove(tracer)
