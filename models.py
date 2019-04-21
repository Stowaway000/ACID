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
        self.items = []
        self.weapons = []
        self.armors = []

    def add(self, item):
        if item in items:
            if item in self.items:
                self.items[item] += 1
            else:
                self.items[item] = 1
        elif item in weapons:
            self.weapons.append(weapon_handler(item))
        elif item in armors:
            self.armors.append(armor_handler(item))

    def get(self, item):
        return self.items[i]

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

        self.fraction = fraction

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
        for i in range(count):
            if self.inventory.weight + get_weight(item) < 4*self.SEACIL[0]:
                self.inventory.add(item)

    def drop_item(self):
        pass

    def store_item(self):
        pass


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
    
