# -*- coding: UTF-8 -*-

from aiogram.fsm.state import State, StatesGroup
     
class FindContact(StatesGroup):
    enter_type_office = State()
    send_order = State()

class GainAccess(StatesGroup):
    enter_type_office = State()
    send_order = State()

class OrderCutway(StatesGroup):
    enter_type_office = State()
    send_order = State()

class OrderOffice(StatesGroup):
    enter_type_office = State()
    send_order = State()


class OrderPass(StatesGroup):
    enter_type_office = State()
    send_order = State()


class OrderTaxi(StatesGroup):
    get_fio_customer = State()
    enter_adress = State()
    choose_rate = State()
    get_phone_and_send_order = State()


class OrderTechnic(StatesGroup):
    enter_type_office = State()
    send_order = State()
    

class CreateMeetingStates(StatesGroup):
    """
    Состояния для создания новой конференции
    """
    get_room = State()
    get_date = State()
    get_start_time = State()
    get_duration = State()
    get_name_create_meeting = State()
    
    
class DeleteMeetingStates(StatesGroup):
    """
    Состояния для удаления конференции
    """
    delete_room = State()
    
class GetListMeetingStates(StatesGroup):
    """
    Состояния для просмотра запланированных конференции
    """
    get_room = State()
    get_date_and_get_planned_meetings = State()