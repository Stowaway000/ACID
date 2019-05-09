import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse

from math import sqrt, sin, cos, radians, atan, degrees
from polygon import skin
from physics import *


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
        stats = list(map(float, file.readline().split()))
        file.close()
        
        self.armor_name = armor_name
        super().__init__(armor_name, stats[2], stats[3])
        self.max_ac = stats[0]  # max_ac - максимальная прочность брони
        self.def_firearm = stats[1]  # def_firearm - защита от огнестрельного оружия


class ArmorHandler():
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
        self.two_handed = bool(stats[5])  # two_handed - флаг двуручного оружия
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
        super().__init__()
        self.cartridge = 0
        self.flag_shoot = False
        self.weapon_name = weapon_name
        self.weapon_anim = Weapon.weapons[weapon_name].weapon_anim
        self.item_sprite = Weapon.weapons[weapon_name].item_sprite
        self.add(self.item_sprite)

    def shoot_anim(self):
        self.item_sprite.image = self.weapon_anim
    
    def get_max_сartrige(self):
        return weapon.weapons[self.weapon_name].max_cartridge,\
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
        pass


class hero_mover(cocos.actions.Move):
    def step(self, dt):
        if not self.target.parent.lurking:
            keyboard = self.target.keyboard
            vel_x = (keyboard[key.D] - keyboard[key.A]) * 50
            vel_y = (keyboard[key.W] - keyboard[key.S]) * 50

            if (self.target.velocity[0] or self.target.velocity[1]) and not (
                    type(self.target.image) is pyglet.image.Animation):
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

            new.cshape.center = eu.Vector2(new.cshape.center.x, new.cshape.center.y + dy)
            if self.target.collider.collision_manager.any_near(new, 0):
                vel_y = 0
                new.cshape.center.y -= dy

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
        else:
            self.target.image = self.target.walk


class npc_mover(cocos.actions.Move):
    def step(self, dt):
        # TODO
        pass


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
    tp = get_type(item)

    return get_global(item).weight


# Получить цену какого-то предмета
def get_cost(item):
    tp = get_type(item)
    
    return get_global(item).cost


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
            return Item.items[item]
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


# Класс персонажа
class character(cocos.layer.ScrollableLayer):
    characters = []
    
    def __init__(self, name, fraction, seacil, mover, pos):
        super().__init__()
        
        self.photo = cocos.sprite.Sprite('res/img/portraits/' + name + '.png')

        self.SEACIL = seacil
        
        self.inventory = inventory()
        
        self.weapon_left = -1
        self.weapon_right = -1
        self.weapon_l_equip = -1
        self.weapon_r_equip = -1
        
        self.armor = -1

        self.skin = skin(name, mover, pos)

        self.add(self.skin)

        self.stand = 'normal'

        self.fraction = fraction

        self.overweight = False

    @staticmethod
    def get_in_sector(me, angle, r, look):
        chars = []
        
        angle = radians(angle)/2
        vector = (look[0]*srqt(r), look[1]*srqt(r))
        r_vector = (vector[0]*cos(angle)-vector[1]*sin(angle),\
                    vector[0]*sin(angle)+vector[1]*cos(angle))
        s = abs(vector[0]*r_vector[1]-vector[1]*r_vector[0]) / 2
        
        for i in character.characters:
            vect = [me[0]-i.skin.x, me[1]-i.skin.y]
            dist = sqrt(vect[0]*vect[0]+vect[1]*vect[1])
            vect[0] *= sqrt(r/dist)
            vect[1] *= sqrt(r/dist)
            if dist <= r:
                if abs(vect[0]*vector[1]-vect[1]*vector[0])/2 <= s:
                    chars.append(i.get_info())

        return chars

    # Получить информацию о персонаже
    def get_info(self):
        #TODO
        return (fraction, self.skin.position)

    # Увеличить характеристику
    def set(self, attr, add):
        if attr == 'hp':
            self.hp += add
        elif attr == 'stamina':
            self.stamina += add
    
    # Получение урона
    def take_damage(self, dmg, k):
        if self.armor != -1:
            dmg -= self.inventory.get_armor(armor).statusAC(dmg, k)

        if dmg > 0:
            self.hp -= dmg

    # Специальная способность
    def use_ability(self):
        pass

    # Достать\спрятать оружие
    def switch_weapon(self):
        if self.weapon_left == -1 and self.weapon_right == -1:
            self.weapon_left = self.weapon_l_equip
            self.weapon_right = self.weapon_r_equip
            self.skin.show()
        else:
            self.weapon_left = -1
            self.weapon_right = -1
            self.skin.hide()

    # Атаковать оружием
    def attack(self, hand):
        if hand == 'r' and self.weapon_right != -1:
            self.inventory.get_weapon(self.weapon_right).shoot()
        elif self.weapon_left != -1:
            self.inventory.get_weapon(self.weapon_left).shoot()

    # Перезарядить оружие
    def reload(self, hand):
        if hand == 'r' and self.weapon_right != -1:
            ammo, ammo_type = self.inventory.get_weapon(self.weapon_right)\
                              .get_max_cartridge()
            ammo = self.inventory.take(ammo_type, ammo)
            change = self.inventory.get_weapon(self.weapon_right).recharge(ammo)
            self.inventory.add(ammo_type, change)
        elif self.weapon_left != -1:
            ammo, ammo_type = self.inventory.get_weapon(self.weapon_left)\
                              .get_max_cartridge()
            ammo = self.inventory.take(ammo_type, ammo)
            change = self.inventory.get_weapon(self.weapon_left).recharge(ammo)
            self.inventory.add(ammo_type, change)

    # Использовать бафф
    def use_item(self, item):
        self.inventory.get_usable(item).use(self)
        self.inventory.take(item, 1)
    
    # Положить вещь в инвентарь
    def take_item(self, item, count):
        if get_type(item) == 'weapon' and self.weapon_l_equip*\
           self.weapon_r_equip > 0:
           self.weapon_r_equip = len(self.inventory.wepons)
           self.skin.add_weapon(item, self.inventory\
                                .get_weapon(self.weapon_r_equip), 'r')
           self.switch_weapon()
        
        self.inventory.add(item, count)
        if self.inventory.weight > 4*self.SEACIL[0]:
            self.overweight = True
    
    # Выбросить педмет из инвентаря
    def drop_item(self):
        pass

    # Выложить предмет в ящик
    def store_item(self):
        pass


# Класс NPC
class NPC(character):
    def __init__(self, name, fraction):
        info = open('stats/chars/'+name+'.txt', 'r')
        stats = list(map(float, info.readline().split()))
        info.close()

        self.hp = stats[0]
        self.stamina = stats[1]
        self.sp_stamina = stats[2]
        
        super().__init__(name, fraction, stats[3:-1], npc_mover(), stats[-1])

        self.angle_velocity = 0

    # AI
    def think(self):
        pass

    # Создать труп и прочее
    def die():
        pass
    

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

        self.interface = None

        self.lurking = False

    def take_damage(self, dmg, k):
        super().take_damage(dmg, k)

        arm = self.inventory.get_armor(self.armor)
        ar_ac = 0
        if arm:
            ar_ac = arm.ac

        dct = {'hp': self.hp,
               'armor': ar_ac}
        self.interface.update(dct)

    def get_stats(self):
        armor = self.inventory.get_armor(self.armor)
        ar_ac = 0
        if armor:
            ar_ac = armor.ac

        dct = {'hp': [self.hp],
               'armor': [ar_ac],
               'stamina': [self.stamina]}
        return dct
    
    # Закончить игру из-за смерти ГГ   
    def die(self):
        pass

    # Получить новый уровень
    def get_level(self):
        pass

    # Поворот взгляда
    def on_mouse_motion(self, x, y, dx, dy):
        if not self.lurking:
            global mouse_x, mouse_y
            mouse_x = x
            mouse_y = y

            self.interface.mouse_pos = x, y

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
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.lurking:
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

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self.lpressed = False
        if button == mouse.RIGHT:
            self.rpressed = False
    
    def on_key_press(self, symbol, modifiers):
        if not self.lurking:
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
                self.stand = 'seat'

    def on_key_release(self, symbol, modifiers):
        if not self.lurking:
            if symbol == key.LCTRL or symbol == key.RCTRL:
                self.stand = 'normal'

    def set_scroller(self, scr):
        self.skin.scroller = scr

    def set_collision(self, manager):
        self.skin.collider = manager
