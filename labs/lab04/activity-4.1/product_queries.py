
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

URI = os.getenv("MONGODB_LOCAL_URI", "mongodb://localhost:27017")
DB_NAME = "lab04_inventory"
COLLECTION = "products"


def show_products(title, cursor):
    print(f"\n=== {title} ===")
    for product in cursor:
        print(
            f"{product['sku']} | {product['name']} | "
            f"Price: {product['price']} | Stock: {product['stock']}"
        )


def paginate_products(collection, page_number, items_per_page):
    if page_number < 1 or items_per_page < 1:
        raise ValueError("Page number and items per page must be positive.")

    skip_count = (page_number - 1) * items_per_page

    return collection.find(
        {},
        {"_id": 0}
    ).sort("name", 1).skip(skip_count).limit(items_per_page)


def main():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("[OK] Connected to MongoDB")

    db = client[DB_NAME]

    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["name", "price", "stock", "tags"],
            "properties": {
                "name": {"bsonType": "string"},
                "price": {
                    "bsonType": ["int", "double", "long", "decimal"],
                    "minimum": 0.01
                },
                "stock": {
                    "bsonType": ["int", "long"],
                    "minimum": 0
                },
                "tags": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                }
            }
        }
    }

    if COLLECTION in db.list_collection_names():
        db.drop_collection(COLLECTION)

    db.create_collection(COLLECTION, validator=validator)
    products = db[COLLECTION]

    with open(Path(__file__).with_name("products.json"), encoding="utf-8") as f:
        data = json.load(f)

    products.insert_many(data)
    print(f"[OK] Inserted {products.count_documents({})} products")

    show_products(
        "COMPARISON: Price between 20 and 50",
        products.find({"price": {"$gte": 20, "$lte": 50}}, {"_id": 0})
    )

    show_products(
        "COMPARISON: Out of stock",
        products.find({"stock": {"$eq": 0}}, {"_id": 0})
    )

    show_products(
        "LOGICAL: Out of stock OR price above 100",
        products.find({
            "$or": [
                {"stock": 0},
                {"price": {"$gt": 100}}
            ]
        }, {"_id": 0})
    )

    show_products(
        "LOGICAL: In stock AND premium",
        products.find({
            "$and": [
                {"stock": {"$gt": 0}},
                {"tags": "premium"}
            ]
        }, {"_id": 0})
    )

    show_products(
        "ARRAY: Both electronics AND wireless",
        products.find({
            "tags": {"$all": ["electronics", "wireless"]}
        }, {"_id": 0})
    )

    show_products(
        "ARRAY: Exactly 2 tags",
        products.find({
            "tags": {"$size": 2}
        }, {"_id": 0})
    )

    print("\n=== PAGINATION: Page 1 (3 products) ===")
    show_products(
        "Sorted alphabetically",
        paginate_products(products, 1, 3)
    )

    print("\n[OK] Lab 4.1 completed")
    client.close()


if __name__ == "__main__":
    main()
