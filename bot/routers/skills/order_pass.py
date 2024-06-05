# -*- coding: UTF-8 -*-

from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot
from aiogram.enums import ParseMode

import logging
from data_storage.keyboards import Keyboards
from data_storage.states import OrderPass
from data_storage.emojis import *

from database.mongodb.interaction import Interaction

bank_of_keys = Keyboards()
router = Router()
emojis =Emojis()


mongodb = Interaction(
			#user= os.environ.get('MONGO_INITDB_ROOT_USERNAME'),
			#password= os.environ.get('MONGO_INITDB_ROOT_PASSWORD')
		)




@router.callback_query(F.data == "order_pass")
async def action_1(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(f'Выбрано: {emojis.SUCCESS} Заказать пропуск')
    await callback.message.answer(f'Введите ФИО человека для которого нужно заказать пропуск')
    
    await callback.answer()
    await state.set_state(OrderPass.enter_type_office)


@router.message(F.text, StateFilter(OrderPass.enter_type_office))
async def action_3(message: Message, state: FSMContext, bot: Bot):
    filter_by_id = {'users.tg_id': message.from_user.id}
    update = {'$set': {'users.$.fio': message.text}}
    await mongodb.update_data(filter_by_id, update)
    
    keyboard = await bank_of_keys.type_office_keyboard()    
    
    await message.answer(f'Выберите офис для которого нужно заказать пропуск', reply_markup=keyboard)
    
    await state.set_state(OrderPass.send_order)

        
        
@router.message(F.text, StateFilter(OrderPass.send_order))
async def action_3(message: Message, state: FSMContext, bot: Bot):
    name_order = await mongodb.get_data(message.from_user.id, 'fio')
    order_message = f"""
    Новый заказ пропуска!
    Офис: {message.text}
    Заказчик: {message.from_user.full_name}
    Телеграмм заказчика: @{message.from_user.username}
    На чье имя пропуск: {name_order}
    Телефон: NONE
    """
    success_flag = 0
    try:
        await bot.send_message('@requests_bot_nbc', order_message, parse_mode=ParseMode.HTML)
        success_flag = 1
    except Exception as e:
        logging.error(e)
    if success_flag:
        await message.answer('Запрос на заказ пропуска успешно отправлен, при необходимости с вами свяжутся')
        await  mongodb.document_the_event(order_message)
    else:
        await message.answer('Произошла какая то ошибка и запрос не отправлен, пожалуйста, свяжитесь с администратором')
    await state.clear()