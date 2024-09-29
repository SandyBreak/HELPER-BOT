#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import asyncio
import logging

from aiogram.types.bot_command import BotCommand
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv



from routers.simple import create_zoom_meeting, universal_event_router
from routers.advanced import order_taxi, order_delivery

from routers import commands, registration, actions
from routers.rezervation_meeting_room import rezervation_meeting_room, get_list_meeting, cancel_rezervation__meeting_room
from admin import admin_panel

from models.long_messages import LONG_DESCRIPTION, SHORT_DESCRIPTION

from config import TELEGRAM_TOKEN


async def set_commands_and_description(bot: Bot) -> None:
    commands = [
    BotCommand(
        command="/menu",
        description="Меню"
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
    await bot.set_my_description(description=LONG_DESCRIPTION)
    await bot.set_my_short_description(short_description=SHORT_DESCRIPTION)
    await bot.set_my_commands(commands)
    
    
async def main():
    load_dotenv()#Потом убрать надо
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m %H:%M')
    
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    
    await set_commands_and_description(bot)
    
    dp.include_router(commands.router)
    dp.include_router(registration.router)
    dp.include_router(actions.router)
    dp.include_router(admin_panel.router)
    
    dp.include_router(create_zoom_meeting.router)
    dp.include_router(universal_event_router.router)
    
    dp.include_router(order_taxi.router)
    #dp.include_router(order_delivery.router)
    
    dp.include_router(rezervation_meeting_room.router)
    dp.include_router(get_list_meeting.router)
    dp.include_router(cancel_rezervation__meeting_room.router)
    

    logging.warning("BOT STARTED")
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    asyncio.run(main())
    