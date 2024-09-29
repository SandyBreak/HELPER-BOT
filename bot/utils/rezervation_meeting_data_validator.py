# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta

import logging
from utils.assistant import MinorOperations
from services.postgres.rezervation_meeting_service import RezervationMeetingService
from exceptions.errors import *


class CheckData:
	def __init__(self, user_id: int) -> None:
		self.user_id = user_id


	async def check_room_for_accuracy(self, office: str) -> None:    
		"""
		Проверка адреса переговорной комнаты на корректность
		"""
		try:
			office_data_map = {
            	'mosenka':'Бизнес-центр \"Mosenka-park-towers\"',
            	'empire': 'Москва-Сити башня \"Империя\"'
        	}
			await RezervationMeetingService.save_data(self.user_id, 'office', office_data_map[office])
			return office_data_map[office]
		except Exception as e:
			logging.error(f"Error during check_room_for_accuracy: {e}")
	
	
	async def checking_the_date_for_accuracy(self, entered_date: str) -> None:
		"""
		Проверка даты на корректность
		"""
		try:
			date = datetime.strptime(entered_date, '%d.%m')
   
			if date.month < datetime.now().month:
				date = datetime.strptime(entered_date + '.' + str(datetime.now().year+1), '%d.%m.%Y')
			else:
				date = datetime.strptime(entered_date + '.' + str(datetime.now().year), '%d.%m.%Y')
				
			await RezervationMeetingService.save_data(self.user_id, 'date', date.strftime('%Y-%m-%d'))
			
			await self.get_available_time_for_meeting(date)
			return date
		except Exception as e:
			logging.error(f"Error during checking_the_date_for_accuracy: {e}")

			
	async def get_available_time_for_meeting(self, entered_date: str) -> None:
		"""Получение временных интервалов недоступных временных интервалов для создания конференции и сохранение их в базу данных

		Args:
			entered_date (str): Дата выбранная пользователем для создания конференции
		"""
		office = await RezervationMeetingService.get_data(self.user_id, 'office')
		meeting_list = await RezervationMeetingService.get_illegel_intervals(entered_date, office)
		illegal_intervals = {office: []}
		for meeting in meeting_list:
			illegal_intervals[office].append((meeting[0].strftime("%Y-%m-%dT%H:%M"),  (meeting[0] + timedelta(minutes=meeting[1])).strftime("%Y-%m-%dT%H:%M")))
		
		
		print('==============')
		print(illegal_intervals)
		print('==============')

		if illegal_intervals:
			await RezervationMeetingService.save_data(self.user_id, "illegal_intervals", illegal_intervals)
	
 
	async def checking_the_start_time_for_accuracy(self, entered_start_time: str) -> None:
		"""
  			Проверка времени начала конференции на корректность

		Args:
			entered_start_time (str): Время начала конференции выбраное пользователем

		Raises:
			LongTimeInputError: Ошибка пересечения конференций
			DataInputError: Любая другая ошибка
		"""
		entered_date = await RezervationMeetingService.get_data(self.user_id, 'date')
		illegal_intervals = await RezervationMeetingService.get_data(self.user_id, 'illegal_intervals')
		
		try:
			start_time = datetime.strptime(entered_date + entered_start_time, '%Y-%m-%d%H:%M')

			is_time_valid = True  # Флаг для проверки корректности времени
			response_logs = []
   
			for account_intervals in illegal_intervals.values():
				print(account_intervals)
				for start, end in account_intervals:
					start = datetime.strptime(start, "%Y-%m-%dT%H:%M")
					end = datetime.strptime(end, "%Y-%m-%dT%H:%M")

        	        # Проверка, попадает ли start_time в интервал
					if (start_time >= start and start_time < end):
						is_time_valid = False
						break
				response_logs.append(is_time_valid)
				is_time_valid = True
    
			print('response_logs:', response_logs)
			if not True in response_logs:
				raise LongTimeInputError
			else:
				await RezervationMeetingService.save_data(self.user_id, 'start_time', entered_start_time)
    
		except LongTimeInputError:
			raise LongTimeInputError
		except Exception as e:
			logging.error(f"Error during checking_the_start_time_for_accuracy: {e}")
			raise DataInputError


	async def checking_the_duration_meeting_for_accuracy(self, duration: str) -> None:
		"""
		Проверка продолжительности конференции на корректность
		"""
		entered_date = await RezervationMeetingService.get_data(self.user_id, 'date')
		start_time = await RezervationMeetingService.get_data(self.user_id, 'start_time')
		illegal_intervals = await RezervationMeetingService.get_data(self.user_id, 'illegal_intervals')
		
		
		try:
			start_conference = datetime.strptime(entered_date + start_time, '%Y-%m-%d%H:%M')
			
			duration_hours = await MinorOperations.duration_conversion(duration)
			valid_account_found = False
			counter_account = 0
			if illegal_intervals:
				for account_intervals in illegal_intervals.values():
					if await MinorOperations.is_duration_valid(account_intervals, start_conference, duration_hours):
						valid_account_found = True
						break
					counter_account += 1
				if not valid_account_found:
					raise LongTimeInputError
			else:
            	# Если нет недоступных интервалов, просто сохраняем данные
				valid_account_found = True
			update = duration_hours
			await RezervationMeetingService.save_data(self.user_id, 'duration', update)
		except LongTimeInputError:
			raise LongTimeInputError
		except Exception as e:
			logging.error(f"Error during checking_the_duration_meeting_for_accuracy: {e}")
			raise DataInputError