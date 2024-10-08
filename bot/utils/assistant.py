# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta

from models.dataclasses import MeetingData
from models.text_maps import order_map
from services.postgres.rezervation_meeting_service import RezervationMeetingService
from services.postgres.create_event_service import CreateEventService
from services.postgres.user_service import UserService

class MinorOperations:
    def __init__(self) -> None:
        pass
    
    
    @staticmethod
    async def fill_delivery_event(user_id: int, tracking_flag: bool) -> str:
        """
        Формирование сообщения запроса
        """
        if tracking_flag: 
            tracking_flag = 'Да'
        else: 
            tracking_flag = 'Нет'
            
        departure_address = await CreateEventService.get_data(user_id, 'departure_address')
        destination_address = await CreateEventService.get_data(user_id, 'destination_address')
        recipient_phone = await CreateEventService.get_data(user_id, 'recipient_phone')
        customer_phone = await CreateEventService.get_data(user_id, 'customer_phone')
        delivery_rate = await CreateEventService.get_data(user_id, 'delivery_rate')
        user_data = await UserService.get_user_data(user_id)


        new_order = f"""
        <b>Новый заказ доставки!</b>
        <b>Кто заказал доставку:</b> {user_data.fio}
        <b>Телеграмм заказчика:</b> @{user_data.nickname}
        <b>Адрес получения (окуда нужно забрать заказ):</b> {departure_address}
        <b>Адрес назначения (Куда нужно доставить заказ):</b> {destination_address}
        <b>Тариф доставки:</b> {delivery_rate}
        <b>Телефон отправителя:</b> {customer_phone}
        <b>Телефон получателя:</b> {recipient_phone}
        <b>Нужно ли отслеживать заказ:</b> {tracking_flag} 
        """
        return new_order
    
    
    @staticmethod
    async def fill_taxi_event(user_id: int, phone_number: str) -> str:
        """
        Формирование сообщения запроса
        """
        departure_address = await CreateEventService.get_data(user_id, 'departure_address')
        destination_address = await CreateEventService.get_data(user_id, 'destination_address')
        taxi_rate = await CreateEventService.get_data(user_id, 'taxi_rate')
        user_data = await UserService.get_user_data(user_id)


        new_order = f"""
        <b>Новый заказ такси!</b>
        <b>Кто заказал такси:</b> {user_data.fio}
        <b>Телеграмм заказчика:</b> @{user_data.nickname}
        <b>Адрес отправки:</b> {departure_address}
        <b>Адрес назначения:</b> {destination_address}
        <b>Тариф такси:</b> {taxi_rate}
        <b>Номер телефона кто поедет на такси:</b> {phone_number}
        """
        return new_order
        
    @staticmethod
    async def fill_simple_event_data(user_id: int, office: str, info: str, type_order: str) -> str:
        """
        Формирование сообщения запроса
        """
        user_data = await UserService.get_user_data(user_id)
        order_details = order_map[f'{type_order}']
        new_order = f"""
        <b>Новый {order_details['type_order']}</b>
        <b>Адрес:</b> {office}
        <b>Заказчик:</b> {user_data.fio}
        <b>Телеграмм заказчика:</b> @{user_data.nickname}
        <b>{order_details['order_info']}:</b> {info}
        """
        return new_order
    
    @staticmethod
    async def duration_conversion(duration: str) -> float:
        """
            Конвертация длительности из часов в минуты
            
        Args:
            duration (str): 

        Returns:
            float: _description_
        """
        dec_duration = float('0.' + duration[2:])
        duration = float(duration.replace(":", "."))

        if dec_duration == 0.15:
            duration = duration//1 + 0.25

        elif dec_duration == 0.3:
            duration = duration//1 + 0.5

        elif dec_duration == 0.45:
            duration = duration//1 + 0.75
		
        return duration
        
        
    async def fill_meeting_data_credits(user_id: int, name: str) -> MeetingData:
        """
        Заполнение структуры данными о созданной конференции
        """
        entered_date = await RezervationMeetingService.get_data(user_id, 'date')
        start_time = await  RezervationMeetingService.get_data(user_id, 'start_time')
        duration = await  RezervationMeetingService.get_data(user_id, 'duration')
        office = await  RezervationMeetingService.get_data(user_id, 'office')
        meeting_data = MeetingData(
	        name=name,
	        start_time=datetime.strptime(entered_date + start_time, '%Y-%m-%d%H:%M'),
	        duration=int(duration * 60),
            office=office
	    )
        return meeting_data
    
    
    @staticmethod
    async def create_worktime_slots(entered_date: str) -> list:
        time_slots = []
        start_time = datetime.strptime(entered_date + "09:00", '%Y-%m-%d%H:%M')  # Начало рабочего дня
        end_time = datetime.strptime(entered_date + "19:00", '%Y-%m-%d%H:%M')  # Конец рабочего дня

        current_slot_start = start_time # Текущий временной интервал
        
        # Генерация временных слотов по 30 минут
        while current_slot_start < end_time:
            current_slot_end = current_slot_start + timedelta(minutes=30)
            time_slots.append(current_slot_start)  # Добавляем слот
            current_slot_start = current_slot_end  # Переходим к следующему слоту

        return time_slots


    @staticmethod
    async def is_slot_valid(slot: datetime, account_intervals: list) -> bool:
        for start, end in account_intervals:  # Здесь мы перебираем интервалы
            start = datetime.strptime(start, "%Y-%m-%dT%H:%M")
            end = datetime.strptime(end, "%Y-%m-%dT%H:%M")
	
            if (start <= slot < end) or (slot < datetime.now()):
                return False
        return True


    @staticmethod
    async def is_duration_valid(account_intervals, start_conference, duration_hours):
        """
        Проверка, доступна ли продолжительность для данного аккаунта
        """
        for start, end in account_intervals:
            start = datetime.fromisoformat(start)
            end = datetime.fromisoformat(end)
            if not ((start < start_conference and end <= start_conference) or (start >= start_conference + timedelta(hours=duration_hours) and end > start_conference + timedelta(hours=duration_hours))):
                return False
        return True

    async def is_conflict(start, end, time_slots):
        for slot in time_slots:
            existing_start = datetime.fromisoformat(slot[0])
            existing_end = datetime.fromisoformat(slot[1])
            # Проверка на пересечение
            if start < existing_end and end > existing_start:
                return True
        return False

    @staticmethod
    def get_max_available_duration(illegal_intervals: list, conference_start: datetime, conference_end_limit: datetime):
        illegal_intervals = [(datetime.fromisoformat(start), datetime.fromisoformat(end)) for start, end in illegal_intervals]
        illegal_intervals.sort()

        available_intervals = []
        last_end = conference_start

        for start, end in illegal_intervals:
            if start > last_end:
                if last_end < conference_end_limit:
                    available_intervals.append((last_end, min(start, conference_end_limit)))
            last_end = max(last_end, end)

        if last_end < conference_end_limit:
            available_intervals.append((last_end, conference_end_limit))

        max_duration = timedelta(0)
        for start, end in available_intervals:
            duration = end - start
            if duration > max_duration:
                max_duration = duration
        return max_duration


    @staticmethod
    async def max_duration_for_account(time_slots: list, conference_start: datetime):
        # Проверка длительностей от 30 минут до 9 часов
        min_duration = timedelta(minutes=30)
        max_duration = timedelta(hours=9)
        step = timedelta(minutes=30)

        available_durations = []
        # Генерация всех возможных длительностей
        duration = min_duration
        while duration <= max_duration:
            conference_end = conference_start + duration
            if not await MinorOperations.is_conflict(conference_start, conference_end, time_slots):
                available_durations.append(duration)
            duration += step
        return_max_duration_value = 0
    	# Вывод доступных длительностей
        for duration in available_durations:
            return_max_duration_value = duration
        if return_max_duration_value:
            return conference_start + return_max_duration_value
        else:
            return conference_start
	
    @staticmethod
    async def is_conflict(start, end, time_slots) -> bool:
        for slot in time_slots:
            existing_start = datetime.fromisoformat(slot[0])
            existing_end = datetime.fromisoformat(slot[1])
            # Проверка на пересечение
            if start < existing_end and end > existing_start:
                return True
        return False