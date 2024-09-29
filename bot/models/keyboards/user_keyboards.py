# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import KeyboardButton, InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import Optional
from models.table_models.created_conference import CreatedConference
import json

class UserKeyboards:
    def __init__(self) -> None:
        pass

    @staticmethod
    async def ultimate_keyboard(type_keyboard: Optional[str] = None) -> InlineKeyboardBuilder:
        """
        Клавиатура выбора переговорной комнаты, адреса местонахождения и кнопки назад для возвращения из состояния именовании конфы к выбору продолжительности конференции
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
        Основная инлайн клавиатура со всеми функциями бота
        """
        builder = InlineKeyboardBuilder(
            markup=[
                [
                    InlineKeyboardButton(text="🚕 Заказать такси", callback_data='order_taxi')
                ],
                [
                    InlineKeyboardButton(text="🚚 Заказать доставку", callback_data='order_delivery')
                ],
                [
                    InlineKeyboardButton(text="🔑 Заказать пропуск", callback_data='order_pass')
                ],
                [
                    InlineKeyboardButton(text="📇 Заказать визитку", callback_data='order_cutaway')
                ],
                [
                    InlineKeyboardButton(text="✏️ Заказать канцелярию", callback_data='order_office')
                ],
                [
                    InlineKeyboardButton(text="🛠️ Заказать/отремонтировать технику", callback_data='order_technic')
                ],
                [
                    InlineKeyboardButton(text="🔓 Получить доступ", callback_data='gain_access')
                ],
                [
                    InlineKeyboardButton(text="📱 Найти контакты сотрудника", callback_data='find_contact')
                ],
                [
                    InlineKeyboardButton(text="🗓️ Забронировать переговорную комнату", callback_data='rezervation_meeting_room')
                ],
                [
                    InlineKeyboardButton(text="🕗 Ознакомиться с бронями преговорных комнат", callback_data='get_list_meeting')
                ],
                [
                    InlineKeyboardButton(text="❌ Отменить бронь переговорной комнаты", callback_data='cancel_rezervation_meeting_room')
                ],
                [
                    InlineKeyboardButton(text="🔵 Создать конференцию в ZOOM", callback_data='create_zoom_meeting')
                ]
            ]
        )
        return builder
    
    
    @staticmethod
    async def recipient_keyboard(type_keyboard: str) -> InlineKeyboardBuilder:
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
        Клавиатура с тарифами такси
        """
        builder = InlineKeyboardBuilder(
            markup= [
                [
                InlineKeyboardButton(text="Вернуться назад", callback_data=json.dumps({'key': 'back'}))
                ],
                [
                    InlineKeyboardButton(text="Эконом", callback_data=json.dumps({'key': 'rate', 'value': 'econom'}))
                ],
                [
                    InlineKeyboardButton(text="Комфорт", callback_data=json.dumps({'key': 'rate', 'value': 'comfort'}))
                ],
                [
                    InlineKeyboardButton(text="Комфорт +", callback_data=json.dumps({'key': 'rate', 'value':'comfort_plus'}))
                ]
            ]
        )
        
        return builder
    
    
    @staticmethod
    async def delivery_rate_keyboard() -> InlineKeyboardBuilder:
        """
        Клавиатура с тарифами доставки
        """
        builder = InlineKeyboardBuilder(
            markup= [
                [
                    InlineKeyboardButton(text="Вернуться назад", callback_data=json.dumps({'key': 'back'}))
                ],
                [
                    InlineKeyboardButton(text="Экспресс", callback_data=json.dumps({'key': 'rate', 'value': 'express'}))
                ],
                [
                    InlineKeyboardButton(text="Экспресс +30", callback_data=json.dumps({'key': 'rate', 'value': 'express30'}))
                ],
                [
                    InlineKeyboardButton(text="Экспресс +60", callback_data=json.dumps({'key': 'rate', 'value':'express60'}))
                ],
                [
                    InlineKeyboardButton(text="4 часа", callback_data=json.dumps({'key': 'rate', 'value':'four_hours'}))
                ]
            ]
        )
        
        return builder
    
    
    @staticmethod
    async def phone_access_request() -> ReplyKeyboardBuilder:
        builder = ReplyKeyboardBuilder(
            markup=[
                [
                    KeyboardButton(text="Отправить свой номер телефона", request_contact=True)
                ]
            ]
            )
        return builder
    
    @staticmethod
    async def delete_meeting_button(meeting: CreatedConference) -> InlineKeyboardBuilder:
        """
        Инлайн кнопка для удаления конференции
        """
        builder = InlineKeyboardBuilder(
            markup=[
                [
                    InlineKeyboardButton(text=f'Удалить {meeting.name}', callback_data=json.dumps({'id_meeting': meeting.id}))
                ]
            ]
        )
        return builder
    