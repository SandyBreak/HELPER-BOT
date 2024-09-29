# -*- coding: UTF-8 -*-

from datetime import datetime
import logging

from sqlalchemy import select, func, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models.table_models.user import User

from services.postgres.database import get_async_session

from exceptions.errors import RegistrationError, UserNotRegError, TelegramAddressNotValidError


class UserService:
    def __init__(self):
        pass
    
    
    @staticmethod
    async def check_user_exists(user_id: int) -> datetime:
        """
            Проверка регистрации и получение даты регистрации.
        Args:
            user_id (int): User telegram ID

        Raises:
            UserNotRegError: Полльзователь не зарегистрирован

        Returns:
            Optional[datetime]: Дата регистрации пользователя
        """
        async for session in get_async_session():
            try:
                check_user_date_reg = await session.execute(select(User.date_reg).where(User.id_tg == user_id))
                date_reg = check_user_date_reg.scalar()
                if date_reg:
                    return date_reg
                else:
                    raise UserNotRegError
            except SQLAlchemyError as e:
                logging.error(f"Ошибка проверки пользователя с id_tg {user_id}: {e}")
                raise e
            
            
    @staticmethod
    async def init_user(user_id: int, nickname: str, full_name: str, fio: str) -> None:
        """
            Регистрация пользователя, сохранение:
            1. ID Аккаунта
            2. Адрес аккаунта
            3. Имя аккаунта
            4. ФИО
            5. Даты регистрации

        Args:
            user_id (int): User telegram ID
            nickname (str): User telegram address
            full_name (str): User telegram Name
            fio (str): ФИО пользователя

        Raises:
            TelegramAddressNotValidError: nickname is None
            RegistrationError: Ошибка регистрации
        """
        async for session in get_async_session():
            try:
                user_exists_query = await session.execute(
                    select(func.count('*'))
                    .where(User.id_tg == user_id)
                )
                user_exists_flag = user_exists_query.scalar()
                
                if not user_exists_flag:
                    new_user = User(
                        id_tg=user_id,
                        nickname=nickname,
                        fullname=full_name,
                        fio=fio,
                        date_reg=datetime.now(),
                    )

                    # Выполнение вставки
                    session.add(new_user)
                    await session.commit()
                
            except IntegrityError as e:
                raise TelegramAddressNotValidError
            except SQLAlchemyError as e:
                logging.error(f"Ошибка регистрации пользователя: {e}")
                raise RegistrationError from e
            
            
    @staticmethod
    async def update_number_created_conferences(user_id: str) -> None:
        """
            Обновление количества конференций созданных пользователем
        Args:
            user_id (str): User telegram ID
        """
        try:
            async for session in get_async_session():
                
                await session.execute(
                    update(User)
                    .where(User.id_tg == user_id)
                    .values(number_created_conferences=func.coalesce(User.number_created_conferences, 0) + 1)
                )
                await session.commit()
                
        except SQLAlchemyError as e:
            logging.critical(f"Ошибка обновления количества созданных конференций: {e}")


    @staticmethod
    async def get_user_data(user_id: int) -> User:
        """
            Получение всех данных о пользователе

        Args:
            user_id (int): User telegram ID

        Returns:
            User: Данные о пользователе
        """
        async for session in get_async_session():
            try:
                get_user_data = await session.execute(select(User).where(User.id_tg == user_id))
                user_data = get_user_data.scalar()
                return user_data
            except SQLAlchemyError as e:
                logging.error(f"Ошибка получения данных пользователя с id_tg {user_id}: {e}")