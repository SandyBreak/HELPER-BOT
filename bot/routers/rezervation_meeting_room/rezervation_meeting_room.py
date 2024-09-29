# -*- coding: UTF-8 -*-

from datetime import timedelta
import logging
import json
from typing import Union
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot

from admin.admin_logs import send_log_message

from services.postgres.rezervation_meeting_service import RezervationMeetingService
from services.postgres.user_service import UserService

from models.keyboards.user_keyboards import  UserKeyboards
from models.keyboards.create_meeting_keyboards import CreateMeeteingKeyboards
from models.states import RezervationMeetingStates
from models.emojis import Emojis

from utils.rezervation_meeting_data_validator import CheckData
from utils.assistant import MinorOperations

from exceptions.errors import DataInputError, LongTimeInputError, CreateMeetingError, UserNotRegError


router = Router()

@router.callback_query(F.data == "rezervation_meeting_room")
async def start_create_new_meeting(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Инициализация пользователя
    """
    await state.clear()
    try:
        
        await UserService.check_user_exists(callback.from_user.id)
        await RezervationMeetingService.delete_temporary_data(callback.from_user.id)
        await RezervationMeetingService.init_new_meeting(callback.from_user.id)
        
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'{Emojis.SUCCESS} Забронировать переговорную комнату {Emojis.SUCCESS}')
        
        room_keyboard = await UserKeyboards.ultimate_keyboard('room')
        delete_message = await callback.message.answer(text="Выберите переговорную комнату", reply_markup=room_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(RezervationMeetingStates.get_room)
    except UserNotRegError:
        delete_message = await callback.message.answer(f"{Emojis.ALLERT} Вы не зарегистрированы! {Emojis.ALLERT}\nДля регистрации введите команду /start", reply_markup=ReplyKeyboardRemove())
        await state.update_data(message_id=delete_message.message_id)
    await callback.answer() 
    


@router.callback_query(F.data, StateFilter(RezervationMeetingStates.get_room))
async def get_office(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Получение адреса переговорной
    """
    data = json.loads(callback.data)
    if data['key'] == 'choice':
        entered_office = await CheckData(callback.from_user.id).check_room_for_accuracy(data['value'])
        calendar_keyboard = await CreateMeeteingKeyboards.calendar_keyboard(0)
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f'Выбрана комната для переговоров по адресу: <b>{[entered_office]}</b>\nВыберите дату конференции:', reply_markup=calendar_keyboard.as_markup(resize_keyboard=True), parse_mode=ParseMode.HTML)

        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(RezervationMeetingStates.get_date)
    else:
        await callback.message.answer("Введены данные неправильного формата!" )


@router.callback_query(F.data, StateFilter(RezervationMeetingStates.get_date))
async def get_date(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
        Получение даты конференции

    Args:
        callback (CallbackQuery): This object represents an incoming callback query from a callback button in an `inline keyboard
        state (FSMContext): Base class for all FSM storages
        bot (Bot): Bot class
    """
    data = json.loads(callback.data)
    message_log = False
    
    if data['key'] == 'month_shift':
        calendar_keyboard = await CreateMeeteingKeyboards.calendar_keyboard(data['value'])
        await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=calendar_keyboard.as_markup(resize_keyboard=True))
    
    elif data['key'] == 'date':
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='⏳ Ищу свободные временные интервалы...')
        await CheckData(callback.from_user.id).checking_the_date_for_accuracy(data['value'])
        
        start_time_keyboard = await CreateMeeteingKeyboards.start_time_keyboard(callback.from_user.id)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Выберите время начала конфренции:', reply_markup=start_time_keyboard.as_markup(resize_keyboard=True))
        
        await state.set_state(RezervationMeetingStates.get_start_time)
    else:
        message_log = await callback.message.answer("Кажется вы нажали не ту кнопку, попробуйте еще раз!")
        await send_log_message(callback, bot, message_log)
					
					
@router.callback_query(F.data, StateFilter(RezervationMeetingStates.get_start_time))
async def get_start_time(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
        Получение времени начала конференции

    Args:
        callback (CallbackQuery): This object represents an incoming callback query from a callback button in an `inline keyboard
        state (FSMContext): Base class for all FSM storages
        bot (Bot): Bot class
    """
    data = json.loads(callback.data)

    message_log = False
    if data['key'] == 'back':
        
        calendar_keyboard = await CreateMeeteingKeyboards.calendar_keyboard(0)
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Введите дату конференции:", reply_markup=calendar_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(RezervationMeetingStates.get_date)
    elif data['key'] == 'start_time':
        try:
            await CheckData(callback.from_user.id).checking_the_start_time_for_accuracy(data['value'])
            
            duration_keyboard = await CreateMeeteingKeyboards.duration_keyboard(callback.from_user.id)
            delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Выберите продолжительность конференции', reply_markup=duration_keyboard.as_markup(resize_keyboard=True))
            
            await state.update_data(message_id=delete_message.message_id)
            await state.set_state(RezervationMeetingStates.get_duration)
        except LongTimeInputError:
            message_log = await callback.message.answer("Ваше время начала пересекается с другой конференцией")
    if message_log: await send_log_message(callback, bot, message_log)


@router.callback_query(F.data, StateFilter(RezervationMeetingStates.get_duration))
async def get_duration_meeting(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
        Получение продолжительности конференции

    Args:
        callback (CallbackQuery): This object represents an incoming callback query from a callback button in an `inline keyboard
        state (FSMContext): Base class for all FSM storages
        bot (Bot): Bot class
    """
    data = json.loads(callback.data)
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    user_id = callback.from_user.id
    message_log = False
    if data['key'] == 'back':
        
        start_time_keyboard = await CreateMeeteingKeyboards.start_time_keyboard(user_id)
        delete_message = await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выберите время начала конфренции:', reply_markup=start_time_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(RezervationMeetingStates.get_start_time)
    elif data['key'] == 'duration':
        try:
            await CheckData(user_id).checking_the_duration_meeting_for_accuracy(data['value'])
            
            record_keyboard = await UserKeyboards.ultimate_keyboard('back')
            delete_message = await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Введите название вашей конференции:', reply_markup=record_keyboard.as_markup(resize_keyboard=True))
            
            await state.update_data(message_id=delete_message.message_id)
            await state.set_state(RezervationMeetingStates.get_name_create_meeting)
        except LongTimeInputError:
            message_log = await callback.message.answer("Ваша конференция пересекается с другой, выберите значение поменьше")
        except DataInputError:
            message_log = await callback.message.answer("Кажется вы ввели данные в неправильном формате, попробуйте еще раз!")
    if message_log: await send_log_message(callback, bot, message_log)


@router.callback_query(F.data, StateFilter(RezervationMeetingStates.get_name_create_meeting))
async def get_name_create_meeting(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
        Возврат назад к получению значения автоматической записи конференции

    Args:
        callback (CallbackQuery): CallbackQuery class
        state (FSMContext): FSMContext class
        bot (Bot): Bot class
    """
    data = json.loads(callback.data)
    if data['key'] == 'back':
        
        duration_keyboard = await CreateMeeteingKeyboards.duration_keyboard(callback.from_user.id)
        delete_message = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Выберите продолжительность вашей конференции', reply_markup=duration_keyboard.as_markup(resize_keyboard=True))
        
        await state.update_data(message_id=delete_message.message_id)
        await state.set_state(RezervationMeetingStates.get_duration)
        

@router.message(F.text, StateFilter(RezervationMeetingStates.get_name_create_meeting))
async def get_name_create_meeting(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Присваивание названия и создание конференции
    """

    load_message = await message.answer("Ваша конференция создается...")
    meeting_data = await MinorOperations.fill_meeting_data_credits(message.from_user.id, message.text)
    try:
            message_log = await message.answer(f"<b>Конференция создана!</b>\n<b>Офис:</b> {meeting_data.office}\n<b>Название:</b> {message.text}\n<b>Дата и время начала:</b> {(meeting_data.start_time).strftime('%d.%m.%Y %H:%M')}\n<b>Продолжительность:</b> {meeting_data.duration} минут", ParseMode.HTML,  reply_markup=ReplyKeyboardRemove())
            await bot.delete_message(chat_id=message.chat.id, message_id=(await state.get_data()).get('message_id'))
            await bot.delete_message(chat_id=message.chat.id, message_id=load_message.message_id)
            
            await RezervationMeetingService.save_created_conference(message.from_user.id, meeting_data)
            await UserService.update_number_created_conferences(message.from_user.id)
            await state.clear()
    except CreateMeetingError:
          message_log = await message.answer("Неудалось создать конференцию, обратитесь в техническую поддержку по адресу: @velikiy_ss")
          
          await state.clear()
    if message_log: await send_log_message(message, bot, message_log)