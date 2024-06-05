# -*- coding: UTF-8 -*-

from aiogram.fsm.state import State, StatesGroup
     
    
class OrderPass(StatesGroup):
    keyboard_entry_break = State()
    manual_entry_break = State()
    enter_type_office = State()