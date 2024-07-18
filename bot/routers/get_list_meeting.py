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
from data_storage.states import GetListMeetingStates
from data_storage.keyboards import Keyboards
from data_storage.emojis_chats import *
from database.mongodb.check_data import CheckData
from exeptions import *


helper = MinorOperations()
bank_of_keys = Keyboards()
db = Interaction()
router = Router()
emojis = Emojis()

@router.message(Command(commands=['meetings']))
@router.callback_query(F.data == "get_list_meeting")
async def start_create_new_meeting(event: Union[Message, CallbackQuery], state: FSMContext) -> None:
    await state.clear()
    """
    Старт заполнения данных
    """
    keyboard = await bank_of_keys.ultimate_keyboard('room')
    if isinstance(event, Message):
        await event.answer(f'Выбрано: {emojis.SUCCESS} Ознакомиться с бронями преговорных комнат')
        await event.answer("Выберите переговорную комнату", reply_markup=keyboard)
    elif isinstance(event, CallbackQuery):
        await event.message.answer(f'Выбрано: {emojis.SUCCESS} Ознакомиться с бронями преговорных комнат')
        await event.message.answer("Выберите переговорную комнату", reply_markup=keyboard)
    
    await state.set_state(GetListMeetingStates.get_room)
    with suppress(TypeError):
        await event.answer()
        

@router.message(F.text, StateFilter(GetListMeetingStates.get_room))
async def get_zoom(message: Message, state: FSMContext) -> None:
    """
    Получение адреса переговорной
    """
    control = CheckData(message.from_user.id)
    keyboard = await bank_of_keys.calendar_keyboard()
    try:
      response = await control.check_room_for_accuracy(message.text)
      
      await message.answer(f"Выбрана комната для переговоров по адресу: <b>{response}</b>", ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
      await message.answer("Введите дату для которой хотите посмотреть запланированные конференции:", reply_markup=keyboard.as_markup(resize_keyboard=True))
      
      await state.set_state(GetListMeetingStates.get_date_and_get_planned_meetings)
    except DataInputError:
      await message.answer("Введены данные неправильного формата, пожалуйста выберите адрес переговорной комнаты используя клавиатуру ниже" )
      

@router.message(F.text, StateFilter(GetListMeetingStates.get_date_and_get_planned_meetings))
async def get_date_and_list_meetings(message: Message, state: FSMContext) -> None:
    """
    Получение даты и вывод запланированных на нее конференций
    """
    control = CheckData(message.from_user.id)
    keyboard = await bank_of_keys.ultimate_keyboard('room')
    
    try:
        await control.checking_the_date_for_accuracy(message.text)
        await message.answer("Получение данных...", reply_markup=ReplyKeyboardRemove())
        meetings_info = await db.get_list_meetings_for_all(message.from_user.id)
        if meetings_info:
            for meeting in meetings_info:

                meeting_name = meeting['name']
                choosen_room = meeting['choosen_room']
                date = meeting['date']
                start_time = meeting['start_time']
                date_start_time = datetime.strftime(datetime.strptime(date+start_time, '%Y-%m-%d%H:%M'), '%d.%m.%Y %H:%M')
                duration_meeting = meeting['duration_meeting']
                """
                Выводим ответ в зависимости от типа обработчика
                """
                await message.answer(f'<b>Название:</b> {meeting_name}\n<b>Офис:</b> {choosen_room}\n<b>Дата и время начала:</b> {date_start_time}\n<b>Продолжительность:</b> {int(duration_meeting * 60)} минут', ParseMode.HTML)

        else:
            await message.answer(f'{emojis.ALLERT} На выбранную дату нет забронированных конференций', reply_markup=ReplyKeyboardRemove())
            
        await state.clear()  

    except DataInputError:
          await message.answer("Кажется вы ввели данные в неправильном формате, попробуйте еще раз!")
          
        
