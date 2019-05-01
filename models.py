import cocos
from cocos.director import director
from cocos.actions import *
from cocos import mapcolliders
import pyglet
from pyglet.window import key, mouse
from math import sqrt, sin, cos, radians, atan, degrees
from polygon import Skin as skin

# Параметры мыши
mouse_x = 10
mouse_y = 10
vector = [0, 0]

class hero_mover(cocos.actions.Move):
    def step(self, dt):
        keyboard = self.target.keyboard
        vel_x = (keyboard[key.D] - keyboard[key.A]) * 50
        vel_y = (keyboard[key.W] - keyboard[key.S]) * 50

        if (self.target.velocity[0] or self.target.velocity[1]) and not(type(self.target.image) is pyglet.image.Animation):
            self.target.image = self.target.walk
        elif not (self.target.velocity[0] or self.target.velocity[1]):
            self.target.image = self.target.static

        dx = vel_x * dt
        dy = vel_y * dt
        last = self.target.rect()

        new = last.copy()
        new.x += dx
        new.y += dy

        self.target.velocity = self.target.collide_map(last, new, vel_x, vel_y)
        self.target.position = new.center
        self.target.scroller.set_focus(*new.center)

        self.target.scroller.set_focus(self.target.x, self.target.y)

        global mouse_x, mouse_y
        if self.target.velocity[0] or self.target.velocity[1]:
            mouse_x, mouse_y = self.target.scroller.world_to_screen(self.target.scroller.fx, self.target.scroller.fy)
            mouse_x += vector[0]
            mouse_y += vector[1]
            director.window.set_mouse_position(mouse_x, mouse_y)


class npc_mover(cocos.actions.Move):
    def step(self, dt):
        #TODO
        pass


# Получить тип какого-то предмета
def get_type(item):
    if item in item.items:
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
        return item.items[item]
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
            self.weapon_left == self.weapon_l_equip
            self.weapon_right == self.weapon_r_equip
            self.skin.show()
        else:
            self.weapon_left == -1
            self.weapon_right == -1
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
        if symbol == key.LCTRL or symbol == key.RCTRL:
            self.stand = 'normal'

    def set_scroller(self, scr):
        self.skin.scroller = scr

    def set_collision(self, layer):
        mapcollider = mapcolliders.TmxObjectMapCollider()
        mapcollider.on_bump_handler = mapcollider.on_bump_bounce
        collision_handler = mapcolliders.make_collision_handler(mapcollider, layer)

        self.skin.collide_map = collision_handler
