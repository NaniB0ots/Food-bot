import DB
from telebot import types


# Список торговых центров (меню)
def makeKeyboard_TC(TC):
    markup = types.InlineKeyboardMarkup()
    for i in TC:
        markup.add(types.InlineKeyboardButton(text=i['name'], callback_data='{"TC":"' + i['name'] + '"}'))
    return markup


# Список фудкортов (меню)
def makeKeyboard_FC(FC):
    TC_name = FC['TC_name']
    if not FC['FC']:
        return makeKeyboard_rest(DB.rest_list(TC_name))
    markup = types.InlineKeyboardMarkup()
    for name in FC['FC']:
        data = f'["{name}","{TC_name}"]'  # [name, TC_name]
        markup.add(types.InlineKeyboardButton(text=name,
                                              callback_data='{"FC":' + data + '}'))
    markup.add(types.InlineKeyboardButton(text='<',
                                          callback_data='start'))

    return markup


# Список рестаранов (меню)
def makeKeyboard_rest(restaurants):
    TC_name = restaurants['TC_name']
    FC = restaurants['FC']
    markup = types.InlineKeyboardMarkup()
    for rest in restaurants['rests']:
        markup.add(
            types.InlineKeyboardButton(text=rest['name'], callback_data='{"rest_id":' + str(rest["rest_id"]) + '}'))

    if FC:
        markup.add(types.InlineKeyboardButton(text='<', callback_data='{"TC":"' + TC_name + '"}'))

    else:
        markup.add(types.InlineKeyboardButton(text='<', callback_data='start'))
        return markup
    markup.add(types.InlineKeyboardButton(text='<<',
                                          callback_data='start'))
    return markup


# Список категорий ресторана
def makeKeyboard_categories(categories):
    rest_id = str(categories['rest_id'])
    TC_name = categories['TC_name']
    FC = categories['FC']

    markup = types.InlineKeyboardMarkup()
    for name in categories['categories']:
        data = f'["{name}", "{rest_id}", ""]'  # [name, rest_id, ""] "" - не после показа фотографии
        markup.add(types.InlineKeyboardButton(text=name, callback_data='{"cat":' + data + '}'))

    if FC:
        data = f'["{FC}", "{TC_name}"]'  # [FC, TC_name]
        markup.add(types.InlineKeyboardButton(text='<',
                                              callback_data='{"FC":' + data + '}'))
    else:
        markup.add(types.InlineKeyboardButton(text='<',
                                              callback_data='{"TC":"' + TC_name + '"}'))
    markup.add(types.InlineKeyboardButton(text='<<',
                                          callback_data='start'))
    return markup


# Список товаров категории
def makeKeyboard_menu(menu):
    markup = types.InlineKeyboardMarkup()
    rest_id = str(menu['rest_id'])
    category = menu['category']
    for m in menu['menu']:
        data = f'[{menu["menu"].index(m)}, "{category}", "{rest_id}"]'  # [int(index), rest_id, category]
        markup.add(types.InlineKeyboardButton(text=m['name'], callback_data='{"menu":' + data + '}'))

    markup.add(types.InlineKeyboardButton(text='<', callback_data='{"rest_id":' + rest_id + '}'))
    return markup


# Меню информации о товаре
def makeKeyboard_food(menu, index, quantity=1):
    markup = types.InlineKeyboardMarkup()
    rest_id = str(menu['rest_id'])
    category = menu['category']
    price = menu['menu'][index]['price']

    # {"f":{"i":' + str(i) + ',"rest_id":' + str(rest_id) + ',"c":"' + category + ',""a:"' + 'struck' + '"}}'

    # -, количество, +
    action = ['-' + str(quantity), '+' + str(quantity)]
    markup.add(types.InlineKeyboardButton(text='-',
                                          callback_data='{"food":[' + rest_id + ',"' + category + '",' + str(
                                              index) + ',"' + action[0] + '"]}'),
               types.InlineKeyboardButton(text=str(quantity),
                                          callback_data='None'),
               types.InlineKeyboardButton(text='+',
                                          callback_data='{"food":[' + rest_id + ',"' + category + '",' + str(
                                              index) + ',"' + action[1] + '"]}'))

    # Добавить в корзину
    action = 'add' + str(quantity)
    markup.add(types.InlineKeyboardButton(text='Добавить в корзину',
                                          callback_data='{"food":[' + rest_id + ',"' + category + '",' + str(
                                              index) + ',"' + action + '"]}'))

    # Состав , Итого
    action = 'sruct'
    markup.add(types.InlineKeyboardButton(text='Состав',
                                          callback_data='{"food":[' + rest_id + ',"' + category + '",' + str(
                                              index) + ',"' + action + '"]}'),
               types.InlineKeyboardButton(text='Итого: ' + str(quantity * int(price)) + ' руб',
                                          callback_data='None'))

    # Назад
    data = f'["{category}", "{rest_id}", "p"]'  # [category, rest_id, "p"] p - после фотографии
    markup.add(types.InlineKeyboardButton(text='Отмена', callback_data='{"cat":' + data + '}'))
    return markup
