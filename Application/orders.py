import json
import os
from datetime import datetime
from config import TZ_IRKUTSK, orders_path


def add_order(rest_id, order):  # Добавление заказа
    content = read_order()
    if not (rest_id in content.keys()):
        content[rest_id] = []
    content[rest_id].append(order)
    print('Order added', content[rest_id][-1])
    save_orders(content)


# Считываем список заказов
def read_order():
    if os.path.isfile(orders_path):
        file = open(orders_path).read()
        if file:
            content = json.loads(file)
            return content
    return {}


# Получаем максимальный номер заказа за текущий день
def get_order_number(content):
    if content:
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
    file = open(orders_path, 'wt')
    file.write(json.dumps(content, indent=4))
