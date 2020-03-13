import os
import pytz

TOKEN = '941022031:AAFgRROWBsU2eY2BT77MH9HbsvPvB9Ccljs'  # Food-bot_test1 @Test1_Food_bot
URL = 'https://bolanebyla.pythonanywhere.com/'
PROVIDER_TOKEN = '381764678:TEST:14257'

Base_DIR = os.path.dirname(__file__)
TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')  # Часовой пояс

basket_bass = f'{Base_DIR}/basket.json'
orders_path = f'{Base_DIR}/orders.json'
