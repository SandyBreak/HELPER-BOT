import schedule
import asyncio
import time


from database.mongodb.interaction import Interaction


mongo_db = Interaction()


# Запускаем функцию каждые 60 минут
schedule.every(2).seconds.do(lambda: asyncio.get_event_loop().run_until_complete(mongo_db.delete_the_expired_meeting()))

while True:
    schedule.run_pending()
    time.sleep(1)