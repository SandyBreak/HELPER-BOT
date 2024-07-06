#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from aiogram.types.bot_command import BotCommand
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

import asyncio
import logging


from routers.skills import create_zoom_meeting, find_contact, gain_access, order_office, order_pass, order_taxi, order_technic 
from routers import rezervation_meeting_room, cancel_rezervation__meeting_room
from helper_classes.assistant import MinorOperations
from database.mongodb.mongo_init import create_db
from data_storage.emojis_chats import Emojis
from routers import main_router


helper = MinorOperations()
emojis = Emojis()


async def set_commands_and_description(bot: Bot) -> None:
    commands = [
    BotCommand(
        command="/menu",
        description="Меню"
		),
    BotCommand(
        command="/create",
        description="Забронировать переговорную комнату"
		),
    BotCommand(
        command="/delete",
        description="Отменить бронирование переговорной комнаты"
		),
    BotCommand(
        command="/cancel",
        description="Отменить действие"
		),
    BotCommand(
        command="/help",
        description="Помощь"
		)
    ]
    description_one = f"{emojis.HELLO} Привет, я бот помощник NBC!\n"
    description_two = f"Нажмите на кнопку внизу экрана чтобы начать диалог {emojis.POINTER}"
    
    await bot.set_my_description(description=description_one+description_two)
    await bot.set_my_short_description(short_description=description_one)
    await bot.set_my_commands(commands)
    
    
async def main():
    load_dotenv()#Потом убрать надо
    
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=await helper.get_tg_token())
    dp = Dispatcher()
    
    await set_commands_and_description(bot)
    dp.include_router(main_router.router)
    dp.include_router(rezervation_meeting_room.router)
    dp.include_router(cancel_rezervation__meeting_room.router)
    
    dp.include_router(create_zoom_meeting.router)
    dp.include_router(find_contact.router)
    dp.include_router(gain_access.router)
    dp.include_router(order_pass.router)
    dp.include_router(order_office.router)
    dp.include_router(order_taxi.router)
    dp.include_router(order_technic.router)

    await create_db()
    logging.info("BOT STARTED")
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    asyncio.run(main())
    