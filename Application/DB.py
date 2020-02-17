def TC_list():
    TC = [{'name': 'Модный'}, {'name': 'Комсомол'}, {'name': 'Сильвер молл'}]
    return TC


def FC_list(TC_name):
    if 'запрос от DB':
        FC = {'TC_name': TC_name, 'FC': ['3-этаж', '2-этаж']}
    else:
        FC = {'TC_name': TC_name, 'FC': None}
    return FC


def rest_list(TC_name, FC=None):
    restaurants = {'TC_name': TC_name, 'FC': FC, 'rests': [{'rest_id': 12345678, 'name': 'Шавуха от Петрухи'},
                                                           {'rest_id': 10101010, 'name': 'KFC'}]}
    return restaurants


def categories_rest(rest_id):
    categories = {'rest_name': 'Шавуха от Петрухи', 'TC_name': 'Сильвер молл', 'FC': '2-этаж', 'rest_id': rest_id,
                  'categories': ['Шаурма', 'Напитки']}
    return categories


def menu_rest(rest_id, category):
    # Например
    rest_name = 'Шавуха от Петрухи'

    path = f'images/{rest_name}/{category}/'
    menu = {'rest_name': 'Шавуха от Петрухи', 'rest_id': rest_id, 'category': category,
            'menu': [{'name': 'Шаурма большая',
                      'img': path + 'Shavuha_Petr2(Shaurma)_Shaurma_midle.jpg',
                      'composition': '', 'price': '150'},
                     {'name': 'Шашлык', 'img': 'images/Шавуха от петрухи/Шаурма/cipa_chachlik_chicken.png',
                      'composition': '', 'price': '310'}]}
    return menu
