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

        # Ensure the collections contain the expected sample data
        products.drop()
        orders.drop()

        product_data = load_json("products.json")
        order_data = load_json("orders.json")

        products.insert_many(product_data)
        orders.insert_many(order_data)

        print(f"Inserted {len(product_data)} products.")
        print(f"Inserted {len(order_data)} orders.")

        # $lookup with a pipeline to filter foreign documents
        filtered_lookup_pipeline = [
            {
                "$lookup": {
                    "from": "orders",
                    "let": {"current_product_id": "$_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {
                                            "$eq": [
                                                "$product_id",
                                                "$$current_product_id"
                                            ]
                                        },
                                        {"$gte": ["$quantity", 2]}
                                    ]
                                }
                            }
                        },
                        {
                            "$project": {
                                "_id": 0,
                                "customer": 1,
                                "quantity": 1,
                                "order_date": 1
                            }
                        }
                    ],
                    "as": "filtered_orders"
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "product_name": "$name",
                    "category": 1,
                    "orders_with_quantity_2_or_more": "$filtered_orders"
                }
            },
            {"$sort": {"product_name": 1}}
        ]

        print("\n" + "=" * 60)
        print("PRODUCTS WITH ORDERS HAVING QUANTITY >= 2")
        print("=" * 60)

        for document in products.aggregate(filtered_lookup_pipeline):
            print(document)

        print("\nFiltered $lookup pipeline completed successfully.")

    except Exception as error:
        print(f"Error: {error}")
        raise

    finally:
        client.close()


if __name__ == "__main__":
    main()
