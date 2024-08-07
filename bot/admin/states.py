# -*- coding: UTF-8 -*-

from aiogram.fsm.state import State, StatesGroup
     
    
class ControlPanelStates(StatesGroup):
    enter_pass = State()
    
    launch_global_newsletter = State()
    
    launch_targeted_newsletter = State()
    
    launch_view_list_users = State()
    
    upload_new_batch = State()
    
    restore_error_qr_codes = State()