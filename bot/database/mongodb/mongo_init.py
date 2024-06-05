from motor.motor_asyncio import AsyncIOMotorClient
import os
from bson import ObjectId
from helper_classes.assistant import MinorOperations

helper = MinorOperations()

async def create_db():
    try:
        login = await helper.get_mongo_login()
        password = await helper.get_mongo_password()
        new_db = AsyncIOMotorClient(f'mongodb://localhost:27017')
        
        
        new_table = new_db["meeting_rooms"]
        col = new_table['current_data_f_new_meeting']
        col = new_table['created_meetings']
        
        obj = {"_id": ObjectId("65f7110e4e9a3762bba43801"), "users": []}
        obj = {"_id": ObjectId("665dd5e9513d61f6a8a66843"), "users": []}
        await col.insert_one(obj)
    except Exception as e:
        print(e)