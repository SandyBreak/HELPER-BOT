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
from database.mongodb.check_data import CheckData
from data_storage.keyboards import Keyboards
from data_storage.states import OrderTechnic
from data_storage.emojis_chats import *
from exeptions import *


helper = MinorOperations()
bank_of_keys = Keyboards()
mongodb = Interaction()
chat_name = ChatNames()
router = Router()
emojis =Emojis()



@router.callback_query(F.data == "order_technic")
async def enter_type_break(callback: CallbackQuery, state: FSMContext) -> None:
    keyboard = await bank_of_keys.breaks_keyboard()    
    await callback.message.answer(f'Выбрано: {emojis.SUCCESS} Заказать/отремонтировать технику')
    await callback.message.answer(f'Выберите тип поломки при помощи предложенной клавиатуры или введите его вручную', reply_markup=keyboard)    
    await callback.answer()
    
    await state.set_state(OrderTechnic.enter_type_office)


@router.message(F.text, StateFilter(OrderTechnic.enter_type_office))
async def enter_office(message: Message, state: FSMContext) -> None:
    filter_by_id = {'users.tg_id': message.from_user.id}
    update = {'$set': {'users.$.secondary_data': message.text}}
    await mongodb.update_data(filter_by_id, update)
    
    keyboard = await bank_of_keys.ultimate_keyboard('room')
    
    await message.answer(f'Выберите офис для которого нужен технический специалист, используя предложенную клавиатуру', reply_markup=keyboard)
    
    await state.set_state(OrderTechnic.send_order)

        
        
@router.message(F.text, StateFilter(OrderTechnic.send_order))
async def send_data(message: Message, state: FSMContext, bot: Bot) -> None:
    control = CheckData(message.from_user.id)
    try:
        await control.check_room_for_accuracy(message.text)
    except DataInputError:
        await message.answer(f'Выберите офис для которого нужен технический специалист, используя предложенную клавиатуру')

    else:
        name_order = await mongodb.get_data(message.from_user.id, 'secondary_data')
        order_message = await helper.fill_event_data(message.text, message.from_user.full_name, message.from_user.username, name_order, 5)
        
        success_flag = 0
        
        try:
            await bot.send_message(chat_name.TEST_QUERIES, order_message, parse_mode=ParseMode.HTML)
            success_flag = 1
        except Exception as e:
            logging.error(e)
            
        if success_flag:
            await message.answer('Запрос на вызов технического специалиста успешно отправлен, при необходимости с вами свяжутся', reply_markup=ReplyKeyboardRemove())
            await  mongodb.document_the_event('order_technic', datetime.now().strftime("%d-%m-%Y %H:%M"), message.text, message.from_user.full_name, message.from_user.username, name_order)
        else:
            await message.answer('Произошла какая то ошибка и запрос не отправлен, пожалуйста, свяжитесь с администратором', reply_markup=ReplyKeyboardRemove())
        
        await state.clear()