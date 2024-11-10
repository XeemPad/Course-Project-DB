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
