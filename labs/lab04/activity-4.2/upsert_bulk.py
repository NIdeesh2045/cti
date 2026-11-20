
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

URI = os.getenv("MONGODB_LOCAL_URI", "mongodb://localhost:27017")
DB_NAME = "lab04_inventory"


def upsert_product(collection, sku, price):
    result = collection.update_one(
        {"sku": sku},
        {
            "$set": {"price": price},
            "$setOnInsert": {
                "sku": sku,
                "name": f"Product {sku}",
                "stock": 10,
                "tags": ["general"],
                "is_active": True
            }
        },
        upsert=True
    )

    if result.upserted_id:
        print(f"[INSERTED] SKU {sku} created with price {price}")
    elif result.modified_count:
        print(f"[UPDATED] SKU {sku} price changed to {price}")
    else:
        print(f"[UNCHANGED] SKU {sku} already has price {price}")


def main():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("[OK] Connected to MongoDB")

    products = client[DB_NAME]["products"]

    # Part 1: Upsert
    print("\n=== UPSERT OPERATIONS ===")

    upsert_product(products, "A", 49.99)   # Existing SKU
    upsert_product(products, "K", 75.00)   # New SKU

    print(f"\nTotal products: {products.count_documents({})}")

    # Part 2: Bulk operations
    print("\n=== BULK WRITE OPERATIONS ===")

    operations = [
        UpdateOne({"sku": "A"}, {"$inc": {"stock": 10}}),
        UpdateOne({"sku": "B"}, {"$inc": {"stock": 10}}),
        UpdateOne({"sku": "C"}, {"$inc": {"stock": 10}}),
        UpdateOne({"sku": "D"}, {"$set": {"is_active": False}}),
        UpdateOne({"sku": "E"}, {"$set": {"is_active": False}})
    ]

    result = products.bulk_write(operations, ordered=True)

    print(f"Matched documents: {result.matched_count}")
    print(f"Modified documents: {result.modified_count}")
    print(f"Upserted documents: {result.upserted_count}")

    # Verify changes
    print("\n=== VERIFICATION ===")

    for sku in ["A", "B", "C", "D", "E", "K"]:
        product = products.find_one({"sku": sku}, {"_id": 0})

        if product:
            print(
                f"{sku} | {product['name']} | "
                f"Stock: {product['stock']} | "
                f"Active: {product.get('is_active', True)}"
            )

    print("\n[OK] Lab 4.2 completed")
    client.close()


if __name__ == "__main__":
    main()
