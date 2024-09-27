# -*- coding: UTF-8 -*-

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram import Router, F, Bot

router = Router()


@router.callback_query(F.data == "create_zoom_meeting")
async def create_zoom_meeting(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"Для создания конференции в ZOOM вы можете воспользоваться этим ботом: @nbc_service_bot\nОн обладает простым и понятным интерфейсом и является разработкой NBC", reply_markup=None)
    await state.clear()