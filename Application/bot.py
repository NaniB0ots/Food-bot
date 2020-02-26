import telebot
import json
import time
import os
import DB
from telebot import types
from telebot.types import Message
from flask import Flask, request
from config import TOKEN
from config import PROVIDER_TOKEN
from config import URL

# ----------------------------------------- WEBHOOK ----------------------------------------
bot = telebot.TeleBot(TOKEN, threaded=False)

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=URL + TOKEN)

app = Flask(__name__)


@app.route(f'/{TOKEN}', methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'ok', 200


# ------------------------------------------------------------------------------------------


# callback_data size max 60
last_data = {}  # Информация о последней нажатой кнопке пользователем
open_basket = {}  # Информация о том открыл ли пользователь корзину или нет
menu_id = {}  # id сообщения с меню для каждого пользователя


@bot.message_handler(commands=['start'])
def start_message(message: Message):
    chat_id = message.chat.id
    message_id = message.message_id

    global last_data
    global open_basket
    global menu_id
    last_data[chat_id] = None
    open_basket[chat_id] = False
    menu_id[chat_id] = message_id

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


# Список товаров категории
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
    markup.add(types.InlineKeyboardButton(text='Отмена',
                                          callback_data='{"cat":{"cat":"' + category +
                                                        '","rest_id":' + rest_id + ',"p":"p"}}'))
    # p - photo

    return markup


# Кнопки корзины
def makeKeyboard_basket(clear=False):
    markup = types.InlineKeyboardMarkup()
    if not clear:
        markup.add(types.InlineKeyboardButton(text='Сформировать заказ', callback_data='pay'))
        markup.add(types.InlineKeyboardButton(text='Очистить',
                                              callback_data='{"basket":"clear"}'),
                   types.InlineKeyboardButton(text='Изменить',
                                              callback_data='{"basket":"change"}'))

    markup.add(types.InlineKeyboardButton(text='Свернуть', callback_data='{"basket":"close"}'))
    return markup


# Добавление товара в корзину
def add_basket(chat_id, food_name='', quantity=1, prise=0, rest_id=None):
    chat_id = str(chat_id)
    rest_id = str(rest_id)
    content = read_basket()
    if not (chat_id in content.keys()):
        content[chat_id] = []
    # Проверяем есть ли уже такой товар в корзине
    check_food = False
    for i in content[chat_id]:
        if 'food_name' in i.keys() and i['food_name'] == food_name:
            i['quantity'] += quantity
            check_food = True
            break
    if not check_food:
        content[chat_id] += [{'rest_id': rest_id, 'food_name': food_name, 'quantity': quantity, 'price': prise}]
    file = open('basket.json', 'wt')
    file.write(json.dumps(content))


# Удаление нулевых эдемнтов корзины
def save_basket(chat_id):
    chat_id = str(chat_id)
    content = read_basket()
    for i in content[chat_id]:
        if 'food_name' in i.keys() and i['quantity'] <= 0:
            content[chat_id].remove(i)
        file = open('basket.json', 'wt')
        file.write(json.dumps(content))


# Считывание данных о товарах в корзине пользователя
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


# Очистка корзины
def del_basket(chat_id):
    chat_id = str(chat_id)
    content = read_basket()
    if chat_id in content:
        del content[chat_id]
        file = open('basket.json', 'wt')
        file.write(json.dumps(content))


# Изменение товаров корзине
def makeKeyboard_changeBasket(basket, chat_id):
    markup = types.InlineKeyboardMarkup()
    chat_id = str(chat_id)
    save_data = []

    for i in range(len(basket)):
        food_name = basket[i]['food_name']
        quantity = basket[i]['quantity']
        action = ['-' + str(quantity), '+' + str(quantity)]
        save_data += [i, quantity]
        # Название товара
        markup.add(types.InlineKeyboardButton(text=food_name, callback_data='None'))
        # -, количество, +
        markup.add(types.InlineKeyboardButton(text='-',
                                              callback_data='{"change":["' + food_name + '","' + action[
                                                  0] + '"]}'),
                   types.InlineKeyboardButton(text=str(quantity) + ' шт.',
                                              callback_data='None'),
                   types.InlineKeyboardButton(text='+',
                                              callback_data='{"change":["' + food_name + '","' + action[
                                                  1] + '"]}'))

    # save_data
    # Сохранить
    markup.add(
        types.InlineKeyboardButton(text='Сохранить', callback_data='{"change":"save"}'))
    return markup


# ===================== ОБРАБОТКА ОТВЕТОВ КЛАВИАТУРЫ ===================== #
@bot.callback_query_handler(func=lambda call: True)
def handle_query(message):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data
    global last_data
    global open_basket
    global menu_id

    # Храним информацию только о 50 последних пользователях
    if len(last_data) > 50:
        last_data = {}
    if len(open_basket) > 50:
        open_basket = {}

    # Проверка что пользователь не нажал две клавиши на одном этапе меню
    if chat_id in last_data.keys() and data == last_data[chat_id]:
        return
    last_data[chat_id] = data
    print(data)

    # Список торговых центров
    if data == 'start':
        menu_id[chat_id] = message_id  # Запоминаем номер сообщения с меню
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text='Список торговых центров',
                              reply_markup=makeKeyboard_TC(DB.TC_list()),
                              parse_mode='HTML')
    # Список фудкортов
    elif data.startswith('{"TC"'):
        menu_id[chat_id] = message_id  # Запоминаем номер сообщения с меню
        TC_name = json.loads(data)['TC']

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=TC_name + '\nСписок фудкортов',
                              reply_markup=makeKeyboard_FC(DB.FC_list(TC_name)),
                              parse_mode='HTML')
    # Список ресторанов
    elif data.startswith('{"FC"'):
        menu_id[chat_id] = message_id  # Запоминаем номер сообщения с меню
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
        menu_id[chat_id] = message_id  # Запоминаем номер сообщения с меню
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
        menu_id[chat_id] = message_id  # Запоминаем номер сообщения с меню
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
        menu_id[chat_id] = message_id  # Запоминаем номер сообщения с меню
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

        # Если корзина открыта, закрываем
        if chat_id in open_basket.keys() and open_basket[chat_id]:
            bot.delete_message(chat_id=chat_id, message_id=open_basket[chat_id])
            open_basket[chat_id] = False

    # Взаимодействие с товаром
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

            # Проверка если начали добавлять товары другого ресторана !!!!!!!! не работает
            basket = read_basket(chat_id)
            # if basket and rest_name != basket[0]['rest_id']:
            #     del_basket(chat_id)

            food_name = menu['menu'][index]['name']
            prise = menu['menu'][index]['price']
            quantity = int(data[3][3:])

            add_basket(chat_id, food_name, quantity, prise, rest_id=rest_id)

            bot.answer_callback_query(callback_query_id=message.id,
                                      show_alert=False,
                                      text=f'В корзину добавлено {food_name} {quantity} шт.')

            bot.send_message(chat_id=chat_id,
                             text=rest_name + '\nМеню',
                             reply_markup=makeKeyboard_menu(menu),
                             parse_mode='HTML')

            menu_id[chat_id] = message_id + 1  # Запоминаем номер сообщения с меню

            # Удаление старого сообщения
            bot.delete_message(chat_id=chat_id, message_id=message_id)

            # Если корзина открыта, закрываем
            if chat_id in open_basket.keys() and open_basket[chat_id]:
                bot.delete_message(chat_id=chat_id, message_id=open_basket[chat_id])
                open_basket[chat_id] = False

    # Взаимодействие с корзиной
    elif data.startswith('{"basket"'):
        data = json.loads(data)
        action = data['basket']
        if action == 'close':
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            open_basket[chat_id] = False
        elif 'clear' in action:
            del_basket(chat_id)
            bot.answer_callback_query(callback_query_id=message.id,
                                      show_alert=False,
                                      text='Корзина очищена')
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            open_basket[chat_id] = False

        elif 'change' in action:
            basket = read_basket(str(chat_id))
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text='<b>Корзина</b> (изменение)',
                                  reply_markup=makeKeyboard_changeBasket(basket=basket, chat_id=chat_id),
                                  parse_mode='HTML')
    # Изменение корзины
    elif data.startswith('{"change"'):
        # {"change": ["Шашлык куриный", "+2"]}
        data = json.loads(data)['change']

        # Кнопка сохранить
        if data == 'save':
            save_basket(chat_id)
            items = read_basket(str(chat_id))

            if not items:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                      text='<b>Корзина пуста</b>',
                                      reply_markup=makeKeyboard_basket(clear=True),
                                      parse_mode='HTML')
                return

            basket_text, amount, basket_info = makeBasket(items)
            rest_id = items[0]['rest_id']
            restaurant = DB.categories_rest(rest_id)
            rest_name = restaurant['rest_name']

            bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                  text=f'<b>Корзина</b>\n{rest_name}\n\n<i>{basket_text}</i>\nИтого: <i>{amount} руб.</i>',
                                  reply_markup=makeKeyboard_basket(),
                                  parse_mode='HTML')
            return

        # Кнопки - и +
        food_name = data[0]
        action = data[1]
        if '-' in action:
            quantity = int(data[1][1:])
            if quantity == 0:
                return
            quantity = - 1
            add_basket(chat_id=chat_id, food_name=food_name, quantity=quantity)
            basket = read_basket(chat_id)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                          reply_markup=makeKeyboard_changeBasket(basket, chat_id=chat_id))
        elif '+' in action:
            quantity = 1
            add_basket(chat_id=chat_id, food_name=food_name, quantity=quantity)
            basket = read_basket(chat_id)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                          reply_markup=makeKeyboard_changeBasket(basket, chat_id=chat_id))
    # Формирование заказа
    elif data == 'pay':

        bot.delete_message(chat_id=chat_id, message_id=message_id)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Оплатить', pay=True),
                   types.InlineKeyboardButton(text='Удалить', callback_data='del_order_or_receipt'))

        items = read_basket(str(chat_id))
        basket_text, amount, basket_info = makeBasket(items)
        rest_id = items[0]['rest_id']
        restaurant = DB.categories_rest(rest_id)
        rest_name = restaurant['rest_name']

        prices = []
        for i in basket_info:
            food_name = i['food_name']
            quantity = i['quantity']
            price = i['price']
            prices.append(
                types.LabeledPrice(label=food_name + ' ' + str(quantity) + ' шт.', amount=price * quantity * 100))

        bot.send_invoice(chat_id=chat_id, title=f'{rest_name}\nЗаказ №...', description=basket_text,
                         invoice_payload={"rtt": "YourPayLoad"},
                         provider_token=PROVIDER_TOKEN, start_parameter="mybot",
                         currency="RUB", prices=prices, reply_markup=markup)

        open_basket[chat_id] = False

    # Удаление заказа или чека
    elif data == 'del_order_or_receipt':
        bot.delete_message(chat_id=chat_id, message_id=message_id)


# Проверка оплаты
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")


# Cообщения после оплаты
@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    chat_id = message.chat.id
    global menu_id
    print(menu_id)
    bot.delete_message(chat_id, message_id=menu_id[chat_id])

    bot.send_message(chat_id=chat_id,
                     text='Список торговых центров',
                     reply_markup=makeKeyboard_TC(DB.TC_list()),
                     parse_mode='HTML')
    del_basket(chat_id=chat_id)  # Удаление информации из корзины

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Свернуть', callback_data='del_order_or_receipt'))
    bot.send_message(message.chat.id, 'Ваш заказ принят!\n'
                                      'Ожидайте сообщения о готовности!\n'
                                      'История покупок останется в чате над основным меню', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def text(message: Message):
    data = message.text

    if data == 'Корзина':
        global last_data
        global open_basket
        print(open_basket)
        chat_id = message.chat.id
        last_data[chat_id] = None
        message_id = message.message_id
        # Удаление сообщения от пользователя
        bot.delete_message(chat_id=chat_id, message_id=message_id)

        if chat_id in open_basket.keys() and open_basket[chat_id]:  # Проверка того, что корзина уже открыта
            return
        open_basket[chat_id] = message_id + 1

        items = read_basket(str(chat_id))
        print(items)
        if not items:
            bot.send_message(chat_id, text='<b>Корзина пуста</b>',
                             reply_markup=makeKeyboard_basket(clear=True),
                             parse_mode='HTML')
            return
        basket_text, amount, basket_info = makeBasket(items)
        rest_id = items[0]['rest_id']
        restaurant = DB.categories_rest(rest_id)
        rest_name = restaurant['rest_name']

        bot.send_message(chat_id,
                         text=f'<b>Корзина</b>\n{rest_name}\n\n<i>{basket_text}</i>\nИтого: <i>{amount} руб.</i>',
                         reply_markup=makeKeyboard_basket(),
                         parse_mode='HTML')


# Формирует информацию о корзине
def makeBasket(items):
    basket_text = ''
    amount = 0
    basket_info = []
    for i in items:
        food_name = i['food_name']
        quantity = i['quantity']
        price = i['price']
        basket_info.append({'food_name': food_name, 'quantity': quantity, 'price': price})
        basket_text += food_name + ' ' + str(quantity) + ' шт.' + ' ' + str(quantity * price) + ' руб.\n'
        amount += quantity * price
    return basket_text, amount, basket_info


if __name__ == '__main__':
    bot.remove_webhook()
    bot.skip_pending = True
    print('Бот запущен')
    bot.polling(none_stop=True, interval=0)
