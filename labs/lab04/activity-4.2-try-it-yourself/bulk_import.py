
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

URI = os.getenv("MONGODB_LOCAL_URI", "mongodb://localhost:27017")


def bulk_import(collection, documents):
    operations = []

    for document in documents:
        operations.append(
            UpdateOne(
                {"sku": document["sku"]},
                {"$set": document},
                upsert=True
            )
        )

    return collection.bulk_write(operations, ordered=False)


def main():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")

    collection = client["lab04_inventory"]["products"]

    with open(Path(__file__).with_name("products_import.json"), encoding="utf-8") as file:
        documents = json.load(file)

    print("=== FIRST IMPORT ===")
    first = bulk_import(collection, documents)
    print(f"Matched: {first.matched_count}")
    print(f"Modified: {first.modified_count}")
    print(f"Upserted: {first.upserted_count}")

    print("\n=== SECOND IMPORT (SAME DATA) ===")
    second = bulk_import(collection, documents)
    print(f"Matched: {second.matched_count}")
    print(f"Modified: {second.modified_count}")
    print(f"Upserted: {second.upserted_count}")

    print(f"\nTotal products in collection: {collection.count_documents({})}")
    print("[OK] Idempotent bulk import completed")

    client.close()


if __name__ == "__main__":
    main()
