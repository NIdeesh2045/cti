import os
import random
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING

load_dotenv("../activity-15.1/.env")

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in activity-15.1/.env")

client = MongoClient(MONGO_URI)
db = client["tenant_migration"]
tasks = db["tasks"]

tenants = ["tenant_a", "tenant_b", "tenant_c", "tenant_d", "tenant_e"]

# Clear only the Lab 15.2 migration collection.
tasks.delete_many({})

documents = []

for tenant_id in tenants:
    for i in range(1, 101):
        documents.append({
            "tenant_id": tenant_id,
            "task_number": i,
            "title": f"{tenant_id} Task {i}",
            "status": random.choice(["open", "in_progress", "completed"]),
            "priority": random.choice(["low", "medium", "high"]),
            "created_at": datetime.now(timezone.utc),
            "owner": f"user_{(i % 5) + 1}"
        })

result = tasks.insert_many(documents)

tasks.create_index(
    [("tenant_id", ASCENDING), ("created_at", ASCENDING)],
    name="tenant_created_at"
)

print("Database:", db.name)
print("Inserted documents:", len(result.inserted_ids))

for tenant_id in tenants:
    print(tenant_id, ":", tasks.count_documents({"tenant_id": tenant_id}))

print("Total documents:", tasks.count_documents({}))

client.close()
