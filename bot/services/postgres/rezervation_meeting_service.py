# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import Union
import logging

from sqlalchemy import select, func, update, delete, insert
from sqlalchemy.exc import SQLAlchemyError

from models.table_models.temporary_conference_data import TemporaryConferenceData
from models.table_models.created_conference import CreatedConference
from models.table_models.user import User

from models.dataclasses import MeetingData


from services.postgres.database import get_async_session

from exceptions.errors import CreateMeetingError
class RezervationMeetingService:
    def __init__(self):
        pass
    
    
    @staticmethod
    async def init_new_meeting(user_id: int) -> None:
        """
        Создание новой записи с данными о создаваемой конференции

        Args:
            user_id (int): User telegram ID
        """
        async for session in get_async_session():
            try:
                new_meeting = TemporaryConferenceData(
                    id_tg=user_id
                )
                session.add(new_meeting)
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка инициализации новой конференции пользователя с id_tg {user_id}: {e}")


    @staticmethod
    async def save_created_conference(user_id: int, meeting_data: MeetingData) -> None:
        """
            Сохранение созданной конфереции
        Args:
            user_id (int): User telegram ID
            meeting_data (MeetingData): Данные о созданной конференции

        Raises:
            CreateMeetingError: Ошибка сохранения созданной конференции
        """
        async for session in get_async_session():
            try:
                get_user_id = await session.execute(
                    select(User.id)
                    .where(User.id_tg == user_id)
                )
                creator_id = get_user_id.scalar()
                await session.execute(
                    insert(CreatedConference)
                    .values(
                        creator_id=creator_id,
                        date_creation=datetime.now(),
                        name=meeting_data.name,
                        office=meeting_data.office,
                        start_time=meeting_data.start_time,
                        duration=meeting_data.duration,
                    )
                )
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка сохранения созданной конференции пользователя с id_tg {user_id}: {e}")
                raise CreateMeetingError
    
    
    @staticmethod
    async def delete_temporary_data(user_id: int) -> None:
        """
            Удаление временных данных о создаваемой конференции
        Args:
            user_id (int): User telegram ID
        """
        async for session in get_async_session():
            try:
                await session.execute(
                    delete(TemporaryConferenceData)
                    .where(TemporaryConferenceData.id_tg == user_id)
                )
                
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка удаления данных о создаваемой конференции пользователя с id_tg {user_id}: {e}")
            
            
    @staticmethod
    async def get_data(user_id: int, type_data: str) -> Union[int, str, dict]:        
        """
            Получение данных о создаваемой конференции
        Args:
            user_id (int): User telegram ID
            type_data (str): Тип получаемых данных

        Returns:
            Union[int, str]: Данные о конференции
        """
        async for session in get_async_session():
            try:
                get_temporary_data = await session.execute(
                    select(TemporaryConferenceData)
                    .where(TemporaryConferenceData.id_tg == user_id)
                )
                temporary_data = get_temporary_data.scalars().all()
                if temporary_data:
                    data_mapping = {
                        'date': temporary_data[0].date,
                        'illegal_intervals': temporary_data[0].illegal_intervals,
                        'start_time': temporary_data[0].start_time,
                        'duration': temporary_data[0].duration,
                        'office': temporary_data[0].office,
                    }
                
                    return data_mapping.get(type_data)
            except SQLAlchemyError as e:
                logging.error(f"Ошибка получения '{type_data}' конференции у пользователя с id_tg {user_id}: {e}")
    
    
    @staticmethod
    async def save_data(user_id: int, type_data: str, insert_value: Union[str, dict, list]) -> None:
        """
            Сохранение данных о создаваемой конференции
        Args:
            user_id (int): User telegram ID
            type_data (str): Тип сохраняемых данных
            insert_value (Union[str, dict, list]): Данные для сохранения
        """
        async for session in get_async_session():
            try:
                values_to_update = {}

                values_to_update[type_data] = insert_value
                await session.execute(
                    update(TemporaryConferenceData)
                    .where(TemporaryConferenceData.id_tg == user_id)
                    .values(**values_to_update)
                )
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка сохранения '{type_data}' конференции у пользователя с id_tg {user_id}: {e}")


    @staticmethod
    async def get_illegel_intervals(entered_date: str, office: str) -> list:
        """
            Получение недоступных временных интервалов для создания конференции
        Args:
            entered_date (str): Выбранная дата
            office (str): Адрес переговорной комнаты

        Returns:
            list: Недоступные временные интервалы для создания конференции
        """
        async for session in get_async_session():
            try:
                get_illegal_intervals_query = await session.execute(
                    select(CreatedConference.start_time, CreatedConference.duration)
                    .where(
                        func.date(CreatedConference.start_time) == entered_date,
                        CreatedConference.office == office
                    )
                )
                illegal_intervals = get_illegal_intervals_query.all()
                
                return illegal_intervals
            except SQLAlchemyError as e:
                logging.error(f"Ошибка получения недоступных временных интервалов для создания конференции: {e}")
                
    
    @staticmethod      
    async def get_list_meetings_for_all(entered_date: str, office: str) -> list:
        """
            Получение списка любых запланированных конференций на введенную дату
        Args:
            entered_date (str): Выбранная дата
            office (str): Адрес переговорной комнаты

        Returns:
            list: Запланированные конференции
        """
        async for session in get_async_session():
            try:
                get_list_meetings_query = await session.execute(
                    select(CreatedConference)
                    .where(
                        func.date(CreatedConference.start_time) == entered_date,
                        CreatedConference.office == office
                    )
                )
                list_meetings = [meeting[0] for meeting in get_list_meetings_query.all()]

                return list_meetings
            except SQLAlchemyError as e:
                logging.error(f"Ошибка получения списка любых запланированных конференций на введенную дату: {e}")
                
    
    @staticmethod
    async def get_list_meetings_for_user(user_id: int) -> list:
        """
            Получение списка запланированных конференций на введенную дату для определенного пользователя
        Args:
            user_id (int): User telegram ID

        Returns:
            list: Запланированные конференции
        """
        async for session in get_async_session():
            try:
                get_user_id = await session.execute(
                    select(User.id)
                    .where(User.id_tg == user_id)
                )
                creator_id = get_user_id.scalar()
                get_list_meetings_query = await session.execute(
                    select(CreatedConference)
                    .where(
                        CreatedConference.creator_id==creator_id
                    )
                )
                list_meetings = [meeting[0] for meeting in get_list_meetings_query.all()]

                return list_meetings
            except SQLAlchemyError as e:
                logging.error(f"Ошибка {e}")
                
    
    @staticmethod        
    async def delete_user_meeting(meeting_id:str) -> None:
        """
            Удаление конференции, запланированной пользователем 
        Args:
            meeting_id (str): meeting_id
        """
        async for session in get_async_session():
            try:
                await session.execute(
                    delete(CreatedConference)
                    .where(
                        CreatedConference.id==meeting_id
                    )
                )
                await session.commit()
            except SQLAlchemyError as e:
                logging.error(f"Ошибка удаления конференции с {meeting_id}: {e}")