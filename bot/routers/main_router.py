# -*- coding: UTF-8 -*-

from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram import Router, F



from helper_classes.assistant import MinorOperations
from data_storage.keyboards import Keyboards
from data_storage.emojis import Emojis
from exeptions import *


from database.mongodb.initialization import Initialization


router = Router()
helper = MinorOperations()
bank_of_keys = Keyboards()
emojis = Emojis()





@router.message(Command(commands=['start','cancel']))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = Initialization(message.from_user.id)

    response = await user.init_user()
    await user.delete_user_meeting_data()
    keyboard = await bank_of_keys.possibilities_keyboard()
    privacy = f"""
       Привет, я бот помощник NBC!\nИ вот что я умею{emojis.POINTER}
    """
    await message.answer(privacy, ParseMode.HTML, disable_web_page_preview=True, reply_markup=keyboard.as_markup())

@router.message(Command(commands=["help"]))
async def welcome(message: Message, state: FSMContext):
    await message.answer('MESSAGE HELP', ParseMode.HTML)
    await state.clear()