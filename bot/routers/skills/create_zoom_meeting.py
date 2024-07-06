# -*- coding: UTF-8 -*-

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram import Router, F


from helper_classes.assistant import MinorOperations
from data_storage.keyboards import Keyboards
from data_storage.emojis_chats import *


helper = MinorOperations()
bank_of_keys = Keyboards()
router = Router()
emojis = Emojis()


@router.callback_query(F.data == "create_zoom_meeting")
async def action_1(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(f'Выбрано: {emojis.SUCCESS} Создать конференцию в ZOOM')
    await callback.message.answer('Для создания конференции в ZOOM вы можете воспользоваться этим ботом: @nbc_service_bot\nОн обладает простым и понятным интерфейсом и является разработкой NBC')
    await callback.answer()
    await state.clear()