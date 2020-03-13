import json
import os
from config import user_orders_path

def add_user_order(rest_id, order):
    chat_id = str(order['chat_id'])
    del order['chat_id']
    order['rest_id'] = rest_id
    content = read_user_order()
    if not (chat_id in content.keys()):
        content[chat_id] = []
    content[chat_id].append(order)
    save_user_orders(content)

def read_user_order():
    if os.path.isfile(user_orders_path):
        file = open(user_orders_path).read()
        if file:
            content = json.loads(file)
            return content
    return {}
# Сохраняем список заказов пользователя
def save_user_orders(content):
    file = open(user_orders_path, 'wt')
    file.write(json.dumps(content, indent=4))

