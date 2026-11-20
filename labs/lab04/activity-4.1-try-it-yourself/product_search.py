
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

URI = os.getenv("MONGODB_LOCAL_URI", "mongodb://localhost:27017")


def search_products(collection, search_text):
    pattern = re.escape(search_text)

    return collection.find(
        {"name": {"$regex": pattern, "$options": "i"}},
        {"_id": 0}
    ).sort("name", 1)


def main():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")

    collection = client["lab04_inventory"]["products"]

    search_text = "wireless"

    print(f"=== Products matching '{search_text}' ===")

    results = list(search_products(collection, search_text))

    for product in results:
        print(
            f"{product['sku']} | {product['name']} | "
            f"Price: {product['price']}"
        )

    print(f"\nTotal matching products: {len(results)}")
    print("[OK] Regex search completed")

    client.close()


if __name__ == "__main__":
    main()
