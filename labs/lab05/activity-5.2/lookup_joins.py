import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

MONGODB_URI = os.getenv("MONGODB_LOCAL_URI", "mongodb://localhost:27017")
DATABASE_NAME = "lab05_lookup"


def load_json(filename):
    with open(Path(__file__).with_name(filename), "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)

    try:
        client.admin.command("ping")
        print("MongoDB connection successful.")

        db = client[DATABASE_NAME]
        products = db["products"]
        orders = db["orders"]

        # Reset only the collections used by this activity
        products.drop()
        orders.drop()

        product_data = load_json("products.json")
        order_data = load_json("orders.json")

        products.insert_many(product_data)
        orders.insert_many(order_data)

        print(f"Inserted {len(product_data)} products.")
        print(f"Inserted {len(order_data)} orders.")

        # Pipeline 1: Join orders with products
        join_pipeline = [
            {
                "$lookup": {
                    "from": "products",
                    "localField": "product_id",
                    "foreignField": "_id",
                    "as": "product_details"
                }
            },
            {"$unwind": "$product_details"},
            {
                "$project": {
                    "_id": 0,
                    "order_date": 1,
                    "product_name": "$product_details.name",
                    "quantity": 1,
                    "total": {
                        "$multiply": [
                            "$quantity",
                            "$product_details.base_price"
                        ]
                    }
                }
            },
            {"$sort": {"order_date": 1}}
        ]

        print("\n" + "=" * 55)
        print("1. ORDERS JOINED WITH PRODUCT DETAILS")
        print("=" * 55)

        for document in orders.aggregate(join_pipeline):
            print(document)

        # Pipeline 2: Find products that have never been ordered
        unused_products_pipeline = [
            {
                "$lookup": {
                    "from": "orders",
                    "localField": "_id",
                    "foreignField": "product_id",
                    "as": "order_details"
                }
            },
            {"$match": {"order_details": {"$eq": []}}},
            {
                "$project": {
                    "_id": 0,
                    "name": 1,
                    "category": 1,
                    "base_price": 1
                }
            },
            {"$sort": {"name": 1}}
        ]

        print("\n" + "=" * 55)
        print("2. PRODUCTS THAT HAVE NEVER BEEN ORDERED")
        print("=" * 55)

        for document in products.aggregate(unused_products_pipeline):
            print(document)

        print("\n$lookup join analysis completed successfully.")

    except Exception as error:
        print(f"Error: {error}")
        raise

    finally:
        client.close()


if __name__ == "__main__":
    main()
