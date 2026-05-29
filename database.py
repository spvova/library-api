# database.py
from pymongo import MongoClient
import os

# Створюється ОДИН раз і безпечно використовується всіма потоками Flask
mongo_uri = os.getenv("MONGODB_URL", "mongodb://mongo_admin:password@localhost:27017/?authSource=admin")
client = MongoClient(mongo_uri)

db = client["library"]

def get_db():
    return db