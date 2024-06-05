# -*- coding: UTF-8 -*-

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import KeyboardButton, InlineKeyboardBuilder


class Keyboards:
    def __init__(self) -> None:
        pass
    
    
    async def phone_access_request(self):
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Предоставить номер телефона", request_contact=True)
                ]
            ],
            resize_keyboard=True, one_time_keyboard=True
            )
        return keyboard


    async def possibilities_keyboard(self):
        builder = InlineKeyboardBuilder(
            markup=[
                [
                    InlineKeyboardButton(text="Заказать такси", callback_data='order_taxi')
                ],
                [
                     InlineKeyboardButton(text="Заказать пропуск", callback_data='order_pass')
                ],
                [
                     InlineKeyboardButton(text="Заказать визитку", callback_data='order_cutaway')
                ],
                [
                     InlineKeyboardButton(text="Заказать канцелярию", callback_data='order_office')
                ],
                [
                     InlineKeyboardButton(text="Заказать/отремонтировать технику", callback_data='order_technic')
                ],
                [
                     InlineKeyboardButton(text="Получить доступ", callback_data='gain_acces')
                ],
                [
                     InlineKeyboardButton(text="Найти контакты сотрудника", callback_data='find_contact')
                ],
                [
                     InlineKeyboardButton(text="Забронировать переговорную комнату", callback_data='book_meeting_room')
                ],
                [
                    InlineKeyboardButton(text="Создать конференцию в ZOOM", callback_data='create_zoom_meeting')
                ]
            ],
        )
        return builder
    
    
    async def type_break_keyboard(self):
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Поломка 1")
                ],
                [
                    KeyboardButton(text="Поломка 2")
                ]
            ],
            resize_keyboard=True, one_time_keyboard=True
        )
        return keyboard
    
    
    async def type_office_keyboard(self):
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Империя")
                ],
                [
                    KeyboardButton(text="Таганка")
                ]
            ],
            resize_keyboard=True, one_time_keyboard=True
        )
        return keyboard