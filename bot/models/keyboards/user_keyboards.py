# -*- coding: UTF-8 -*-

import json

from aiogram.utils.keyboard import KeyboardButton, InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from models.table_models.created_conference import CreatedConference


class UserKeyboards:
    def __init__(self) -> None:
        pass

    @staticmethod
    async def ultimate_keyboard(type_keyboard: str) -> InlineKeyboardBuilder:
        """
        Args:
            type_keyboard (str): Тип клавиатуры

        Returns:
            InlineKeyboardBuilder: Клавиатура выбора переговорной комнаты, адреса местонахождения и кнопки назад
        """
        builder = InlineKeyboardBuilder()
        
        if type_keyboard == 'back':
            builder.row(InlineKeyboardButton(text="Вернуться назад", callback_data=json.dumps({'key': 'back'}))) # Кнопка для возврата назад
        if type_keyboard == 'office':           
            builder.row(InlineKeyboardButton(text="Москва-Сити башня \"Империя\"", callback_data=json.dumps({'key': 'choice', 'value': 'empire'})))
            builder.row(InlineKeyboardButton(text="Бизнес-центр \"Mosenka-park-towers\"", callback_data=json.dumps({'key': 'choice', 'value': 'mosenka'})))
        
        return builder
    
    
    
    @staticmethod
    async def possibilities_keyboard() -> InlineKeyboardBuilder:
        """
        Returns:
            InlineKeyboardBuilder: Основная инлайн клавиатура со всеми функциями бота
        """
        builder = InlineKeyboardBuilder()
        
        builder.row(InlineKeyboardButton(text="🚕 Заказать такси", callback_data='order_taxi'))
        #builder.row(InlineKeyboardButton(text="🚚 Заказать доставку", callback_data='order_delivery')
        builder.row(InlineKeyboardButton(text="🔑 Заказать пропуск", callback_data='order_pass'))
        builder.row(InlineKeyboardButton(text="📇 Заказать визитку", callback_data='order_cutaway'))
        builder.row(InlineKeyboardButton(text="✏️ Заказать канцелярию", callback_data='order_office'))
        builder.row(InlineKeyboardButton(text="🛠️ Заказать/отремонтировать технику", callback_data='order_technic'))
        builder.row(InlineKeyboardButton(text="🔓 Получить доступ", callback_data='gain_access'))
        builder.row(InlineKeyboardButton(text="📱 Найти контакты сотрудника", callback_data='find_contact'))
        builder.row(InlineKeyboardButton(text="🗓️ Забронировать переговорную комнату", callback_data='rezervation_meeting_room'))
        builder.row(InlineKeyboardButton(text="🕗 Ознакомиться с бронями преговорных комнат", callback_data='get_list_meeting'))
        builder.row(InlineKeyboardButton(text="❌ Отменить бронь переговорной комнаты", callback_data='cancel_rezervation_meeting_room'))
        builder.row(InlineKeyboardButton(text="🔵 Создать конференцию в ZOOM", callback_data='create_zoom_meeting'))

        return builder
    
    
    @staticmethod
    async def recipient_keyboard(type_keyboard: str) -> InlineKeyboardBuilder:
        """
        Args:
            type_keyboard (str): Тип клавиатуры

        Returns:
            InlineKeyboardBuilder: Клавиатура с кнопками что пользователь вызывает такси или доставку для себя
        """
        builder = InlineKeyboardBuilder()
        
        if type_keyboard == 'taxi':
            builder.row(InlineKeyboardButton(text=f'Я поеду на такси', callback_data=json.dumps({'key': 'recipient'})))
        if type_keyboard == 'delivery':
            builder.row(InlineKeyboardButton(text="Вернуться назад", callback_data=json.dumps({'key': 'back'})))
            builder.row(InlineKeyboardButton(text=f'Заказ нужно доставить мне', callback_data=json.dumps({'key': 'recipient'})))
        
        return builder
    
    
    @staticmethod
    async def taxi_rate_keyboard() -> InlineKeyboardBuilder:
        """
        Returns:
            InlineKeyboardBuilder: Клавиатура с тарифами такси
        """
        builder = InlineKeyboardBuilder()
        
        builder.row(InlineKeyboardButton(text="Вернуться назад", callback_data=json.dumps({'key': 'back'})))
        builder.row(InlineKeyboardButton(text="Эконом", callback_data=json.dumps({'key': 'rate', 'value': 'econom'})))
        builder.row(InlineKeyboardButton(text="Комфорт", callback_data=json.dumps({'key': 'rate', 'value': 'comfort'})))
        builder.row(InlineKeyboardButton(text="Комфорт +", callback_data=json.dumps({'key': 'rate', 'value':'comfort_plus'})))
        
        return builder
    
    
    @staticmethod
    async def delivery_rate_keyboard() -> InlineKeyboardBuilder:
        """
        Returns:
            InlineKeyboardBuilder: Клавиатура с тарифами доставки
        """
        builder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(text="Вернуться назад", callback_data=json.dumps({'key': 'back'})))
        builder.row(InlineKeyboardButton(text="Экспресс", callback_data=json.dumps({'key': 'rate', 'value': 'express'})))
        builder.row(InlineKeyboardButton(text="Экспресс +30", callback_data=json.dumps({'key': 'rate', 'value': 'express30'})))
        builder.row(InlineKeyboardButton(text="Экспресс +60", callback_data=json.dumps({'key': 'rate', 'value':'express60'})))
        builder.row(InlineKeyboardButton(text="4 часа", callback_data=json.dumps({'key': 'rate', 'value':'four_hours'})))

        return builder
    
    
    @staticmethod
    async def phone_access_request() -> ReplyKeyboardBuilder:
        """
        Returns:
            ReplyKeyboardBuilder: Клавиатура с кнопкой отправки своего контакта
        """
        builder = ReplyKeyboardBuilder()
        
        builder.row(KeyboardButton(text="Отправить свой номер телефона", request_contact=True))
        
        return builder
    
    
    @staticmethod
    async def delete_meeting_button(meeting: CreatedConference) -> InlineKeyboardBuilder:
        """
        Args:
            meeting (CreatedConference): Строка с данными о конференции

        Returns:
            InlineKeyboardBuilder: Клавиатура с кнопкой для удаления конференции
        """
        builder = InlineKeyboardBuilder(
            markup=[
                [
                    InlineKeyboardButton(text=f'Удалить {meeting.name}', callback_data=json.dumps({'id_meeting': meeting.id}))
                ]
            ]
        )
        return builder
    