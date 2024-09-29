# -*- coding: UTF-8 -*-

import logging
import json

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.enums import ParseMode
from aiogram import Router, F, Bot

from admin.admin_logs import send_log_message
from models.keyboards.user_keyboards import UserKeyboards
from models.states import FindContact
from models.admin_chats import AdminChats
from models.emojis import Emojis
from models.text_maps import choice_message_map, get_info_message_map, success_message_map
from services.postgres.create_event_service import CreateEventService
from services.postgres.user_service import UserService

from utils.meeting_data_validator import CheckData
from utils.assistant import MinorOperations

from exceptions.errors import *

router = Router()


@router.callback_query(F.data.in_(["find_contact", "gain_access", "order_cutaway", "order_office", "order_pass", "order_technic"]))
async def enter_office(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await callback.answer()
    await state.update_data(type_event=callback.data)
    try:
        await UserService.check_user_exists(callback.from_user.id)

        await CreateEventService.delete_temporary_data(callback.from_user.id)
        await CreateEventService.init_new_event(callback.from_user.id, callback.data)

        office_keyboard = await UserKeyboards.ultimate_keyboard('room')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"{Emojis.SUCCESS} {choice_message_map[callback.data]} {Emojis.SUCCESS}\nВыберите офис в котором вы находитесь:", reply_markup=office_keyboard.as_markup(resize_keyboard=True))

        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(FindContact.get_info)
    except UserNotRegError:
        delete_message = await callback.message.answer(f"{Emojis.ALLERT} Вы не зарегистрированы! {Emojis.ALLERT}\nДля регистрации введите команду /start", reply_markup=ReplyKeyboardRemove())
        await state.update_data(message_id=delete_message.message_id)

@router.callback_query(F.data, StateFilter(FindContact.get_info))
async def get_info(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    
    data = json.loads(callback.data)
    type_event = (await state.get_data()).get('type_event')
    if data['key'] == 'choice':
        await CreateEventService.save_data(callback.from_user.id, 'office', data['value'])
        delete_message = await callback.message.answer(f'{get_info_message_map[type_event]}', reply_markup=ReplyKeyboardRemove())
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(FindContact.send_order)

        
        
@router.message(F.text, StateFilter(FindContact.send_order))
async def send_data(message: Message, state: FSMContext, bot: Bot) -> None:
    type_event = (await state.get_data()).get('type_event')
    await CreateEventService.save_data(message.from_user.id, 'info', message.text)
    office = await CreateEventService.get_data(message.from_user.id, 'office')
    order_message = await MinorOperations.fill_simple_event_data(office, message.from_user.full_name, message.from_user.username, message.text, type_event)
        
    try:
        await bot.send_message(AdminChats.ADMIN_ALESYA, order_message, parse_mode=ParseMode.HTML)
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
        message_log = await message.answer(f'{Emojis.SUCCESS} Запрос на {success_message_map[type_event]} успешно отправлен, при необходимости с вами свяжутся')
        await  CreateEventService.save_created_event(message.from_user.id)
    except Exception as e:
        message_log = await message.answer(f'{Emojis.FAIL} Произошла какая то ошибка и запрос не отправлен, пожалуйста, свяжитесь с администратором по адресу: @global_aide_bot', reply_markup=ReplyKeyboardRemove())
        logging.critical(e)
        
    await state.clear()
    if message_log: await send_log_message(message, bot, message_log)