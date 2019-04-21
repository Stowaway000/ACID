import cocos
from cocos.director import director

class character(cocos.layer.ScrollableLayer):
    def __init__(self, name, fraction):
        self.photo = cocos.sprite.Sprite('res/img/portraits/' + name + '.png')

        self.inventory = []
        self.armors = []
        self.weapons = []
        
        self.weapon_left = -1
        self.weapon_right = -1
        self.weapon_l_equip = -1
        self.weapon_r_equip = -1
        
        self.armor = -1

        self.skin = Skin(name)

        self.fraction = fraction

    def take_damage(dmg, k):
        if self.armor != -1:
            dmg -= self.armors[armor].statusAC(dmg, k)

        if dmg > 0:
            self.hp -= dmg

    def use_ability():
        pass

    def switch_weapon():
        if self.weapon_left == -1 and self.weapon_right == -1:
            self.weapon_left == self.weapon_l_equip
            self.weapon_right == self.weapon_r_equip
        else:
            self.weapon_left == -1
            self.weapon_right == -1

    def attack(hand):
        if hand == 'r' and self.weapon_right != -1:
            self.weapons[self.weapon_right].shoot()
        elif self.weapon_left != -1:
            self.weapons[self.weapon_left].shoot()
            
    def reload(hand):
        if hand == 'r' and self.weapon_right != -1:
            ammo, ammo_type = self.weapon.get_max_cartridge()
            ammo = self.get_bullets(ammo, ammo_type)
            self.weapons[self.weapon_right].recharge(ammo)
        elif self.weapon_left != -1:
            ammo, ammo_type = self.weapon.get_max_cartridge()
            ammo = self.get_bullets(ammo, ammo_type)
            self.weapons[self.weapon_left].recharge(ammo)

    def take_item(item, count):
        #if get_weight(item) + self 
        if item in items:
            if item in self.inventory:
                self.inventory[item] += 1
            else:
                self.inventory[item] = 1
        elif item in armors:
            self.weapons[item] = armor_handler(item)
        elif item in weapons:
            self.weapons[item] = weapon_handler(item)

    def drop_item():
        pass

    def store_item():
        pass
