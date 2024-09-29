# -*- coding: UTF-8 -*-

import logging
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, Contact
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.enums import ParseMode
from aiogram import Router, F, Bot
from datetime import datetime
import json

from admin.admin_logs import send_log_message
from models.keyboards.user_keyboards import UserKeyboards
from models.states import OrderTaxi
from models.emojis import Emojis
from models.admin_chats import AdminChats

from services.postgres.user_service import UserService
from services.postgres.create_event_service import CreateEventService

from utils.assistant import MinorOperations

from exceptions.errors import *

router = Router()


@router.callback_query(F.data == "order_taxi")
async def start_order_taxi(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await callback.answer()
    try:
        await UserService.check_user_exists(callback.from_user.id)
        await CreateEventService.delete_temporary_data(callback.from_user.id)
        await CreateEventService.init_new_event(callback.from_user.id, callback.data)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'{Emojis.SUCCESS} Заказать такси {Emojis.SUCCESS}')
        
        
        taxi_recipient_keyboard = await UserKeyboards.recipient_keyboard('taxi')
        delete_message = await callback.message.answer(text=f"Введите ФИО человека для которого нужно заказать такси:", reply_markup=taxi_recipient_keyboard.as_markup(resize_keyboard=True))

        
        await state.set_state(OrderTaxi.get_fio_recipient)
    except UserNotRegError:
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"{Emojis.ALLERT} Вы не зарегистрированы! {Emojis.ALLERT}\nДля регистрации введите команду /start")
    
    await state.update_data(message_id=delete_message.message_id)

@router.callback_query(F.data, StateFilter(OrderTaxi.get_fio_recipient))
async def get_fio_recipient(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    if data['key'] == 'recipient':
        user_data = await UserService.get_user_data(callback.from_user.id)
        await CreateEventService.save_data(callback.from_user.id, 'recipient_fio', user_data.fio)
        back_keyboard = await UserKeyboards.ultimate_keyboard('back')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'Введите адрес отправки (Место откуда начнется поездка):', reply_markup=back_keyboard.as_markup(resize_keyboard=True))
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderTaxi.get_departure_address)

@router.message(F.text, StateFilter(OrderTaxi.get_fio_recipient))
async def get_fio_recipient(message: Message, state: FSMContext, bot: Bot) -> None:
    if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    await CreateEventService.save_data(message.from_user.id, 'recipient_fio', message.text)
    
    back_keyboard = await UserKeyboards.ultimate_keyboard('back')
    delete_message = await message.answer(f'Введите адрес отправки (Место откуда начнется поездка):', reply_markup=back_keyboard.as_markup(resize_keyboard=True))
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(OrderTaxi.get_departure_address)

@router.callback_query(F.data, StateFilter(OrderTaxi.get_departure_address))
async def get_departure_address(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    if data['key'] == 'back':
        taxi_recipient_keyboard = await UserKeyboards.taxi_recipient_keyboard('taxi')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"Введите ФИО человека для которого нужно заказать такси:", reply_markup=taxi_recipient_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderTaxi.get_fio_recipient)
        
@router.message(F.text, StateFilter(OrderTaxi.get_departure_address))
async def get_departure_address(message: Message, state: FSMContext, bot: Bot) -> None:
    if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    await CreateEventService.save_data(message.from_user.id, 'departure_address', message.text)
    back_keyboard = await UserKeyboards.ultimate_keyboard('back')
    delete_message = await message.answer(f'Введите адрес назначения (Место где поездка завершится):', reply_markup=back_keyboard.as_markup(resize_keyboard=True))
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(OrderTaxi.get_destination_address)


@router.callback_query(F.data, StateFilter(OrderTaxi.get_destination_address))
async def get_destination_address(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    if data['key'] == 'back':
        back_keyboard = await UserKeyboards.ultimate_keyboard('back')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"Введите адрес отправки (Место откуда начнется поездка):", reply_markup=back_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderTaxi.get_departure_address)
        
        
@router.message(F.text, StateFilter(OrderTaxi.get_destination_address))
async def get_destination_address(message: Message, state: FSMContext, bot: Bot) -> None:
    if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    await CreateEventService.save_data(message.from_user.id, 'destination_address', message.text)
    taxi_rate_keyboard = await UserKeyboards.taxi_rate_keyboard()
    delete_message = await message.answer(f'Выберите тариф:', reply_markup=taxi_rate_keyboard.as_markup(resize_keyboard=True))
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(OrderTaxi.choose_rate)
    
    
@router.callback_query(F.data, StateFilter(OrderTaxi.choose_rate))
async def enter_rate(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    if data['key'] == 'back':
        back_keyboard = await UserKeyboards.ultimate_keyboard('back')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"Введите адрес назначения (Место где поездка завершится):", reply_markup=back_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderTaxi.get_destination_address)
    elif data['key'] == 'rate':
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=callback.message.chat.id, message_id=delete_message_id)
        await CreateEventService.save_data(callback.from_user.id, 'taxi_rate', data['value'])
        phone_access_keyboard = await UserKeyboards.phone_access_request()
        delete_message = await callback.message.answer(f'Отправьте контакт человека которому нужно заказать такси, либо напишите его номер вручную. Если такси нужно вам, то можете отправить свой контакт, нажав на кнопку ниже {Emojis.POINTER}', reply_markup=phone_access_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderTaxi.get_phone_and_send_order)
    
@router.message(F.text, StateFilter(OrderTaxi.get_phone_and_send_order))
@router.message(F.contact, StateFilter(OrderTaxi.get_phone_and_send_order))
async def send_data(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.contact:
        recipient_phone = message.contact.phone_number
    elif message.text:
        recipient_phone = message.text
    
    await CreateEventService.save_data(message.from_user.id, 'recipient_phone', recipient_phone)
    order_message = await MinorOperations.fill_taxi_event(message.from_user.id, recipient_phone)
    
    try:
        await bot.send_message(AdminChats.ADMIN_ALESYA, order_message, parse_mode=ParseMode.HTML)
        message_log = await message.answer(f'{Emojis.SUCCESS} Запрос на заказ такси успешно отправлен, при необходимости с вами свяжутся', reply_markup=ReplyKeyboardRemove())
        await  CreateEventService.save_created_event(message.from_user.id)
    except Exception as e:
        message_log = await message.answer(f'{Emojis.FAIL} Произошла какая то ошибка и запрос не отправлен, пожалуйста, свяжитесь с администратором по адресу: @velikiy_ss', reply_markup=ReplyKeyboardRemove())
        logging.error(e)
    if message_log: await send_log_message(message, bot, message_log)
    await state.clear()