import json
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient

# Load MongoDB connection settings from the repository's .env file
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

MONGODB_URI = os.getenv("MONGODB_LOCAL_URI", "mongodb://localhost:27017")
DATABASE_NAME = "lab05_sales"
COLLECTION_NAME = "orders"


def load_orders():
    """Load JSON orders and convert order_date strings into datetime objects."""
    json_path = Path(__file__).with_name("orders.json")

    with open(json_path, "r", encoding="utf-8") as file:
        orders = json.load(file)

    for order in orders:
        order["order_date"] = datetime.strptime(
            order["order_date"], "%Y-%m-%d"
        )

    return orders


def main():
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)

    try:
        client.admin.command("ping")
        print("MongoDB connection successful.")

        db = client[DATABASE_NAME]
        orders_collection = db[COLLECTION_NAME]

        # Reset only this lab's orders collection
        orders_collection.drop()

        orders = load_orders()
        result = orders_collection.insert_many(orders)

        print(f"\nInserted {len(result.inserted_ids)} orders.")
        print(f"Database: {DATABASE_NAME}")
        print(f"Collection: {COLLECTION_NAME}")

        # Pipeline 1: Monthly revenue
        monthly_revenue_pipeline = [
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m",
                            "date": "$order_date"
                        }
                    },
                    "total_revenue": {
                        "$sum": {
                            "$multiply": ["$quantity", "$unit_price"]
                        }
                    },
                    "total_orders": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "month": "$_id",
                    "total_revenue": 1,
                    "total_orders": 1
                }
            }
        ]

        print("\n" + "=" * 55)
        print("1. MONTHLY REVENUE")
        print("=" * 55)

        for document in orders_collection.aggregate(monthly_revenue_pipeline):
            print(document)

        # Pipeline 2: Top 3 customers and products purchased
        top_customers_pipeline = [
            {
                "$group": {
                    "_id": "$customer",
                    "total_spending": {
                        "$sum": {
                            "$multiply": ["$quantity", "$unit_price"]
                        }
                    },
                    "products_bought": {"$addToSet": "$product"}
                }
            },
            {"$sort": {"total_spending": -1}},
            {"$limit": 3},
            {
                "$project": {
                    "_id": 0,
                    "customer": "$_id",
                    "total_spending": 1,
                    "products_bought": 1
                }
            }
        ]

        print("\n" + "=" * 55)
        print("2. TOP 3 CUSTOMERS BY TOTAL SPENDING")
        print("=" * 55)

        for document in orders_collection.aggregate(top_customers_pipeline):
            print(document)

        # Pipeline 3: Average order value by status
        average_order_pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "average_order_value": {
                        "$avg": {
                            "$multiply": ["$quantity", "$unit_price"]
                        }
                    },
                    "order_count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "status": "$_id",
                    "average_order_value": {
                        "$round": ["$average_order_value", 2]
                    },
                    "order_count": 1
                }
            }
        ]

        print("\n" + "=" * 55)
        print("3. AVERAGE ORDER VALUE BY STATUS")
        print("=" * 55)

        for document in orders_collection.aggregate(average_order_pipeline):
            print(document)

        print("\nSales analytics pipeline completed successfully.")

    except Exception as error:
        print(f"Error: {error}")
        raise

    finally:
        client.close()


if __name__ == "__main__":
    main()
