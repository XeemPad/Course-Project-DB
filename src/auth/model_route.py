from dataclasses import dataclass
from database.select import insert, select_line
from database.sql_provider import SQLProvider
import os


@dataclass
class UserInfoResponse:
    user_info: dict
    status: bool
    error_message: str


sql_provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


def model_route_auth_request(db_config, user_input_data):
    ''' Функция обрабатывающая попытку входа в аккаунт '''
    login_inp, pwd_inp = user_input_data['login'], user_input_data['password']
    # Сначала проверяем среди внешних пользователей
    ext_sql = sql_provider.get('external_user.sql', login=login_inp, password=pwd_inp)
    result = select_line(db_config, ext_sql)
    print(f'External users search result: {result}')

    if result:  # Если нашёлся такой пользователь
        return UserInfoResponse(result, error_message='', status=True)
    
    # Иначе ишем среди внутренних пользователей:
    int_sql = sql_provider.get('internal_user.sql', login=login_inp, password=pwd_inp)
    result = select_line(db_config, int_sql)
    print(f'Internal users search result: {result}')

    if result:  # Если нашёлся такой пользователь
        return UserInfoResponse(result, error_message='', status=True)
    
    # Если не нашли такого аккаунта среди внутренних и внешних пользователей:
    return UserInfoResponse(result, error_message=f'No user found using queries:\n1. {ext_sql}\n2. {int_sql}', 
                            status=False)


def model_route_reg_exist_check(db_config, user_input_data):
    _sql = sql_provider.get('check_user.sql', login=user_input_data['login'])

    dict_ = select_line(db_config, _sql)
    if dict_:
        return UserInfoResponse(dict_, error_message='', status=True)
    return UserInfoResponse(dict_, error_message=f'No user found using query:\n{_sql}', 
                            status=False)


def model_route_reg_new(db_config, user_input_data):
    newuser_group = 'client'

    _sql = sql_provider.get('create_extuser.sql',
                            login=user_input_data['login'],
                            password=user_input_data['password'],
                            group=newuser_group)
    result = insert(db_config, _sql)
    if result:
        return UserInfoResponse(dict(), error_message='', status=True)
    return UserInfoResponse(dict(), error_message=f'Couldnt insert using query:\n{_sql}.',
                            status=False)


def hash_password(password: str):
    from hashlib import sha256
    # Ideally should not be sha256
    return sha256(str(password).encode()).hexdigest()