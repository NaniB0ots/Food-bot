import telebot
import ast  # ?
import json
import os
import DB
from telebot import types
from telebot.types import Message
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

print(str(None))


@bot.message_handler(commands=['start'])
def start_message(message: Message):
    chat_id = message.chat.id

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn = types.KeyboardButton('Корзина')
    markup.add(btn)

    bot.send_message(chat_id=chat_id,
                     text='Привет!',
                     reply_markup=markup,
                     parse_mode='HTML')

    bot.send_message(chat_id=chat_id,
                     text='Список торговых центров',
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
                                              callback_data='{"cat":{"cat":"' + name +
                                                            '","rest_id":' + rest_id + ',"p":""}}'))
        # p - photo
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
    rest_id = str(menu['rest_id'])
    category = menu['category']
    for m in menu['menu']:
        markup.add(
            types.InlineKeyboardButton(text=m['name'],
                                       callback_data='{"menu":{"i":' + str(menu['menu'].index(m)) +
                                                     ',"rest_id":' + rest_id + ',"cat":"' + category + '"}}'))

    markup.add(types.InlineKeyboardButton(text='<', callback_data='{"rest_id":' + rest_id + '}'))
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
    markup.add(types.InlineKeyboardButton(text='Отмена',
                                          callback_data='{"cat":{"cat":"' + category +
                                                        '","rest_id":' + rest_id + ',"p":"p"}}'))
    # p - photo

    return markup


# callback_data size max 60

def makeKeyboard_basket():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Оплатить',
                                          callback_data='None'),
               types.InlineKeyboardButton(text='Очистить',
                                          callback_data='{"basket":"clear"}'))

    markup.add(types.InlineKeyboardButton(text='Свернуть', callback_data='{"basket":"close"}'))
    return markup


def add_basket(chat_id, food_name='', quantity=1, prise=0):
    chat_id = str(chat_id)
    content = read_basket()
    if not chat_id in content.keys():
        content[chat_id] = []
    content[chat_id] += [{'food_name': food_name, 'quantity': quantity, 'price': prise}]
    print(content)
    file = open('basket.json', 'wt')
    file.write(
        json.dumps(content))  # Преобразовываем словарь в текст формата JSON, а затем записываем эти данные в файл


def read_basket(chat_id=''):
    chat_id = str(chat_id)
    if os.path.isfile('basket.json'):
        file = open('basket.json').read()
        if file:
            content = json.loads(file)
            if not chat_id:
                return content
            if not chat_id in content.keys():
                return {}
            basket = content[chat_id]
            return basket
    return {}


def del_basket(chat_id):
    chat_id = str(chat_id)
    content = read_basket()
    if chat_id in content:
        del content[chat_id]
        file = open('basket.json', 'wt')
        file.write(json.dumps(content))



old_data = ''


@bot.callback_query_handler(func=lambda call: True)
def handle_query(message):
    global old_data
    data = message.data

    # Проверка что пользователь не нажал две клавиши на одном этапе меню
    if data[:4] == old_data[:4] and data[:4] != '{"fo' and data[:4] != '{"ba':
        return
    old_data = data
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

        photo = data['cat']['p']
        if not photo:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=rest_name + '\nМеню',
                                  reply_markup=makeKeyboard_menu(menu),
                                  parse_mode='HTML')
        else:
            bot.send_message(chat_id=chat_id,
                             text=rest_name + '\nМеню',
                             reply_markup=makeKeyboard_menu(menu),
                             parse_mode='HTML')
            # Удаление старого сообщения
            bot.delete_message(chat_id=chat_id, message_id=message_id)

    # Список товаров (меню рестрана)
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

    elif data.startswith('{"food'):
        '{"food": [12345678, "Шаурма", 0, "-1"]}'
        data = json.loads(data)['food']
        rest_id = data[0]
        category = data[1]
        index = data[2]
        action = data[3]
        menu = DB.menu_rest(rest_id=rest_id, category=category)

        if '-' in action:
            quantity = int(data[3][1:])
            if quantity == 1:
                return
            quantity -= 1
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                          reply_markup=makeKeyboard_food(menu, index, quantity=quantity))
        elif '+' in action:
            quantity = int(data[3][1:])
            quantity += 1
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                          reply_markup=makeKeyboard_food(menu, index, quantity=quantity))
        elif 'sruct' in action:

            bot.answer_callback_query(callback_query_id=message.id,
                                      show_alert=True,
                                      text='Состав:\n' + menu['menu'][index]['composition'])
        elif 'add' in action:
            rest_name = menu['rest_name']
            food_name = menu['menu'][index]['name']
            prise = menu['menu'][index]['price']
            quantity = int(data[3][3:])

            add_basket(chat_id, food_name, quantity, prise)

            bot.answer_callback_query(callback_query_id=message.id,
                                      show_alert=True,
                                      text=f'В корзину добавлено {food_name} {quantity} шт.')

            bot.send_message(chat_id=chat_id,
                             text=rest_name + '\nМеню',
                             reply_markup=makeKeyboard_menu(menu),
                             parse_mode='HTML')
            # Удаление старого сообщения
            bot.delete_message(chat_id=chat_id, message_id=message_id)

    elif data.startswith('{"basket"'):
        data = json.loads(data)
        action = data['basket']
        if action == 'close':
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        elif 'clear' in action:
            del_basket(chat_id)
            bot.answer_callback_query(callback_query_id=message.id,
                                      show_alert=False,
                                      text='Корзина очищена')
            bot.delete_message(chat_id=chat_id, message_id=message_id)


@bot.message_handler(content_types=['text'])
def text(message: Message):
    data = message.text

    if data == 'Корзина':
        chat_id = message.chat.id
        message_id = message.message_id
        bot.delete_message(chat_id=chat_id, message_id=message_id)

        items = read_basket(str(chat_id))
        print(items)
        if not items:
            bot.send_message(chat_id, text='<b>                  Корзина</b>                  \n' + 'Корзина пуста',
                             reply_markup=makeKeyboard_basket(),
                             parse_mode='HTML')
            return

        basket = ''
        amount = 0
        for i in items:
            food_name = i['food_name']
            quantity = i['quantity']
            price = i['price']
            basket += food_name + 4 * ' ' + str(quantity) + ' шт.' + 4 * ' ' + str(quantity * price) + ' руб.\n'
            amount += quantity * price
            print(i)
        basket += f'Итого: {amount} руб'

        bot.send_message(chat_id, text='<b>                  Корзина</b>                  \n' + basket,
                         reply_markup=makeKeyboard_basket(),
                         parse_mode='HTML')


print('Бот запущен')
bot.polling()
