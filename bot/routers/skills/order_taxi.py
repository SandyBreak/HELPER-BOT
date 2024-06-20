# -*- coding: UTF-8 -*-

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.enums import ParseMode
from aiogram import Router, F, Bot
from datetime import datetime
import logging


from database.mongodb.interaction import Interaction
from data_storage.keyboards import Keyboards
from data_storage.states import OrderTaxi
from data_storage.emojis import *


bank_of_keys = Keyboards()
router = Router()
emojis =Emojis()
mongodb = Interaction(
			#user= os.environ.get('MONGO_INITDB_ROOT_USERNAME'),
			#password= os.environ.get('MONGO_INITDB_ROOT_PASSWORD')
		)


@router.callback_query(F.data == "order_taxi")
async def enter_fio(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(f'Выбрано: {emojis.SUCCESS} Заказать такси')
    await callback.message.answer(f'Введите ФИО человека для которого нужно заказать такси', reply_markup=ReplyKeyboardRemove())    
    await callback.answer()
    await state.set_state(OrderTaxi.enter_adress)


@router.message(F.text, StateFilter(OrderTaxi.enter_adress))
async def enter_office(message: Message, state: FSMContext) -> None:
    filter_by_id = {'users.tg_id': message.from_user.id}
    update = {'$set': {'users.$.fio': message.text}}
    await mongodb.update_data(filter_by_id, update)
    
    keyboard = await bank_of_keys.type_office_keyboard()    
    
    await message.answer(f'Введите адреса отправки и назначения', reply_markup=keyboard)
    
    await state.set_state(OrderTaxi.send_order)

        
        
@router.message(F.text, StateFilter(OrderTaxi.send_order))
async def send_data(message: Message, state: FSMContext, bot: Bot) -> None:
    name_order = await mongodb.get_data(message.from_user.id, 'fio')
    order_message = f"""
    Новый заказ такси!
    Адрес: {message.text}
    Заказчик: {message.from_user.full_name}
    Телеграмм заказчика: @{message.from_user.username}
    На чье имя заказ такси: {name_order}
    """
    success_flag = 0
    try:
        await bot.send_message('@requests_bot_nbc', order_message, parse_mode=ParseMode.HTML)
        success_flag = 1
    except Exception as e:
        logging.error(e)
    if success_flag:
        await message.answer('Запрос на заказ такси успешно отправлен, при необходимости с вами свяжутся', reply_markup=ReplyKeyboardRemove())
        await  mongodb.document_the_event('order_taxi', datetime.now().strftime("%d-%m-%Y %H:%M"), message.text, message.from_user.full_name, message.from_user.username, name_order)
    else:
        await message.answer('Произошла какая то ошибка и запрос не отправлен, пожалуйста, свяжитесь с администратором', reply_markup=ReplyKeyboardRemove())
    await state.clear()