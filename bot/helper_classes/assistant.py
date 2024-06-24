# -*- coding: UTF-8 -*-

import os

from exeptions import *


class MinorOperations:
    def __init__(self) -> None:
        pass
    
    
    async def get_tg_token(self) -> str:
        return os.environ.get('TELEGRAM_TOKEN')
    
    
    def get_mongo_login(self) -> str:
        return os.environ.get('MONGO_INITDB_ROOT_USERNAME')
    
    
    def get_mongo_password(self) -> str:
        return os.environ.get('MONGO_INITDB_ROOT_PASSWORD')
    
    
    async def fill_event_data(self, office: str, customer: str, tg_customer: str, order: str, type_order: int) -> str:
        types_order= [
            'запрос контакта!',
            'запрос доступа!',
            'заказ канцелярии!',
            'заказ пропуска!',
            'заказ такси!',
            'вызов специалиста!'
        ]
        order_info = [
            'Имя контакта',
            'Тип доступа',
            'Требуемые товары',
            'На чье имя пропуск',
            'На чье имя заказ такси',
            'Тип поломки'
        ]

        new_order = f"""
        Новый {types_order[type_order]}
        Адрес: {office}
        Заказчик: {customer}
        Телеграмм заказчика: @{tg_customer}
        {order_info[type_order]}: {order}
        """
        return new_order
        