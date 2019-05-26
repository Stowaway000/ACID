import cocos
from cocos.director import director
import pyglet
from cocos import mapcolliders
import cocos.euclid as eu
import cocos.collision_model as cm
from physics import *


class MapLayer(cocos.layer.ScrollableLayer):
    def __init__(self, name):
        super().__init__()
        level = cocos.tiles.load("maps/" + name + "/map.tmx")
        self.layer_floor = level["floor"]
        self.layer_vertical = level["wall"]
        self.layer_above = level["up"]
        self.layer_objects = level["obj"]
        self.layer_decoration = level["decorations"]
        self.layer_collision = level["collision"]
        self.layer_collision.objects += self.layer_objects.objects

        self.layer_anim_up = cocos.layer.ScrollableLayer()

        anims = open("maps/" + name + "/anim_up.txt", 'r')
        s = anims.readline()
        while s:
            args = s.split()
            img = pyglet.image.load("res/img/map_anims/" + args[0] + ".png")
            img_grid = pyglet.image.ImageGrid(img, int(args[1]), int(args[2]),\
                                              item_width=int(args[3]),\
                                              item_height=int(args[4]))
            anim = pyglet.image.Animation.from_image_sequence(img_grid[:],\
                                                              float((args[5])), loop=True)
            anim = Sprite(anim)
            anim.position = (int(args[6]), int(args[7]))
            
            self.layer_anim_up.add(anim)
            
            s = anims.readline()


class Port(cocos.sprite.Sprite):
    def __init__(name, number, cur_x, cur_y, new_x, new_y):
        self.next_map = MapLayer(name)
        self.number = number
        self.position = cur_x,cur_y
        self.new_position = new_x, nex_y
        img = pyglet.image.load("res/img/port.png")
        super().__init__(img, cur_x,cur_y)
        self.cshape = cm.AARectShape(eu.Vector2(*self.position), self.width/2, self.height/2)
    def change_map(self):
        pass


class map_manager(cocos.scene.Scene):
    def __init__(self, cur_map, hero):
        self.layer = MapLayer(cur_map)
        self.ports = []
        self.main_hero = hero
        cur_ports = open("maps/" + cur_map + "/ports.txt")
        p = cur_ports.readline()
        while p:
            p = p.split()
            port = Port(p[0],p[1],p[2],p[3],p[4])
            self.ports.append(port)
            self.add(port)
            p = cur_ports.readline()

        self.map_collider = circle_map_collider(self.layer)
        hero.set_collision(self.map_collider)
        scroller = cocos.layer.ScrollingManager()
        scroller.scale = 2
        
        scroller.add(hero, 2)
        scroller.add(self.layer.layer_floor, -1)
        scroller.add(self.layer.layer_vertical, 2)
        scroller.add(self.layer.layer_objects, 2)
        scroller.add(self.layer.layer_above, 3)
        scroller.add(self.layer.layer_decoration, 1)
        scroller.add(self.layer.layer_collision, 1)
        
        cur_npc = open("maps/" + cur_map + "/npc.txt")
        n = cur_npc.readline()
        while n:
            pass
        self.main_hero.set_scroller(scroller)
        super().__init__(scroller)

            
    def update(self):
        pass
    '''
        for port in self.ports:
            if self.coll_manager.they_collide(self.port, self.main_hero):
                port.change_map
        '''
