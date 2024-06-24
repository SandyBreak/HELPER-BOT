# -*- coding: UTF-8 -*-

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram import Router, F



from data_storage.keyboards import Keyboards
from data_storage.emojis_chats import Emojis
from exeptions import *


from database.mongodb.initialization import Initialization


router = Router()
bank_of_keys = Keyboards()
emojis = Emojis()


@router.message(Command(commands=['start', 'menu', 'cancel', ]))
async def cmd_start(message: Message, state: FSMContext)  -> None:
    await state.clear()
    user = Initialization(message.from_user.id, message.from_user.username)
    
    await user.init_user()
    await user.delete_user_meeting_data()
    
    keyboard = await bank_of_keys.possibilities_keyboard()
    
    hello_message = f"""
       Привет, я бот помощник NBC!\nИ вот что я умею{emojis.POINTER}
    """
    
    await message.answer(hello_message, ParseMode.HTML, disable_web_page_preview=True, reply_markup=keyboard.as_markup())


@router.message(Command(commands=['help']))
async def welcome(message: Message, state: FSMContext) -> None:
    await message.answer('MESSAGE HELP', ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
    await state.clear()