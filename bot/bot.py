#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from aiogram.types.bot_command import BotCommand
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

import asyncio
import logging


from helper_classes.assistant import MinorOperations
from database.mongodb.mongo_init import create_db
from routers.skills import order_pass, order_office, order_technic, gain_access, order_taxi, create_zoom_meeting
from data_storage.emojis import Emojis
from routers import main_router


helper = MinorOperations()
emojis = Emojis()


async def set_commands_and_description(bot: Bot) -> None:
    commands = [
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
    dp.include_router(order_taxi.router)
    dp.include_router(main_router.router)
    dp.include_router(order_pass.router)
    dp.include_router(order_office.router)
    dp.include_router(order_technic.router)
    dp.include_router(gain_access.router)
    dp.include_router(create_zoom_meeting.router)

    await create_db()
    logging.info("BOT STARTED")
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(create_database())
    asyncio.run(main())
    