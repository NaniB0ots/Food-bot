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
                                              callback_data='{"cat":{"cat":"' + name + '","rest_id":"' + rest_id + '"}}'))
    if FC:
        markup.add(types.InlineKeyboardButton(text='<',
                                              callback_data='{"FC":{"name":"' + FC + '","TC_name":"' + TC_name + '"}}'))
    else:
        markup.add(types.InlineKeyboardButton(text='<',
                                              callback_data='{"TC":"' + TC_name + '"}'))
    markup.add(types.InlineKeyboardButton(text='<<',
                                          callback_data='start'))
    return markup


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
    # elif data.startswith():
    #     rest_id = json.loads(message.data)['rest_id']


print('Бот запущен')
bot.polling()
