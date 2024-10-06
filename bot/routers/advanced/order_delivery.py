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
        
        delivery_rate_keyboard = await UserKeyboards.delivery_rate_keyboard()
        delete_message = await callback.message.answer(f'Выберите тариф доставки', reply_markup=delivery_rate_keyboard.as_markup(resize_keyboard=True))
        
        await state.set_state(OrderDelivery.choose_rate)
    except UserNotRegError:
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"{Emojis.ALLERT} Вы не зарегистрированы! {Emojis.ALLERT}\nДля регистрации введите команду /start")
    
    await state.update_data(message_id=delete_message.message_id)

@router.callback_query(F.data, StateFilter(OrderDelivery.choose_rate))
async def choose_rate(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    if data['key'] == 'back':
        office_keyboard = await UserKeyboards.ultimate_keyboard('office')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"Выберите офис в котором вы находитесь:", reply_markup=office_keyboard.as_markup(resize_keyboard=True))
        
        await state.set_state(OrderDelivery.get_office)
    elif data['key'] == 'rate':
        #if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=callback.message.chat.id, message_id=delete_message_id)
        await CreateEventService.save_data(callback.from_user.id, 'delivery_rate', data['value'])
        
        back_keyboard = await UserKeyboards.ultimate_keyboard('back')
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'Введите адрес отправки (Место откуда нужно забрать заказ):', reply_markup=back_keyboard.as_markup(resize_keyboard=True))
        
        await state.set_state(OrderDelivery.get_departure_address)
    
    await state.update_data(message_id=delete_message.message_id)
        


  
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
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"Введите адрес отправки (Откуда нужно забрать заказ):", reply_markup=back_keyboard.as_markup(resize_keyboard=True))
        
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
        await state.set_state(OrderDelivery.get_destination_address)
        
@router.message(F.text, StateFilter(OrderDelivery.get_info))
async def get_fio_recipient(message: Message, state: FSMContext, bot: Bot) -> None:
    if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    await CreateEventService.save_data(message.from_user.id, 'info', message.text)
    
    customer_phone_keyboard = await UserKeyboards.phone_access_request()
    delete_message = await message.answer(f'Введите телефон или отправьте контакт человека у которого нужно забрать заказ, если заказ нужно забрать у вас отправьте свой свой номер телефона, нажав на кнопку ниже {Emojis.POINTER}:', reply_markup=customer_phone_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
        
    await state.update_data(message_id=delete_message.message_id)
    await state.set_state(OrderDelivery.get_customer_phone)
        



@router.message(F.text, StateFilter(OrderDelivery.get_customer_phone))
@router.message(F.contact, StateFilter(OrderDelivery.get_customer_phone))
async def get_info(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.text == 'Вернуться назад':
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
        back_keyboard = await UserKeyboards.ultimate_keyboard('back')
        delete_message = await message.answer(text=f'Напишите комментарий к доставке', reply_markup=back_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderDelivery.get_info)
    else:
        customer_phone = message.contact.phone_number if message.contact else message.text   
        await CreateEventService.save_data(message.from_user.id, 'customer_phone', customer_phone)
    
        recipient_phone_keyboard = await UserKeyboards.phone_access_request()
        delete_message = await message.answer(f'Введите телефон или отправьте контакт человека которому нужно доставить заказ, если заказ нужно доставить вам отправьте свой свой номер телефона, нажав на кнопку ниже {Emojis.POINTER}:', reply_markup=recipient_phone_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))

        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderDelivery.get_recipient_phone)



        
@router.message(F.text, StateFilter(OrderDelivery.get_recipient_phone))
@router.message(F.contact, StateFilter(OrderDelivery.get_recipient_phone))
async def get_recipient_phone(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.text == 'Вернуться назад':
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
        customer_phone_keyboard = await UserKeyboards.phone_access_request()
        delete_message = await message.answer(f'Введите телефон или отправьте контакт человека у которого нужно забрать заказ, если заказ нужно забрать у вас отправьте свой свой номер телефона, нажав на кнопку ниже {Emojis.POINTER}:', reply_markup=customer_phone_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
     
        await state.set_state(OrderDelivery.get_customer_phone)
    else:
        phone_recipient = message.contact.phone_number if message.contact else message.text    
        await CreateEventService.save_data(message.from_user.id, 'recipient_phone', phone_recipient)
        
        tracking_keyboard = await UserKeyboards.tracking_keyboard()
        delete_message = await message.answer(f'Вам нужно отслеживать заказ? Если ответ Положительный администратор отправит вам ссылку длля отслеживания', reply_markup=tracking_keyboard.as_markup(resize_keyboard=True))

        await state.set_state(OrderDelivery.get_tracking_flag_and_send_order)  
    await state.update_data(message_id=delete_message.message_id)





@router.callback_query(F.data, StateFilter(OrderDelivery.get_tracking_flag_and_send_order))
async def get_info(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = json.loads(callback.data)
    if data['key'] == 'back':
        if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=callback.message.chat.id, message_id=delete_message_id)
        recipient_phone_keyboard = await UserKeyboards.phone_access_request()
        delete_message = await callback.message.answer(f'Введите телефон или отправьте контакт человека которому нужно доставить заказ, если заказ нужно доставить вам отправьте свой свой номер телефона, нажав на кнопку ниже {Emojis.POINTER}:', reply_markup=recipient_phone_keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True))
    
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(OrderDelivery.get_recipient_phone)
    elif data['key'] == 'track':
        try:
            await CreateEventService.save_data(callback.from_user.id, 'tracking_flag', data['value'])
            order_message = await MinorOperations.fill_delivery_event(callback.from_user.id, data['value'])
            if callback.from_user.id == 5890864355:
                message_log = await bot.send_message(AdminChats.BASE, order_message, parse_mode=ParseMode.HTML)
            else:
                message_log = await bot.send_message(AdminChats.ADMIN_ALESYA, order_message, parse_mode=ParseMode.HTML)
            await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'{Emojis.SUCCESS} Запрос на заказ доставки успешно отправлен, при необходимости с вами свяжутся')
            await  CreateEventService.save_created_event(callback.from_user.id)
        except Exception as e:
            message_log = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'{Emojis.FAIL} Произошла какая то ошибка и запрос не отправлен, пожалуйста, свяжитесь с администратором по адресу: @global_aide_bot')
            logging.error(e)
        if message_log: await send_log_message(callback, bot, message_log)
        await state.clear()
    
    
    