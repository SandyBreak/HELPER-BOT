# -*- coding: UTF-8 -*-

from sqlalchemy import Column, String, Integer, Float, Boolean, ARRAY, TIMESTAMP, BigInteger, JSON

from .base import Base


class TemporaryEventsData(Base):
    __tablename__ = 'temporary_events_data'
    
    id = Column(Integer, primary_key=True)
    
    id_tg = Column(BigInteger, nullable=False)
    
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
    