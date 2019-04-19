import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse

class item():
    def __init__(sprite_name, weight, cost):
        self.sprite_name = sprite_name 
        self.weight = weight
        self.cost = cost

class armor(item):
    # 0 <= mac_ac <= 100\
    # 0 <= def_firearm <= 0.99
    def __init__(self, max_ac = 0, ac = 0, def_firearm = 0):
        super().__init__()
        self.max_ac = max_ac # max_ac - максимальная прочность брони
        self.ac = ac # ac - текущая прочность брони
        self.def_firearm = def_firearm # def_firearm - защита от огнестрельного оружия
    
    def get_damage(self, dmg, k = 1):
        # dmg - кол-во урона
        # k - коэффициент пробития
        # mainHero.hp -= dmg * k * (1 - self.def_firearm)
        mainHero.hp -= 23
    
    def destroyArmor(self):
        return self.ac <= 0
    
    def statusAC(self, dmg, k = 1):
        # dmg - кол-во урона
        # k - коэффициент пробития
        # self.ac -= dmg * k / self.max_ac
        self.ac -= 1
        if self.destroyArmor():
            self.def_firearm = 0
            #mainHero.disEquip
            
class weapon(item):
    # stats = [damage, breachness, max_cartridge]
    def __init__(self, weapon_type, stats):
        super().__init__()
        self.damage = stats[0] # damage - урон
        self.weapon_type = weapon_type
        self.breachness = stats[1] # breachness - пробивная способность
        self.max_cartridge = stats[2] # max_cartridge - размер обоймы
        self.cartridge = stats[2]
            
    def recharge(self, bulletType):
        # bulletType - патроны определенного типа в инвентаре
        # .count - кол-во патронов данного типа в нвентаре
        bulletType.count -= self.max_cartridge - self.cartridge
        self.cartridge = self.max_cartridge