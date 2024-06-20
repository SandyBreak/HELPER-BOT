# -*- coding: UTF-8 -*-

from aiogram.fsm.state import State, StatesGroup
     

class OrderPass(StatesGroup):
    enter_fio = State()
    enter_type_office = State()
    send_order = State()


class OrderOffice(StatesGroup):
    enter_fio = State()
    enter_type_office = State()
    send_order = State()
    

class OrderTechnic(StatesGroup):
    enter_type_break = State()
    enter_type_office = State()
    send_order = State()
    

class GainAccess(StatesGroup):
    enter_type_access = State()
    enter_type_office = State()
    send_order = State()
    
    
class OrderTaxi(StatesGroup):
    enter_adress = State()
    send_order = State()