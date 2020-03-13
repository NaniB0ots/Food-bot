import telebot
import json
import time
import os
import DB
from telebot import types
from telebot.types import Message
from datetime import datetime
import pytz

from flask import Flask, request

from config import TOKEN
from config import PROVIDER_TOKEN
from config import URL

from menu import makeKeyboard_TC, makeKeyboard_FC, makeKeyboard_rest
from menu import makeKeyboard_categories, makeKeyboard_menu, makeKeyboard_food

from basket import makeKeyboard_basket, makeKeyboard_changeBasket, add_basket
from basket import save_basket, read_basket, del_basket

from orders import add_order, read_order, get_order_number, save_orders

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
TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')  # Часовой пояс
Base_DIR = os.path.dirname(__file__)


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
    print(chat_id, ':', data)

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

        TC_name = data['FC'][1]  # TC_name
        FC_name = data['FC'][0]  # FC_name
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
        rest_id = data['cat'][1]
        category = data['cat'][0]
        menu = DB.menu_rest(rest_id=rest_id, category=category)
        rest_name = menu['rest_name']

        photo = data['cat'][2]
        if not photo:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=rest_name + '\nМеню\n' + category,
                                  reply_markup=makeKeyboard_menu(menu),
                                  parse_mode='HTML')
        else:
            bot.send_message(chat_id=chat_id,
                             text=rest_name + '\nМеню\n' + category,
                             reply_markup=makeKeyboard_menu(menu),
                             parse_mode='HTML')
            # Удаление старого сообщения
            bot.delete_message(chat_id=chat_id, message_id=message_id)

    # Список товаров (меню рестрана)
    elif data.startswith('{"menu"'):
        menu_id[chat_id] = message_id  # Запоминаем номер сообщения с меню
        data = json.loads(data)
        rest_id = data['menu'][2]
        category = data['menu'][1]
        index = data['menu'][0]

        # Отправка изображния
        menu = DB.menu_rest(rest_id=rest_id, category=category)
        try:
            img = open(menu['menu'][index]['img'], 'rb')
        except:
            print('Image not found:', menu['menu'][index]['img'])
            return
        bot.send_photo(chat_id=chat_id, photo=img, reply_markup=makeKeyboard_food(menu, index))

        # Удаление старого сообщения
        bot.delete_message(chat_id=chat_id, message_id=message_id)

        # Если корзина открыта, закрываем
        if chat_id in open_basket.keys() and open_basket[chat_id]:
            bot.delete_message(chat_id=chat_id, message_id=open_basket[chat_id])
            open_basket[chat_id] = False

    # Взаимодействие с товаром
    elif data.startswith('{"food'):
        # '{"food": [rest_id, category, index, action]}'
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

            # Проверка если начали добавлять товары другого ресторана
            basket = read_basket(chat_id)
            update_text = ''
            if basket and int(rest_id) != int(basket[0]['rest_id']):
                del_basket(chat_id)
                update_text = 'Корзина обновлена '

            food_name = menu['menu'][index]['name']
            prise = menu['menu'][index]['price']
            quantity = int(data[3][3:])

            add_basket(chat_id, food_name, quantity, prise, rest_id=rest_id)

            bot.answer_callback_query(callback_query_id=message.id,
                                      show_alert=False,
                                      text=f'{update_text}В корзину добавлено {food_name} {quantity} шт.')

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
        print(rest_name)

        prices = []
        for i in basket_info:
            food_name = i['food_name']
            quantity = i['quantity']
            price = i['price']
            prices.append(
                types.LabeledPrice(label=food_name + ' ' + str(quantity) + ' шт.', amount=price * quantity * 100))
        print(items)
        bot.send_invoice(chat_id=chat_id, title=rest_name, description=basket_text,
                         invoice_payload={"bla": "bla"},
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
    bot.delete_message(chat_id, message_id=menu_id[chat_id])

    bot.send_message(chat_id=chat_id,
                     text='Список торговых центров',
                     reply_markup=makeKeyboard_TC(DB.TC_list()),
                     parse_mode='HTML')
    # Формируем заказ
    basket = read_basket(chat_id)
    rest_id = basket[0]['rest_id']
    rest_name = DB.categories_rest(rest_id)['rest_name']
    date = datetime.now(TZ_IRKUTSK).date().strftime("%d.%m.%Y")
    if rest_id in read_order().keys():
        order_number = get_order_number(read_order()[rest_id])
    else:
        order_number = 1
    receipt = ''
    order_list = []
    for i in basket:
        order_list.append((i['food_name'], i['quantity'], i['price']))

    order = {'chat_id': chat_id, 'rest_name': rest_name, 'order_list': order_list, 'date': date,
             'order_number': order_number, 'receipt': receipt}
    add_order(rest_id, order)

    # Очищаем корзину
    del_basket(chat_id=chat_id)  # Удаление информации из корзины

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Свернуть', callback_data='del_order_or_receipt'))
    order_number = (3 - len(str(order_number))) * '0' + str(order_number)
    bot.send_message(message.chat.id, f'Ваш заказ принят!\nНомер заказа {order_number}.\n'
                                      'Ожидайте сообщения о готовности!\n\n'
                                      'История покупок останется в чате над основным меню', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def text(message: Message):
    data = message.text

    if data == 'Корзина':
        global last_data
        global open_basket
        chat_id = message.chat.id
        last_data[chat_id] = None
        message_id = message.message_id
        # Удаление сообщения от пользователя
        bot.delete_message(chat_id=chat_id, message_id=message_id)

        if chat_id in open_basket.keys() and open_basket[chat_id]:  # Проверка того, что корзина уже открыта
            return
        open_basket[chat_id] = message_id + 1

        items = read_basket(str(chat_id))
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
    file = open('basket.json', 'wt')
    file.write(json.dumps({}, indent=4))
    bot.remove_webhook()
    bot.skip_pending = True
    print('Бот запущен')
    bot.polling(none_stop=True, interval=0)

file = open('basket.json', 'wt')
file.write(json.dumps({}, indent=4))
print('Бот запущен')
