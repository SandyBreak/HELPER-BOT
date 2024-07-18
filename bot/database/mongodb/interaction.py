# -*- coding: UTF-8 -*-

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from typing import Union
from bson import ObjectId
import logging

from helper_classes.assistant import MinorOperations



helper = MinorOperations()

class Interaction:
	#def __init__(self) -> None:#Инициализатор класса для локального запуска проекта
	#	mongo_client = AsyncIOMotorClient(f'mongodb://localhost:27017')
	#	self.__db = mongo_client['helper_bot']
	#	self.__current_data = self.__db['general_info_about_user'] #Коллекция с данными о пользователях
	#	self.__happened_events =  self.__db['happened_events'] #Коллекция с данными о сделанных запросах
	#	self.__created_meetings =  self.__db['meeting_rooms'] #Коллекция с данными о созданных конференциях

	def __init__(self,) -> None:#Инициализатор класса для запуска проекта на сервере
		user = helper.get_mongo_login()
		password = helper.get_mongo_password()
		mongo_client = AsyncIOMotorClient(f'mongodb://{user}:{password}@mongodb:27017')
		self.__db = mongo_client['helper_bot']
		self.__current_data = self.__db['general_info_about_user']	#Коллекция с данными о пользователях
		self.__happened_events =  self.__db['happened_events']	#Коллекция с данными о сделанных запросах
		self.__created_meetings =  self.__db['meeting_rooms']	#Коллекция с данными о созданных конференциях
  
	
	async def find_data(self, filter: dict) -> dict:
		"""
    	Точка входа в таблицу с данными о пользователях
    	"""
		return await self.__current_data.find_one(filter)

	
	async def update_data(self, filter: dict, update: int) -> None:
		"""
    	Обновление данных о создаваемой конференции
    	"""
		await self.__current_data.update_one(filter, update)

	
	async def get_data(self, user_id: int, type_data: str) -> Union[int, str, float, dict]:
		"""
    	Получение данных о создаваемой конференции
    	"""
		filter_by_id = {'tg_id': user_id}
		result = await self.__current_data.find_one({'users': {'$elemMatch': filter_by_id}},{'users.$': 1})

		return result['users'][0][f'{type_data}']

	
	async def document_the_event(self, type_event: str, current_date: str, office: str, fullname: str, tg_addr: str, info: str) -> None:
		"""
    	Создание записи о запросе сделанном пользователем
    	"""
		document = await self.__happened_events.find_one({"_id": ObjectId("66894f046b7cfb15ca1d84e3")})
		new_order = {
			'type_event': type_event,
   			'date_of_creation': current_date,
			'creator_addr': f'@{tg_addr}',
			'creator name': fullname,
			'office': office,
			'info': info
     	}
		update = {'$push': {'events': new_order}}
		response = await self.__happened_events.update_one(document, update)
		logging.info(f'Journal event are {response.acknowledged}')
	
 
	
	async def document_the_meeting(self, user_id: int, user_addr: str, name_meeting: str)  -> None:
		"""
    	Создание записи о созданной конференции
    	"""
		document = await self.__created_meetings.find_one({"_id": ObjectId("66894f166b7cfb15ca1d84e6")})
		new_order = {
			"tg_id": user_id,
      		"tg_addr": user_addr,
      		"date": await self.get_data(user_id, 'date'),
      		"choosen_room": await self.get_data(user_id, 'choosen_room'),
      		"start_time": await self.get_data(user_id, 'start_time'),
      		"duration_meeting": await self.get_data(user_id, 'duration_meeting'),
			"name": name_meeting
     	}
		update = {'$push': {'created_meetings': new_order}}
		response = await self.__created_meetings.update_one(document, update)
		logging.info(f'Journal meeting are {response.acknowledged}')


	async def get_list_meetings_for_user(self, user_id: int) -> dict:
		"""
    	Получение списка конференций созданных ползователем
    	"""
		list_meetings = await self.__created_meetings.find_one({"_id": ObjectId("66894f166b7cfb15ca1d84e6")})
  
		quantity_meetings = len(list_meetings['created_meetings'])
		created_meetings = []
		for meeting in range(quantity_meetings):
			creator_id = list_meetings["created_meetings"][meeting]["tg_id"]
			if creator_id == int(user_id):
				created_meetings.append(list_meetings["created_meetings"][meeting])

		return created_meetings


	async def get_list_meetings_for_all(self, user_id: int) -> dict:
		"""
    	Получение списка конференций созданных всеми пользователями
    	"""
		list_meetings = await self.__created_meetings.find_one({"_id": ObjectId("66894f166b7cfb15ca1d84e6")})
  
		date = await self.get_data(user_id, 'date')
		room = await self.get_data(user_id, 'choosen_room')

		quantity_meetings = len(list_meetings['created_meetings'])
		created_meetings = []
  
		for meeting in range(quantity_meetings):
			date_meeting = list_meetings["created_meetings"][meeting]["date"]
			room_meeting = list_meetings["created_meetings"][meeting]["choosen_room"]
			if (date_meeting == date) and (room_meeting == room):
				created_meetings.append(list_meetings["created_meetings"][meeting])

		return created_meetings


	async def delete_user_meeting(self, name_meeting: str, start_time: str) -> None:
		"""
    	Удаление конференции которую выбрал пользователь
    	"""
		list_meetings = await self.__created_meetings.find_one({"_id": ObjectId("66894f166b7cfb15ca1d84e6")})
		quantity_meetings = len(list_meetings['created_meetings'])
		for meeting in range(quantity_meetings):
			if list_meetings["created_meetings"][meeting]["name"] == name_meeting and list_meetings["created_meetings"][meeting]["start_time"] == start_time:

				result = await self.__created_meetings.update_one(
					{"_id": ObjectId("66894f166b7cfb15ca1d84e6")},
					{"$pull": {"created_meetings": list_meetings["created_meetings"][meeting]}}
    	        )
				logging.info(f"{result.modified_count} meeting record deleted.")


	async def delete_the_expired_meeting(self) -> None:
		"""
    	Удаление конференций которые уже состоялись
    	"""
		list_meetings = await self.__created_meetings.find_one({"_id": ObjectId("66894f166b7cfb15ca1d84e6")})

		now = datetime.now()
		quantity_meetings = len(list_meetings['created_meetings'])
  
		for meeting in range(quantity_meetings):
			meeting_date = list_meetings["created_meetings"][meeting]["date"]
			meeting_time = list_meetings["created_meetings"][meeting]["start_time"]
			meeting_datetime = datetime.strptime(meeting_date+meeting_time,"%Y-%m-%d%H:%M")
			expired_time = meeting_datetime + timedelta(minutes=30)
			logging.info('ОК')

			if now > expired_time:
				result = await self.__created_meetings.update_one(
					{"_id": ObjectId("66894f166b7cfb15ca1d84e6")},
					{"$pull": {"created_meetings": list_meetings["created_meetings"][meeting]}}
    	        )
				logging.info(f"{result.modified_count} meeting record deleted.")
	
	
	async def get_illegal_intervals(self, user_id: int, date: str) -> dict:
		"""
    	Получение временных интервалов, недоступных для создания конференции
    	"""
		document = await self.__created_meetings.find_one({"_id": ObjectId("66894f166b7cfb15ca1d84e6")})
		intervals =[]
  
		quantity_meetings = len(document['created_meetings'])

		for meetings in range(quantity_meetings):
			similar_date = document['created_meetings'][meetings]['date']
			similar_room = document['created_meetings'][meetings]['choosen_room']
			room = await self.get_data(user_id, 'choosen_room')
			if similar_date == date and room == similar_room:# Поиск ячейки хранения данных для пользователя
				intervals.append([document['created_meetings'][meetings]['start_time'], document['created_meetings'][meetings]['duration_meeting']])
    
		return intervals

	async def get_users_id(self):
		document = await self.find_data({"_id": ObjectId("66894ef06b7cfb15ca1d84e0")})
		quantity_users = len(document['users'])
		users_ids = []
		for users in range(quantity_users):
			user_id = document['users'][users]['tg_id']
			users_ids.append(str(user_id))
		
		return users_ids
