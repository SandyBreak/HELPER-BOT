# -*- coding: UTF-8 -*-

from aiogram.fsm.state import State, StatesGroup
     
class FindContact(StatesGroup):
    enter_type_office = State()
    send_order = State()

class GainAccess(StatesGroup):
    enter_type_office = State()
    send_order = State()


class OrderOffice(StatesGroup):
    enter_type_office = State()
    send_order = State()


class OrderPass(StatesGroup):
    enter_type_office = State()
    send_order = State()


class OrderTaxi(StatesGroup):
    enter_adress = State()
    send_order = State()


class OrderTechnic(StatesGroup):
    enter_type_office = State()
    send_order = State()
    

    
    