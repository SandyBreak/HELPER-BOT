# -*- coding: UTF-8 -*-

from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.utils.deep_linking import create_start_link
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot

import hashlib
import qrcode
import os


from helper_classes.assistant import MinorOperations
from data_storage.keyboards import Keyboards
from data_storage.states import OrderPass
from data_storage.emojis import *
from exeptions import *


helper = MinorOperations()
bank_of_keys = Keyboards()
router = Router()
emojis =Emojis()







@router.callback_query(F.data == "order_pass")
async def action_1(callback: CallbackQuery, state: FSMContext):
    keyboard = await bank_of_keys.type_break_keyboard()
    await callback.message.answer(f'Выбрано: {emojis.SUCCESS} Заказать пропуск')
    await callback.message.answer('Выберите тип поломки используя клавиатуру, или введите его вручную', reply_markup=keyboard)
    await state.set_state(OrderPass.keyboard_entry_break)

    
    
@router.message(F.text, StateFilter(OrderPass.keyboard_entry_break))
async def action_2(message: Message, state: FSMContext, bot: Bot):
    keyboard = await bank_of_keys.type_office_keyboard()
    await message.answer(f'Выберите офис в котором случилась поломка', reply_markup=keyboard)
    
    await bot.send_message('@requests_bot_nbc', f'Новый заказ пропуска!\nОфис: {message.text}\nЗаказчик: {message.from_user.full_name}\nТелефон: NONE\nТелеграмм: @{message.from_user.username}')
    await state.clear()