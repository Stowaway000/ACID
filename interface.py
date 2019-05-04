import cocos
from cocos.sprite import Sprite
from cocos.text import Label


class interface(cocos.layer.Layer):
    def __init__(self, stats):
        self.bars = {}

        super().__init__()

        for key, val in stats.items():
            self.bars[key] = Label(str(val[0]), val[1], font_name='Calibri',\
                                   color=(229, 23, 20, 255), anchor_x='center'\
                                   , anchor_y='center')
            spr = Sprite('res/img/interface/' + key + '.png')
            spr.position = val[1]
            self.add(spr)

        for key, val in self.bars.items():
            self.add(val, name=key)

    def update(self, stats):
        for key, val in stats.items():
            self.change(key, val)

    def change(self, stat, new):
        self.remove(stat)

        old_pos = self.bars[stat].position
        self.bars[stat] = Label(str(new), old_pos)

        self.add(self.bars[stat], name=stat)
