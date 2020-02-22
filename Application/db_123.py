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

#Ввод данных

def insert_TC_list(id_TC,TC_name):
    conn = get_connection()
    c = conn.cursor()
    temp = (id_TC,TC_name)
    c.executemany('INSERT INTO TC_list VALUES(?,?)',(temp,))
    conn.commit()
    print('TC_list updated')
    c.close()
    conn.close()

def insert_FC_list(id_FC,FC,id_TC):
    conn = get_connection()
    c = conn.cursor()
    temp=(id_FC,FC,id_TC)
    c.executemany('INSERT INTO FC_list VALUES(?,?,?)',(temp,))
    conn.commit()
    print('FC_list updated')
    c.close()
    conn.close()

def insert_rest_list(id_rest,rest_name,id_FC):
    conn = get_connection()
    c = conn.cursor()
    temp = (id_rest,rest_name,id_FC)
    c.executemany('INSERT INTO rest_list VALUES(?,?,?)', (temp,))
    conn.commit()
    print('rest_list updated')
    c.close()
    conn.close()

def insert_categories_rest(id_categories,categories,id_rest):
    conn = get_connection()
    c = conn.cursor()
    temp = (id_categories,categories,id_rest)
    c.executemany('INSERT INTO categories_rest VALUES(?,?,?)', (temp,))
    conn.commit()
    print('categories_rest updated')
    c.close()
    conn.close()

def insert_menu_rest(id_menu,menu,id_categories):
    conn = get_connection()
    c = conn.cursor()
    temp = (id_menu,menu,id_categories)
    c.executemany('INSERT INTO menu_rest VALUES(?,?,?)', (temp,))
    conn.commit()
    print('menu_rest updated')
    c.close()
    conn.close()

