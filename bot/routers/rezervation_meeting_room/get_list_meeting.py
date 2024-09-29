# -*- coding: UTF-8 -*-

import json

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from aiogram.enums import ParseMode
from aiogram import Router, F, Bot

from admin.admin_logs import send_log_message

from models.keyboards.create_meeting_keyboards import CreateMeeteingKeyboards
from models.keyboards.user_keyboards import UserKeyboards
from models.states import GetListMeetingStates
from models.emojis import Emojis

from services.postgres.rezervation_meeting_service import RezervationMeetingService

from utils.rezervation_meeting_data_validator import CheckData

router = Router()


@router.callback_query(F.data == "get_list_meeting")
async def start_create_new_meeting(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Старт заполнения данных
    """
    await state.clear()
    ultimate_keyboard = await UserKeyboards.ultimate_keyboard('office')
    
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'{Emojis.SUCCESS} Ознакомиться с бронями преговорных комнат {Emojis.SUCCESS}')
    delete_message = await callback.message.answer("Выберите переговорную комнату", reply_markup=ultimate_keyboard.as_markup(resize_keyboard=True))
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(GetListMeetingStates.get_office)
        

@router.callback_query(F.data, StateFilter(GetListMeetingStates.get_office))
async def get_zoom(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Получение адреса переговорной
    """
    data = json.loads(callback.data)
    if data['key'] == 'choice':
        entered_office = await CheckData(callback.from_user.id).check_room_for_accuracy(data['value'])
        
        calendar_keyboard = await CreateMeeteingKeyboards.calendar_keyboard(0)
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'Выбрана комната для переговоров по адресу: <b>{entered_office}</b> Выберите дату для которой хотите посмотреть запланированные конференции:', reply_markup=calendar_keyboard.as_markup(resize_keyboard=True), parse_mode=ParseMode.HTML)

        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(GetListMeetingStates.get_date_and_get_planned_meetings)
    else:
        await callback.message.answer("Введены данные неправильного формата!" )
      

@router.callback_query(F.data, StateFilter(GetListMeetingStates.get_date_and_get_planned_meetings))
async def get_date_and_list_meetings(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Получение даты и вывод запланированных на нее конференций
    """
    data = json.loads(callback.data)
    message_log = False
    
    if data['key'] == 'month_shift':
        calendar_keyboard = await CreateMeeteingKeyboards.calendar_keyboard(data['value'])
        await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=calendar_keyboard.as_markup(resize_keyboard=True))
    
    elif data['key'] == 'date':
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='⏳Получение данных...')
        entered_date = await CheckData(callback.from_user.id).checking_the_date_for_accuracy(data['value'])
        
        office = await RezervationMeetingService.get_data(callback.from_user.id, 'office')
        list_meetings = await RezervationMeetingService.get_list_meetings_for_all(entered_date, office)
        if list_meetings:
            list_meetings_message = f'Брони на {entered_date.strftime("%d.%m.%Y")}\n\n'
            for meeting in list_meetings:
                list_meetings_message += f'<b>Название:</b> {meeting.name}\n<b>Офис:</b> {meeting.office}\n<b>Дата и время начала:</b> {(meeting.start_time).strftime("%d.%m.%Y %H:%M")}\n<b>Продолжительность:</b> {int(meeting.duration)} минут\n\n'
                await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'{list_meetings_message}', parse_mode=ParseMode.HTML)
        else:
            await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'{Emojis.ALLERT} На выбранную дату нет броней')
    else:
        message_log = await callback.message.answer("Кажется вы нажали не ту кнопку, попробуйте еще раз!")
        await send_log_message(callback, bot, message_log)
        
    await state.clear()
          
        
