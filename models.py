import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse

from cocos.actions import *
from cocos import mapcolliders
from math import sqrt, sin, cos, radians, atan, degrees, hypot
from random import randint
from physics import *

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
        self.item_sprite = armor.armors[armor_name].item_sprite
        self.ac = armor.armors[armor_name].max_ac
        self.def_firearm = armor.armors[armor_name].def_firearm

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


class weapon_handler(cocos.sprite.Sprite):
    def __init__(self, weapon_name):
        self.cartridge = 0
        self.flag_shoot = False
        self.weapon_name = weapon_name
        self.weapon_anim = weapon.weapons[weapon_name].weapon_anim
        self.item_sprite = weapon.weapons[weapon_name].item_sprite

        super().__init__(self.item_sprite.image)

        # self.add(self.item_sprite)

    def shoot_anim(self):
        self.image = self.weapon_anim

    def get_max_сartrige(self):
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
        self.shoot_anim()


class hero_mover(cocos.actions.Move):
    def step(self, dt):
        keyboard = self.target.keyboard
        vel_x = (keyboard[key.D] - keyboard[key.A]) * 50
        vel_y = (keyboard[key.W] - keyboard[key.S]) * 50

        if self.target.velocity[0] or self.target.velocity[1]:
            self.target.walk(True)
        elif not (self.target.velocity[0] or self.target.velocity[1]):
            self.target.walk(False)

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


class npc_mover(cocos.actions.Move):
    def __init__(self):
        super().__init__()
        self.x = self.target.position[0]
        self.y = self.target.position[1]

    def step(self, dt):
        vel_x = (self.x / hypot(self.x, self.y)) * 50
        vel_y = (self.y / hypot(self.x, self.y)) * 50

        if self.target.velocity[0] or self.target.velocity[1]:
            self.target.walk(True)
        elif not (self.target.velocity[0] or self.target.velocity[1]):
            self.target.walk(False)

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

    def update(self, x, y):
        self.x = x
        self.y = y


# Получить тип какого-то предмета
def get_type(item):
    if item in Item.items:
        return 'item'
    elif item in weapon.weapons:
        return 'weapon'
    elif item in armor.armors:
        return 'armor'
    elif item in usable_obj.usable_objs:
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
        return usable_obj.usable_objs[item]


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
            return usable_obj.usable_objs[item]
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

        angle = radians(angle) / 2
        vector = (look[0] * sqrt(r), look[1] * sqrt(r))
        r_vector = (vector[0] * cos(angle) - vector[1] * sin(angle), \
                    vector[0] * sin(angle) + vector[1] * cos(angle))
        s = abs(vector[0] * r_vector[1] - vector[1] * r_vector[0]) / 2

        for i in character.characters:
            vect = [me[0] - i.skin.x, me[1] - i.skin.y]
            dist = sqrt(vect[0] * vect[0] + vect[1] * vect[1])
            vect[0] *= sqrt(r / dist)
            vect[1] *= sqrt(r / dist)
            if dist <= r:
                if abs(vect[0] * vector[1] - vect[1] * vector[0]) / 2 <= s:
                    chars.append(i.get_info())

        return chars

    # Получить информацию о персонаже
    def get_info(self):
        # TODO
        return (self.fraction, self.skin.position)

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
            self.skin.show_weapon()
        else:
            self.weapon_left = -1
            self.weapon_right = -1
            self.skin.hide_weapon()

    # Атаковать оружием
    def attack(self, hand):
        if hand == 'r' and self.weapon_right != -1:
            self.inventory.get_weapon(self.weapon_right).shoot()
        elif self.weapon_left != -1:
            self.inventory.get_weapon(self.weapon_left).shoot()

    # Перезарядить оружие
    def reload(self, hand):
        if hand == 'r' and self.weapon_right != -1:
            ammo, ammo_type = self.inventory.get_weapon(self.weapon_right) \
                .get_max_cartridge()
            ammo = self.inventory.take(ammo_type, ammo)
            change = self.inventory.get_weapon(self.weapon_right).recharge(ammo)
            self.inventory.add(ammo_type, change)
        elif self.weapon_left != -1:
            ammo, ammo_type = self.inventory.get_weapon(self.weapon_left) \
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
        if get_type(item) == 'weapon' and self.weapon_l_equip * \
                self.weapon_r_equip > 0:
            self.weapon_r_equip = len(self.inventory.weapons)
            self.inventory.add(item, count)
            if self.inventory.weight > 4 * self.SEACIL[0]:
                self.overweight = True

            self.skin.add_weapon(self.inventory \
                                 .get_weapon(self.weapon_r_equip), 'r')
            self.switch_weapon()

    # Выбросить педмет из инвентаря
    def drop_item(self):
        pass

    # Выложить предмет в ящик
    def store_item(self):
        pass


# Класс NPC
class NPC(character):
    def __init__(self, name, fraction):
        info = open('stats/chars/' + name + '.txt', 'r')
        stats = list(map(float, info.readline().split()))
        info.close()

        self.hp = stats[0]
        self.stamina = stats[1]
        self.sp_stamina = stats[2]
        self.ai = AI()

        super().__init__(name, fraction, stats[3:-1], self.ai.mover, stats[-1])

        self.angle_velocity = 0

    # Создать труп и прочее
    def die(self):
        pass


class AI:
    def __init__(self, rad_patrol):
        self.mover = npc_mover()
        self.state = "patrol"
        self.rad_patrol = rad_patrol

    def change_state(self):
        if self.state == "patrol":
            self.state = "fight"
        else:
            self.state = "patrol"

    def get_way(self, x, y):
        self.mover.update(x, y)

    def think(self):
        if self.state == "patrol":
            x, y = self.patrol.choose_point()
            self.get_way(x, y)
        else:
            pass


class patroling(AI):
    def choose_point(self):
        pass

    def trade(self):
        pass

    def think(self):
        pass


class fight(AI):
    def choose_enemy(self):
        pass

    def choose_cover(self):
        pass

    def danger(self):
        pass

    def attack(self):
        pass

    def think(self):
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


class skin(cocos.sprite.Sprite):
    def __init__(self, name, mover, pos):
        stat = pyglet.image.load("res/img/skins/init.png")
        w_img = pyglet.image.load("res/img/skins/" + name + "/" + name + "_walk.png")
        w_img_grid = pyglet.image.ImageGrid(w_img, 1, 9, item_width=29, item_height=14)
        anim = pyglet.image.Animation.from_image_sequence(w_img_grid[:], 0.05, loop=True)

        super().__init__(stat)

        self.scroller = None
        self.keyboard = key.KeyStateHandler()
        director.window.push_handlers(self.keyboard)

        self.body = cocos.sprite.Sprite("res/img/skins/" + name + "/" + name + "_body.png")
        self.body_seat = cocos.sprite.Sprite("res/img/skins/" + name + "/" + name + "_body_seat.png")
        self.lhand = cocos.sprite.Sprite("res/img/skins/" + name + "/" + name + "_lhand.png")
        self.rhand = cocos.sprite.Sprite("res/img/skins/" + name + "/" + name + "_rhand.png")
        self.head = cocos.sprite.Sprite("res/img/skins/" + name + "/" + name + "_head.png")

        self.body.position = 0, 0
        self.body_seat.position = 0, 0
        self.head.position = 0, 0
        self.lhand.position = -10, 7
        self.rhand.position = 10, 7

        self.add(self.body, name="body", z=1)
        self.add(self.head, name="head", z=2)

        self.armor = None
        self.lweapon = None
        self.rweapon = None
        self.both = False

        #        self.static = stat
        self.animation = cocos.sprite.Sprite(anim)

        self.seating = False
        self.walking = False

        self.position = pos
        self.velocity = (0, 0)

        self.cshape = collision_unit([eu.Vector2(*self.position), self.body.width / 2], "circle")
        self.do(mover)

    def redraw(self):
        if self.both:
            self.remove(self.lhand)
            self.remove(self.rhand)
            self.add(self.rweapon, z=2)
        else:
            if self.lweapon:
                self.add(self.lhand, z=0)
            if self.rweapon:
                self.add(self.rhand, z=0)

        if self.seating:
            self.add(self.body_seat, z=1)
        else:

            if self.armor:
                self.add(self.armor, z=1)
            else:
                self.add(self.body, z=1)

        self.show_weapon()

    def walk(self, new_state):
        if self.walking != new_state:
            self.walking = new_state
            if not self.seating:
                if self.walking:
                    self.remove("body")
                    self.add(self.animation, name="body", z=1)
                else:
                    self.remove("body")
                    self.add(self.body, name="body", z=1)

    def seat(self):
        self.seating = not self.seating
        if self.seating:
            self.remove("body")
            self.add(self.body_seat, name="body_seat", z=1)
        if not self.seating:
            self.remove("body_seat")
            self.add(self.body, name="body", z=1)

    def add_weapon(self, sprite, hand):
        if False:
            # if weapon.weapons[name].two_handed:
            if self.lhand:
                self.remove("lhand")
            if self.rhand:
                self.remove("rhand")
            self.lweapon = False
            self.rweapon = sprite
            self.rweapon.position = 10, 10
            self.both = True
        else:
            self.both = False
            if hand == 'l':
                self.lweapon = sprite
                self.lweapon.position = -10, 10
            if hand == 'r':
                self.rweapon = sprite
                self.rweapon.position = 10, 10

    def remove_weapon(self, hand):
        if hand == "l":
            self.lweapon = None
            self.remove("lhand")
            self.remove("lweapon")
        else:
            self.rweapon = None
            self.remove("rhand")
            self.remove("rweapon")

    def add_armor(self, sprite):
        self.armor = sprite
        self.remove("body")
        self.add(self.armor, name="body", z=1)

    def remove_armor(self):
        self.armor = None
        self.remove("body")
        self.add(self.body, name="body", z=1)

    def show_weapon(self):
        if self.both:
            self.add(self.rweapon, name="rweapon", z=0)
        else:
            if self.lweapon:
                self.add(self.lhand, name="lhand", z=0)
                self.add(self.lweapon, name="lweapon", z=2)
            if self.rweapon:
                self.add(self.rhand, name="rhand", z=0)
                self.add(self.rweapon, name="rweapon", z=2)

    def hide_weapon(self):
        if self.both:
            self.remove("both")
        else:
            if self.lweapon:
                self.remove("lhand")
                self.remove("lweapon")
            if self.rweapon:
                self.remove("rhand")
                self.remove("rweapon")
