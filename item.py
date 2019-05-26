import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse
from physics import *
from utils import add_label, add_text

# Параметры мыши
mouse_x = 10
mouse_y = 10
vector = [0, 0]


class Item(cocos.sprite.Sprite):
    items = dict()

    def __init__(self, name, weight, cost):
        if not (name in Armor.armors or name in Weapon.weapons\
                or name in Item.items or name in UsableObj.usable_objs):
            Item.items[name] = self
        self.name = name
        self.item_sprite = Sprite("res/img/items/" + name + ".png")
        self.item_inv_sprite = Sprite("res/img/items/" + name + "_inv.png")
        self.weight = weight
        self.cost = cost
        self.description = "Well... I don't know"

    def get_info(self):
        info = 'Weight: ' + str(self.weight) + '<br>'
        info += 'Cost: ' + str(self.cost) + '<br>'
        info += 'Description:<br>' + self.description
        return info


class UsableObj(Item):
    usable_objs = dict()

    def __init__(self, usable_obj_name):
        if usable_obj_name not in UsableObj.usable_objs:
            UsableObj.usable_objs[usable_obj_name] = self
        file = open("res/stats/usable_obj/" + usable_obj_name + ".txt")
        stats = file.readline().split()
        file.close()
        
        self.buff_type = stats[0]  # Изменяемая характеристика
        self.buff_value = int(stats[1])  # Значение, на которое изменяется характеристика
        super().__init__(usable_obj_name, float(stats[2]), float(stats[3]))
    
    def use(self, char):
        char.set(self.buff_type, self.buff_value)


class Armor(Item):
    armors = dict()
    # 0 <= mac_ac <= 100
    # 0 <= def_firearm <= 0.99

    def __init__(self, armor_name):
        if armor_name not in Armor.armors:
            Armor.armors[armor_name] = self
        # формат файла
        # max_ac def_firearm weight cost
        file = open("res/stats/armor/" + armor_name + ".txt")
        stats = list(map(int, file.readline().split()))
        file.close()

        w_img = pyglet.image.load("res/img/items/" + armor_name + "_walk.png")
        walk_grid = ImageGrid(w_img, 1, 9, item_width=29, item_height=14)
        self.walk_sprite = Sprite(Animation.from_image_sequence\
                                  (walk_grid[:], 0.05, loop=True))
        
        self.armor_name = armor_name
        super().__init__(armor_name, stats[2], stats[3])
        self.max_ac = stats[0]  # max_ac - максимальная прочность брони
        self.def_firearm = stats[1]  # def_firearm - защита от огнестрельного оружия


class ArmorHandler(Sprite):
    def __init__(self, armor_name):
        self.armor_name = armor_name
        self.item_sprite = Armor.armors[armor_name].item_sprite
        self.item_inv_sprite = Armor.armors[armor_name].item_inv_sprite
        self.walk_sprite = Armor.armors[armor_name].walk_sprite
        self.ac = Armor.armors[armor_name].max_ac
        self.def_firearm = Armor.armors[armor_name].def_firearm

        super().__init__(self.item_sprite.image)

    def statusAC(self, dmg=1, k=1):
        # dmg - кол-во урона
        # k - коэффициент пробития
        # self.ac -= dmg * k / self.max_ac
        self.ac -= 1
        if self.ac <= 0:
            self.def_firearm = 0
        return dmg * 0.5  # пока я не придумаю адекватную формулу, будет так, потом исправим


class Weapon(Item):
    weapons = dict()

    def __init__(self, weapon_name):
        if weapon_name not in Weapon.weapons:
            Weapon.weapons[weapon_name] = self
        file = open("res/stats/weapon/" + weapon_name + ".txt")
        stats = file.readline().split()
        file.close()

        super().__init__(weapon_name, float(stats[6]), float(stats[7]))
        self.weapon_name = weapon_name  # weapon_name - имя оружия
        anim_name = "res/img/items/" + weapon_name + "_anim.png"
        self.damage = float(stats[0])  # damage - урон
        self.breachness = float(stats[1])  # breachness - пробивная способность
        self.max_cartridge = int(stats[2])  # max_cartridge - размер обоймы
        self.ammo_type = stats[3]  # ammo_type - тип патронов
        self.shoot_type = stats[4]  # shoot_type - тип стрельбы - auto/half auto
        self.two_handed = bool(int(stats[5]))  # two_handed - флаг двуручного оружия
        # (1 - двуручное, 0 - одноручное)

        if self.shoot_type == "auto":
            self.firerate = int(stats[11])  # firerate - скорострельность

        self.count_anim = int(stats[10])  # count_anim - кол-во спрайтов в анимации
        self.width_anim = int(stats[9])  # width_anim - ширина спрайта в анимации"
        self.height_anim = int(stats[8])  # height_anim - высота спрайта в анимации

        # self.item_sprite.position = 400, 400

        shoot_img = load(anim_name)
        shoot_grid = ImageGrid(shoot_img, 1,
                               self.count_anim,
                               item_height=self.height_anim,
                               item_width=self.width_anim)
        self.weapon_anim = Animation.from_image_sequence(shoot_grid[:], 0.05, loop=False)

    def shoot(self, x, y):
        pass


class WeaponHandler(cocos.sprite.Sprite):
    def __init__(self, weapon_name):
        self.cartridge = 0
        self.flag_shoot = False
        self.weapon_name = weapon_name
        self.weapon_anim = Weapon.weapons[weapon_name].weapon_anim
        self.item_sprite = Weapon.weapons[weapon_name].item_sprite
        self.item_inv_sprite = Weapon.weapons[weapon_name].item_inv_sprite

        super().__init__(self.item_sprite.image)

    def shoot_anim(self):
        self.image = self.weapon_anim

    def get_max_cartridge(self):
        return Weapon.weapons[self.weapon_name].max_cartridge, \
               Weapon.weapons[self.weapon_name].ammo_type

    def recharge(self, count_bullet):
        # count_bullet - кол-во патронов для перезарядки
        if self.cartridge + count_bullet > Weapon.weapons[self.weapon_name].max_cartridge:
            remainder = self.cartridge + count_bullet - Weapon.weapons[self.weapon_name].max_cartridge
            self.cartridge = Weapon.weapons[self.weapon_name].max_cartridge
            return remainder
        else:
            self.cartridge += count_bullet
            return 0

    def shoot(self):
        self.shoot_anim()


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
                self.weapons.append(WeaponHandler(item))
        elif tp == 'armor':
            for i in range(count):
                self.armors.append(ArmorHandler(item))
        elif tp == 'usable':
            if item in self.usables:
                self.usables[item] += count
            else:
                self.usables[item] = count

    # Получить экземпляр предмета по имени
    def get(self, item):
        if item in self.items:
            return Item.items[item]
        return None

    # Забрать count предметов из инвентаря
    def take(self, item, count=-1, index=0):
        n = self.count(item)
        if count == 'all' or n < count:
            count = n
        self.weight -= get_weight(item) * count

        tp = get_type(item)
        if tp == 'item':
            self.items[item] -= n
            if not self.items[item]:
                self.items.pop(item)

        elif tp == 'usable':
            self.usables[item] -= n
            if not self.usables[item]:
                self.usables.pop(item)
        
        elif tp == 'weapon':
            if count != -1:
                get = 0
                i = 0
                while get < count:
                    if self.weapons[i].weapon_name == item:
                        self.weapons.pop(i)
                        i -= 1
                        get += 1
                    i += 1
            elif self.weapons[index].weapon_name == item:
                self.weapons.pop(index)
                
        
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
                if i.weapon_name == item:
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
        if len(self.armors):
            return self.armors[i]
        else:
            return None

    # Получить экземпляр оружия из инвентаря по номеру
    def get_weapon(self, i):
        return self.weapons[i]

    # Получить экземпляр используемого из инвентаря по номеру
    def get_usable(self, item):
        if item in self.usables:
            return usable_object.objects[item]
        return None


class PickableObject(cocos.layer.ScrollableLayer):
    pickables = {}
    
    def __init__(self, name, pos, count):
        super().__init__()
        self.spr = get_global(name).item_sprite
        self.spr.position = pos

        self.selector = Sprite('res/img/outline.png')
        self.selector.position = pos
        self.selector.scale_x = (self.spr.width+10) / self.selector.width
        self.selector.scale_y = (self.spr.height+10) / self.selector.height
        
        self.e = add_label('E', (pos[0]-5, pos[1]+self.spr.height-15), size=8)

        self.add(self.spr)
        
        self.name = name
        self.count = count

        index = len(PickableObject.pickables)
        self.sprite_name = self.name + str(index)
        PickableObject.pickables[self.sprite_name] = self

        radius = max(self.spr.width, self.spr.height) / 2
        self.cshape = collision_unit([eu.Vector2(*self.spr.position),\
                                      radius], "circle")

    def destruct(self):
        PickableObject.pickables.pop(self.sprite_name)
        self.parent.remove(self.sprite_name)

    def place(self, scr):
        scr.add(self, name=self.sprite_name)

    def select(self):
        self.add(self.selector, name='selector')
        self.add(self.e, name='E')

    def deselect(self):
        self.remove('selector')
        self.remove('E')


# Получить тип какого-то предмета
def get_type(item):
    if item in Item.items:
        return 'item'
    elif item in Weapon.weapons:
        return 'weapon'
    elif item in Armor.armors:
        return 'armor'
    elif item in UsableObj.usable_objs:
        return 'usable'


# Получить образец предмета
def get_global(item):
    tp = get_type(item)
    
    if tp == 'item':
        return Item.items[item]
    elif tp == 'weapon':
        return Weapon.weapons[item]
    elif tp == 'armor':
        return Armor.armors[item]
    elif tp == 'usable':
        return UsableObj.usable_objs[item]


# Получить вес какого-то предмета
def get_weight(item):
    return get_global(item).weight


# Получить цену какого-то предмета
def get_cost(item):
    return get_global(item).cost
