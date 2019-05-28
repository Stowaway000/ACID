import cocos
from cocos.director import director
import pyglet
from cocos import mapcolliders
import cocos.euclid as eu
import cocos.collision_model as cm
from physics import *
from cocos.sprite import Sprite
from item import PickableObject, Stash, inventory


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
    def __init__(self, name, number, cur_x, cur_y, new_x, new_y, width):
        self.next_map = name
        self.number = number
        self.new_position = new_x*32, new_y*32
        self.vector = new_x - cur_x, new_y - cur_y
        
        super().__init__("res/img/port.png", anchor=(0, 16))
        self.position = cur_x*32, cur_y*32
        for i in range(width-1):
            spr = Sprite("res/img/port.png", anchor=(0, 16))
            spr.position = (32+i*32, 0)
            self.add(spr)
        
        self.cshape = cm.AARectShape(eu.Vector2(self.position[0]+self.width/2*width, self.position[1]),\
                                     self.width/2*width, self.height/2)
    
    def change_map(self, main_hero):
        scene = None
        if self.next_map not in map_manager.maps:
            scene = map_manager(self.next_map, main_hero, self.number)
        else:
            scene = map_manager.maps[self.next_map]
            main_hero.set_collision(scene.map_collider)
            main_hero.set_scroller(scene.scroller)
            main_hero.set_position(scene.ports[self.number].new_position)

        director.replace(scene)


class map_manager(cocos.scene.Scene):
    maps = {}
    
    def __init__(self, cur_map, hero, port_n):
        map_manager.maps[cur_map] = self
        
        self.layer = MapLayer(cur_map)
        self.ports = []
        self.main_hero = hero
        
        self.map_collider = circle_map_collider(self.layer)
        hero.set_collision(self.map_collider)
        scroller = cocos.layer.ScrollingManager()
        scroller.scale = 2
        self.main_hero.set_scroller(scroller)

        port_handler = cocos.layer.ScrollableLayer()
        cur_ports = open("maps/" + cur_map + "/ports.txt")
        p = cur_ports.readline()
        i = 0
        while p:
            p = p.split()
            port = Port(p[0], *map(int, p[1:]))
            self.ports.append(port)
            port_handler.add(port)
            
            p = cur_ports.readline()

            if i == port_n:
                self.main_hero.set_position(port.new_position)
            
            i += 1
        
        scroller.add(hero, 2)
        scroller.add(self.layer.layer_floor, -1)
        scroller.add(self.layer.layer_decoration, 1)
        scroller.add(port_handler, 1)
        scroller.add(self.layer.layer_vertical, 2)
        scroller.add(self.layer.layer_objects, 2)
        scroller.add(self.layer.layer_above, 3)
        scroller.add(self.layer.layer_anim_up, 3)
        scroller.add(self.layer.layer_collision, 1)

        stashes = open("maps/" + cur_map + "/stashes.txt")
        p = stashes.readline()
        while p:
            p = p.split()
            inv = inventory()
            Stash(inv, p[0], (int(p[1]), int(p[2]))).place(scroller)
            
            p = stashes.readline()
            while p.strip():
                arg = p.split()
                inv.add(arg[0], int(arg[1]))
                p = stashes.readline()
            p = stashes.readline()

        picks = open("maps/" + cur_map + "/pick.txt")
        p = picks.readline()
        while p:
            p = p.split()
            digits = tuple(map(int, p[1:]))
            PickableObject(p[0], (digits[0], digits[1]), digits[2]).place(scroller)
        
        cur_npc = open("maps/" + cur_map + "/npc.txt")
        n = cur_npc.readline()
        while n:
            pass
        self.scroller = scroller
        super().__init__(scroller)
        
        self.add(hero.interface, 100)

        self.schedule_interval(self.update, 1/20)

    def update(self, dt):
        for port in self.ports:
            if self.map_collider.collision_manager\
               .they_collide(port, self.main_hero.skin.cshape):
                port.change_map(self.main_hero)
