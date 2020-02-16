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
    restaurants = {'TC_name': TC_name, 'FC': FC, 'rests': [{'rest_id': 12345678, 'name': 'Шавуха у Петрухи'},
                                                           {'rest_id': 10101010, 'name': 'KFC'}]}
    return restaurants


def categories_rest(id_rest):
    categories = {'rest_id': id_rest, 'categories': ['Шаурма', 'Напитки']}
    return categories


def menu_rest(rest_id, category):
    menu = {'rest_id': rest_id, 'menu': [{'name': '', 'img': '', 'composition': '', 'price': ''}]}
    return menu
