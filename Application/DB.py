import sqlite3

__connection = None


# Подключение
def get_connection():
    global __connection
    if __connection is None:
        __connection = sqlite3.connect('test_bot.db')
        print("Connected to BD")
    return __connection


# Инициализация ДБ
def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('PRAGMA foreign_keys=on')

    # Создание таблицы TC_list
    c.execute('''
        CREATE TABLE IF NOT EXISTS TC_list (
              id_TC     INTEGER PRIMARY KEY,
              name      TEXT NOT NULL
        )
    ''')

    # Создание таблицы FC_list
    c.execute('''
            CREATE TABLE IF NOT EXISTS FC_list (
                  id_FC         INTEGER PRIMARY KEY,
                  FC            VARCHAR(25) NOT NULL,
                  id_TC         INTEGER NOT NULL,
                  FOREIGN KEY(id_TC) REFERENCES TC_list(id_TC)
            )
        ''')
    # Создание таблицы rest_list
    c.execute('''
            CREATE TABLE IF NOT EXISTS rest_list (
                  id_rest       INTEGER PRIMARY KEY,
                  rest_name     TEXT_not NULL,
                  id_FC         INTEGER NOT NULL,
                  FOREIGN KEY(id_FC) REFERENCES FC_list(id_FC)
            )
        ''')

    # Создание таблицы categories_rest
    c.execute('''
            CREATE TABLE IF NOT EXISTS categories_rest (
                  id_categories        INTEGER PRIMARY KEY,
                  categories           TEXT NOT NULL,
                  id_rest              INTEGER NOT NULL,
                  FOREIGN KEY(id_rest) REFERENCES rest_list(id_rest)
                  
            )
        ''')

    # Создание таблицы  menu_rest
    c.execute('''
            CREATE TABLE IF NOT EXISTS menu_rest (
                  id_menu           INTEGER PRIMARY KEY,
                  menu              TEXT NOT NULL,
                  id_categories     INTEGER NOT NULL,
                  FOREIGN KEY(id_categories) REFERENCES categories_rest(id_categories)
            )
        ''')
    conn.commit()
    c.close()
    conn.close()


# Ввод данных

def insert_TC_list(id_TC, TC_name):
    conn = get_connection()
    c = conn.cursor()
    temp = (id_TC, TC_name)
    c.executemany('INSERT INTO TC_list VALUES(?,?)', (temp,))
    conn.commit()
    print('TC_list updated')
    c.close()
    conn.close()


def insert_FC_list(id_FC, FC, id_TC):
    conn = get_connection()
    c = conn.cursor()
    temp = (id_FC, FC, id_TC)
    c.executemany('INSERT INTO FC_list VALUES(?,?,?)', (temp,))
    conn.commit()
    print('FC_list updated')
    c.close()
    conn.close()


def insert_rest_list(id_rest, rest_name, id_FC):
    conn = get_connection()
    c = conn.cursor()
    temp = (id_rest, rest_name, id_FC)
    c.executemany('INSERT INTO rest_list VALUES(?,?,?)', (temp,))
    conn.commit()
    print('rest_list updated')
    c.close()
    conn.close()


def insert_categories_rest(id_categories, categories, id_rest):
    conn = get_connection()
    c = conn.cursor()
    temp = (id_categories, categories, id_rest)
    c.executemany('INSERT INTO categories_rest VALUES(?,?,?)', (temp,))
    conn.commit()
    print('categories_rest updated')
    c.close()
    conn.close()


def insert_menu_rest(id_menu, menu, id_categories):
    conn = get_connection()
    c = conn.cursor()
    temp = (id_menu, menu, id_categories)
    c.executemany('INSERT INTO menu_rest VALUES(?,?,?)', (temp,))
    conn.commit()
    print('menu_rest updated')
    c.close()
    conn.close()


# Вывод данных

def TC_list():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT name FROM TC_list')
    names = c.fetchall()
    temp = []
    for i in names:
        temp.append({'name': "".join(i)})
    print('ТЕСТ ВОЗВРАТА: ', temp)
    c.close()
    conn.close()
    return temp


def FC_list(TC_name):
    '''
        if 'запрос от DB':
        FC = {'TC_name': TC_name, 'FC': ['3-этаж', '2-этаж']}
    else:
        FC = {'TC_name': TC_name, 'FC': None}
    return FC
    '''
    conn = get_connection()
    c = conn.cursor()
    temp = []
    c.execute('SELECT id_TC FROM TC_list where name = (?)', (TC_name,))
    id = c.fetchone()
    c.execute('''SELECT FC FROM FC_list INNER JOIN TC_list 
                ON TC_list.id_TC = FC_list.id_TC 
                WHERE TC_list.id_TC = (?)''',
              (id))
    FC = c.fetchall()
    if len(FC) > 1:
        temp = []
        for i in FC:
            temp.append("".join(i))
        temp = {'TC_name': TC_name, 'FC': temp}
    else:
        temp = {'TC_name': TC_name, 'FC': None}
    print('ТЕСТ ВОЗВРАТА: ', temp)
    return temp


def rest_list(TC_name, FC=None):
    '''
    restaurants = {'TC_name': TC_name, 'FC': FC, 'rests': [{'rest_id': 12345678, 'name': 'Шавуха от Петрухи'},
                                                           {'rest_id': 10101010, 'name': 'KFC'}]}
    '''

    conn = get_connection()
    c = conn.cursor()
    temp = []
    c.execute('SELECT id_TC FROM TC_list where name = (?)', (TC_name,))
    id_TC = int(str(c.fetchone())[1:-2])
    c.execute('SELECT id_FC FROM FC_list where FC = (?)', (FC,))
    id_FC = int(str(c.fetchone())[1:-2])
    ids = (id_FC, id_TC)
    c.execute('''SELECT id_rest, rest_name FROM rest_list LEFT JOIN FC_list
                 ON rest_list.id_FC = FC_list.id_FC
                 LEFT JOIN TC_list ON TC_list.id_TC = FC_list.id_FC
                 WHERE (rest_list.id_FC = (?)) AND (FC_list.id_TC = (?))''',
                  (ids))
    rest_names = c.fetchall()
    for i in rest_names:
        temp.append({'rest_id': i[0], 'name': "".join(i[1])})
    temp = {'TC_name': TC_name, 'FC': FC, 'rests': temp}
    print('ТЕСТ ВЫВОДА: ', temp)
    return temp


def categories_rest(rest_id):
    '''
    categories = {'rest_name': 'Шавуха от Петрухи', 'TC_name': 'Сильвер молл', 'FC': '2-этаж', 'rest_id': rest_id,
                  'categories': ['Шаурма', 'Напитки']}
    '''

    conn = get_connection()
    c = conn.cursor()
    temp = []
    c.execute('SELECT rest_name FROM rest_list where id_rest = (?)', (rest_id,))
    rest_name = str(c.fetchone())[1:-2]
    c.execute('SELECT id_FC FROM rest_list where id_rest = (?)', (rest_id,))
    id_FC = int(str(c.fetchone())[1:-2])
    c.execute('SELECT id_TC FROM FC_list where id_FC = (?)', (id_FC,))
    id_TC = int(str(c.fetchone())[1:-2])
    c.execute('SELECT FC FROM FC_list where id_FC = (?)', (id_FC,))
    FC = str(c.fetchone())[1:-2]
    c.execute('SELECT name FROM TC_list WHERE id_TC = (?)', (id_TC,))
    TC = str(c.fetchone())[1:-2]
    c.execute('''SELECT categories FROM categories_rest INNER JOIN rest_list
                     ON categories_rest.id_rest = rest_list.id_rest
                     INNER JOIN FC_list ON rest_list.id_FC = FC_list.id_FC
                     INNER JOIN TC_list ON FC_list.id_TC = TC_list.id_TC
                     WHERE (categories_rest.id_rest = (?))''',
                        (rest_id))
    categories_temp = c.fetchall()
    categories=[]
    for i in categories_temp:
        categories.append("".join(i))
    temp = {'rest_name': rest_name, 'TC_name' : TC , 'FC' : FC, 'rest_id' : rest_id, 'categories' : categories }
    print('ТЕСТ ВЫВОДА: ', temp)
