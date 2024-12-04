from math import prod
import re
from flask import Blueprint, session, redirect, url_for, render_template, current_app, request
from access import login_required, check_authorization
from cache.wrapper import fetch_from_cache
from database.select import select_dict, select_line, CursorError
from order.model_route import transaction_order
import os
from database.sql_provider import SQLProvider


order_blueprint = Blueprint('order_bp', __name__, template_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@order_blueprint.route('/', methods=['GET'])
@login_required
def basket_index():
    ''' Получение списка блюд, которые можно добавить в корзину (заказ) '''
    
    # Получаем список всех блюд из Кэша 
    cache_select_dict = fetch_from_cache('dishes_cached', current_app.config['cache_config'])(select_dict)
    _sql = provider.get('all_dishes.sql')
    dishes = cache_select_dict(current_app.config['db_config'], _sql)
    print('Dishes list from cache:', dishes)

    # Убеждаемся, что в сессии есть корзина:
    if 'basket' not in session:
        session['basket'] = {str(session['user_id']): {}}
    print("Basket from session: ", session['basket'])

    current_basket = form_basket(dishes)
    print("Current basket: ", current_basket)
    
    return render_template('basket_dynamic.html', dishes=dishes, basket=current_basket,
                           auth_msg=check_authorization()[0])

@order_blueprint.route('/', methods=['POST'])
@login_required
def basket_main():

    # Нужно извлечь id официанта:
    user_id = str(session['user_id'])

    # Получаем корзину:
    session['basket'] = session.get('basket', {user_id: {}})
    if user_id not in session['basket']:
        session['basket'][user_id] = {}

    # Получаем список всех блюд из Кэша 
    cache_select_dict = fetch_from_cache('dishes_cached', current_app.config['cache_config'])(select_dict)
    _sql = provider.get('all_dishes.sql')
    dishes = cache_select_dict(current_app.config['db_config'], _sql)
    
    current_basket = session['basket'][user_id]
    print("BASKET=", current_basket)

    # При нажатии кнопки Добавить:
    if request.form.get('buy'):

        # Достаём информацию о продукте из кэша:
        dish = tuple(filter(lambda dict_: dict_['idDish'] == int(request.form['dish_display_id']), dishes))[0]
        print(dish)

        dish_id = str(dish['idDish'])  # json поддерживает только строки
        if dish_id in current_basket:
            amount = int(current_basket[dish_id])
            session['basket'][user_id][dish_id] = str(amount + 1)
        else:
            print("NEW dish")
            session['basket'][user_id][dish_id] = '1'
            print(session['basket'])
        session.modified = True

    if request.form.get('product_display_plus') or request.form.get('product_display_minus'):
        if request.form.get('product_display_plus'):  # increasing count in basket
            add = 1
        else:  # decreasing count in basket
            add = -1
        
        # Достаём информацию о продукте из кэша:
        dish = tuple(filter(lambda dict_: dict_['idDish'] == int(request.form['dish_display_id']), dishes))[0]
        print(dish)

        amount = int(session['basket'][user_id][str(dish['idDish'])])
        if amount + add == 0:
            session['basket'][user_id].pop(str(dish['idDish']))
        else:
            session['basket'][user_id][str(dish['idDish'])] = str(amount + add)
        session.modified = True

    return redirect(url_for('order_bp.basket_index'))


@order_blueprint.route('/clear_basket')
@login_required
def clear_basket():
    user_id = str(session['user_id'])
    basket = session.get('basket', {})
    if basket:
        session['basket'].pop(user_id)
        session['basket'][user_id] = {}
        session.modified = True
    
    return redirect(url_for('order_bp.basket_index'))

@order_blueprint.route('/save_order', methods=['POST'])
@login_required
def save_order():
    if not session.get('basket', {}):
        return redirect(url_for('order_bp.basket_index'))

    db_config = current_app.config['db_config']

    # Получаем id официанта в таблице Waiters:
    user_id = str(session['user_id'])
    _sql = provider.get('get_waiter_id_from_users.sql', user_id=user_id)
    try:
        waiter_id = select_line(db_config, _sql)['idWaiter']
    except CursorError as ce:
        print('waiter_id', ce)
        return render_template("order_error.html", error_title="Заказ не был создан", 
                               error_msg="Не удалось подключиться к базе данных",
                               auth_msg=check_authorization()[0])
    except KeyError as ce:
        print('waiter_id', ce)
        return render_template("order_error.html", error_title="Заказ не был создан", 
                               error_msg="Не удалось найти официанта связанного с данным аккаунтом",
                               auth_msg=check_authorization()[0])

    current_basket = session['basket'][user_id]
    table_id = request.form.get('table_id')
    if not select_line(db_config, provider.get('get_table.sql', table_id=table_id)):
        return render_template("order_error.html", error_title="Заказ не был создан", 
                               error_msg="Указан неверный номер столика",
                               auth_msg=check_authorization()[0])
    if not current_basket:
        return render_template("order_error.html", error_title="Заказ не был создан", 
                               error_msg="Корзина пуста",
                               auth_msg=check_authorization()[0])


    cache_select_dict = fetch_from_cache('dishes_cached', current_app.config['cache_config'])(select_dict)
    dishes = cache_select_dict(db_config, provider.get('all_dishes.sql'))

    result = transaction_order(db_config, current_basket, dishes, waiter_id, table_id)
    print("Order success")
    if result.status:
        clear_basket()
        return render_template("order_finish.html", order_id=result.result[0],
                               auth_msg=check_authorization()[0])
    return render_template("error.html", error_title="Заказ не был создан", error_msg=result.error_message,
                           auth_msg=check_authorization()[0])


def form_basket(dishes_info: list[dict]) -> list[dict]:
    user_id = str(session['user_id'])
    if 'basket' not in session or user_id not in session['basket']:
        return []
    
    basket = []
    for dish_id, dish_amount in session['basket'][user_id].items():
        dish = tuple(filter(lambda dict_: dict_['idDish'] == int(dish_id), dishes_info))[0]  # find dish in cache
        print(dish)
        dish['amount'] = dish_amount
        basket.append(dish)
    return basket




