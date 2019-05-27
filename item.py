import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse
from cocos.actions import *
from cocos import mapcolliders
from math import sqrt, sin, cos, radians, atan, degrees
from physics import collision_unit
import cocos.euclid as eu
import cocos.collision_model as cm
from cocos.actions import FadeOut
from random import randint

# Параметры мыши
mouse_x = 10
mouse_y = 10
vector = [0, 0]


class Item(cocos.sprite.Sprite):
    items = dict()

    def __init__(self, name, weight, cost):
        if not (name in armor.armors or name in weapon.weapons \
                or name in Item.items or name in usable_obj.usable_objs):
            Item.items[name] = self

        self.name = name
        self.item_sprite = Sprite("res/img/items/" + name + ".png")
        self.weight = weight
        self.cost = cost


class usable_obj(Item):
    usable_objs = dict()

    def __init__(self, usable_obj_name):
        if not usable_obj_name in usable_obj.usable_objs:
            usable_obj.usable_objs[usable_obj_name] = self
        file = open("res/stats/usable_obj/" + usable_obj_name + ".txt")
        stats = file.readline().split()
        file.close()

        self.buff_type = stats[0]  # Изменяемая характеристика
        self.buff_value = int(stats[1])  # Значение, на которое изменяется характеристика
        super().__init__(usable_obj_name, float(stats[2]), float(stats[3]))

    def use(self, char):
        char.set(self.buff_type, self.buff_value)


class armor(Item):
    armors = dict()

    # 0 <= mac_ac <= 100
    # 0 <= def_firearm <= 0.99
    def __init__(self, armor_name):
        if not armor_name in armor.armors:
            armor.armors[armor_name] = self
        # формат файла
        # max_ac def_firearm weight cost
        file = open("res/stats/armor/" + armor_name + ".txt")
        stats = list(map(float, file.readline().split()))
        file.close()

        self.armor_name = armor_name
        super().__init__(armor_name, stats[2], stats[3])
        self.max_ac = stats[0]  # max_ac - максимальная прочность брони
        self.def_firearm = stats[1]  # def_firearm - защита от огнестрельного оружия


class armor_handler():
    def __init__(self, armor_name):
        self.armor_name = armor_name
        self.item_sprite = armors[armor_name].item_sprite
        self.ac = armors[armor_name].max_ac
        self.def_firearm = armors[armor_name].def_firearm

    def statusAC(self, dmg=1, k=1):
        # dmg - кол-во урона
        # k - коэффициент пробития
        # self.ac -= dmg * k / self.max_ac
        self.ac -= 1
        if self.ac <= 0:
            self.def_firearm = 0
        return dmg * 0.5  # пока я не придумаю адекватную формулу, будет так, потом исправим


class weapon(Item):
    weapons = dict()

    def __init__(self, weapon_name):
        if not weapon_name in weapon.weapons:
            weapon.weapons[weapon_name] = self
        file = open("res/stats/weapon/" + weapon_name + ".txt")
        stats = ' '.join(file.readlines()).split()
        file.close()

        super().__init__(weapon_name, float(stats[6]), float(stats[7]))
        self.weapon_name = weapon_name  # weapon_name - имя оружия
        anim_name = "res/img/items/" + weapon_name + "_anim.png"
        self.shoot_type = stats[4]  # shoot_type - тип стрельбы - auto/half auto
        anim_length = 0.05
        if self.shoot_type == "auto":
            self.firerate = int(stats[11])  # firerate - скорострельность
            anim_length = 60/self.firerate
        if self.shoot_type == "auto":
            anim_in_name = "res/img/items/" + weapon_name + "_anim_in.png"
            shoot_in_img = load(anim_in_name)
            shoot_grid = ImageGrid(shoot_in_img, 1,
                                   int(stats[12]),
                                   item_height=int(stats[14]),
                                   item_width=int(stats[13]))
            self.weapon_in_anim = Animation.from_image_sequence(shoot_grid[:], anim_length, loop=True)
            
        anim_end_name = "res/img/items/" + weapon_name + "_anim_end.png"
        self.damage = float(stats[0])  # damage - урон
        self.breachness = float(stats[1])  # breachness - пробивная способность
        self.max_cartridge = int(stats[2])  # max_cartridge - размер обоймы
        self.ammo_type = stats[3]  # ammo_type - тип патронов
        self.two_handed = bool(int(stats[5]))  # two_handed - флаг двуручного оружия
        self.by_shot = int(stats[18])
        self.angle = int(stats[19])
        self.bspeed = int(stats[20])
        # (1 - двуручное, 0 - одноручное)

        self.count_anim = int(stats[10])  # count_anim - кол-во спрайтов в анимации
        self.width_anim = int(stats[9])  # width_anim - ширина спрайта в анимации"
        self.height_anim = int(stats[8])  # height_anim - высота спрайта в анимации

        shoot_img = load(anim_name)
        shoot_grid = ImageGrid(shoot_img, 1,
                               self.count_anim,
                               item_height=self.height_anim,
                               item_width=self.width_anim)
        self.weapon_anim = Animation.from_image_sequence(shoot_grid[:], anim_length, loop=False)

        shoot_end_img = load(anim_end_name)
        shoot_grid = ImageGrid(shoot_end_img, 1,
                               int(stats[15]),
                               item_height=int(stats[17]),
                               item_width=int(stats[16]))
        self.weapon_end_anim = Animation.from_image_sequence(shoot_grid[:], anim_length, loop=False)

    def shoot(self, x, y):
        pass


class shooter(cocos.actions.Move):
    def step(self, dt):
        self.target.shoot_time += dt
        if not self.target.shoot_check():
            if self.target.shot_len <= self.target.shoot_time:
                self.target.shoot_time -= self.target.shot_len
                self.target.shot()
                
                if not self.target.flag_shooting:
                    self.target.shoot_in()


class weapon_handler(cocos.sprite.Sprite):
    def __init__(self, weapon_name):
        self.cartridge = 999
        self.flag_shoot = False
        self.flag_shooting = False
        self.shoot_time = 0

        self.weapon_ref = get_global(weapon_name)
        self.weapon_name = weapon_name
        self.weapon_anim = self.weapon_ref.weapon_anim
        if self.weapon_ref.shoot_type == 'auto':
            self.weapon_in_anim = self.weapon_ref.weapon_in_anim
            self.shot_len = 60/self.weapon_ref.firerate
        
        self.weapon_end_anim = self.weapon_ref.weapon_end_anim
        self.item_sprite = self.weapon_ref.item_sprite

        super().__init__(self.item_sprite.image)

    def shot(self):
        if self.cartridge == 0:
            self.flag_shoot = False
        else:
            total = self.weapon_ref.by_shot
            self.cartridge -= 1
            elem_ang = self.weapon_ref.angle / total
            for i in range(total):
                angle = self.parent.rotation+elem_ang*int(i-total/2)+randint(-1, 2)
                bul = bullet("res/img/" + self.weapon_ref.ammo_type + ".png", self.parent.position,\
                             angle,
                             self.parent.collider, self.weapon_ref.bspeed)
            
                self.parent.parent.parent.add(bul, name=bul.name, z=1)
            
                tr_l = cocos.layer.ScrollableLayer()
                tr_l.add(bul.tracer)
                bul.parent.add(tr_l)

                bul.do(bullet_mover())
    
    def shoot_anim(self, how=''):
        self.image = self.weapon_anim

        if how:
            self.do(MoveBy((0, 0.05)) + CallFunc(self.shoot_check))

    def shoot_in(self):
        self.flag_shooting = True
        self.image = self.weapon_in_anim

    def shoot_check(self):
        if not self.flag_shoot:
            if self.flag_shooting:
                self.image = self.weapon_end_anim
            self.flag_shoot = False
            self.flag_shooting = False
            self.shoot_time = 0
            self.stop()
            return True
        return False

    def get_max_cartridge(self):
        return weapon.weapons[self.weapon_name].max_cartridge, \
               weapon.weapons[self.weapon_name].ammo_type

    def recharge(self, count_bullet):
        # count_bullet - кол-во патронов для перезарядки
        if self.cartridge + count_bullet > weapon.weapons[self.weapon_name].max_cartridge:
            remainder = self.cartridge + count_bullet - weapon.weapons[self.weapon_name].max_cartridge
            self.cartridge = weapon.weapons[self.weapon_name].max_cartridge
            return remainder
        else:
            self.cartridge += count_bullet
            return 0

    def shoot(self):
        if not self.flag_shoot and self.cartridge:
            if self.weapon_ref.shoot_type == 'auto':
                self.do(shooter())
                self.flag_shoot = True
                self.shoot_anim()
            else:
                self.shoot_anim('one')
                self.flag_shoot = True
                self.flag_shooting = True
            self.shot()

    def refresh(self):
        self.flag_shoot = False


# Класс инвентаря
class inventory():
    def __init__(self):
        self.weight = 0
        self.items = {}
        self.usables = {}
        self.weapons = []
        self.armors = []

    # Добавить count предметов типа item в инвентарь
    def add(self, item, count):
        self.weight += get_weight(item) * count
        tp = get_type(item)
        if tp == 'item':
            if item in self.items:
                self.items[item] += count
            else:
                self.items[item] = count
        elif tp == 'weapon':
            for i in range(count):
                self.weapons.append(weapon_handler(item))
        elif tp == 'armor':
            for i in range(count):
                self.armors.append(armor_handler(item))
        elif tp == 'usable':
            if item in self.usables:
                self.usables[item] += count
            else:
                self.usables[item] = count

    # Получить экземпляр предмета по имени
    def get(self, item):
        if item in self.items:
            return item.items[item]
        return None

    # Забрать count предметов из инвентаря
    def take(self, item, count):
        n = self.count(item)
        self.weight -= get_weight(item) * n
        if n < count:
            count = n

        tp = get_type(item)
        if tp == 'item':
            self.items[item] -= n

        elif tp == 'usable':
            self.usables[item] -= n

        elif tp == 'weapon':
            get = 0
            i = 0
            while get < count:
                if self.weapons[i].name == item:
                    self.weapons.pop(i)
                    i -= 1
                    get += 1
                i += 1

        elif tp == 'armor':
            get = 0
            i = 0
            while get < count:
                if self.armors[i].name == item:
                    self.armors.pop(i)
                    i -= 1
                    get += 1
                i += 1

        return count

    # Посчитать количество предметов типа item в инвентаре
    def count(self, item):
        tp = get_type(item)
        if tp == 'item':
            return self.items[item]
        elif tp == 'usable':
            return self.usables[item]
        elif tp == 'weapon':
            n = 0
            for i in self.weapons:
                if i.name == item:
                    n += 1
            return n
        elif tp == 'armor':
            n = 0
            for i in self.armors:
                if i.name == item:
                    n += 1
            return n

    # Получить экземпляр брони из инвентаря по номеру
    def get_armor(self, i):
        return self.armors[i]

    # Получить экземпляр оружия из инвентаря по номеру
    def get_weapon(self, i):
        return self.weapons[i]

    # Получить экземпляр используемого из инвентаря по номеру
    def get_usable(self, item):
        if item in self.usables:
            return usable_object.objects[item]
        return None


# Получить тип какого-то предмета
def get_type(item):
    if item in Item.items:
        return 'item'
    elif item in weapon.weapons:
        return 'weapon'
    elif item in armor.armors:
        return 'armor'
    elif item in usable_object.usable_objs:
        return 'usable'


# Получить образец предмета
def get_global(item):
    tp = get_type(item)

    if tp == 'item':
        return Item.items[item]
    elif tp == 'weapon':
        return weapon.weapons[item]
    elif tp == 'armor':
        return armor.armors[item]
    elif tp == 'usable':
        return usable_object.usable_objs[item]


# Получить вес какого-то предмета
def get_weight(item):
    tp = get_type(item)

    return get_global(item).weight


# Получить цену какого-то предмета
def get_cost(item):
    tp = get_type(item)

    return get_global(item).cost


def del_tracer(tracer):
    tracer.parent.remove(tracer)


class bullet(cocos.layer.ScrollableLayer):
    def __init__(self, path, pos, rot, man, speed):
        super().__init__()
        self.bul = cocos.sprite.Sprite(path)
        self.bul.position = pos#(pos[0] + 10 + 10*cos(radians(rot)), pos[1] + 15 - 15*sin(radians(rot)))
        self.add(self.bul, z=3)
        self.position = (10, 10)
        self.bul.rotation = rot
        self.speed = speed
        self.manager = man
        self.cshape = collision_unit((pos, 2), "circle")
        self.name = str(hash(self))

        self.tracer = Sprite('res/img/tracer.png', anchor=(0, 0))
        self.tracer.rotation = rot -90
        self.tracer.position = pos
        self.tracer.opacity = 75
        self.dot = pos
        self.tracer.do(FadeOut(0.05)+CallFunc(lambda:del_tracer(self.tracer)))
        self.tracer.scale_x = 0.01

    def stop_move(self):
        self.stop()
        hole_l = tr_l = cocos.layer.ScrollableLayer()
        spr = Sprite('res/img/hole.png')
        spr.position = self.bul.position
        hole_l.add(spr)
        self.parent.add(hole_l)
            
        self.parent.remove(self.name)


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

        new.cshape.center = eu.Vector2(new.cshape.center[0] + dx, new.cshape.center[1])
        if self.target.manager.collision_manager.any_near(new, 0):
            self.target.stop_move()
            return 1

        new.cshape.center = eu.Vector2(new.cshape.center[0], new.cshape.center[1] + dy)
        if self.target.manager.collision_manager.any_near(new, 0):
            self.target.stop_move()
            return 1

        return 0
