import json
import os
from datetime import datetime
import pytz

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')  # Часовой пояс
Base_DIR = os.path.dirname(__file__)

def add_order(rest_id, order):  # Добавление заказа
    content = read_order()
    if not (rest_id in content.keys()):
        content[rest_id] = []
    content[rest_id].append(order)
    print('Order added', content[rest_id][-1])
    save_orders(content)


# Считываем список заказов
def read_order():
    global Base_DIR
    if os.path.isfile(Base_DIR + '/orders.json'):
        file = open(Base_DIR + '/orders.json').read()
        if file:
            content = json.loads(file)
            return content
    return {}


# Получаем максимальный номер заказа за текущий день
def get_order_number(content):
    if content:
        global TZ_IRKUTSK
        date_now = datetime.now(TZ_IRKUTSK).date().strftime("%d.%m.%Y")
        last_order = content[-1]
        if last_order['date'] != date_now:
            order_number = 0
        else:
            order_number = last_order['order_number']
        order_number += 1
        return order_number
    return 1


# Сохраняем список заказов
def save_orders(content):
    global Base_DIR
    file = open(Base_DIR + '/orders.json', 'wt')
    file.write(json.dumps(content, indent=4))
