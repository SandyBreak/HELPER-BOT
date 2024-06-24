# -*- coding: UTF-8 -*-

from bson import ObjectId
import logging

from database.mongodb.interaction import Interaction
from helper_classes.assistant import MinorOperations



helper = MinorOperations()
mongo_db = Interaction()

class Initialization:
	def __init__(self, user_id: str, user_name: str) -> None:
		self.user_id = user_id
		self.user_name = user_name

	async def init_user(self) -> str:
		"""
		Инициализация юзера в ячейке хранения данных
		"""
		document = await mongo_db.find_data({"_id": ObjectId("665dd5e9513d61f6a8a66843")})
		quantity_users = len(document['users'])
		user_log = 0

		for users in range(quantity_users):
			is_user_log_in= document['users'][users]['tg_id']
			if is_user_log_in == self.user_id:# Поиск ячейки хранения данных для пользователя
				user_log = 1
				break

		if not(user_log):
			new_user = {
	        	'tg_id': self.user_id,
				'tg_addr': f'@{self.user_name}',
	        	'date': '',
				'choosen_room': 0,
	        	'start_time': '',
	        	'duration_meeting': 0,
				'illegal_intervals': [],
				'secondary_data': ''
	    }

			update = {'$push': {'users': new_user}}
			await mongo_db.update_data(document, update)

			logging.info(f"Added new user: {self.user_id} Total number of users: {quantity_users}")


	async def delete_user_meeting_data(self) -> None:
		"""
		Обнуление массива с данными о создаваемой конференции в данный момент 
		"""
		filter_by_id = {'users.tg_id': self.user_id}
		delete_data = {'$set': {'users.$.date': '', 'users.$.choosen_zoom': 0, 'users.$.start_time': '', 'users.$.duration_meeting': 0, 'users.$.illegal_intervals': [], 'users.$.fio': ''}}

		await mongo_db.update_data(filter_by_id, delete_data)
  


	