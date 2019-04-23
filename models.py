import cocos
from cocos.director import director

def get_weight(item):
    if item in items:
        return items[item].weight
    elif item in weapons:
        return weapons[item].weight
    elif item in armors:
        return armors[item].weight


class inventory():
    def __init__(self):
        self.weight = 0
        self.items = {}
        self.weapons = []
        self.armors = []

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

    def get(self, item):
        if item in self.items:
            return items[item]
        return None

    def take(self, item, count):
        d = 0
        n = self.count(item)
        if n < count:
            d = count - self.count(item)
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
        
        return d
    
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

    def get_armor(i):
        return self.armors[i]

    def get_weapon(i):
        return self.weapons[i]


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

    def take_damage(self, dmg, k):
        if self.armor != -1:
            dmg -= self.inventory.get_armor(armor).statusAC(dmg, k)

        if dmg > 0:
            self.hp -= dmg

    def use_ability(self):
        pass

    def switch_weapon(self):
        if self.weapon_left == -1 and self.weapon_right == -1:
            self.weapon_left == self.weapon_l_equip
            self.weapon_right == self.weapon_r_equip
        else:
            self.weapon_left == -1
            self.weapon_right == -1

    def attack(self, hand):
        if hand == 'r' and self.weapon_right != -1:
            self.inventory.get_weapon(self.weapon_right).shoot()
        elif self.weapon_left != -1:
            self.inventory.get_weapon(self.weapon_left).shoot()

    def get_bullets(ammo, ammo_type):
        return min(ammo, self.inventory.count(ammo_type))
    
    def reload(self, hand):
        if hand == 'r' and self.weapon_right != -1:
            ammo, ammo_type = self.inventory.get_weapon(self.weapon_right)\
                              .get_max_cartridge()
            ammo = self.get_bullets(ammo, ammo_type)
            self.inventory.get_weapon(self.weapon_right).recharge(ammo)
        elif self.weapon_left != -1:
            ammo, ammo_type = self.inventory.get_weapon(self.weapon_left)\
                              .get_max_cartridge()
            ammo = self.get_bullets(ammo, ammo_type)
            self.inventory.get_weapon(self.weapon_left).recharge(ammo)

    def take_item(self, item, count):
        if self.inventory.weight + get_weight(item)*count > 4*self.SEACIL[0]:
            self.overweight = True
        self.inventory.add(item, count)

    def drop_item(self):
        pass

    def store_item(self):
        pass

    def seat():
        if self.stand == 'normal':
            self.stand = 'seat'
        else:
            self.stand = 'normal'


class NPC(character):
    def __init__(self, name, fraction):
        info = open('stats/chars/'+name+'txt', 'r')
        '''
        TODO
        '''
        info.close()
        super().__init__(name, fraction, seacil)

        self.state = 'friendly'

    def think(self):
        pass
    

class hero(character):
    def __init__(self, name, fraction, seacil, stats):
        super().__init__(name, fraction, seacil)

        '''
        TODO
        '''
        self.expirience = 0
        self.level = 0
        self.next_level = 1000
    
    def die():
        pass

    def get_level():
        pass
