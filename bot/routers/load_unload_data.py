# -*- coding: UTF-8 -*-

from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.utils.deep_linking import create_start_link
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot

import hashlib
import qrcode
import os


from helper_classes.assistant import MinorOperations
from data_storage.keyboards import Keyboards
from data_storage.emojis import *
from exeptions import *


helper = MinorOperations()
bank_of_keys = Keyboards()
router = Router()
emojis =Emojis()


@router.message(Command('secret'))
async def get_pass(message: Message, state: FSMContext):
    await message.answer(f"{emojis.ALLERT} Для доступа в режим менеджера введите пароль {emojis.ALLERT}")
    await state.set_state(LoadData.enter_pass)
    
    
#@router.message(StateFilter(LoadData.enter_pass))
async def enter_pass(message: Message, state: FSMContext):
    keyborad = await bank_of_keys.manager_keyboard()
    
    data = await state.get_data()
    attempts = data.get('attempts', 0)
    
    manager_password = await helper.get_manager_password()
    max_attempts = int(await helper.get_attempts_enter_wrong_password())
    
    if (attempts < max_attempts) and (hashlib.sha256(message.text.encode()).hexdigest() == manager_password):
        await message.answer(f"{emojis.SUCCESS} Доступ разрешен! {emojis.SUCCESS}")
        await message.answer(f"{emojis.ARROW_DOWN} Выберите одно из нижеперечисленных действий {emojis.ARROW_DOWN}", reply_markup=keyborad.as_markup())
   #     await state.set_state(LoadData.choose_action)
    else:
        attempts += 1
        await state.update_data(attempts=attempts)
        
        if attempts >= max_attempts:
            await message.answer(f"{emojis.FAIL} Превышен лимит попыток ввода пароля {emojis.FAIL}")
            await message.answer(f"{emojis.ALLERT} Доступ заблокирован! {emojis.ALLERT}\n\nДля разблокировки обратитесь к администратору @raptor_f_22")
        else:
            await message.answer(f"{emojis.FAIL} Доступ запрещён! {emojis.FAIL}")
            await message.answer(f"{emojis.ALLERT} Осталось попыток: {max_attempts - attempts} {emojis.ALLERT} ")
        

@router.callback_query(F.data == "upload_new_batch")
async def action_1(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(f'Выбрано: {emojis.SUCCESS} Загрузить данные о новой партии товара')
    await callback.message.answer('Пожалуйста отправьте мне EXEL файл с данными')

  #  await state.set_state(LoadData.upload_new_batch)
    await callback.answer()


@router.callback_query(F.data == "get_user_data")
async def action_2(callback: CallbackQuery,  state: FSMContext, bot: Bot):
    await callback.message.answer(f'Выбрано: {emojis.SUCCESS} Получить данные о пользователях')
    
   # user_data = await db_interface.get_user_table()
    zip_name = await helper.create_user_data_exel_document(user_data, callback.message.from_user.id)
    
    chat_id = callback.message.chat.id
    send_zip_name = FSInputFile(zip_name)
    
    await bot.send_document(chat_id=chat_id, document=send_zip_name)
    os.remove(zip_name)
    
    await state.clear()
    await callback.answer()

    
@router.callback_query(F.data == "get_scanned_product_data")
async def action_3(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.answer(f'Выбрано: {emojis.SUCCESS} Получить данные об отсканированном товаре')
    #scanned_data = await db_interface.get_scanned_table()
    zip_name = await helper.create_scanned_data_exel_document(scanned_data, callback.message.from_user.id)
    
    chat_id = callback.message.chat.id
    send_zip_name = FSInputFile(zip_name)
    
    await bot.send_document(chat_id=chat_id, document=send_zip_name)
    os.remove(zip_name)
    
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "get_unscanned_product_data")
async def action_4(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.answer(f'Выбрано: {emojis.SUCCESS} Получить данные о не отсканированном товаре')
  #  unscanned_data = await db_interface.get_unscanned_table()
   # zip_name = await helper.create_unscanned_data_exel_document(unscanned_data, callback.message.from_user.id)
    
    chat_id = callback.message.chat.id
    send_zip_name = FSInputFile(zip_name)
    
    await bot.send_document(chat_id=chat_id, document=send_zip_name)
    os.remove(zip_name)
    
    await state.clear()
    await callback.answer()

    
@router.callback_query(F.data == "get_full_export")
async def action_5(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.answer(f'Выбрано: {emojis.SUCCESS} Получить общую выгрузку базы данных')
    
  #  user_data = await db_interface.get_user_table()
  #  scanned_data = await db_interface.get_scanned_table()
   # unscanned_data = await db_interface.get_unscanned_table()
    
   # zip_name = await helper.create_full_bd_exel_document(user_data, scanned_data, unscanned_data, callback.message.from_user.id)
    
    chat_id = callback.message.chat.id
   #send_zip_name = FSInputFile(zip_name)
    
   # await bot.send_document(chat_id=chat_id, document=send_zip_name)
  #  os.remove(zip_name)
    
    await state.clear()
    await callback.answer()
    




#@router.message(StateFilter(LoadData.upload_new_batch))
async def load_data(message: Message, state: FSMContext,  bot: Bot):
    if message.document:
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path

        # Скачиваем файл
        downloaded_file = await bot.download_file(file_path)
        
        # Сохраняем файл на сервере
        path_table = f'./downloads/{message.document.file_name}'
        with open(f'./downloads/{message.document.file_name}', 'wb') as new_file:
            new_file.write(downloaded_file.read())
            
        await message.answer(f'{emojis.TIME} Загрузка данных началась')
        try:
   #         uploaded_data =  await db_interface.load_data(path_table)

            # Чтение данных из листа
            for row in uploaded_data:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                date = row[0][1]
                date = date.replace('.', '')
                stroke = date + "-" + str(row[0][2]) + "-" +  str(row[0][3])
                #await message.answer(stroke)

                link = await create_start_link(bot, stroke)
                link = link.replace('-', '=')

                qr.add_data(link)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                name_qr_code = 'qr_code' + str(row[0][2]) + '.png'
                img.save(f'./photos/{name_qr_code}')
    
            zip_filename = 'qr_codes.zip'
            qr_codes_folder = 'photos'
            items = os.listdir(qr_codes_folder)
            await helper.create_zip("qr_codes.zip", qr_codes_folder, "w")

            chat_id = message.chat.id

             # Создаем экземпляр FSInputFile с путем к файлу
            archive_file = FSInputFile(zip_filename)

            await bot.send_document(chat_id=chat_id, document=archive_file)
            await message.answer(f"{emojis.SUCCESS}Данные загружены.\nАрхив с QR-кодами сгенерирован и отправлен")
            
            for photo in items:
                os.remove(qr_codes_folder +'/' +photo)
            os.remove(path_table)
            os.remove(zip_filename)
            
        except DoubleDataExeption:
            await message.answer('В загружаемой вами таблице нету ни одного уникального значения, все данные уже загружены в базу товаров')
    else:
        await message.answer('Пожалуйста, отправьте файл для скачивания.')





