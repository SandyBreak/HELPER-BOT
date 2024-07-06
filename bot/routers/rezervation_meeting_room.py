# -*- coding: UTF-8 -*-

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from contextlib import suppress
from aiogram import Router, F
from typing import Union




from database.mongodb.initialization import Initialization
from helper_classes.assistant import MinorOperations
from database.mongodb.interaction import Interaction
from data_storage.states import CreateMeetingStates
from database.mongodb.check_data import CheckData
from data_storage.keyboards import Keyboards
from data_storage.emojis_chats import *
from exeptions import *



helper = MinorOperations()
bank_of_keys = Keyboards()
db = Interaction()
router = Router()
emojis = Emojis()

@router.message(Command(commands=['create']))
@router.callback_query(F.data == "rezervation_meeting_room")
async def start_create_new_meeting(event: Union[Message, CallbackQuery], state: FSMContext) -> None:
    """
    Инициализация пользователя
    """
    await state.clear()
    user = Initialization(event.from_user.id, event.from_user.username)
    await user.init_user()
    await user.delete_user_meeting_data()
    keyboard = await bank_of_keys.ultimate_keyboard('room')
    """
    Выводим ответ в зависимости от типа обработчика
    """
    if isinstance(event, Message):
        await event.answer(f'Выбрано: {emojis.SUCCESS} Забронировать переговорную комнату')
        await event.answer("Выберите переговорную комнату", reply_markup=keyboard)
    elif isinstance(event, CallbackQuery):
        await event.message.answer(f'Выбрано: {emojis.SUCCESS} Забронировать переговорную комнату')
        await event.message.answer("Выберите переговорную комнату", reply_markup=keyboard)
        
    
    await state.set_state(CreateMeetingStates.get_room)
    with suppress(TypeError):
        await event.answer()


@router.message(F.text, StateFilter(CreateMeetingStates.get_room))
async def get_zoom(message: Message, state: FSMContext) -> None:
    """
    Получение адреса переговорной
    """
    control = CheckData(message.from_user.id)
    keyboard = await bank_of_keys.calendar_keyboard()
    try:
      response = await control.check_room_for_accuracy(message.text)
      
      await message.answer(f"Выбрана комната для переговоров по адресу: <b>{response}</b>", ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
      await message.answer("Введите дату конференции:", reply_markup=keyboard.as_markup(resize_keyboard=True))
      
      await state.set_state(CreateMeetingStates.get_date)
    except DataInputError:
      await message.answer("Введены данные неправильного формата, пожалуйста выберите адрес переговорной комнаты используя клавиатуру ниже" )


@router.message(F.text, StateFilter(CreateMeetingStates.get_date))
async def get_date(message: Message, state: FSMContext) -> None:
    """
    Получение даты конференции
    """
    control = CheckData(message.from_user.id)
    keyboard = await bank_of_keys.ultimate_keyboard('room')
    
    if message.text == "Вернуться назад":
      await message.answer("Выберите переговорную комнату:", reply_markup=keyboard)
      await state.set_state(CreateMeetingStates.get_room)
    else:
      try:
          response = await control.checking_the_date_for_accuracy(message.text)
          illegal_intervals = await control.get_available_time_for_meeting(response)
          keyboard = await bank_of_keys.start_time_keyboard(message.from_user.id, illegal_intervals)
          await message.answer("Теперь выберите время начала. Ниже в сообщении могут представлены недоступные вам временные интервалы уже запланированных конференций на введенную вами дату.", reply_markup=keyboard.as_markup(resize_keyboard=True))
          if illegal_intervals:
          	for start, end in illegal_intervals:
                    await message.answer(f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}")
          await state.set_state(CreateMeetingStates.get_start_time)  

      except DataInputError:
          await message.answer("Кажется вы ввели данные в неправильном формате, попробуйте еще раз!")
					
					
@router.message(F.text, StateFilter(CreateMeetingStates.get_start_time))
async def get_start_time(message: Message, state: FSMContext) -> None:
    """
    Получение времени начала конференции
    """
    control = CheckData(message.from_user.id)
    
    if message.text == "Вернуться назад":
        keyboard = await bank_of_keys.calendar_keyboard()
        
        await message.answer("Введите дату конференции:", reply_markup = keyboard.as_markup(resize_keyboard=True))
        await state.set_state(CreateMeetingStates.get_date)
    else:
      try:
          await control.checking_the_start_time_for_accuracy(message.text)
          keyboard = await bank_of_keys.duration_keyboard(message.from_user.id)
          
          await message.answer("Выберите продолжительность вашей конференции", reply_markup=keyboard.as_markup(resize_keyboard=True))
          
          await state.set_state(CreateMeetingStates.get_duration)
      except DataInputError:
          await message.answer("Кажется вы ввели данные в неправильном формате, попробуйте еще раз!")
      except HalfTimeInputError:
         await message.answer("Началом конференции может являтся время которое кратно 30 минутам, напрмер 10:00 или 10:30")
      except LongTimeInputError:
          await message.answer("Ваше время начала пересекается с другой конференцией")


@router.message(F.text, StateFilter(CreateMeetingStates.get_duration))
async def get_duration_meeting(message: Message, state: FSMContext) -> None:
    """
    Получение продолжительности конференции
    """
    control = CheckData(message.from_user.id)
    
    if message.text == "Вернуться назад":
        illegal_intervals = await db.get_data(message.from_user.id, 'illegal_intervals')
        keyboard = await bank_of_keys.start_time_keyboard(message.from_user.id, illegal_intervals)
        
        await message.answer("Теперь выберите время начала. Ниже могут представлены недоступные вам временные интервалы уже запланированных конференций на введенную вами дату.", reply_markup=keyboard.as_markup(resize_keyboard=True))
        await state.set_state(CreateMeetingStates.get_start_time)
    else:
        try:
            await control.checking_the_duration_meeting_for_accuracy(message.text)
            keyboard = await bank_of_keys.ultimate_keyboard('back_to_duration')
            
            await message.answer("Введите название своей конференции", reply_markup=keyboard)
            
            await state.set_state(CreateMeetingStates.get_name_create_meeting)
        except LongTimeInputError:
            await message.answer("Ваша конференция пересекается с другой, введите значение поменьше")
        except DataInputError:
            await message.answer("Кажется вы ввели данные в неправильном формате, попробуйте еще раз!")
        except HalfTimeInputError:
            await message.answer("Количество минут должно быть кратным 15")


@router.message(F.text, StateFilter(CreateMeetingStates.get_name_create_meeting))
async def get_auto_recording(message: Message, state: FSMContext) -> None:
    """
    Присваивание название и создание конференции
    """
    control = CheckData(message.from_user.id)
    if message.text == "Вернуться назад":
        keyboard = await bank_of_keys.duration_keyboard(message.from_user.id)
        
        await message.answer("Выберите продолжительность вашей конференции", reply_markup=keyboard.as_markup(resize_keyboard=True))
        
        await state.set_state(CreateMeetingStates.get_duration.state)
    else:
        await message.answer("Ваша конференция создается...")
        try:
            meeting_data = await helper.fill_meeting_data_credits(message.from_user.id, message.text, db)
            await db.document_the_meeting(message.from_user.id, message.from_user.username, message.text)
            await message.answer(f"<b>Конференция создана!</b>\n<b>Офис:</b> {meeting_data.office}\n<b>Название:</b> {message.text}\n<b>Дата и время начала:</b> {(meeting_data.start_time).strftime('%d.%m.%Y %H:%M')}\n<b>Продолжительность:</b> {meeting_data.duration} минут", ParseMode.HTML,  reply_markup=ReplyKeyboardRemove())
            
            await state.clear()
        except CreateMeetingError:
          await message.answer("Неудалось создать конференцию, обратитесь в техническую поддержку")
          
          await state.clear()