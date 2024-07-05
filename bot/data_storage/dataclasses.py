# -*- coding: UTF-8 -*-

from dataclasses import dataclass
    
    
@dataclass
class MeetingData:
    """
    Данные о создаваемой конференции
    """
    topic: str
    start_time: str
    duration: int
    office: str