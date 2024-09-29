# -*- coding: UTF-8 -*-

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram import Router, Bot

from models.keyboards.user_keyboards import UserKeyboards
from models.long_messages import HELP_MESSAGE
from models.emojis import Emojis

from services.postgres.user_service import UserService
from exceptions.errors import UserNotRegError

router = Router()


@router.message(Command(commands=['menu', 'cancel']))
async def cmd_start(message: Message, state: FSMContext, bot: Bot)  -> None:
    if (delete_message_id := (await state.get_data()).get('message_id')): await bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
    await state.clear()
    try:
        await UserService.check_user_exists(message.from_user.id)
    
        delete_message = await message.answer(f"{Emojis.TIME} Отмена...", ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
        await bot.delete_message(chat_id=delete_message.chat.id, message_id=delete_message.message_id)
    
        possibilities_keyboard = await UserKeyboards.possibilities_keyboard()
        delete_message = await message.answer(f'Привет, я бот помощник NBC!\nВот что я умею {Emojis.POINTER}', ParseMode.HTML, disable_web_page_preview=True, reply_markup=possibilities_keyboard.as_markup())
    except UserNotRegError:
        delete_message = await message.answer(f"{Emojis.ALLERT} Вы не зарегистрированы! {Emojis.ALLERT}\nДля регистрации введите команду /start", reply_markup=ReplyKeyboardRemove())
    
    await state.update_data(message_id=delete_message.message_id)

@router.message(Command(commands=['help']))
async def help_message(message: Message, state: FSMContext) -> None:
    await message.answer(HELP_MESSAGE, ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
    await state.clear()