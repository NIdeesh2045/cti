from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load Lab 15.1 MongoDB credentials
load_dotenv("../activity-15.1/.env")

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MongoDB URI not found")

client = MongoClient(MONGO_URI)
db = client["tenant_migration"]

source = db["tasks"]

tenants = [
    "tenant_a",
    "tenant_b",
    "tenant_c",
    "tenant_d",
    "tenant_e"
]

print("STARTING TENANT DATA MIGRATION")
print("=" * 45)

total_migrated = 0

for tenant_id in tenants:

    target_name = f"tasks_{tenant_id}"
    target = db[target_name]

    # Remove previous migration data for this tenant
    target.delete_many({})

    # Fetch only this tenant's documents
    tenant_tasks = list(source.find({"tenant_id": tenant_id}))

    if tenant_tasks:
        target.insert_many(tenant_tasks)

    migrated_count = target.count_documents({"tenant_id": tenant_id})
    total_migrated += migrated_count

    print(f"{tenant_id}: {migrated_count} documents migrated")

print("=" * 45)
print(f"TOTAL MIGRATED: {total_migrated}")

# Validation
print("\nMIGRATION VALIDATION")
print("=" * 45)

all_valid = True

for tenant_id in tenants:

    target_name = f"tasks_{tenant_id}"
    target = db[target_name]

    source_count = source.count_documents({"tenant_id": tenant_id})
    target_count = target.count_documents({})

    # Check for cross-tenant data leakage
    wrong_tenant_count = target.count_documents({
        "tenant_id": {"$ne": tenant_id}
    })

    valid = (
        source_count == target_count
        and wrong_tenant_count == 0
    )

    if not valid:
        all_valid = False

    print(
        f"{tenant_id}: "
        f"Source={source_count}, "
        f"Target={target_count}, "
        f"Leakage={wrong_tenant_count}, "
        f"Status={'PASS' if valid else 'FAIL'}"
    )

print("=" * 45)
print("FINAL RESULT:", "SUCCESS" if all_valid else "FAILED")

client.close()