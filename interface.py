import cocos
from cocos.director import director
from cocos.sprite import Sprite
from cocos.text import Label
from cocos.actions import FadeIn, FadeOut, MoveBy, RotateBy, CallFunc
from pyglet.window import key
from cocos.scenes import pause


def add_label(txt, point, anchor='center'):
    return Label(txt, point, font_name='Calibri',\
                 color=(229, 23, 20, 255), anchor_x=anchor,\
                 anchor_y='center')


class interface(cocos.layer.Layer):
    is_event_handler = True
    
    def __init__(self, stats, scene):
        self.bars = {}

        super().__init__()

        for key, val in stats.items():
            self.bars[key] = add_label(str(val[0]), val[1])
            spr = Sprite('res/img/interface/' + key + '.png')
            spr.position = val[1]
            self.add(spr)

        for key, val in self.bars.items():
            self.add(val, name=key)

        self.announcer = cocos.layer.ColorLayer(255, 255, 255, 255)
        self.announcer.position = (director.window.width/2,\
                                   director.window.height-100)
        self.announcer.opacity = 0
        self.add(self.announcer)

        self.pause = pause.PauseScene(scene)

        self.queue = []

    def update(self, stats):
        for key, val in stats.items():
            self.change(key, val)

    def change(self, stat, new):
        self.remove(stat)

        old_pos = self.bars[stat].position
        self.bars[stat] = add_label(str(new), old_pos)

        self.add(self.bars[stat], name=stat)

    def next(self, title):
        self.queue.remove(title)
        if len(self.queue):
            self.make_announce(self.queue[0])
    
    def make_announce(self, title):
        names = self.announcer.children_names.copy()
        for i in names:
            self.announcer.remove(i)
        
        star = Sprite('res/img/interface/done.png', anchor = (0, 0))
        star.position = (0, 0)
        star.opacity = 0

        header = add_label('Выполнено!', (star.width + 10, star.height-15),\
                           'left')
        text = add_label(title, (star.width + 10, 30), 'left')

        
        self.announcer.height = star.height
        
        self.announcer.add(header, name='header')
        self.announcer.add(text, name='text')
        self.announcer.add(star, name='star')

        self.announcer.width = star.width + 20 + max(len(title), 10)*10

        fade_time = 1
        self.announcer.do((MoveBy((0, -50), fade_time)|FadeIn(fade_time)) +\
                   RotateBy(0, fade_time*2) + (MoveBy((0, 50), fade_time)\
                                               |FadeOut(fade_time))+CallFunc(lambda :self.next(title)))
        for i in self.announcer.get_children():
            i.do(FadeIn(fade_time)+ RotateBy(0, fade_time*2) + FadeOut(fade_time))
        
    def quest_done(self, title):
        self.queue.append(title)
        if len(self.queue) == 1:
            self.make_announce(title)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            director.push(self.pause)
