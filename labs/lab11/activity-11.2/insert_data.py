from datetime import datetime, timedelta, timezone
from bson import ObjectId
from pymongo import MongoClient, InsertOne

client = MongoClient("mongodb://localhost:27217/")
db = client["lab11db"]

hotspot = db["hotspot_data"]
even = db["even_data"]

TOTAL = 10000
BASE_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)

hotspot.delete_many({})
even.delete_many({})

print("Preparing 10,000 documents for each collection...")

hotspot_docs = []
even_docs = []

for i in range(TOTAL):
    hotspot_docs.append({
        "ts": BASE_DATE + timedelta(seconds=i),
        "event_id": i,
        "message": f"Timestamp event {i}"
    })

    even_docs.append({
        "user_id": ObjectId(),
        "event_id": i,
        "message": f"User event {i}"
    })

print("Inserting timestamp-based documents...")
hotspot.insert_many(hotspot_docs, ordered=False)

print("Inserting hashed-key documents...")
even.insert_many(even_docs, ordered=False)

print("\nInsertion completed.")
print("hotspot_data:", hotspot.count_documents({}))
print("even_data:", even.count_documents({}))

client.close()
