# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import KeyboardButton, InlineKeyboardBuilder, ReplyKeyboardBuilder
from database.mongodb.interaction import Interaction


db = Interaction()
class Keyboards:
    def __init__(self) -> None:
        pass


    async def ultimate_keyboard(self, type_keyboard: str) -> ReplyKeyboardMarkup:
        """
        Клавиатура выбора переговорной комнаты, адреса местонахождения и кнопки назад для возвращения из состояния именовании конфы к выбору продолжительности конференции
        """
        if type_keyboard == 'room':
            keyboard = ReplyKeyboardMarkup(
                keyboard = [
                    [
                        KeyboardButton(text="Москва-Сити башня \"Империя\"")
                    ],
                    [
                        KeyboardButton(text="Бизнес-центр \"Mosenka-park-towers\"")
                    ]
                ],
                resize_keyboard=True, one_time_keyboard=True
            )
        elif type_keyboard == 'back_to_duration':
            keyboard = ReplyKeyboardMarkup(
                keyboard = [
                    [
                        KeyboardButton(text="Вернуться назад")
                    ]
                ],
                resize_keyboard=True, one_time_keyboard=True
            )     
        return keyboard
    
    
    async def calendar_keyboard(self) -> InlineKeyboardBuilder:
        """
        Клавиатура с календарем
        """ 
        builder = ReplyKeyboardBuilder()
        buttons = []
        builder.row(KeyboardButton(text="Вернуться назад"))

        now = datetime.now()

        current_month = now.month

        builder.row(KeyboardButton(text=datetime.now().strftime('%B')))

        for i in range(0, 5*7*3+int(now.isoweekday())):
            day = now + timedelta(days=i)
            buttons.append(KeyboardButton(text=day.strftime('%d.%m')))

            if day.strftime('%A') == 'Sunday':

                if len(buttons) != 7 and len(buttons) != 0:

                    for a in range(0, 7 - len(buttons)):
                        buttons.insert(0, KeyboardButton(text=f'----'))

                builder.row(*buttons)
                buttons = []
    
            if day.month != current_month:
                if buttons:  # Проверка на пустой список
                    buttons.pop()

                if len(buttons) != 7 and len(buttons) != 0:

                    for a in range(0, 7 - len(buttons)):
                        buttons.append(KeyboardButton(text=f"----"))

                builder.row(*buttons)
                builder.row(KeyboardButton(text=day.strftime('%B')))
                buttons = []
                buttons.append(KeyboardButton(text=day.strftime('%d.%m')))
                current_month = day.month

        if len(buttons) != 7 and len(buttons) != 0:
                    for a in range(0, 7 - len(buttons)):
                        buttons.append(KeyboardButton(text="----"))

        builder.row(*buttons)

        return builder
    
    
    async def start_time_keyboard(self, user_id: int, no_access_intervals: dict) -> ReplyKeyboardBuilder:
        """
        Клавиатура с временем начала конференции
        """
        builder = ReplyKeyboardBuilder()
        buttons = []
        builder.row(KeyboardButton(text="Вернуться назад"))

        entered_date = await db.get_data(user_id, 'date')
        time_slots = []
        start_time = datetime.strptime(entered_date + "09:00", '%Y-%m-%d%H:%M')
        end_time = datetime.strptime(entered_date + "19:00", '%Y-%m-%d%H:%M')

        current_slot_start = start_time

        while current_slot_start < end_time:
            current_slot_end = current_slot_start + timedelta(minutes=30)
            time_slots.append(current_slot_start)
            current_slot_start = current_slot_end

        available_time_slots = []
        response_logs = []

        if no_access_intervals:
          for slot in time_slots:
              for start, end in no_access_intervals:
                  if not(start <= slot < end) and (slot > datetime.now()):
                      response_logs.append('True')
                  else:
                      response_logs.append('False')
              if 'False' in response_logs:
                  response_logs = []
              else:
                  available_time_slots.append(slot)
                  response_logs = []
        else:
          for slot in time_slots:
              if (slot > datetime.now()):
                available_time_slots.append(slot)

        for ctr in range(0, len(available_time_slots)-1, 2):
            buttons.append(KeyboardButton(text=available_time_slots[ctr].strftime('%H:%M')))
            buttons.append(KeyboardButton(text=available_time_slots[ctr+1].strftime('%H:%M')))
            
            builder.row(*buttons)
            buttons=[]

        return builder
    
    
    async def duration_keyboard(self, user_id: int) -> ReplyKeyboardBuilder:
        """
        Клавиатура с длительностью конференции
        """
        builder = ReplyKeyboardBuilder()
        buttons = []
        builder.row(KeyboardButton(text="Вернуться назад"))
        
        start_time = await db.get_data(user_id, 'start_time')
        entered_date = await db.get_data(user_id, 'date')
        illegal_intervals = await db.get_data(user_id, 'illegal_intervals')
    
        start_time = datetime.strptime(entered_date + start_time, '%Y-%m-%d%H:%M')
        end_meeting = datetime.strptime(entered_date + "19:00", '%Y-%m-%d%H:%M')
    
        for start, end in illegal_intervals:
            if (start > start_time):
                end_meeting = start
                break
            
        current_slot_start = start_time
        quantity_buttons = 0
        
        while current_slot_start < end_meeting:
            current_slot_end = current_slot_start + timedelta(minutes=30)
            duration = current_slot_end-start_time
            
            buttons.append(KeyboardButton(text=str(duration)[:-3]))
            
            quantity_buttons+=1
            current_slot_start = current_slot_end
            
            if quantity_buttons == 2:
                builder.row(*buttons)
                buttons = []
                quantity_buttons = 0
        
        builder.row(*buttons)

        return builder
    
    
    async def delete_meeting_button(self, name_meeting: str, start_time: str) -> InlineKeyboardBuilder:
        """
        Инлайн кнопка для удаления клавиатуры
        """
        builder = InlineKeyboardBuilder(
            markup=[
                [
                    InlineKeyboardButton(text=f'Удалить {name_meeting}', callback_data=f'{name_meeting},{start_time}')
                ]
            ]
        )
        return builder
    
    
    async def possibilities_keyboard(self) -> InlineKeyboardBuilder:
        """
        Основная инлайн клавиатура со всеми функциями бота
        """
        builder = InlineKeyboardBuilder(
            markup=[
                [
                    InlineKeyboardButton(text="🚕Заказать такси", callback_data='order_taxi')
                ],
                [
                    InlineKeyboardButton(text="🔑Заказать пропуск", callback_data='order_pass')
                ],
                [
                    InlineKeyboardButton(text="❌Заказать визитку", callback_data='order_cutaway')
                ],
                [
                    InlineKeyboardButton(text="✏️Заказать канцелярию", callback_data='order_office')
                ],
                [
                    InlineKeyboardButton(text="🛠️Заказать/отремонтировать технику", callback_data='order_technic')
                ],
                [
                    InlineKeyboardButton(text="🔓Получить доступ", callback_data='gain_access')
                ],
                [
                    InlineKeyboardButton(text="📱Найти контакты сотрудника", callback_data='find_contact')
                ],
                [
                    InlineKeyboardButton(text="🗓️Забронировать переговорную комнату", callback_data='rezervation_meeting_room')
                ],
                [
                    InlineKeyboardButton(text="❌Отменить бронь переговорной комнаты", callback_data='cancel_rezervation_meeting_room')
                ],
                [
                    InlineKeyboardButton(text="🔵Создать конференцию в ZOOM", callback_data='create_zoom_meeting')
                ]
            ]
        )
        return builder
    
    
    async def breaks_keyboard(self) -> ReplyKeyboardMarkup:
        """
        Клавиатура с типами поломок
        """
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Принтер")
                ],
                [
                    KeyboardButton(text="Ноутбук")
                ],
                [
                    KeyboardButton(text="Комплюктер")
                ]
            ],
            resize_keyboard=True, one_time_keyboard=True
        )
        
        return keyboard
    
