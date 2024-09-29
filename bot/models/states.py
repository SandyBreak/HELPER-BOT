# -*- coding: UTF-8 -*-

from aiogram.fsm.state import State, StatesGroup
    
class UniversalEventRouterStates(StatesGroup):
    get_info = State()
    send_order = State()

class OrderTaxi(StatesGroup):
    get_fio_recipient = State()
    get_departure_address = State()
    get_destination_address = State()
    choose_rate = State()
    get_phone_and_send_order = State()

class OrderDelivery(StatesGroup):
    get_office = State()
    choose_rate = State()
    get_departure_address = State()
    get_destination_address = State()
    get_info = State()
    get_fio_recipient = State()
    get_recipient_phone = State()  
    get_customer_phone_and_send_order = State()

class RezervationMeetingStates(StatesGroup):
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
    
    
class RegUserStates(StatesGroup):
    """
    Состояния для регистрации пользователя
    """
    get_fio = State()
