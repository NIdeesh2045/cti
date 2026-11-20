import json
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

MONGODB_URI = os.getenv("MONGODB_LOCAL_URI", "mongodb://localhost:27017")
DATABASE_NAME = "lab05_sales"
COLLECTION_NAME = "bucket_orders"


def main():
    json_path = Path(__file__).with_name("orders_bucket.json")

    with open(json_path, "r", encoding="utf-8") as file:
        orders = json.load(file)

    for order in orders:
        order["order_date"] = datetime.strptime(
            order["order_date"], "%Y-%m-%d"
        )

    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)

    try:
        client.admin.command("ping")
        print("MongoDB connection successful.")

        collection = client[DATABASE_NAME][COLLECTION_NAME]
        collection.drop()

        result = collection.insert_many(orders)
        print(f"Inserted {len(result.inserted_ids)} orders.")

        bucket_pipeline = [
            {
                "$addFields": {
                    "order_value": {
                        "$multiply": ["$quantity", "$unit_price"]
                    }
                }
            },
            {
                "$bucket": {
                    "groupBy": "$order_value",
                    "boundaries": [0, 50, 201, float("inf")],
                    "default": "Other",
                    "output": {
                        "number_of_orders": {"$sum": 1},
                        "total_revenue": {"$sum": "$order_value"},
                        "orders": {
                            "$push": {
                                "customer": "$customer",
                                "product": "$product",
                                "order_value": "$order_value"
                            }
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "category": {
                        "$switch": {
                            "branches": [
                                {
                                    "case": {"$eq": ["$_id", 0]},
                                    "then": "Small (under $50)"
                                },
                                {
                                    "case": {"$eq": ["$_id", 50]},
                                    "then": "Medium ($50-$200)"
                                },
                                {
                                    "case": {"$eq": ["$_id", 201]},
                                    "then": "Large (over $200)"
                                }
                            ],
                            "default": "Other"
                        }
                    },
                    "number_of_orders": 1,
                    "total_revenue": 1,
                    "orders": 1
                }
            },
            {"$sort": {"category": 1}}
        ]

        print("\n" + "=" * 55)
        print("ORDER VALUE CATEGORIZATION USING $BUCKET")
        print("=" * 55)

        for document in collection.aggregate(bucket_pipeline):
            print(document)

        print("\nBucket analysis completed successfully.")

    except Exception as error:
        print(f"Error: {error}")
        raise

    finally:
        client.close()


if __name__ == "__main__":
    main()
