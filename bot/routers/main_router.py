# -*- coding: UTF-8 -*-

from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message


from helper_classes.assistant import MinorOperations
from data_storage.keyboards import Keyboards
from data_storage.emojis import Emojis
from exeptions import *


router = Router()
helper = MinorOperations()
bank_of_keys = Keyboards()
emojis = Emojis()




@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    keyboard = await bank_of_keys.possibilities_keyboard()
    privacy = f"""
       Привет, я бот помощник NBC!\nИ вот что я умею{emojis.POINTER}
    """
    await message.answer(privacy, ParseMode.HTML, disable_web_page_preview=True, reply_markup=keyboard.as_markup())

@router.message(Command(commands=["help"]))
async def welcome(message: Message, state: FSMContext):
    await message.answer('MESSAGE HELP', ParseMode.HTML)
    await state.clear()