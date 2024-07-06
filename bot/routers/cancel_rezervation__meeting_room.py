# -*- coding: UTF-8 -*-

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from contextlib import suppress
from datetime import datetime
from aiogram import Router, F
from typing import Union


from helper_classes.assistant import MinorOperations
from database.mongodb.interaction import Interaction
from data_storage.states import DeleteMeetingStates
from data_storage.keyboards import Keyboards
from data_storage.emojis_chats import *



helper = MinorOperations()
bank_of_keys = Keyboards()
db = Interaction()
router = Router()
emojis = Emojis()

@router.message(Command(commands=['delete']))
@router.callback_query(F.data == "cancel_rezervation_meeting_room")
async def start_create_new_meeting(event: Union[Message, CallbackQuery], state: FSMContext) -> None:
    await state.clear()
    """
    Получаем список конференций
    """
    meetings_info = await db.get_list_meetings(event.from_user.id)
    if meetings_info:
        for meeting in meetings_info:
            
            meeting_name = meeting['name']
            choosen_room = meeting['choosen_room']
            date = meeting['date']
            start_time = meeting['start_time']
            date_start_time = datetime.strftime(datetime.strptime(date+start_time, '%Y-%m-%d%H:%M'), '%d.%m.%Y %H:%M')
            duration_meeting = meeting['duration_meeting']
            
            keyboard = await bank_of_keys.delete_meeting_button(meeting_name, start_time)
            """
            Выводим ответ в зависимости от типа обработчика
            """
            if isinstance(event, Message):
                await event.answer(f'<b>Название:</b> {meeting_name}\n<b>Офис:</b> {choosen_room}\n<b>Дата и время начала:</b> {date_start_time}\n<b>Продолжительность:</b> {int(duration_meeting * 60)} минут', ParseMode.HTML, reply_markup=keyboard.as_markup(resize_keyboard=True))
            elif isinstance(event, CallbackQuery):
                await event.message.answer(f'<b>Название:</b> {meeting_name}\n<b>Офис:</b> {choosen_room}\n<b>Дата и время начала:</b> {date_start_time}\n<b>Продолжительность:</b> {int(duration_meeting * 60)} минут', ParseMode.HTML, reply_markup=keyboard.as_markup(resize_keyboard=True))
    else:
        if isinstance(event, Message):
            await event.answer(f'{emojis.ALLERT} На ваше имя нет забронированных конференций', reply_markup=ReplyKeyboardRemove())
        elif isinstance(event, CallbackQuery):
            await event.message.answer(f'{emojis.ALLERT} На ваше имя нет забронированных конференций', reply_markup=ReplyKeyboardRemove())
            
    await state.set_state(DeleteMeetingStates.delete_room)
    with suppress(TypeError):
        await event.answer()


@router.callback_query(F.data, StateFilter(DeleteMeetingStates.delete_room))
async def delete_meeting(callback: CallbackQuery) -> None:
    deleting_meeting = callback.data.split(',')
    """
    Удаляем конференцию из базы
    """
    await db.delete_user_meeting(deleting_meeting[0], deleting_meeting[1])
    """
    Изменяем текст сообщения
    """
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(f'{emojis.SUCCESS} Конференция удалена!')
        await callback.message.edit_reply_markup(reply_markup=None)
