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
    def __init__(self, max_ac, def_firearm, sprite_name, weight, cost):
        super().__init__(sprite_name, weight, cost)
        self.max_ac = max_ac # max_ac - максимальная прочность брони
        self.def_firearm = def_firearm # def_firearm - защита от огнестрельного оружия        


class armor_handler():
    def __init__(ac, armor_name):
        self.armor_name = armor_name
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


class weapon_handler(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self, weapon_name):
        super().__init__()
        self.weapon_name = weapon_name
        self.cartridge = 0
        self.anim_name = items[weapon_name].anim_name
        self.sprite_name = items[weapon_name].sprite_name
        
        self.shoot_img = load(self.anim_name)
        self.shoot_grid = ImageGrid(self.shoot_img, 1,
                                    items[weapon_name].count_anim,
                                    item_height=items[weapon_name].height_anim,
                                    item_width=items[weapon_name].width_anim)
        self.weapon_sprite = items[weapon_name].weapon_sprite
        self.add(self.weapon_sprite)
        
    def on_mouse_press(self, x, y, button, modifiers):
        if button & mouse.LEFT:
            self.weapon_sprite.image = Animation.from_image_sequence(self.shoot_grid[:], 0.05, loop=False)    
    
    def recharge(self, bulletType):
        # bulletType - патроны определенного типа в инвентаре
        # .count - кол-во патронов данного типа в нвентаре
        bulletType.count -= self.max_cartridge - self.cartridge
        self.cartridge = self.max_cartridge
