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
from data_storage.states import FindContact
from data_storage.emojis_chats import *
from exeptions import *


helper = MinorOperations()
bank_of_keys = Keyboards()
mongodb = Interaction()
chat_name = ChatNames()
router = Router()
emojis =Emojis()


@router.callback_query(F.data == "order_cutaway")
async def enter_fio_employee(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(f'Выбрано: {emojis.SUCCESS} Заказать визитку')
    await callback.message.answer(f'Введите ФИО сотрудника для которого вам нужна визитка:', reply_markup=ReplyKeyboardRemove())    
    await callback.answer()
    
    await state.set_state(FindContact.enter_type_office)


@router.message(F.text, StateFilter(FindContact.enter_type_office))
async def enter_office(message: Message, state: FSMContext) -> None:
    filter_by_id = {'users.tg_id': message.from_user.id}
    update = {'$set': {'users.$.secondary_data': message.text}}
    await mongodb.update_data(filter_by_id, update)
    
    keyboard = await bank_of_keys.ultimate_keyboard('room')    
    
    await message.answer(f'Выберите офис в котором вы находитесь, используя предложенную клавиатуру', reply_markup=keyboard)
    
    await state.set_state(FindContact.send_order)

        
        
@router.message(F.text, StateFilter(FindContact.send_order))
async def send_data(message: Message, state: FSMContext, bot: Bot) -> None:
    control = CheckData(message.from_user.id)
    try:
        await control.check_room_for_accuracy(message.text)
    except DataInputError:
        await message.answer(f'Выберите офис в котором вы находитесь, используя предложенную клавиатуру')

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
            await message.answer(f'{emojis.SUCCESS} Запрос на создание визитки успешно отправлен, при необходимости с вами свяжутся', reply_markup=ReplyKeyboardRemove())
            await  mongodb.document_the_event('order_cutaway', datetime.now().strftime("%d-%m-%Y %H:%M"), message.text, message.from_user.full_name, message.from_user.username, name_order)
        else:
            await message.answer(f'{emojis.FAIL} Произошла какая то ошибка и запрос не отправлен, пожалуйста, свяжитесь с администратором по адресу: @velikiy_ss', reply_markup=ReplyKeyboardRemove())
        
        await state.clear()