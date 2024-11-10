# -*- coding: UTF-8 -*-

import logging
import json

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F, Bot, suppress
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.enums import ParseMode

from admin.admin_logs import send_log_message

from models.text_maps import choice_message_map, get_info_message_map, success_message_map
from models.keyboards.user_keyboards import UserKeyboards
from models.states import UniversalEventRouterStates
from models.admin_chats import AdminChats
from models.emojis import Emojis

from services.postgres.create_event_service import CreateEventService
from services.postgres.user_service import UserService

from utils.assistant import MinorOperations

from exceptions.errors import UserNotRegError

router = Router()


@router.callback_query(F.data.in_(["find_contact", "gain_access", "order_cutaway", "order_office", "order_pass", "order_technic"]))
async def start_create_event(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Инициализация запроса
    """
    await callback.answer()
    await state.update_data(type_event=callback.data)
    try:
        await UserService.check_user_exists(callback.from_user.id)

        await CreateEventService.delete_temporary_data(callback.from_user.id)
        await CreateEventService.init_new_event(callback.from_user.id, callback.data)

        office_keyboard = await UserKeyboards.ultimate_keyboard('office')
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'{Emojis.SUCCESS} {choice_message_map[callback.data]} {Emojis.SUCCESS}')
        delete_message = await callback.message.answer(f"Выберите офис в котором вы находитесь:", reply_markup=office_keyboard.as_markup(resize_keyboard=True))

        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(UniversalEventRouterStates.get_office)
    except UserNotRegError:
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"{Emojis.ALLERT} Вы не зарегистрированы! {Emojis.ALLERT}\nДля регистрации введите команду /start")
        await state.update_data(message_id=delete_message.message_id)


@router.callback_query(F.data, StateFilter(UniversalEventRouterStates.get_office))
async def get_info(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Получение офиса
    """
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    
    data = json.loads(callback.data)
    type_event = (await state.get_data()).get('type_event')
    if data['key'] == 'choice':
        await CreateEventService.save_data(callback.from_user.id, 'office', data['value'])
        back_keyboard = await UserKeyboards.ultimate_keyboard('back')
        delete_message = await callback.message.answer(f'{get_info_message_map[type_event]}', reply_markup=back_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(UniversalEventRouterStates.get_info_and_send_order)


@router.callback_query(F.data, StateFilter(UniversalEventRouterStates.get_info_and_send_order))
async def back_to_get_office(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Возврат к получению офиса
    """
    data = json.loads(callback.data)
    if data['key'] == 'back':
        
        office_keyboard = await UserKeyboards.ultimate_keyboard('office')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"Выберите офис в котором вы находитесь:", reply_markup=office_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(UniversalEventRouterStates.get_office)
        
        
@router.message(F.text, StateFilter(UniversalEventRouterStates.get_info_and_send_order))
async def send_data(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получение дополнительной информации к запросу и отправка запроса 
    """
    type_event = (await state.get_data()).get('type_event')
    await CreateEventService.save_data(message.from_user.id, 'info', message.text)
    office = await CreateEventService.get_data(message.from_user.id, 'office')
    order_message = await MinorOperations.fill_simple_event_data(message.from_user.id, office, message.text, type_event)
        
    try:
        if message.from_user.id == 5890864355:
            message_log = await bot.send_message(AdminChats.BASE, order_message, parse_mode=ParseMode.HTML)
        else:
            message_log = await bot.send_message(AdminChats.ADMIN_ALESYA, order_message, parse_mode=ParseMode.HTML)
        with suppress(TelegramBadRequest):
            if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
        await message.answer(f'{Emojis.SUCCESS} Запрос на {success_message_map[type_event]} успешно отправлен, при необходимости с вами свяжутся')
        await  CreateEventService.save_created_event(message.from_user.id)
    except Exception as e:
        message_log = await message.answer(f'{Emojis.FAIL} Произошла какая то ошибка и запрос не отправлен, пожалуйста, свяжитесь с администратором по адресу: @global_aide_bot')
        logging.critical(e)
        
    await state.clear()
    if message_log: await send_log_message(message, bot, message_log)