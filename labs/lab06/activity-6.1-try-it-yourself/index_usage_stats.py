import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, DESCENDING

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

MONGO_URI = os.getenv("MONGODB_LOCAL_URI")

if not MONGO_URI:
    raise ValueError("MONGODB_LOCAL_URI not found in .env")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")

db = client["lab06_indexing"]
products = db["products"]

print("=" * 65)
print("LAB 6.1 - TRY IT YOURSELF: INDEX USAGE STATISTICS")
print("=" * 65)

print("\n[1] Running representative queries repeatedly...")

for iteration in range(5):
    list(products.find(
        {"category": "Electronics"}
    ).sort("price", ASCENDING).limit(100))

    list(products.find(
        {"price": {"$gte": 100, "$lte": 500}}
    ).limit(100))

    list(products.find(
        {"tags": "wireless"}
    ).limit(100))

    list(products.find(
        {"$text": {"$search": "Smart Phone"}}
    ).limit(100))

    list(products.find(
        {"rating": 5}
    ).sort("stock", DESCENDING).limit(100))

    print(f"Query workload iteration {iteration + 1}/5 completed")

print("\n[2] Collecting index usage statistics...")

stats = list(products.aggregate([
    {"$indexStats": {}}
]))

stats.sort(
    key=lambda item: item.get("accesses", {}).get("ops", 0),
    reverse=True
)

for item in stats:
    accesses = item.get("accesses", {})

    print("\nIndex:", item.get("name"))
    print("Operations:", accesses.get("ops", 0))
    print("Since:", accesses.get("since", "N/A"))
    print("Host:", item.get("host", "N/A"))

print("\n[3] Index usage analysis")

used_indexes = [
    item for item in stats
    if item.get("accesses", {}).get("ops", 0) > 0
]

if used_indexes:
    most_used = used_indexes[0]
    print("Most frequently used index:", most_used["name"])
    print("Operations:",
          most_used.get("accesses", {}).get("ops", 0))
else:
    print("No index usage was recorded.")

print("\nLab 6.1 index usage analysis completed.")

client.close()
