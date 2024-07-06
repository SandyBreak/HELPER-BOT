from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import logging

from helper_classes.assistant import MinorOperations

helper = MinorOperations()


async def create_db():
    try:
        """
        Подключение к базе для локального развертывания проекта
        """
        #new_db = AsyncIOMotorClient(f'mongodb://localhost:27017')
        
        """
        Подключение к базе для развертывания проекта на сервере
        """
        user = helper.get_mongo_login()
        password = helper.get_mongo_password()
        new_db = AsyncIOMotorClient(f'mongodb://{user}:{password}@mongodb:27017')
        
        
        new_table = new_db["helper_bot"]
        general_info_about_user = new_table['general_info_about_user'] #Коллекция с данными о пользователях
        meeting_rooms = new_table['meeting_rooms'] #Коллекция с данными о сделанных запросах
        happened_events = new_table['happened_events'] #Коллекция с данными о созданных конференциях
         
        users = {"_id": ObjectId("665dd5e9513d61f6a8a66843"), "users": []}
        created_meetings = {"_id": ObjectId("65f7110e4e9a3762bba43801"), "created_meetings": []}
        events = {"_id": ObjectId("66606c99b6c0c50083906389"), "events": []}
        
        await general_info_about_user.insert_one(users)
        await meeting_rooms.insert_one(created_meetings)
        await happened_events.insert_one(events)
        
    except Exception as e:
        logging.error(e)