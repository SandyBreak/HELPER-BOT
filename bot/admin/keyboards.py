# -*- coding: UTF-8 -*-
from aiogram.utils.keyboard import KeyboardButton, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton

from database.mongodb.interaction import Interaction

mongodb_interface = Interaction()


class AdminKeyboards:
    def __init__(self) -> None:
        pass

    
    async def ban_or_access_keyboard(self, user_id: int) -> InlineKeyboardBuilder:
        """
        Бан или добавление пользователя в админы
        """
        builder = InlineKeyboardBuilder(
            markup=[
                [
                    InlineKeyboardButton(text="Забанить", callback_data=f'BAN,{user_id}')
                ],
                [
                    InlineKeyboardButton(text="Добавить в админы", callback_data=f'ACCESS,{user_id}')
                ]
            ]
        )
        return builder
    
    
    async def keyboard_for_adding_users_in_targeted_newsletter(self) -> InlineKeyboardBuilder:
        """
        Выбор пользователей для точечной рассылки
        """
        builder = InlineKeyboardBuilder()
        buttons = []
        users = await mongodb_interface.get_users_id_and_tg_adreses()
        for user in users:
            user_id = user[0]
            user_tg_addr = user[1]
            builder.row(InlineKeyboardButton(text=f'{user_id} {user_tg_addr}', callback_data=f'ADD,{user_id},{user_tg_addr}'))
        return builder
    
    
    async def possibilities_keyboard(self) -> InlineKeyboardBuilder:
        """
        Основная клавиатура админа
        """
        builder = InlineKeyboardBuilder(
            markup=[
                [
                    InlineKeyboardButton(text="РУКОВОДСТВО АДМИН ПАНЕЛИ", callback_data=f'manual')
                ],
                [
                    InlineKeyboardButton(text="Запустить глобальную рассылку", callback_data=f'global_newsletter')
                ],
                [
                    InlineKeyboardButton(text="Запустить точечную рассылку", callback_data=f'targeted_newsletter')
                ],
                [
                    InlineKeyboardButton(text="Посмотреть список активных/не активных пользователей", callback_data=f'view_active_users')
                ],
                [
                    InlineKeyboardButton(text="Заново отправить сообщение с действиями", callback_data='menu')
                ]
            ]
        )
        return builder