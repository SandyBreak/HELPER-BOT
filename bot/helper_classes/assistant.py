# -*- coding: UTF-8 -*-

import os
from datetime import datetime
from data_storage.dataclasses import MeetingData
from exeptions import *


class MinorOperations:
    def __init__(self) -> None:
        pass
    
    async def get_tg_token(self) -> str:
        """
        Получение токена бота
        """
        return os.environ.get('TELEGRAM_TOKEN')
    
    
   
    def get_mongo_login(self) -> str:
        """
        Получение логина пользователя
        """
        return os.environ.get('MONGO_INITDB_ROOT_USERNAME')
    
    
    def get_mongo_password(self) -> str:
        """
        Получение пароля пользователя
        """
        return os.environ.get('MONGO_INITDB_ROOT_PASSWORD')
    
    
    async def fill_event_data(self, office: str, customer: str, tg_customer: str, order: str, type_order: int) -> str:
        """
        Формирование сообщения запроса
        """
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
        <b>Новый {types_order[type_order]}</b>
        <b>Адрес:</b> {office}
        <b>Заказчик:</b> {customer}
        <b>Телеграмм заказчика:</b> @{tg_customer}
        <b>{order_info[type_order]}:</b> {order}
        """
        return new_order
    
    async def duration_conversion(self, duration: int) -> float:
        """
        Конвертация длительности из часов в минуты
        """
        dec_duration = float('0.' + duration[2:])
        duration = float(duration.replace(":", "."))

        if dec_duration == 0.15:
            duration = duration//1 + 0.25

        elif dec_duration == 0.3:
            duration = duration//1 + 0.5

        elif dec_duration == 0.45:
            duration = duration//1 + 0.75
		
        return duration
        
    async def fill_meeting_data_credits(self, user_id: int, name: str, mongo_db) -> MeetingData:
        """
        Заполнение структуры данными о созданной конференции
        """
        entered_date = await mongo_db.get_data(user_id, 'date')
        start_time = await  mongo_db.get_data(user_id, 'start_time')
        duration = await  mongo_db.get_data(user_id, 'duration_meeting')
        office = await  mongo_db.get_data(user_id, 'choosen_room')
        meeting_data = MeetingData(
	        topic=name,
	        start_time=datetime.strptime(entered_date + start_time, '%Y-%m-%d%H:%M'),
	        duration=int(duration * 60),
            office=office
	    )
        return meeting_data