import os
import time
import statistics
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv("../activity-15.1/.env")

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MongoDB URI not found")

client = MongoClient(MONGO_URI)
db = client["tenant_migration"]

shared = db["tasks"]
tenant_collection = db["tasks_tenant_a"]

TENANT_ID = "tenant_a"
ITERATIONS = 100


def measure(label, operation):
    timings = []

    for _ in range(ITERATIONS):
        start = time.perf_counter()
        operation()
        timings.append((time.perf_counter() - start) * 1000)

    avg = statistics.mean(timings)
    print(f"{label}: {avg:.4f} ms (average of {ITERATIONS} runs)")
    return avg


print("TENANT ISOLATION PERFORMANCE BENCHMARK")
print("=" * 55)

# 1. Listing 100 tasks
print("\n1. LISTING 100 TASKS")

shared_list = measure(
    "Document-level isolation",
    lambda: list(shared.find({"tenant_id": TENANT_ID}).limit(100))
)

collection_list = measure(
    "Collection-per-tenant",
    lambda: list(tenant_collection.find({}).limit(100))
)

# 2. Creating a task
print("\n2. CREATING A TASK")

def create_shared():
    doc = {
        "tenant_id": TENANT_ID,
        "title": "Benchmark Task",
        "created_at": datetime.now(timezone.utc)
    }
    result = shared.insert_one(doc)
    shared.delete_one({"_id": result.inserted_id})


def create_separate():
    doc = {
        "tenant_id": TENANT_ID,
        "title": "Benchmark Task",
        "created_at": datetime.now(timezone.utc)
    }
    result = tenant_collection.insert_one(doc)
    tenant_collection.delete_one({"_id": result.inserted_id})


shared_create = measure("Document-level isolation", create_shared)
collection_create = measure("Collection-per-tenant", create_separate)

# 3. Cross-tenant analytics
print("\n3. CROSS-TENANT ANALYTICS")

def shared_analytics():
    return list(shared.aggregate([
        {"$group": {
            "_id": "$tenant_id",
            "total_tasks": {"$sum": 1}
        }}
    ]))


def collection_analytics():
    result = []

    for tenant in ["tenant_a", "tenant_b", "tenant_c",
                   "tenant_d", "tenant_e"]:
        count = db[f"tasks_{tenant}"].count_documents({})
        result.append({"tenant": tenant, "total_tasks": count})

    return result


shared_analytics_time = measure(
    "Document-level isolation",
    shared_analytics
)

collection_analytics_time = measure(
    "Collection-per-tenant",
    collection_analytics
)

print("\n" + "=" * 55)
print("BENCHMARK SUMMARY")
print("=" * 55)

print(f"Listing: shared={shared_list:.4f} ms | separate={collection_list:.4f} ms")
print(f"Creating: shared={shared_create:.4f} ms | separate={collection_create:.4f} ms")
print(f"Analytics: shared={shared_analytics_time:.4f} ms | separate={collection_analytics_time:.4f} ms")

print("\nBenchmark completed successfully.")

client.close()