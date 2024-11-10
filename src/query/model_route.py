from dataclasses import dataclass
from database.select import select_list, select_line

from database.sql_provider import SQLProvider
import os


sql_provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


@dataclass
class DishesInfoResponse:
    header: tuple
    result: tuple
    error_message: str
    status: bool


def get_dishes_from_db(db_config, user_input_data):
    if 'dish_name' not in user_input_data:  # пользователь не ввёл название блюда
        err_msg = f"dish_name was not inputted; user_input_data={user_input_data}"
        return DishesInfoResponse(tuple(), error_message=err_msg, status=False)
    
    _sql = sql_provider.get('dish.sql', dish_name=user_input_data['dish_name'])
    select = select_list(db_config, _sql)
    result, schema = select
    if result:
        return DishesInfoResponse(schema, result, error_message='', status=True)
    return DishesInfoResponse(schema, result, 
                              error_message=f'No rows found for query "{_sql}"', status=False)


@dataclass
class WaiterInfoResponse(DishesInfoResponse):
    pass


def get_waiters_from_db(db_config, user_input_data):
    if 'waiter_name' not in user_input_data:  # пользователь не ввёл имя официанта
        err_msg = f"waiter_name was not inputted; user_input_data={user_input_data}"
        return WaiterInfoResponse(tuple(), error_message=err_msg, status=False)
    
    _sql = sql_provider.get('waiter.sql', waiter_name=user_input_data['waiter_name'])
    select = select_list(db_config, _sql)
    result, schema = select
    if result:
        return WaiterInfoResponse(schema, result, error_message='', status=True)
    return WaiterInfoResponse(schema, result, 
                              error_message=f'No rows found for query "{_sql}"', status=False)


@dataclass
class TableInfoResponse:
    res_dict: dict
    error_message: str
    status: bool


def get_table_from_db(db_config, user_input_data):
    if 'table_id' not in user_input_data:  # пользователь не ввёл имя официанта
        err_msg = f"table_id was not inputted; user_input_data={user_input_data}"
        return TableInfoResponse(dict(), error_message=err_msg, status=False)
    
    _sql = sql_provider.get('table.sql', table_id=user_input_data['table_id'])
    result: dict = select_line(db_config, _sql)
    if result:
        return TableInfoResponse(result, error_message='', status=True)
    return TableInfoResponse(result, error_message=f'No rows found for query "{_sql}"', status=False)