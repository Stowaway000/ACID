import cocos
from cocos.director import director

# Получить вес какого-то предмета
def get_weight(item):
    if item in items:
        return items[item].weight
    elif item in weapons:
        return weapons[item].weight
    elif item in armors:
        return armors[item].weight


# Класс инвентаря
class inventory():
    def __init__(self):
        self.weight = 0
        self.items = {}
        self.weapons = []
        self.armors = []

    # Добавить count предметов типа item в инвентарь
    def add(self, item, count):
        if item in items:
            if item in self.items:
                self.items[item] += count
            else:
                self.items[item] = count
        elif item in weapons:
            for i in range(count):
                self.weapons.append(weapon_handler(item))
        elif item in armors:
            for i in range(count):
                self.armors.append(armor_handler(item))

    # Получить экземпляр предмета по имени
    def get(self, item):
        if item in self.items:
            return items[item]
        return None

    # Забрать count предметов из инвентаря
    def take(self, item, count):
        n = self.count(item)
        if n < count:
            count = n
        
        if item in items:
            self.items[item] -= n
        
        elif item in weapons:
            get = 0
            i = 0
            while get < count:
                if self.weapons[i].name == item:
                    self.weapons.pop(i)
                    i -= 1
                    get += 1
                i += 1
        
        elif item in armors:
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
        if item in items:
            return self.items[item]
        elif item in weapons:
            n = 0
            for i in self.weapons:
                if i.name == item:
                    n += 1
            return n
        elif item in armors:
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


# Класс персонажа
class character(cocos.layer.ScrollableLayer):
    def __init__(self, name, fraction, seacil):
        self.photo = cocos.sprite.Sprite('res/img/portraits/' + name + '.png')

        self.SEACIL = seacil
        
        self.inventory = inventory()
        
        self.weapon_left = -1
        self.weapon_right = -1
        self.weapon_l_equip = -1
        self.weapon_r_equip = -1
        
        self.armor = -1

        self.skin = Skin(name)

        self.stand = 'normal'

        self.fraction = fraction

        self.overweight = False

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
            self.inventory.get_weapon(self.weapon_right).recharge(ammo)
        elif self.weapon_left != -1:
            ammo, ammo_type = self.inventory.get_weapon(self.weapon_left)\
                              .get_max_cartridge()
            ammo = self.inventory.take(ammo_type, ammo)
            self.inventory.get_weapon(self.weapon_left).recharge(ammo)

    # Положить вещь в инвентарь
    def take_item(self, item, count):
        if self.inventory.weight + get_weight(item)*count > 4*self.SEACIL[0]:
            self.overweight = True
        self.inventory.add(item, count)

    # Выбросить педмет из инвентаря
    def drop_item(self):
        pass

    # Выложить предмет в ящик
    def store_item(self):
        pass

    # Присесть\встать
    def seat(self):
        if self.stand == 'normal':
            self.stand = 'seat'
        else:
            self.stand = 'normal'


# Класс NPC
class NPC(character):
    def __init__(self, name, fraction):
        info = open('stats/chars/'+name+'.txt', 'r')
        stats = list(map(float, info.readline().split()))
        info.close()

        self.hp = stats[0]
        self.stamina = stats[1]
        self.sp_stamina = stats[2]
        
        super().__init__(name, fraction, stats[3:])

        self.state = 'friendly'

    # AI
    def think(self):
        pass
    

# Класс ГГ
class hero(character):
    def __init__(self, name, fraction, seacil, stats):
        super().__init__(name, fraction, seacil)

        self.hp = stats[0]
        self.stamina = stats[1]
        self.sp_stamina = stats[2]
        
        self.expirience = 0
        self.level = 0
        self.next_level = 1000

    # Закончить игру из-за смерти ГГ   
    def die():
        pass

    # Получить новый уровень
    def get_level():
        pass
