# -*- coding: UTF-8 -*-

from typing import Optional
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, update, insert

from services.postgres.database import get_async_session

from models.table_models.user import User
from models.table_models.admin_group import AdminGroup
from models.table_models.user_chat import UserChat


class GroupService:
    def __init__(self):
        pass


    @staticmethod
    async def group_init(id_group: int) -> None:
        """
            Сохранение ID группы в которую был добавлен бот
        Args:
            id_group (int): Telegram group ID
        """
        try:
            async for session in get_async_session():
                session.add(AdminGroup(group_id=id_group))
                
                await session.commit()
                
                await session.close()
        except Exception as e:  # Ловим все исключения
            logging.error(f"Ошибка при сохранении ID группы: {e}")
    
    
    @staticmethod
    async def group_reset() -> None:
        """
        Сброс ID группы
        """
        try:
            async for session in get_async_session():
                await session.execute(delete(AdminGroup))
                
                await session.commit()
        except Exception as e:
            await session.rollback()
            logging.error(f"Ошибка сброса ID группы: {e}")
    
    
    @staticmethod
    async def get_group_id() -> Optional[int]:
        """
            Получение ID группы
        Returns:
            Optional[int]: Telegram group ID or None
        """
        try:
            async for session in get_async_session():
                get_group_id = await session.execute(select(AdminGroup.group_id))
                id_group = get_group_id.scalar()
                if id_group:
                    await session.close()
                    return id_group
                else:
                    return None
        except Exception as e:
            logging.error(f"Ошибка получения ID группы: {e}")
            
            
    @staticmethod
    async def get_user_message_thread_id(user_id: int) -> int:
        """
            Получаение id чата с пользователем в группе
        Args:
            user_id (int): User telegram ID

        Returns:
            int: User message thread ID
        """
        try:
            async for session in get_async_session():
                subquery = select(User.id).where(User.id_tg == user_id).scalar_subquery()
                get_user_message_thread_id = await session.execute(select(UserChat.id_topic_chat)
                    .select_from(UserChat)
                    .where(UserChat.user_id == subquery)
                )
                message_thread_id = get_user_message_thread_id.scalar()
                await session.close()
                return message_thread_id
        except Exception as e:
            logging.error(f"Ошибка получения id чата пользователя в группе c id_tg {user_id}: {e}")
    
    
    @staticmethod
    async def update_user_message_thread_id(user_id: int, message_thread_id: int) -> None:
        """
            Обновление id чата с пользователем в группе.
        Args:
            user_id (int): User telegram ID
            message_thread_id (int): User message thread ID
        """
        try:
            async for session in get_async_session():
                subquery = select(User.id).where(User.id_tg == user_id).scalar_subquery()
                await session.execute(
                        update(UserChat)
                        .where(UserChat.user_id == subquery)
                        .values(id_topic_chat=message_thread_id)
                        )
                await session.commit()
        except Exception as e:
            logging.error(f"Ошибка обновления id чата пользователя в группе c id_tg {user_id}: {e}")

    
    @staticmethod
    async def save_user_message_thread_id(user_id: int, message_thread_id: int) -> None:
        """
            Сохранение id чата с пользователем в группе
        Args:
            user_id (int): User telegram ID
            message_thread_id (int): User message thread ID
        """
        try:
            async for session in get_async_session():
                subquery = select(User.id).where(User.id_tg == user_id).scalar_subquery()
                await session.execute(
                        insert(UserChat)
                        .values(user_id=subquery, id_topic_chat=message_thread_id)
                        )
                await session.commit()
        except Exception as e:
            logging.error(f"Ошибка при сохранение id чата пользователя в группе c id_tg {user_id}: {e}")