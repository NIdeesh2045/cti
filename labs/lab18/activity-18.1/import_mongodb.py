
import json
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient, InsertOne, DESCENDING

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "threats_100k.jsonl"

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "lab18_threats"

BATCH_SIZE = 2000

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")

db = client[DATABASE_NAME]
threats = db["threats"]
full_threats = db["full_threats"]

# Prevent accidental duplicate imports.
existing_count = full_threats.count_documents({})

if existing_count > 0:
    raise RuntimeError(
        f"Import stopped: {existing_count} records already exist "
        "in lab18_threats.full_threats. No records were inserted."
    )

print("Connected to Lab18 MongoDB successfully!")
print("Starting import of synthetic threat records...")

batch = []
total_inserted = 0

with DATA_FILE.open("r", encoding="utf-8") as file:
    for line in file:
        if not line.strip():
            continue

        record = json.loads(line)

        # Convert ISO timestamp into a MongoDB datetime.
        record["published_at"] = datetime.fromisoformat(
            record["published_at"]
        )

        batch.append(InsertOne(record))

        if len(batch) >= BATCH_SIZE:
            result = full_threats.bulk_write(batch, ordered=False)
            total_inserted += result.inserted_count
            batch.clear()

            if total_inserted % 10000 == 0:
                print(f"Inserted: {total_inserted:,}")

if batch:
    result = full_threats.bulk_write(batch, ordered=False)
    total_inserted += result.inserted_count

# Maintain the dashboard document with the latest 50 threats.
latest = list(
    full_threats.find(
        {},
        {"_id": 0}
    ).sort("published_at", DESCENDING).limit(50)
)

threats.update_one(
    {"_id": "lab18_dashboard"},
    {
        "$set": {
            "recent_threats": latest,
            "total_threats": total_inserted,
            "is_synthetic": True,
            "last_updated": datetime.now(timezone.utc)
        }
    },
    upsert=True
)

final_count = full_threats.count_documents({})
dashboard = threats.find_one({"_id": "lab18_dashboard"})

print("\nMongoDB import completed!")
print(f"Inserted this run: {total_inserted:,}")
print(f"Verified total records: {final_count:,}")
print(f"Dashboard recent threats: {len(dashboard['recent_threats'])}")
print(f"Database: {DATABASE_NAME}")

client.close()
