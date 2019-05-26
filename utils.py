from cocos.text import Label, HTMLLabel


def safe_remove(parent, name):
    if name in parent.children_names:
        parent.remove(name)


def add_label(txt, point, anchor='center', size=14):
    return Label(txt, point, font_name='Calibri', font_size=size,\
                 anchor_x=anchor, anchor_y='center')


def add_text(txt, point, anchor='center', size=14, padding=10, width=200):
    point = (point[0]+padding, point[1]-padding)
    txt = '<font face="Calibri" size="' + str(size) + '" color="white">'\
          + txt + '</font>'
    return HTMLLabel(txt, point, anchor_x=anchor, anchor_y='top',\
                     multiline=True, width=width-padding*2)
