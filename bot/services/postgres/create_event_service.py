# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import Union
import logging

from sqlalchemy import select, func, update, delete, insert
from sqlalchemy.exc import SQLAlchemyError

from models.table_models.temporary_events_data import TemporaryEventsData
from models.table_models.user import User
from models.table_models.created_events import CreatedEvent
from models.dataclasses import MeetingData


from services.postgres.database import get_async_session


class CreateEventService:
    def __init__(self):
        pass
    
    
    @staticmethod
    async def init_new_event(user_id: int, type_event: str) -> None:
        """
        Создание новой записи с данными о создаваемой конференции
        """
        async for session in get_async_session():
            try:
                new_meeting = TemporaryEventsData(
                    id_tg=user_id,
                    type_event=type_event
                )
                session.add(new_meeting)
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка инициализации новой конференции пользователя с id_tg {user_id}: {e}")


    @staticmethod
    async def save_created_event(user_id: int) -> None:
        """
        Добавдение записи о созданном запросе
        """
        
        async for session in get_async_session():
            try:
                get_user_id = await session.execute(
                    select(User.id)
                    .where(User.id_tg == user_id)
                )
                creator_id = get_user_id.scalar()
                get_event_data = await session.execute(
                    select(TemporaryEventsData)
                    .where(TemporaryEventsData.id_tg == user_id)
                )
                event_data = get_event_data.scalars().all()[0]
                await session.execute(
                    insert(CreatedEvent)
                    .values(
                        creator_id=creator_id,
                        date_creation=datetime.now(),
                        type_event=event_data.type_event,
                        office=event_data.office,
                        delivery_rate=event_data.delivery_rate,
                        taxi_rate=event_data.taxi_rate,
                        departure_address=event_data.departure_address,
                        destination_address=event_data.destination_address,
                        customer_fio=event_data.customer_fio,
                        customer_phone=event_data.customer_phone,
                        recipient_fio=event_data.recipient_fio,
                        recipient_phone=event_data.recipient_phone,
                        info=event_data.info
                    )
                )
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка сохранения созданной конференции пользователя с id_tg {user_id}: {e}")
    
    
    @staticmethod
    async def delete_temporary_data(user_id: int) -> None:
        async for session in get_async_session():
            try:
                await session.execute(
                    delete(TemporaryEventsData)
                    .where(TemporaryEventsData.id_tg == user_id)
                )
                
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка удаления данных о создаваемой конференции пользователя с id_tg {user_id}: {e}")
            
            
    @staticmethod
    async def get_data(user_id: int, type_data: str) -> Union[int, str, dict]:
        """
        Получение данных о создаваемой конференции
        """
        async for session in get_async_session():
            try:
                get_temporary_data = await session.execute(
                    select(TemporaryEventsData)
                    .where(TemporaryEventsData.id_tg == user_id)
                )
                temporary_data = get_temporary_data.scalars().all()
                if type_data == 'all':
                    return temporary_data[0]

                data_mapping = {
                    'type_event': temporary_data[0].type_event,
                    'office': temporary_data[0].office,
                    'delivery_rate': temporary_data[0].delivery_rate,
                    'taxi_rate': temporary_data[0].taxi_rate,
                    'departure_address': temporary_data[0].departure_address,
                    'destination_address': temporary_data[0].destination_address,
                    'customer_fio': temporary_data[0].customer_fio,
                    'customer_phone': temporary_data[0].customer_phone,
                    'recipient_fio': temporary_data[0].recipient_fio,
                    'recipient_phone': temporary_data[0].recipient_phone,
                    'info': temporary_data[0].info
                }
                
                return data_mapping.get(type_data)
            except SQLAlchemyError as e:
                logging.error(f"Ошибка получения '{type_data}': {e}")
    
    
    @staticmethod
    async def save_data(user_id: int, type_data: str, insert_value: Union[str, dict, list]) -> None:
        """
        Сохранение данных о создаваемой конференции
        """
        async for session in get_async_session():
            try:
                values_to_update = {}

                match type_data:
                    case 'taxi_rate':
                        taxi_rate_data_map = {
                            'econom': "Эконом",
                            'comfort': "Комфорт",
                            'comfort_plus': "Комфорт +"
                        }
                        values_to_update[type_data] = taxi_rate_data_map[insert_value]
                    case 'delivery_rate':
                        delivery_rate_data_map = {
                            'express': "Экспресс",
                            'express30': "Экспресс +30",
                            'express60': "Экспресс +60",
                            'four_hours': "4 часа"
                        }
                        values_to_update[type_data] = delivery_rate_data_map[insert_value]
                    case 'office':
                        office_data_map = {
                            'mosenka':'Бизнес-центр \"Mosenka-park-towers\"',
                            'empire': 'Москва-Сити башня \"Империя\"'
                        }
                        values_to_update[type_data] = office_data_map[insert_value]
                    case _:
                        values_to_update[type_data] = insert_value
                await session.execute(
                    update(TemporaryEventsData)
                    .where(TemporaryEventsData.id_tg == user_id)
                    .values(**values_to_update)
                )
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка сохранения '{type_data}': {e}")
