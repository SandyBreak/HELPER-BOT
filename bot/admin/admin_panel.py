# -*- coding: UTF-8 -*-

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, FSInputFile
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import Router, Bot, F
from contextlib import suppress
import logging
import hashlib
import re

from admin.config import BANNED_USERS, MAX_ATTEMPTS, ADMIN_USERS, LIST_USERS_TO_NEWSLETTER
from admin.states import ControlPanelStates
from admin.assistant import AdminOperations
from admin.keyboards import AdminKeyboards


from database.mongodb.interaction import Interaction
from data_storage.emojis_chats import Emojis
from exeptions import *


mongodb_interface = Interaction()
bank_of_keys = AdminKeyboards()
helper = AdminOperations()
router = Router()
emojis =Emojis()
emojis = Emojis()


@router.message(Command('control'))
async def get_pass(message: Message, state: FSMContext, bot: Bot):
    if str(message.from_user.id) in BANNED_USERS:
        await message.answer('Зачем вам туда?)', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return
    elif not(str(message.from_user.id) in ADMIN_USERS):
        keyboard = await bank_of_keys.ban_or_access_keyboard(message.from_user.id)
        await message.answer(f"{emojis.ALLERT} Ты зашел не туда и скоро c тобой поговорят важные люди...")
        await bot.send_message(chat_id='5890864355', text=f'Кто то попытался войти в режим менеджера!\nID: {message.from_user.id}\nАДРЕС: @{message.from_user.username}\nИМЯ: {message.from_user.full_name}\nЗабанить его или дать доступ?', reply_markup=keyboard.as_markup())
    elif str(message.from_user.id) in ADMIN_USERS:
        await message.answer(f"{emojis.ALLERT} Для доступа в режим менеджера введите пароль {emojis.ALLERT}")
        await state.set_state(ControlPanelStates.enter_pass)
    

@router.message(StateFilter(ControlPanelStates.enter_pass))
async def enter_pass(message: Message, state: FSMContext):
    manager_password = await helper.get_manager_password()
    root_keyboard = await bank_of_keys.possibilities_keyboard()
    
    global MAX_ATTEMPTS
    if (MAX_ATTEMPTS > 0) and (hashlib.sha256(message.text.encode()).hexdigest() == manager_password):
        await message.answer(f"{emojis.SUCCESS} Доступ разрешен! {emojis.SUCCESS}")
        await message.answer(f"{emojis.ARROW_DOWN} Выберите одно из нижеперечисленных действий {emojis.ARROW_DOWN}", reply_markup=root_keyboard.as_markup())
    else:
        MAX_ATTEMPTS -= 1
        if MAX_ATTEMPTS <= 0:
            await message.answer(f"{emojis.FAIL} Превышен лимит попыток ввода пароля {emojis.FAIL}")
            await message.answer(f"{emojis.ALLERT} Доступ заблокирован! {emojis.ALLERT}")
            
            await state.clear()
        else:
            await helper.update_attempts_enter_wrong_password(MAX_ATTEMPTS)
            await message.answer(f"{emojis.FAIL} Доступ запрещён! {emojis.FAIL}")
            await message.answer(f"{emojis.ALLERT} Осталось попыток: {MAX_ATTEMPTS} {emojis.ALLERT} ")


@router.callback_query(lambda callback: not re.search(r'^(order_taxi|order_delivery|order_pass|order_cutaway|order_office|order_technic|gain_access|find_contact|rezervation_meeting_room|get_list_meeting|cancel_rezervation_meeting_room|create_zoom_meeting)$', str(callback.data)))
async def choose_action(callback: CallbackQuery, state: FSMContext, bot: Bot):
    action, user_id, user_tg_addr = await helper.parse_callback_data(callback.data)
    
    if action == 'manual':
        await get_manual_admin_panel(callback)
        await callback.answer()
    if action == 'menu':
        root_keyboard = await bank_of_keys.possibilities_keyboard()
        await callback.message.answer(f"{emojis.ARROW_DOWN} Выберите одно из нижеперечисленных действий {emojis.ARROW_DOWN}", reply_markup=root_keyboard.as_markup())
        await callback.answer()
    elif action == 'global_newsletter':
        await callback.message.answer(f'Отправьте сообщение для глобальной рассылки:')
        await state.set_state(ControlPanelStates.launch_global_newsletter)
        await callback.answer()
    elif action == 'targeted_newsletter':
        list_users = await bank_of_keys.keyboard_for_adding_users_in_targeted_newsletter()
        await callback.message.answer(f'Выберите пользователей которым хотите отправить сообщение и напишите это сообщение:', reply_markup=list_users.as_markup())
        await state.set_state(ControlPanelStates.launch_targeted_newsletter)
        await callback.answer()
    elif action == 'view_active_users':
        await view_active_users(callback, bot)
    elif action == 'ADD':
        await add_user_to_newsletter(callback, user_id, user_tg_addr)
    elif action == 'BAN':
        await ban_user(callback, bot, user_id)
    elif action == 'ACCESS':
        await assign_user_as_admin(callback, bot, user_id)


async def get_manual_admin_panel(callback: CallbackQuery):
    manual_message = """
Заново вызвать админ панель:
/menu

<b>Запустить глобальную рассылку:</b>
Написать и отправить сообщение всем пользователям

<b>Запустить точечную рассылку:</b>
1. Выбрать пользователей с помощью сгенерированной клавиатуры
2. Написать и отправить сообщение выбранным пользователям

<b>Посмотреть список активных/не активных пользователей:</b>
Получить список активных пользователей
    """
    await callback.message.answer(manual_message, ParseMode.HTML)
    await callback.answer()


@router.message(StateFilter(ControlPanelStates.launch_global_newsletter))
async def global_newsletter(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Глобальная рассылка обновлений
    """

    user_data = await mongodb_interface.get_users_id_and_tg_adreses()
    try:
        received_users = []
        not_received_users =[]
        for user in user_data:
            user_id = user[0]
            user_tg_addr = user[1]
            try:
                if message.photo:
                    photo = await bot.get_file(message.photo[-1].file_id)
                    downloaded_photo = await bot.download_file(photo.file_path)
                    path_table = await helper.save_photo(message.from_user.id, downloaded_photo)
                    sended_photo = FSInputFile(path_table)
                    chat = await bot.get_chat(user_id)
                    await bot.send_photo(chat.id, photo=sended_photo, caption=message.caption, parse_mode=ParseMode.HTML)
                    received_users.append([user_id, user_tg_addr])
                elif message.text:
                    await bot.send_message(user_id, message.text, parse_mode=ParseMode.HTML)
                    received_users.append([user_id, user_tg_addr])
            except Exception as e:
                if "chat not found" in str(e):
                    logging.warning(f"Skipping user_id {user_id} due to 'chat not found' error")
                    not_received_users.append([user_id, user_tg_addr, 'Чат не найден'])
                elif "bot was blocked" in str(e):
                    logging.warning(f"Skipping user_id {user_id} due to 'chat not found' error")
                    not_received_users.append([user_id, user_tg_addr, 'Заблокировал бота'])
                else:
                    logging.warning(f"Skipping user_id {user_id} unknown error{e}")
                    not_received_users.append([user_id, user_tg_addr, f'Другая ошибка{e}'])
        
        if received_users:
            message_report = 'Получившие пользователи:\n'
            
            for user in received_users:
                user_id=user[0]
                user_tg_addr=user[1]
                message_report += f'ID: {user_id} Адрес: {user_tg_addr}\n'
            
        if not_received_users:
            message_report += 'Не получившие пользователи:\n'
            for user in not_received_users:
                user_id = user[0]
                user_tg_addr = user[1]
                reason = user[2]
                message_report += f'ID: {user_id} Адрес: {user_tg_addr} Причина: {reason}\n'  
        
        await message.answer(f'{emojis.SUCCESS} Рассылка завершена успешно!')
        await message.answer(f'{message_report}')
    except Exception as e:
        logging.error(f"Error during global_newsletter: {e}")
    await state.clear()


@router.message(F.text, StateFilter(ControlPanelStates.launch_targeted_newsletter))    
async def targeted_newsletter(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Точечная рассылка обновлений
    """
    user_data = LIST_USERS_TO_NEWSLETTER
    try:
        received_users = []
        not_received_users =[]
        for user in user_data:
            user_id = user[0]
            user_tg_addr = user[1]
            try:
                if message.photo:
                    photo = await bot.get_file(message.photo[-1].file_id)
                    downloaded_photo = await bot.download_file(photo.file_path)
                    path_table = await helper.save_photo(message.from_user.id, downloaded_photo)
                    sended_photo = FSInputFile(path_table)
                    chat = await bot.get_chat(user_id)
                    await bot.send_photo(chat.id, photo=sended_photo, caption=message.caption, parse_mode=ParseMode.HTML)
                    received_users.append([user_id, user_tg_addr])
                elif message.text:
                    await bot.send_message(user_id, message.text, parse_mode=ParseMode.HTML)
                    received_users.append([user_id, user_tg_addr])
            except Exception as e:
                if "chat not found" in str(e):
                    logging.warning(f"Skipping user_id {user_id} due to 'chat not found' error")
                    not_received_users.append([user_id, user_tg_addr, 'Чат не найден'])
                elif "bot was blocked" in str(e):
                    logging.warning(f"Skipping user_id {user_id} due to 'chat not found' error")
                    not_received_users.append([user_id, user_tg_addr, 'Заблокировал бота'])
                else:
                    logging.warning(f"Skipping user_id {user_id} unknown error{e}")
                    not_received_users.append([user_id, user_tg_addr, f'Другая ошибка{e}'])
        
        message_report = 'Получившие пользователи:\n'
        if received_users:
            for user in received_users:
                user_id=user[0]
                user_tg_addr=user[1]
                message_report += f'ID: {user_id} Адрес: {user_tg_addr}\n'
        
        message_report += 'Не получившие пользователи:\n'
        if not_received_users:
            for user in not_received_users:
                user_id = user[0]
                user_tg_addr = user[1]
                reason = user[2]
                message_report += f'ID: {user_id} Адрес: {user_tg_addr} Причина: {reason}\n' 
        LIST_USERS_TO_NEWSLETTER.clear()
        await message.answer(f'{emojis.SUCCESS} Рассылка завершена успешно!')
        await message.answer(f'{message_report}')
    except Exception as e:
        logging.error(f"Error during targeted_newsletter: {e}")
    await state.clear()
    

async def view_active_users(callback: CallbackQuery, bot: Bot) -> None:
    user_data = await mongodb_interface.get_users_id_and_tg_adreses()
    
    active_users = []
    not_active_users = []
    other_users = []
    
    users_list_str = 'Список пользователей:\n'
    
    for user in user_data:
        user_id = user[0]
        user_tg_addr = user[1]
        try:
            chat = await bot.get_chat(chat_id=user_id)
            if chat:
                active_users.append([user_id, user_tg_addr])
        except Exception as e:
                if "chat not found" in str(e):
                    logging.warning(f"Skipping user_id {user_id} due to 'chat not found' error")
                    not_active_users.append([user_id, user_tg_addr,])
                else:
                    logging.warning(f"Skipping user_id {user_id} unknown error{e}")
                    other_users.append([user_id, user_tg_addr, e])
    
    if active_users:
        users_list_str += '\nСтатус АКТИВЕН:\n'
        for user in active_users:
            user_id=user[0]
            user_tg_addr=user[1]
            users_list_str += f'ID: {user_id} Адрес: {user_tg_addr}\n'
    
    if not_active_users:
        users_list_str += '\nСтатус НЕ АКТИВЕН:\n'
        for user in not_active_users:
            user_id=user[0]
            user_tg_addr=user[1]
            users_list_str += f'ID: {user_id} Адрес: {user_tg_addr}\n'
    
    if other_users:
        users_list_str += '\nСтатус ДРУГАЯ ОШИБКА:\n'
        for user in other_users:
            user_id=user[0]
            user_tg_addr=user[1]
            error = user[2]
            users_list_str += f'ID: {user_id} Адрес: {user_tg_addr} Ошибка: {error}\n'
            
    await callback.message.answer(users_list_str)
    await callback.answer()


async def add_user_to_newsletter(callback: CallbackQuery, user_id: str, user_tg_addr: str):
    if [user_list for user_list in LIST_USERS_TO_NEWSLETTER if user_id in user_list]:
        LIST_USERS_TO_NEWSLETTER.pop()
        await callback.message.answer(f'{emojis.ALLERT} Пользователь удален из рассылки:\nID: {user_id}\nАдрес: {user_tg_addr}')
        await callback.answer()    
    else:
        LIST_USERS_TO_NEWSLETTER.append([user_id, user_tg_addr])
        await callback.message.answer(f'{emojis.SUCCESS} Пользователь добавлен в рассылку:\nID: {user_id}\nАдрес: {user_tg_addr}')
        await callback.answer()
            
            
async def ban_user(callback: CallbackQuery, bot: Bot, user_id: str):
    with suppress(TelegramBadRequest):
        if user_id in ADMIN_USERS:
            await callback.message.edit_text(f'{emojis.FAIL} Невозможно забанить пользователя, он является администратором!')
        elif user_id not in BANNED_USERS:
            BANNED_USERS.append(user_id)
            await callback.message.edit_text(f'{emojis.SUCCESS} Пользователь забанен!')
            await bot.send_message(chat_id=f'{user_id}', text=f'{emojis.ALLERT} Вы заблокированы администратором')
            await helper.update_list_banned_users(BANNED_USERS)
        else:
            await callback.message.edit_text(f'{emojis.SUCCESS} Пользователь уже в бане!')
        await callback.message.edit_reply_markup(reply_markup=None)
    with suppress(TypeError):
        await callback.answer()


async def assign_user_as_admin(callback: CallbackQuery, bot: Bot, user_id: str):
    with suppress(TelegramBadRequest):
        if user_id in BANNED_USERS:
            await callback.message.edit_text(f'{emojis.FAIL} Невозможно добавить админа, пользователь уже находится в бане!')
        elif user_id not in ADMIN_USERS:
            ADMIN_USERS.append(user_id)
            await callback.message.edit_text(f'{emojis.SUCCESS} Пользователь добавлен в список админов!')
            try:
                await bot.send_message(chat_id=f'{user_id}', text=f'Поздравляю, теперь вы администратор\\!\nДля входа в панель управления введите команду /control\nПароль: ||Nbcprxt3405||', parse_mode=ParseMode.MARKDOWN_V2)
            except Exception as e:
                logging.error(f'Error sending message to user {user_id}: {e}')
            await helper.update_list_admin_users(ADMIN_USERS)
        else:
            await callback.message.edit_text(f'{emojis.SUCCESS} Пользователь уже админ!')
        await callback.message.edit_reply_markup(reply_markup=None)
    with suppress(TypeError):
        await callback.answer()