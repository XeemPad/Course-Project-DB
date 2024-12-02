from flask import Blueprint, session, redirect, url_for, render_template, current_app, request
from auth.model_route import model_route_auth_request, model_route_reg_exist_check, model_route_reg_new
from auth.auth import check_authorization


auth_blueprint = Blueprint('auth_bp', __name__, template_folder='templates')


@auth_blueprint.route('/', methods=['GET'])
def auth_index():
    info = session.pop('info', default='')
    return render_template('login.html', info=info, 
                           auth_msg=check_authorization()[0])


@auth_blueprint.route('/', methods=['POST'])
def auth_main():
    user_data = request.form
    res_info = model_route_auth_request(current_app.config['db_config'], user_data)
    print(res_info)
    if not res_info.status:
        print('Ошибка авторизации:', res_info.error_message)
        return render_template('auth_error.html', error_title='Не удалось войти', 
                               error_msg='Неверный логин или пароль', auth_msg=check_authorization()[0])

    session['login'] = res_info.user_info['login']
    session['user_group'] = res_info.user_info['user_group']
    session['user_id'] = int(res_info.user_info['idIntUser'] if 'idIntUser' in res_info.user_info 
                          else res_info.user_info['idExtUser'])
    print(f'User with user_id {session['user_id']} ({session['user_group']}) authorized')

    
    if 'next' in session:
        prev_url = session.pop('next')
        return redirect(prev_url)
    return redirect(url_for('main_menu'))


@auth_blueprint.route('/registration', methods=['GET'])
def registration_index():
    return render_template('registration.html', auth_msg=check_authorization()[0])


@auth_blueprint.route('/registration', methods=['POST'])
def registration_main():
    user_data = request.form
    res_info = model_route_reg_exist_check(current_app.config['db_config'], user_data)
    print(res_info)
    if res_info.status:
        return render_template('auth_error.html', error_title='Не удалось зарегистрироваться', 
                               error_msg="Такой пользователь уже существует", auth_msg=check_authorization()[0])

    if user_data['password'] != user_data['password_verify']:
        return render_template('auth_error.html', error_title='Не удалось зарегистрироваться', 
                               error_msg="Пароли не совпадают", auth_msg=check_authorization()[0])
    res_info = model_route_reg_new(current_app.config['db_config'], user_data)
    if not res_info.status:
        return render_template('auth_error.html', error_title='Не удалось зарегистрироваться', 
                               error_msg=res_info.error_message, auth_msg=check_authorization()[0])

    print("Регистрация успешна")

    return render_template('reg_success.html', auth_msg=check_authorization()[0])
