# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
from typing import Union
import ast
import os
import logging
from helper_classes.assistant import MinorOperations
from database.mongodb.interaction import Interaction
#from zoom_api.zoom import get_list_meeting
from exeptions import *



helper = MinorOperations()
db = Interaction()


class CheckData:
	def __init__(self, user_id: int) -> None:
		self.user_id = user_id


	async def check_room_for_accuracy(self, choosen_room: str) -> Union[str, dict]:
		"""
		Проверка адреса переговорной комнаты на корректность
		"""
		if choosen_room not in ['Москва-Сити башня \"Империя\"', 'Бизнес-центр \"Mosenka-park-towers\"']:
			raise DataInputError

		try:
			if choosen_room:
				filter_by_id = {'users.tg_id': self.user_id}
				update = {'$set': {'users.$.choosen_room': choosen_room}}
				await  db.update_data(filter_by_id, update)
				return choosen_room

		except Exception as e:
			raise DataInputError
	
	
	async def checking_the_date_for_accuracy(self, entered_date: str) -> str:
		"""
		Проверка даты на корректность
		"""
		if len(entered_date.split('.')) != 2:
			raise DataInputError
		try:
				date = datetime.strptime(entered_date, '%d.%m')

				if date.month < datetime.now().month:
					date = datetime.strptime(entered_date+'.'+str(datetime.now().year+1), '%d.%m.%Y')
				else:
					date = datetime.strptime(entered_date+'.'+str(datetime.now().year), '%d.%m.%Y')
				
				date = date.strftime('%Y-%m-%d')

				filter_by_id = {'users.tg_id': self.user_id}
				update = {'$set': {'users.$.date': f'{date}',}}
				await db.update_data(filter_by_id, update)

				return date
		
		except Exception as e:
				raise DataInputError

			

	async def get_available_time_for_meeting(self,entered_date: str) -> dict:
		"""
		Получение временных интервалов доступных временных интервалов для создания конференции
		"""
		filter_by_id = {'users.tg_id': self.user_id}

		date = datetime.strptime(entered_date, '%Y-%m-%d')


		meeting_list = await db.get_illegal_intervals(self.user_id, date.strftime('%Y-%m-%d'))
		planned_meeting_list = []

		for start, duration in meeting_list:
			start_time = datetime.strptime(entered_date+start, '%Y-%m-%d%H:%M')
			end_time = datetime.strptime(entered_date+start, '%Y-%m-%d%H:%M') + timedelta(hours=duration)
			planned_meeting_list.append([start_time, end_time])
	

		if planned_meeting_list:
			update = {'$set': {'users.$.illegal_intervals': planned_meeting_list}}
			await db.update_data(filter_by_id, update)

			return planned_meeting_list
	



	async def checking_the_start_time_for_accuracy(self, entered_start_time: str) -> None:
		"""
		Проверка времени начала конференции на корректность
		"""
		if len(entered_start_time.split(':')) != 2:
			raise DataInputError
		
		filter_by_id = {'users.tg_id': self.user_id}
		entered_date = await db.get_data(self.user_id, 'date')
		illegal_intervals = await db.get_data(self.user_id, 'illegal_intervals')

		try:
			start_time = datetime.strptime(entered_date + entered_start_time, '%Y-%m-%d%H:%M')

			if start_time.minute %30 != 0:
				raise HalfTimeInputError
			
			response_logs = []
			for start, end in illegal_intervals:

				if ((start_time > start) and (start_time >= end)) or ((start_time < start) and (start_time <= end)):
					response_logs.append('True')
				else:
					response_logs.append('False')
					
			if 'False' in response_logs:
				raise LongTimeInputError
			else:
				update = {'$set': {'users.$.start_time': entered_start_time}}
				await db.update_data(filter_by_id, update)

		except Exception as e:
				raise DataInputError


	async def checking_the_duration_meeting_for_accuracy(self, duration: str) -> None:
		"""
		Проверка продолжительности конференции на корректность
		"""
		
		filter_by_id = {'users.tg_id': self.user_id}
		entered_date = await db.get_data(self.user_id, 'date')
		start_time = await db.get_data(self.user_id, 'start_time')
		illegal_intervals = await db.get_data(self.user_id, 'illegal_intervals')

		if len(start_time.split(':')) != 2:
			raise DataInputError
		
		try:
			date = datetime.strptime(entered_date + start_time, '%Y-%m-%d%H:%M')
			if int(duration[2:]) %15 != 0:
				raise HalfTimeInputError
			
			duration = await helper.duration_conversion(duration)

			if illegal_intervals:
				for start, end in illegal_intervals:
					if ((start < date and end <= date) or (start >= date + timedelta(hours=duration) and end > date + timedelta(hours=duration))):
						update = {'$set': {'users.$.duration_meeting': duration}}
					else:
						raise LongTimeInputError
			else:
				update = {'$set': {'users.$.duration_meeting': duration}}
			await db.update_data(filter_by_id, update)

		except Exception as e:

			raise DataInputError