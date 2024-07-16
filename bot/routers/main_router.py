# -*- coding: UTF-8 -*-

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram import Router, F


from database.mongodb.initialization import Initialization
from data_storage.keyboards import Keyboards
from data_storage.emojis_chats import Emojis
from exeptions import *


bank_of_keys = Keyboards()
router = Router()
emojis = Emojis()


@router.message(Command(commands=['start', 'menu', 'cancel', ]))
async def cmd_start(message: Message, state: FSMContext)  -> None:
    await state.clear()
    
    user = Initialization(message.from_user.id, message.from_user.username)
    await user.init_user()
    await user.delete_user_meeting_data()
    
    keyboard = await bank_of_keys.possibilities_keyboard()
    
    hello_message = f"""Привет, я бот помощник NBC!"""
    await message.answer(hello_message, ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
    await message.answer(f'Вот что я умею {emojis.POINTER}', ParseMode.HTML, disable_web_page_preview=True, reply_markup=keyboard.as_markup())
    

@router.message(Command(commands=['help']))
async def help_message(message: Message, state: FSMContext) -> None:
    message_help = """
    Описание команд:
/menu - Вызов основного меню бота
/create - Команда дублирующая кнопку "Забронировать переговорную комнату"
/delete - Команда дублирующая кнопку "Отменить бронь переговорной комнаты"
/cancel - Отмена текущего сценария заполнения данных
/help - Кнопка помощи
Адрес разработчика для связи, если возникает проблема с работой бота: @velikiy_ss
Для корректной работы бота у вашего аккаунта не должно быть пустым имя пользователя. Имя пользователя это ваш уникальный телеграмм адрес который выглядит примерно так: @Your_tg_address. Его можно задать в настройках вашего телеграмм аккаунта.
    """
    await message.answer(message_help, ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
    await state.clear()