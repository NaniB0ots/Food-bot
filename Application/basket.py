import json
import os
from telebot import types
from config import basket_bass


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
    file = open(basket_bass, 'wt')
    file.write(json.dumps(content, indent=4))


# Удаление нулевых элемнтов корзины
def save_basket(chat_id):
    chat_id = str(chat_id)
    content = read_basket()
    for i in content[chat_id]:
        if 'food_name' in i.keys() and i['quantity'] <= 0:
            content[chat_id].remove(i)
        file = open(basket_bass, 'wt')
        file.write(json.dumps(content, indent=4))


# Считывание данных о товарах в корзине пользователя
def read_basket(chat_id=''):
    chat_id = str(chat_id)
    if os.path.isfile(basket_bass):
        file = open(basket_bass).read()
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
        file = open(basket_bass, 'wt')
        file.write(json.dumps(content, indent=4))


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
