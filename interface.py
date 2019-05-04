import cocos
from cocos.sprite import Sprite


class interface(cocos.layer.Layer):
    def __init__(self, stats):
        self.bars = {}

        super().__init__()

        for key, val in stats.items():
            self.bars[key] = cocos.text.Label(str(val[0]), val[1])

        for key, val in self.bars.items():
            self.add(val, name=key)

    def update(self, stats):
        for key, val in stats.items():
            self.change(key, val)

    def change(self, stat, new):
        self.remove(stat)

        old_pos = self.bars[stat].position
        self.bars[stat] = cocos.text.Label(str(new), old_pos)

        self.add(self.bars[stat], name=stat)
