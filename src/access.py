from functools import wraps

from flask import current_app, session, request, redirect, url_for, render_template

from auth.auth import check_authorization


def login_required(func):
    @wraps(func)  # Preserves the original function's metadata and docstring.
    def wrapper(*args, **kwargs):
        if 'user_group' in session:  # Пользователь авторизован

            cur_user_group = session['user_group']  # роль пользователя
            available_bps = current_app.config['db_access'][cur_user_group] # доступные ему блюпринты
            requested_bp = request.blueprint  # куда пользователь хочет попасть
            if requested_bp in available_bps:  # если ему туда можно
                return func(*args, **kwargs)  # то продолжаем выполнение функции
            # иначе выводим ошибку
            return render_template('error.html', error_title='Отказано в доступе', 
                                   error_msg=f'Ваша роль {cur_user_group} не имеет прав для доступа к этой странице', 
                                   auth_msg=check_authorization()[0])
            
        # Если не авторизован, по редиректим на авторизацию
        session['next'] = request.url  # потом вернемся на предыдущую страницу
        session['info'] = 'Для доступа к данной странице необходимо авторизоваться'
        return redirect(url_for('auth_bp.auth_index'))
    return wrapper
