import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(
    os.getenv("MONGO_URI"),
    serverSelectionTimeoutMS=10000
)

try:
    print(client.admin.command("ping"))
    print("MongoDB Atlas connected successfully!")
finally:
    client.close()
    