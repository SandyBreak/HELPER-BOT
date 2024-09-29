# -*- coding: UTF-8 -*-

import json

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from aiogram.enums import ParseMode
from aiogram import Router, F, Bot

from models.states import DeleteMeetingStates
from models.keyboards.user_keyboards import UserKeyboards
from models.emojis import Emojis

from services.postgres.rezervation_meeting_service import RezervationMeetingService

router = Router()


@router.callback_query(F.data == "cancel_rezervation_meeting_room")
async def start_create_new_meeting(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await state.clear()
    """
    Получаем список конференций
    """
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'{Emojis.SUCCESS} Отменить бронирование переговорной комнаты {Emojis.SUCCESS}')

    meetings_list = await RezervationMeetingService.get_list_meetings_for_user(callback.from_user.id)
    if meetings_list:
        for meeting in meetings_list:
            
            keyboard = await UserKeyboards.delete_meeting_button(meeting)
            await callback.message.answer(f'<b>Название:</b> {meeting.name}\n<b>Офис:</b> {meeting.office}\n<b>Дата и время начала:</b> {(meeting.start_time).strftime("%d.%m.%Y %H:%M")}\n<b>Продолжительность:</b> {int(meeting.duration)} минут\n\n', ParseMode.HTML, reply_markup=keyboard.as_markup(resize_keyboard=True))

    else:
        await callback.message.answer(f'{Emojis.ALLERT} На ваше имя нет забронированных конференций {Emojis.ALLERT}')
            
    await state.set_state(DeleteMeetingStates.delete_room)


@router.callback_query(F.data, StateFilter(DeleteMeetingStates.delete_room))
async def delete_meeting(callback: CallbackQuery, bot: Bot) -> None:
    data = json.loads(callback.data)
    """
    Удаляем конференцию из базы
    """
    if data['id_meeting']:
        await RezervationMeetingService.delete_user_meeting(data['id_meeting'])
    """
    Изменяем текст сообщения
    """
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'{Emojis.SUCCESS} Конференция удалена! {Emojis.SUCCESS}')