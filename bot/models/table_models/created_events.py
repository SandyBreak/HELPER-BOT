# -*- coding: UTF-8 -*-

from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from .base import Base

class CreatedEvent(Base):
    __tablename__ = 'created_events'
    
    id = Column(Integer, primary_key=True, nullable=False)
    creator_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="created_events")

    date_creation = Column(TIMESTAMP, nullable=False) 
    type_event = Column(String(length=128), nullable=False) 
    
    office = Column(String(length=128), nullable=True)
    info = Column(String(length=2048), nullable=True)
    
    delivery_rate = Column(String(length=128), nullable=True)
    taxi_rate = Column(String(length=128), nullable=True)
    
    departure_address = Column(String(length=256), nullable=True)
    destination_address = Column(String(length=256), nullable=True)
    
    customer_fio = Column(String(length=256), nullable=True)
    customer_phone = Column(String(length=32), nullable=True)
    
    recipient_fio = Column(String(length=256), nullable=True)
    recipient_phone = Column(String(length=32), nullable=True)
    
