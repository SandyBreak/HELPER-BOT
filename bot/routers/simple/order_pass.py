# -*- coding: UTF-8 -*-

import logging
import json

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.enums import ParseMode
from aiogram import Router, F, Bot

from models.keyboards.user_keyboards import UserKeyboards
from models.states import FindContact
from models.admin_chats import AdminChats
from models.emojis import Emojis

from services.postgres.create_event_service import CreateEventService
from services.postgres.user_service import UserService

from utils.meeting_data_validator import CheckData
from utils.assistant import MinorOperations

from exceptions.errors import *

router = Router()


@router.callback_query(F.data == "order_pass")
async def enter_office(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await callback.answer()
    await UserService.init_user(callback.from_user.id, callback.from_user.username, callback.from_user.full_name)
    await CreateEventService.delete_temporary_data(callback.from_user.id)
    await CreateEventService.init_new_event(callback.from_user.id, 'order_pass')
    
    office_keyboard = await UserKeyboards.ultimate_keyboard('room')
    delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"{Emojis.SUCCESS} Заказать пропуск {Emojis.SUCCESS}\nВыберите офис в котором вы находитесь:", reply_markup=office_keyboard.as_markup(resize_keyboard=True))

    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(FindContact.get_info)


@router.callback_query(F.data, StateFilter(FindContact.get_info))
async def enter_fio_employee(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    
    data = json.loads(callback.data)
    
    if data['key'] == 'choice':
        await CheckData(callback.from_user.id).check_room_for_accuracy(data['value'])
        delete_message = await callback.message.answer(f'Введите ФИО человека для которого нужно заказать пропуск', reply_markup=ReplyKeyboardRemove())
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(FindContact.send_order)

        
        
@router.message(F.text, StateFilter(FindContact.send_order))
async def send_data(message: Message, state: FSMContext, bot: Bot) -> None:

    await CreateEventService.save_data(message.from_user.id, 'info', message.text)
    office = await CreateEventService.get_data(message.from_user.id, 'office')
    order_message = await MinorOperations.fill_simple_event_data(office, message.from_user.full_name, message.from_user.username, message.text, 'order_pass')
        
    try:
        await bot.send_message(AdminChats.ADMIN_ALESYA, order_message, parse_mode=ParseMode.HTML)
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
        await message.answer(f'{Emojis.SUCCESS} Запрос на заказ пропуска успешно отправлен, при необходимости с вами свяжутся')
        await  CreateEventService.save_created_event(message.from_user.id)
    except Exception as e:
        await message.answer(f'{Emojis.FAIL} Произошла какая то ошибка и запрос не отправлен, пожалуйста, свяжитесь с администратором по адресу: @global_aide_bot', reply_markup=ReplyKeyboardRemove())
        await bot.send_message(AdminChats.ADMIN_VSS, f'Ошибка отправки данных пользователя! ID: {message.from_user.id}\nАдрес: {message.from_user.username}\nОшибка:{e}', parse_mode=ParseMode.HTML)
        logging.error(e)
        
    await state.clear()