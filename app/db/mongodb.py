# app/db/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongodb = MongoDB()

async def connect_to_mongo():
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGO_URI)
        mongodb.db = mongodb.client[settings.MONGO_DB_NAME]
        print(f"✅ MongoDB connected successfully: {settings.MONGO_DB_NAME}")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)

async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        print("🛑 MongoDB connection closed.")
