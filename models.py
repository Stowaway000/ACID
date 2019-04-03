import cocos
import cocos.collision_model as cm
import cocos.euclid as eu
from cocos.actions import MoveTo, Repeat

class armor(item):
    # 0 <= mac_ac <= 100
    # 0 <= def_cold <= 0.99
    # 0 <= def_firearm <= 0.99
    def __init__(self, max_ac = 0, ac = 0, def_cold = 0, def_firearm = 0):
        self.max_ac = max_ac # max_ac - максимальная прочность брони
        self.ac = ac # ac - текущая прочность брони
        self.def_cold = def_cold # def_cold - защита от холодного оружия
        self.def_firearm = def_firearm # def_firearm - защита от огнестрельного оружия
    
    def get_damage(self, damageType, dmg, k = 1):
        # damageType - тип урона; принимает значения "cold" или "firearm"
        # dmg - кол-во урона
        # k - коэффициент пробития
        #if damageType == "firearm":
            #mainHero.hp -= dmg * k * (1 - self.def_firearm)
        #elif damageType == "cold":
            #mainHero.hp -= dmg * (1 - self.def_cold)
        mainHero.hp -= 23
    
    def destroyArmor(self):
        if self.ac <= 0:
            return True
        else:
            return False
    
    def statusAC(self, dmg, k = 1):
        # dmg - кол-во урона
        # k - коэффициент пробития
        # self.ac -= dmg * k / self.max_ac
        self.ac -= 1
        if self.destroyArmor():
            self.def_cold = 0
            self.def_firearm = 0
            #mainHero.disEquip
            
class weapon(item):
    
    # if weapon_type = "cold"
    # stats = [damage, sector, range]
    # if weapon_type = "firearm"
    # stats = [damage, breachness, max_cartridge]
    def __init__(self, weapon_type, stats):
        # weapon_type - тип оружия; принимает значения "cold" или "firearm"
        self.damage = stats[0] # damage - урон
        self.weapon_type = weapon_type
        if weapon_type == "firearm":
            self.breachness = stats[1] # breachness - пробивная способность
            self.max_cartridge = stats[2] # max_cartridge - размер обоймы
            self.cartridge = stats[2]
        elif weapon_type == "cold":
            self.sector = stats[1] # sector - сектор по которому бьет оружие
            self.range = stats[2] # range - дальность атаки
            
        def recharge(self, bulletType):
            # bulletType - патроны определенного типа в инвентаре
            # .count - кол-во патронов данного типа в нвентаре
            bulletType.count -= self.max_cartridge - self.cartridge
            self.cartridge = self.max_cartridge
            