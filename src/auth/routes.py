from flask import Blueprint, session, redirect, url_for, render_template, current_app, request
from auth.model_route import model_route_auth_request
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
    session['user_id'] = (res_info.user_info['idIntUser'] if 'idIntUser' in res_info.user_info 
                          else res_info.user_info['idExtUser'])
    print(f'User with user_id {session['user_id']} ({session['user_group']}) authorized')

    
    if 'next' in session:
        prev_url = session.pop('next')
        return redirect(prev_url)
    return redirect(url_for('main_menu'))

