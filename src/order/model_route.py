from dataclasses import dataclass
from database.select import select_line, insert, update
from datetime import datetime
from database.DBcm import DBContextManager
import os
from database.sql_provider import SQLProvider
from pymysql import Error


@dataclass
class ProductInfoRespronse:
    result: tuple
    error_message: str
    status: bool


sql_provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


def transaction_order(db_config: dict, basket: dict, dishes: list[dict], waiter_id: int, table_id: int):
    try:
        with DBContextManager(db_config) as cursor:
            ddate = datetime.today().replace(microsecond=0)  # microseconds aren't stored in DB
            _sql = sql_provider.get('create_order.sql', e_table_id=table_id, e_waiter_id=waiter_id, e_order_date=ddate)
            print(_sql)
            result = insert(db_config, _sql, cursor)
            if not result:
                return ProductInfoRespronse(tuple(), error_message="Заказ не был создан. Проверьте номер столика", 
                                            status=False)
            
            _sql = sql_provider.get('get_order.sql', e_waiter_id=waiter_id, e_order_date=ddate)
            res_dict = select_line(db_config, _sql, cursor)
            print(_sql)
            if not res_dict:
                return ProductInfoRespronse(tuple(), error_message=f"Не удалось получить созданный заказ.", 
                                            status=False)

            order_id = res_dict['idOrder']
            print(basket)
            total_cost = 0
            for key, value in basket.items():
                _sql = sql_provider.get('insert_order_line.sql',
                                        e_order_id=order_id,
                                        e_dish_id=int(key),
                                        e_amount=int(value))
                result = insert(db_config, _sql, cursor)
                print(_sql)

                cur_dish = tuple(filter(lambda dict_: dict_['idDish'] == int(key), dishes))[0]

                total_cost += int(value) * cur_dish['priceInRubles']

            _sql = sql_provider.get('update_order.sql', total_cost=total_cost, e_order_id=order_id)
            status, msg = update(db_config, _sql, cursor)
            if not status:
                return ProductInfoRespronse(tuple(), error_message=f"Не удалось обновить общую стоимость заказа. {msg}", 
                                            status=False)

            return ProductInfoRespronse((order_id, ), error_message="", status=True)
    except Exception as e:
        return ProductInfoRespronse(tuple(), error_message=f"Произошла непредвиденная ошибка: {e}", 
                                    status=False)
