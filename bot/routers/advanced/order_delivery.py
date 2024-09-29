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
from models.states import OrderDelivery
from models.emojis import Emojis
from models.admin_chats import AdminChats

from services.postgres.user_service import UserService
from services.postgres.create_event_service import CreateEventService

from utils.assistant import MinorOperations

from exceptions.errors import *

router = Router()


@router.callback_query(F.data == "order_delivery")
async def start_order_delivery(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await callback.answer()
    try:
        await UserService.check_user_exists(callback.from_user.id)
        await CreateEventService.delete_temporary_data(callback.from_user.id)
        await CreateEventService.init_new_event(callback.from_user.id, callback.data)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'{Emojis.SUCCESS} Заказать доставку {Emojis.SUCCESS}')
        
        office_keyboard = await UserKeyboards.ultimate_keyboard('office')
        delete_message = await callback.message.answer(text=f"Выберите офис в котором вы находитесь:", reply_markup=office_keyboard.as_markup(resize_keyboard=True))

        
        await state.set_state(OrderDelivery.get_office)
    except UserNotRegError:
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"{Emojis.ALLERT} Вы не зарегистрированы! {Emojis.ALLERT}\nДля регистрации введите команду /start")
    
    await state.update_data(message_id=delete_message.message_id)

    
@router.callback_query(F.data, StateFilter(OrderDelivery.get_office))
async def get_office(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    
    data = json.loads(callback.data)
    type_event = (await state.get_data()).get('type_event')
    if data['key'] == 'choice':
        await CreateEventService.save_data(callback.from_user.id, 'office', data['value'])
        delivery_rate_keyboard = await UserKeyboards.delivery_rate_keyboard()
        delete_message = await callback.message.answer(f'Выберите тариф доставки', reply_markup=delivery_rate_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderDelivery.choose_rate)
        

@router.callback_query(F.data, StateFilter(OrderDelivery.choose_rate))
async def choose_rate(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    if data['key'] == 'back':
        office_keyboard = await UserKeyboards.ultimate_keyboard('office')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"Выберите офис в котором вы находитесь:", reply_markup=office_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderDelivery.get_office)
    elif data['key'] == 'rate':
        #if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=callback.message.chat.id, message_id=delete_message_id)
        await CreateEventService.save_data(callback.from_user.id, 'delivery_rate', data['value'])
        
        back_keyboard = await UserKeyboards.ultimate_keyboard('back')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'Введите адрес отправки (Место откуда нужно забрать заказ):', reply_markup=back_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderDelivery.get_departure_address)
        


  
@router.callback_query(F.data, StateFilter(OrderDelivery.get_departure_address))
async def get_departure_address(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    if data['key'] == 'back':
        delivery_rate_keyboard = await UserKeyboards.delivery_rate_keyboard()
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'Выберите тариф доставки', reply_markup=delivery_rate_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderDelivery.choose_rate)
        
@router.message(F.text, StateFilter(OrderDelivery.get_departure_address))
async def get_departure_address(message: Message, state: FSMContext, bot: Bot) -> None:
    if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    await CreateEventService.save_data(message.from_user.id, 'departure_address', message.text)
    back_keyboard = await UserKeyboards.ultimate_keyboard('back')
    delete_message = await message.answer(f'Введите адрес назначения (Куда нужно доставить заказ):', reply_markup=back_keyboard.as_markup(resize_keyboard=True))
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(OrderDelivery.get_destination_address)      
        
       
       
        
@router.callback_query(F.data, StateFilter(OrderDelivery.get_destination_address))
async def get_destination_address(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    if data['key'] == 'back':
        back_keyboard = await UserKeyboards.ultimate_keyboard('back')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"Введите адрес отправки (Место откуда начнется поездка):", reply_markup=back_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderDelivery.get_departure_address)
              
@router.message(F.text, StateFilter(OrderDelivery.get_destination_address))
async def get_destination_address(message: Message, state: FSMContext, bot: Bot) -> None:
    if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    await CreateEventService.save_data(message.from_user.id, 'destination_address', message.text)
    back_keyboard = await UserKeyboards.ultimate_keyboard('back')
    delete_message = await message.answer(f'Напишите комментарий к доставке', reply_markup=back_keyboard.as_markup(resize_keyboard=True))
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(OrderDelivery.get_info)
        
        
        
        
@router.callback_query(F.data, StateFilter(OrderDelivery.get_info))
async def get_fio_recipient(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    if data['key'] == 'back':
        back_keyboard = await UserKeyboards.ultimate_keyboard('back')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"Введите адрес назначения (Куда нужно доставить заказ):", reply_markup=back_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderDelivery.get_departure_address)
        
@router.message(F.text, StateFilter(OrderDelivery.get_info))
async def get_fio_recipient(message: Message, state: FSMContext, bot: Bot) -> None:
    if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    await CreateEventService.save_data(message.from_user.id, 'info', message.text)
    
    recipient_keyboard = await UserKeyboards.recipient_keyboard('delivery')
    delete_message = await message.answer(f'Введите ФИО человека которому нужно доставить заказ:', reply_markup=recipient_keyboard.as_markup(resize_keyboard=True))
        
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(OrderDelivery.get_fio_recipient)




@router.callback_query(F.data, StateFilter(OrderDelivery.get_fio_recipient))
async def get_info(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    print(1)
    if data['key'] == 'back':
        back_keyboard = await UserKeyboards.ultimate_keyboard('back')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'Напишите комментарий к доставке', reply_markup=back_keyboard.as_markup(resize_keyboard=True))
        await state.set_state(OrderDelivery.get_info)
    elif data['key'] == 'recipient':
        user_data = await UserService.get_user_data(callback.from_user.id)
        await CreateEventService.save_data(callback.from_user.id, 'recipient_fio', user_data.fio)
        await CreateEventService.save_data(callback.from_user.id, 'customer_fio', user_data.fio)
        
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=callback.message.chat.id, message_id=delete_message_id)
        phone_access_keyboard = await UserKeyboards.phone_access_request()
        delete_message = await callback.message.answer(f'Отправьте свой свой номер телефона, нажав на кнопку ниже {Emojis.POINTER} или напишите его вручную', reply_markup=phone_access_keyboard.as_markup(resize_keyboard=True))
        
        await state.set_state(OrderDelivery.get_customer_phone_and_send_order)
    await state.update_data(message_id=delete_message.message_id)

@router.message(F.text, StateFilter(OrderDelivery.get_fio_recipient))
async def get_info(message: Message, state: FSMContext, bot: Bot) -> None:
    if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    user_data = await UserService.get_user_data(message.from_user.id)
    await CreateEventService.save_data(message.from_user.id, 'recipient_fio', message.text)
    await CreateEventService.save_data(message.from_user.id, 'customer_fio', user_data.fio)
    delete_message = await message.answer(f'Отправьте контакт человека которому нужно доставить заказ, либо напишите его номер вручную.')
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(OrderDelivery.get_recipient_phone)
    
    
@router.message(F.text, StateFilter(OrderDelivery.get_recipient_phone))
@router.message(F.contact, StateFilter(OrderDelivery.get_recipient_phone))
async def get_recipient_phone(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.contact:
        phone_recipient = message.contact.phone_number
    elif message.text:
        phone_recipient = message.text    
    await CreateEventService.save_data(message.from_user.id, 'recipient_phone', phone_recipient)
    phone_access_keyboard = await UserKeyboards.phone_access_request()
    delete_message = await message.answer(f'Отправьте свой свой номер телефона, нажав на кнопку ниже {Emojis.POINTER} или напишите его вручную', reply_markup=phone_access_keyboard.as_markup(resize_keyboard=True))
    
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(OrderDelivery.get_customer_phone_and_send_order)  

@router.message(F.text, StateFilter(OrderDelivery.get_customer_phone_and_send_order))
@router.message(F.contact, StateFilter(OrderDelivery.get_customer_phone_and_send_order))
async def send_data(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.contact:
        customer_phone = message.contact.phone_number
    elif message.text:
        customer_phone = message.text
    if await CreateEventService.get_data(message.from_user.id, 'recipient_fio') == await CreateEventService.get_data(message.from_user.id, 'customer_fio'):
        await CreateEventService.save_data(message.from_user.id, 'recipient_phone', customer_phone)    
    await CreateEventService.save_data(message.from_user.id, 'customer_phone', customer_phone)
    order_message = await MinorOperations.fill_delivery_event(message.from_user.id, customer_phone)
    
    try:
        await bot.send_message(AdminChats.ADMIN_ALESYA, order_message, parse_mode=ParseMode.HTML)
        message_log = await message.answer(f'{Emojis.SUCCESS} Запрос на заказ доставки успешно отправлен, при необходимости с вами свяжутся', reply_markup=ReplyKeyboardRemove())
        await  CreateEventService.save_created_event(message.from_user.id)
    except Exception as e:
        message_log = await message.answer(f'{Emojis.FAIL} Произошла какая то ошибка и запрос не отправлен, пожалуйста, свяжитесь с администратором по адресу: @velikiy_ss', reply_markup=ReplyKeyboardRemove())
        logging.error(e)
    if message_log: await send_log_message(message, bot, message_log)
    await state.clear()
    
    
    