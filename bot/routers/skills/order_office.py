# -*- coding: UTF-8 -*-

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.enums import ParseMode
from aiogram import Router, F, Bot
from datetime import datetime
import logging


from database.mongodb.interaction import Interaction
from helper_classes.assistant import MinorOperations
from data_storage.keyboards import Keyboards
from data_storage.states import OrderOffice
from data_storage.emojis_chats import *
from exeptions import *


helper = MinorOperations()
bank_of_keys = Keyboards()
mongodb = Interaction()
chat_name = ChatNames()
router = Router()
emojis =Emojis()


@router.callback_query(F.data == "order_office")
async def enter_product(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(f'Выбрано: {emojis.SUCCESS} Заказать канцелярию')
    await callback.message.answer(f'Введите товары которые нужно заказать', reply_markup=ReplyKeyboardRemove())   
    await callback.answer()
    
    await state.set_state(OrderOffice.enter_type_office)


@router.message(F.text, StateFilter(OrderOffice.enter_type_office))
async def enter_office(message: Message, state: FSMContext) -> None:
    filter_by_id = {'users.tg_id': message.from_user.id}
    update = {'$set': {'users.$.secondary_data': message.text}}
    await mongodb.update_data(filter_by_id, update)
    
    keyboard = await bank_of_keys.type_office_keyboard()    
    
    await message.answer(f'Выберите офис для которого нужно заказать товары, используя предложенную клавиатуру', reply_markup=keyboard)
    
    await state.set_state(OrderOffice.send_order)

        
        
@router.message(F.text, StateFilter(OrderOffice.send_order))
async def send_data(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        if message.text not in ['Империя','Таганка']:
            raise DataInputError
    except DataInputError:
        await message.answer(f'Выберите офис для которого нужно заказать товары, используя предложенную клавиатуру')

    else:
        name_order = await mongodb.get_data(message.from_user.id, 'secondary_data')
        order_message = await helper.fill_event_data(message.text, message.from_user.full_name, message.from_user.username, name_order, 2)
        
        success_flag = 0
        
        try:
            await bot.send_message(chat_name.TEST_QUERIES, order_message, parse_mode=ParseMode.HTML)
            success_flag = 1
        except Exception as e:
            logging.error(e)
        
        if success_flag:
            await message.answer('Запрос на заказ канцелярии успешно отправлен, при необходимости с вами свяжутся', reply_markup=ReplyKeyboardRemove())
            await  mongodb.document_the_event('order_office', datetime.now().strftime("%d-%m-%Y %H:%M"), message.text, message.from_user.full_name, message.from_user.username, name_order)
        else:
            await message.answer('Произошла какая то ошибка и запрос не отправлен, пожалуйста, свяжитесь с администратором', reply_markup=ReplyKeyboardRemove())
        
        await state.clear()