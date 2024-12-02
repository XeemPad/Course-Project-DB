from math import prod
import re
from flask import Blueprint, session, redirect, url_for, render_template, current_app, request
from access import login_required, check_authorization
from cache.wrapper import fetch_from_cache
from database.select import select_dict
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
    _sql = provider.get('all_goods.sql')
    products = cache_select_dict(current_app.config['db_config'], _sql)
    print(products)

    # Достаём текущую корзину из сессии:
    if 'basket' not in session:
        session['basket'] = {session['user_id']: {}}
    basket = session['basket']
    print("Basket from session: ", basket)
    current_basket = form_basket(products)
    
    return render_template('basket_dynamic.html', products=products, basket=current_basket,
                           auth_msg=check_authorization()[0])

@order_blueprint.route('/', methods=['POST'])
@login_required
def basket_main():
    db_config = current_app.config['db_config']
    user_id = session['user_id']
    session['basket'] = session.get('basket', {user_id: {}})
    if user_id not in session['basket']:
        session['basket'][user_id] = {}
    basket = session['basket']
    print(basket)
    current_basket = basket[user_id]
    print("BASKET=", current_basket)
    if request.form.get('buy'):
        # adding to basket
        if not 'basket' in session:
            session['basket'][user_id] = {user_id: {}}
        _sql = provider.get('one_good.sql', e_prod_id=int(request.form['product_display']))
        products = select_dict(db_config, _sql)
        if not products:
            return render_template('error.html', error_title='Не удалось получить товар', 
                                   error_msg='Возможно, БД не работает', auth_msg=check_authorization()[0])
        product = products[0]
        print(product)
        
        # сессия поддерживает сериализацию через json, поэтому ключ может быть только строчкой
        # сессия не запоминает изменения значений по ключу, только добавление или удалени
        # поэтому нужно вручную указывать изменение сессии

        if str(product['id']) in current_basket:
            prid = str(product['id'])
            amount = int(session['basket'][user_id][prid])
            session['basket'][user_id][prid] = str(amount+1)
            session.modified = True
        else:
            print("NEW PRODUCT")
            prid = str(product['id'])
            session['basket'][user_id][prid] = '1'
            print(session['basket'][user_id])
            session.modified = True

    if request.form.get('product_display_plus'):
        # increasing count in basket
        _sql = provider.get('one_good.sql', e_prod_id=int(request.form['product_display']))
        product = select_dict(db_config, _sql)[0]
        amount = int(session['basket'][user_id][str(product['id'])])
        session['basket'][user_id][str(product['id'])] = str(amount + 1)
        session.modified = True

    if request.form.get('product_display_minus'):
        # decreasing count in basket
        _sql = provider.get('one_good.sql', e_prod_id=int(request.form['product_display']))
        product = select_dict(db_config, _sql)[0]
        amount = int(session['basket'][user_id][str(product['id'])])
        if amount == 1:
            session['basket'][user_id].pop(str(product['id']))
        else:
            session['basket'][user_id][str(product['id'])] = str(amount - 1)
        session.modified = True

    return redirect(url_for('basket_bp.basket_index'))

@order_blueprint.route('/clear_basket')
@login_required
def clear_basket():
    user_id = session['user_id']
    basket = session.get('basket', {user_id: {}})[user_id]
    if basket:
        session['basket'].pop(user_id)
        print(session['basket'])
        session['basket'][user_id] = {}
        session.modified = True
     
    return redirect(url_for('basket_bp.basket_index'))

@order_blueprint.route('/save_order')
@login_required
def save_order():
    if not session.get('basket',{}):
        return redirect(url_for('basket_bp.basket_index'))
    # if not session.get('user_id',""):
    #     return render_template("error.html", message="Вы не авторизованы на сайте, авторизируйтесь для регистрации заказа")
    print("Order success")
    current_basket = session.get('basket', {})
    user_id = session.get('user_id', -1)
    result = transaction_order(current_app.config['db_config'], current_basket[user_id], user_id)
    if result.status:
        clear_basket()
        return render_template("order_finish.html", order_id = result.result[0],
                               auth_msg=check_authorization()[0])
    else:
        return render_template("error.html", error_title="Заказ не был создан",
                               auth_msg=check_authorization()[0])


def form_basket(dishes_info: dict):
    if 'basket' not in session or session['user_id'] not in session['basket']:
        return []
    basket = []
    for k, v in session['basket'][session['user_id']].items():
        dish = dishes_info
        dish['amount'] = v
        basket.append(dish)
    return basket




