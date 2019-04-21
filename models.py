import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse

class item():
    def __init__(self, sprite_name, weight, cost):
        self.sprite_name = sprite_name 
        self.weight = weight
        self.cost = cost

class armor(item):
    # 0 <= mac_ac <= 100
    # 0 <= def_firearm <= 0.99
    def __init__(self, max_ac=0, def_firearm=0, sprite_name, weight, cost):
        super().__init__(sprite_name, weight, cost)
        self.max_ac = max_ac # max_ac - максимальная прочность брони
        self.def_firearm = def_firearm # def_firearm - защита от огнестрельного оружия        

class armor_handler():
    def __init__(ac, armor_name):
        self.armor_nae = armor_name
        self.ac = ac # ac - текущая прочность брони
    
    def get_damage(self, dmg=1, k=1):
        # dmg - кол-во урона
        # k - коэффициент пробития
        # mainHero.hp -= dmg * k * (1 - self.def_firearm)
        mainHero.hp -= dmg
    
    def statusAC(self, dmg=1, k=1):
        # dmg - кол-во урона
        # k - коэффициент пробития
        # self.ac -= dmg * k / self.max_ac
        self.ac -= 1
        if self.ac <= 0:
            self.def_firearm = 0
            
class weapon(item):
    # stats = [damage, breachness, max_cartridge]
    # anim_name - sprite анимации
    def __init__(self, stats, sprite_name, anim_name, weight, cost, height_anim, width_anim, count_anim):
        super().__init__(sprite_name, weight, cost)
        self.anim_name = anim_name
        self.damage = stats[0] # damage - урон
        self.breachness = stats[1] # breachness - пробивная способность
        self.max_cartridge = stats[2] # max_cartridge - размер обоймы
        
        self.count_anim = count_anim
        self.width_anim = width_anim
        self.height_anim = height_anim
        
        self.weapon_sprite = Sprite(self.sprite_name, scale=8)
        self.weapon_sprite.position = 400, 400
        self.weapon_sprite.velocity = (0, 0)