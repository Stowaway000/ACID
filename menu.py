from cocos.director import director


# Убираем настройки по-умолчанию
def set_menu_style(menu, size=32):
    menu.font_item_selected['font_size'] = size
    menu.font_item_selected['font_name'] = 'Calibri'
    menu.font_item['font_name'] = 'Calibri'
    menu.font_item_selected['color'] = (229, 43, 80, 240)
    menu.font_item['color'] = (192, 192, 192, 200)

    menu.on_key_press = None


def go_back(n):
    for i in range(n):
        director.pop()


def previous():
    go_back(1)


def quit_game():
    director.window.close()
