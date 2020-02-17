import telebot
import ast  # ?
import json
import DB
from telebot import types
from telebot.types import Message
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

print(str(None))


@bot.message_handler(commands=['start'])
def start_message(message: Message):
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id,
                     text='Привет!',
                     reply_markup=makeKeyboard_TC(DB.TC_list()),
                     parse_mode='HTML')


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
        markup.add(types.InlineKeyboardButton(text=name,
                                              callback_data='{"FC":{"name":"' + name + '","TC_name":"' + TC_name + '"}}'))
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
            types.InlineKeyboardButton(text=rest['name'], callback_data='{"rest_id":' + str(
                rest["rest_id"]) + '}'))

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
    print(FC)

    markup = types.InlineKeyboardMarkup()
    for name in categories['categories']:
        markup.add(types.InlineKeyboardButton(text=name,
                                              callback_data='{"cat":{"cat":"' + name + '","rest_id":' + rest_id + '}}'))
    if FC:
        markup.add(types.InlineKeyboardButton(text='<',
                                              callback_data='{"FC":{"name":"' + FC + '","TC_name":"' + TC_name + '"}}'))
    else:
        markup.add(types.InlineKeyboardButton(text='<',
                                              callback_data='{"TC":"' + TC_name + '"}'))
    markup.add(types.InlineKeyboardButton(text='<<',
                                          callback_data='start'))
    return markup


def makeKeyboard_menu(menu):
    markup = types.InlineKeyboardMarkup()
    rest_id = menu['rest_id']
    category = menu['category']
    for m in menu['menu']:
        markup.add(
            types.InlineKeyboardButton(text=m['name'],
                                       callback_data='{"menu":{"i":' + str(menu['menu'].index(m)) +
                                                     ',"rest_id":' + str(rest_id) + ',"cat":"' + category + '"}}'))
    return markup


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

    # Состав , Итого
    action = 'sruct'
    markup.add(types.InlineKeyboardButton(text='Состав',
                                          callback_data='{"food":[' + rest_id + ',"' + category + '",' + str(
                                              index) + ',"' + action + '"]}'),
               types.InlineKeyboardButton(text='Итого: ' + str(quantity * price) + ' руб',
                                          callback_data='None'))

    # Добавить в корзину
    action = 'add' + str(quantity)
    markup.add(types.InlineKeyboardButton(text='Добавить в корзину',
                                          callback_data='{"food":[' + rest_id + ',"' + category + '",' + str(
                                              index) + ',"' + action + '"]}'))

    # Назад
    # Добавить флаг удаления сообщения
    markup.add(types.InlineKeyboardButton(text='Назад',
                                          callback_data='{"cat":{"cat":"' + category + '","rest_id":' + rest_id + '}}'))

    return markup


# callback_data size max 60

@bot.callback_query_handler(func=lambda call: True)
def handle_query(message):
    data = message.data
    print(data)
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    # Список торговых центров
    if data == 'start':
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text='Список торговых центров',
                              reply_markup=makeKeyboard_TC(DB.TC_list()),
                              parse_mode='HTML')
    # Список фудкортов
    elif data.startswith('{"TC"'):
        TC_name = json.loads(data)['TC']

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=TC_name + '\nСписок фудкортов',
                              reply_markup=makeKeyboard_FC(DB.FC_list(TC_name)),
                              parse_mode='HTML')
    # Список ресторанов
    elif data.startswith('{"FC"'):
        data = json.loads(data)
        TC_name = data['FC']['TC_name']
        FC_name = data['FC']['name']
        if FC_name:
            txt = f'{TC_name}\n{FC_name}\n'
        else:
            txt = f'{TC_name}\n'
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=txt + 'Список ресторанов',
                              reply_markup=makeKeyboard_rest(DB.rest_list(TC_name=TC_name, FC=FC_name)),
                              parse_mode='HTML')

    # Ктегории ресторана
    elif data.startswith('{"rest_id"'):
        data = json.loads(data)
        rest_id = data['rest_id']
        categories = DB.categories_rest(rest_id=rest_id)
        FC = categories["FC"]
        if FC:
            txt = f'{categories["TC_name"]}\n{FC}\n{categories["rest_name"]}\n'
        else:
            txt = f'{categories["TC_name"]}\n{categories["rest_name"]}\n'
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=txt + 'Категории',
                              reply_markup=makeKeyboard_categories(categories),
                              parse_mode='HTML')

    # Меню ресторана
    elif data.startswith('{"cat"'):
        data = json.loads(data)
        rest_id = data['cat']['rest_id']
        category = data['cat']['cat']
        menu = DB.menu_rest(rest_id=rest_id, category=category)
        rest_name = menu['rest_name']

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=rest_name + '\nМеню',
                              reply_markup=makeKeyboard_menu(menu),
                              parse_mode='HTML')

    elif data.startswith('{"menu"'):
        data = json.loads(data)
        rest_id = data['menu']['rest_id']
        category = data['menu']['cat']
        index = data['menu']['i']

        # Отправка изображния
        menu = DB.menu_rest(rest_id=rest_id, category=category)
        img = open(menu['menu'][index]['img'], 'rb')
        bot.send_photo(chat_id=chat_id, photo=img, reply_markup=makeKeyboard_food(menu, index))

        # Удаление старого сообщения
        bot.delete_message(chat_id=chat_id, message_id=message_id)


print('Бот запущен')
bot.polling()
