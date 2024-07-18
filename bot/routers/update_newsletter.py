# -*- coding: UTF-8 -*-

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message 
from aiogram import Router, Bot
import logging

from database.mongodb.interaction import Interaction
from data_storage.emojis_chats import *



db = Interaction()
router = Router()
emojis = Emojis()

@router.message(Command(commands=['update']))
async def update_message(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получение идентификаторов пользователей
    """
    await state.clear()
    user_ids = await db.get_users_id()
    update_message = """
        Уважаемые пользователи @NBC_HelperBot!

    Хочу сообщить вам об обновлении нашего бота.
    
Была добавлена кнопка <b>"🕗Ознакомиться с бронями преговорных комнат"</b>, которая позволяет смотреть список броней для выбранных вами переговорной комнаты и даты.

Теперь бронирование переговорных комнат осуществляется без участия нашего замечательного офис менеджера Алеси и она не имеет к этому никакого отношения. Это было сделано чтобы уменьшить количество конфликтов при бронировании переговорных комнат и убрать большинство недопониманий между сотрудниками.

При возникновении ситуации когда сотрудник забронировал переговорную комнату с помощью бота, а другой воспользовался ей и помешал ему, хотя не бронировал ее при помощи бота, будет прав первый сотрудник, который воспользовался ботом.

Пожалуйста, для предотвращения недопониманий и конфликтов пользуйтесь всем предложенным вам фукнционалом. Вы можете не только забронировать комнату и посмотреть список броней на другие даты, но и удалить вашу бронь если вы не можете ею воспользоваться.

По прошествии часа с начала вашего бронирования запись о брони удаляется.

С уважением @velikiy_ss 
    """
    try:
        for user_id in user_ids:
            try:
                await bot.send_message(user_id, update_message, parse_mode=ParseMode.HTML)
                await message.answer(f'Message send success {emojis.SUCCESS} recipient: {user_id}')
            except Exception as e:
                if "chat not found" in str(e):
                    # Игнорируем ошибку "chat not found"
                    logging.warning(f"Skipping user_id {user_id} due to 'chat not found' error")
                else:
                    logging.error(e)
        await message.answer(f'Update success {emojis.SUCCESS}')
    except Exception as e:
        logging.error(e)

    await state.clear()

