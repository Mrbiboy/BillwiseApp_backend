from motor.motor_asyncio import AsyncIOMotorClient
import os

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(os.getenv("DATABASE_URL", "mongodb://localhost:27017"))
    db.database = db.client.billwise

async def close_mongo_connection():
    db.client.close()

async def get_db():
    if db.database is None:
        await connect_to_mongo()
    return db.database

async def save_prediction(prediction_data: dict):
    if db.database is not None:
        await db.database.predictions.insert_one(prediction_data)