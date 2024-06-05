from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import logging
from helper_classes.assistant import MinorOperations

helper = MinorOperations()

async def create_db():
    try:
        login = await helper.get_mongo_login()
        password = await helper.get_mongo_password()
        new_db = AsyncIOMotorClient(f'mongodb://localhost:27017')
        
        
        new_table = new_db["helper_bot"]
        col1 = new_table['general_info_about_user']
        col2 = new_table['meeting_rooms']
        col3 = new_table['happened_events']
         
        obj1 = {"_id": ObjectId("665dd5e9513d61f6a8a66843"), "users": []}
        obj2 = {"_id": ObjectId("65f7110e4e9a3762bba43801"), "created_meetings": []}
        obj3 = {"_id": ObjectId("66606c99b6c0c50083906389"), "events": []}
        
        await col1.insert_one(obj1)
        await col2.insert_one(obj2)
        await col3.insert_one(obj3)
        
    except Exception as e:
        logging.error(e)