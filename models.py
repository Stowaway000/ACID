import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse


class item(cocos.sprite.Sprite):
    def __init__(self, name, weight, cost):
        self.name = name
        self.item_sprite = Sprite("res/img/items/" + name + ".png")
        self.weight = weight
        self.cost = cost


class armor(item):
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
    def __init__(armor_name):
        self.armor_name = armor_name
        self.item_sprite = armors[armor_name].item_sprite
        self.ac = armors[armor_name].max_ac
        self.def_firearm = armors[armor_name].def_firearm

    def statusAC(self, dmg=1, k=1):
        # dmg - кол-во урона
        # k - коэффициент пробития
        # self.ac -= dmg * k / self.max_ac
        self.ac -= 1
        if self.ac <= 0:
            self.def_firearm = 0
        return dmg * 0.5 # пока я не придумаю адекватную формулу, будет так, потом исправим


class weapon(item):
    weapons = dict()
    def __init__(self, weapon_name):
        if not weapon_name in weapon.weapons:
            weapon.weapons[weapon_name] = self
        file = open("res/stats/weapon/" + weapon_name + ".txt")
        stats = list(map(float, file.readline().split()))
        file.close()
        
        super().__init__(weapon_name, stats[5], stats[6])
        self.flag_shoot = False
        self.weapon_name = weapon_name # weapon_name - имя оружия
        anim_name = "res/img/items/" + weapon_name + "_anim.png"
        self.damage = stats[0]  # damage - урон
        self.breachness = stats[1]  # breachness - пробивная способность
        self.max_cartridge = stats[2]  # max_cartridge - размер обоймы
        self.ammo_type = stats[3] # ammo_type - тип патронов
        self.shoot_type = stats[4] # shoot_type - тип стрельбы - auto/half auto
        
        if self.shoot_type == "auto":
            self.firerate = stats[10] # firerate - скорострельность

        self.count_anim = int(stats[9]) # count_anim - кол-во спрайтов в анимации
        self.width_anim = int(stats[8]) # width_anim - ширина спрайта в анимации"
        self.height_anim = int(stats[7]) # height_anim - высота спрайта в анимации

        # self.item_sprite.position = 400, 400
        
        shoot_img = load(anim_name)
        shoot_grid = ImageGrid(shoot_img, 1,
                               self.count_anim,
                               item_height=self.height_anim,
                               item_width=self.width_anim)
        self.weapon_anim = Animation.from_image_sequence(shoot_grid[:], 0.05, loop=False)
        
        def shoot(x, y):
            pass


class weapon_handler(cocos.sprite.Sprite):

    def __init__(self, weapon_name):
        super().__init__()
        self.cartridge = 0
        self.weapon_name = weapon_name
        self.weapon_anim = weapons[weapon_name].weapon_anim
        self.item_sprite = weapons[weapon_name].item_sprite
        self.add(self.item_sprite)

    def shoot_anim():
        self.item_sprite.image = self.weapon_anim
    
    def get_max_artrige():
        return weapons[self.weapon_name].max_cartridge, weapons[self.weapon_name].ammo_type

    def recharge(self, count_bullet):
        # count_bullet - кол-во патронов для перезарядки
        if self.cartridge + count_bullet > weapons[self.weapon_name].max_cartridge:
            remainder = self.cartridge + count_bullet - weapons[self.weapon_name].max_cartridge
            self.cartridge = weapons[self.weapon_name].max_cartridge
            return remainder
        else:
            self.cartridge += count_bullet
            return 0
    
    def shoot():
        pass

