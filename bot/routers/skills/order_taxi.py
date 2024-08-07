# -*- coding: UTF-8 -*-

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, Contact
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.enums import ParseMode
from aiogram import Router, F, Bot
from datetime import datetime
import logging


from database.mongodb.interaction import Interaction
from helper_classes.assistant import MinorOperations
from data_storage.keyboards import Keyboards
from data_storage.states import OrderTaxi
from data_storage.emojis_chats import *
from exeptions import *


helper = MinorOperations()
bank_of_keys = Keyboards()
mongodb_interface = Interaction()
chat_name = ChatNames()
router = Router()
emojis =Emojis()



@router.callback_query(F.data == "order_taxi")
async def enter_fio_employee(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(f'Выбрано: {emojis.SUCCESS} Заказать такси')
    await callback.message.answer(f'Введите ФИО человека для которого нужно заказать такси', reply_markup=ReplyKeyboardRemove())    
    await callback.answer()
    
    await state.set_state(OrderTaxi.get_fio_customer)


@router.message(F.text, StateFilter(OrderTaxi.get_fio_customer))
async def enter_fio(message: Message, state: FSMContext) -> None:
    filter_by_id = {'users.tg_id': message.from_user.id}
    update = {'$set': {'users.$.secondary_data': message.text}}
    await mongodb_interface.update_data(filter_by_id, update)
    
    await message.answer(f'Введите адреса отправки и назначения')
    
    await state.set_state(OrderTaxi.enter_adress)


@router.message(F.text, StateFilter(OrderTaxi.enter_adress))
async def enter_adress(message: Message, state: FSMContext) -> None:
    filter_by_id = {'users.tg_id': message.from_user.id}
    update = {'$set': {'users.$.taxi_adreses': message.text}}
    await mongodb_interface.update_data(filter_by_id, update)
    rates_keyborad = await bank_of_keys.taxi_rate_keyboard()
    await message.answer(f'Выберите тариф такси', reply_markup=rates_keyborad)
    
    await state.set_state(OrderTaxi.choose_rate)


@router.message(F.text, StateFilter(OrderTaxi.choose_rate))
async def enter_rate(message: Message, state: FSMContext) -> None:
    rates_keyborad = await bank_of_keys.taxi_rate_keyboard()
    if message.text not in ['Эконом','Комфорт', 'Комфорт +']:
        await message.answer(f'Пожалуста выберите тариф использовав предложенную клавиатуру ниже {emojis.POINTER}', reply_markup=rates_keyborad)    
    else:
        filter_by_id = {'users.tg_id': message.from_user.id}
        update = {'$set': {'users.$.taxi_rate': message.text}}
        await mongodb_interface.update_data(filter_by_id, update)
        phone_access_keyboard = await bank_of_keys.phone_access_request()
        await message.answer(f'Отправьте контакт человека которому нужно заказать такси, либо напишите его номер вручную. Если такси нужно вам, то можете отправить свой контакт, нажав на кнопку ниже {emojis.POINTER}', reply_markup=phone_access_keyboard)
        
        await state.set_state(OrderTaxi.get_phone_and_send_order)
    
@router.message(F.text, StateFilter(OrderTaxi.get_phone_and_send_order))
@router.message(F.contact, StateFilter(OrderTaxi.get_phone_and_send_order))
async def send_data(message: Message, state: FSMContext, bot: Bot) -> None:
    fio_customer = await mongodb_interface.get_data(message.from_user.id, 'secondary_data')
    adress = await mongodb_interface.get_data(message.from_user.id, 'taxi_adreses')
    taxi_rate = await mongodb_interface.get_data(message.from_user.id, 'taxi_rate')
    if message.contact:
        order_message = await helper.fill_taxi_or_delivery_event(message.from_user.full_name, message.from_user.username, adress, fio_customer, taxi_rate, message.contact.phone_number, 0)
    elif message.text:
        order_message = await helper.fill_taxi_or_delivery_event(message.from_user.full_name, message.from_user.username, adress, fio_customer, taxi_rate, message.text, 0)
        
    success_flag = 0
    
    try:
        await bot.send_message('@requests_bot_nbc', order_message, parse_mode=ParseMode.HTML)
        #await bot.send_message(chat_name.ADMIN_ALESYA, order_message, parse_mode=ParseMode.HTML)
        success_flag = 1
    except Exception as e:
        await bot.send_message(chat_name.ADMIN_VSS, f'Ошибка отправки данных пользователю! ID: {message.from_user.id}\nАдрес: {message.from_user.username}\nОшибка:{e}', parse_mode=ParseMode.HTML)
        logging.error(e)
        
    if success_flag:
        await message.answer(f'{emojis.SUCCESS} Запрос на заказ такси успешно отправлен, при необходимости с вами свяжутся', reply_markup=ReplyKeyboardRemove())
        await  mongodb_interface.document_the_event('order_taxi', datetime.now().strftime("%d-%m-%Y %H:%M"), message.text, message.from_user.full_name, message.from_user.username, order_message)
    else:
        await message.answer(f'{emojis.FAIL} Произошла какая то ошибка и запрос не отправлен, пожалуйста, свяжитесь с администратором по адресу: @velikiy_ss', reply_markup=ReplyKeyboardRemove())
    
    await state.clear()