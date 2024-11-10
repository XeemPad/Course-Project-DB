from flask import Blueprint, render_template, current_app, request, url_for
from access import login_required
from query.model_route import get_dishes_from_db, get_waiters_from_db, get_table_from_db, \
    DishesInfoResponse, WaiterInfoResponse, TableInfoResponse
from auth.auth import check_authorization

query_blueprint = Blueprint(
    'query_bp',
    __name__,
    template_folder='templates'
)


@query_blueprint.route('/')
@login_required
def queries_menu():
    ''' Меню выбора запроса '''
    return render_template('queries_menu.html', auth_msg=check_authorization()[0])


@query_blueprint.route('/dishes', methods=['GET'])
@login_required
def request_dish_info():
    return render_template("input_dish.html", auth_msg=check_authorization()[0])


@query_blueprint.route('/waiters', methods=['GET'])
@login_required
def request_waiter_info():
    return render_template("input_waiter.html", auth_msg=check_authorization()[0])


@query_blueprint.route('/tables', methods=['GET'])
@login_required
def request_table_info():
    return render_template("input_table.html", auth_msg=check_authorization()[0])


@query_blueprint.route('/dishes', methods=['POST'])
@login_required
def output_dish():
    request_data = request.form
    res_info: DishesInfoResponse = get_dishes_from_db(current_app.config['db_config'], request_data)
    if res_info.status:
        header = res_info.header
        rows = res_info.result
        print("Dishes from db:", rows)
        dishes_title = 'Блюда с подходящим названием'
        return render_template("table_out.html", table_title=dishes_title, header=header, 
                               rows=rows, prev_page=url_for('query_bp.request_dish_info'), 
                               auth_msg=check_authorization()[0])
    else:
        err_msg = res_info.error_message
        print(err_msg)
        return render_template("query_error.html", error_title='Нет результатов', 
                               error_msg=err_msg, prev_page=url_for('query_bp.request_dish_info'),
                               auth_msg=check_authorization()[0])



@query_blueprint.route('/waiters', methods=['POST'])
@login_required
def output_waiter():
    request_data = request.form
    res_info: WaiterInfoResponse = get_waiters_from_db(current_app.config['db_config'], request_data)
    if res_info.status:
        header = res_info.header
        rows = res_info.result
        print("Waiters from db:", rows)
        waiters_title = 'Официанты с подходящим именем'
        return render_template("table_out.html", table_title=waiters_title, header=header, 
                               rows=rows, prev_page=url_for('query_bp.request_waiter_info'), 
                               auth_msg=check_authorization()[0])
    else:
        err_msg = res_info.error_message
        print(err_msg)
        return render_template("query_error.html", error_title='Нет результатов', 
                               error_msg=err_msg, prev_page=url_for('query_bp.request_waiter_info'),
                               auth_msg=check_authorization()[0])


@query_blueprint.route('/tables', methods=['POST'])
@login_required
def output_table():
    request_data = request.form
    res_info: TableInfoResponse = get_table_from_db(current_app.config['db_config'], request_data)
    if res_info.status:
        res_dict: dict = res_info.res_dict
        print("Table from db:", res_dict)
        tables_title = f'Искомый стол'
        return render_template("row_out.html", table_title=tables_title, dictionary=res_dict, 
                               prev_page=url_for('query_bp.request_table_info'), 
                               auth_msg=check_authorization()[0])
    else:
        err_msg = res_info.error_message
        print(err_msg)
        return render_template("query_error.html", error_title='Нет результатов', 
                               error_msg=err_msg, prev_page=url_for('query_bp.request_table_info'),
                               auth_msg=check_authorization()[0])
