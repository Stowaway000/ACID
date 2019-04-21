import cocos
from cocos.director import director
from cocos.sprite import Sprite
import pyglet
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key, mouse


class item(cocos.sprite.Sprite):
    def __init__(self, name, weight, cost):
        self.sprite_name = Sprite("res/img/items/" + name + ".png", scale=8)
        self.weight = weight
        self.cost = cost


class armor(item):
    # 0 <= mac_ac <= 100
    # 0 <= def_firearm <= 0.99
    def __init__(self, armor_name):
        # формат файла
        # max_ac def_firearm weight cost
        file = open("res/stats/armor/" + armor_name + ".txt")
        stats = list(map(float, file.readline().split()))
        file.close()
        
        self.armor_name = armor_name
        super().__init__(armor_name, stats[2], stats[3])
        self.max_ac = stats[0]  # max_ac - максимальная прочность брони
        self.def_firearm = stats[1]  # def_firearm - защита от огнестрельного оружия
        self.ac = max_ac # ac - текущая прочность брони


class armor_handler():
    def __init__(armor_name):
        self.armor_name = armor_name
        self.ac = items[armor_name].ac
        self.def_firearm = items[armor_name].def_firearm

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
    def __init__(self, weapon_name):
        file = open("res/stats/weapon/" + weapon_name + ".txt")
        stats = list(map(float, file.readline().split()))
        file.close()
        
        super().__init__(weapon_name, stats[3], stats[4])
        self.weapon_name = weapon_name
        self.anim_name = "res/img/items/" + weapon_name + "_anim.png"
        self.damage = stats[0]  # damage - урон
        self.breachness = stats[1]  # breachness - пробивная способность
        self.max_cartridge = stats[2]  # max_cartridge - размер обоймы

        self.count_anim = int(stats[7])
        self.width_anim = int(stats[6])
        self.height_anim = int(stats[5])

        self.sprite_name.position = 400, 400
        test_shoot.add(self.sprite_name)
        
        shoot_img = load(self.anim_name)
        shoot_grid = ImageGrid(shoot_img, 1,
                               self.count_anim,
                               item_height=self.height_anim,
                               item_width=self.width_anim)
        self.weapon_anim = Animation.from_image_sequence(shoot_grid[:], 0.05, loop=False)


class weapon_handler(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, weapon_name):
        super().__init__()
        self.weapon_name = weapon_name
        self.cartridge = 0
        self.anim_name = items[weapon_name].anim_name
        self.sprite_name = items[weapon_name].sprite_name

        self.weapon_anim = items[weapon_name].weapon_anim
        self.sprite_name = items[weapon_name].sprite_name
        self.add(self.sprite_name)

    def on_mouse_press(self, x, y, button, modifiers):
        if button & mouse.LEFT:
            self.sprite_name.image = self.weapon_anim

    def recharge(self, bulletType):
        # bulletType - патроны определенного типа в инвентаре
        # .count - кол-во патронов данного типа в нвентаре
        bulletType.count -= self.max_cartridge - self.cartridge
        self.cartridge = self.max_cartridge

