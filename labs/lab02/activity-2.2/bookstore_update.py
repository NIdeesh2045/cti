
import json
import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

MONGO_URI = os.getenv("MONGODB_LOCAL_URI")
DATABASE_NAME = "lab02_bookstore"
COLLECTION_NAME = "books"


def main():
    client = None

    try:
        print("=" * 55)
        print("ACTIVITY 2.2 - BOOKSTORE PRICE UPDATE")
        print("=" * 55)

        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=10000
        )

        client.admin.command("ping")
        print("\n[OK] Connected to Docker MongoDB")

        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # Load books from JSON
        with open("activity-2.2/books.json", "r") as file:
            books = json.load(file)

        # Reset collection for repeatable execution
        collection.drop()

        # CREATE: Insert books
        print("\n=== CREATE: Inserting Books ===")
        result = collection.insert_many(books)
        print(f"[OK] Inserted {len(result.inserted_ids)} books")

        # READ: Display prices before update
        print("\n=== BEFORE UPDATE ===")

        before = list(
            collection.find(
                {},
                {"_id": 0, "title": 1, "year": 1, "price": 1}
            ).sort("year", 1)
        )

        for book in before:
            print(
                f"{book['title']:<40} "
                f"Year: {book['year']} "
                f"Price: ${book['price']:.2f}"
            )

        # UPDATE: Increase price by 10% only for books before 2010
        print("\n=== UPDATE: 10% Increase for Books Before 2010 ===")

        update_result = collection.update_many(
            {"year": {"$lt": 2010}},
            {"$mul": {"price": 1.10}}
        )

        print(f"[OK] Matched documents: {update_result.matched_count}")
        print(f"[OK] Modified documents: {update_result.modified_count}")

        # READ: Verify updated prices
        print("\n=== AFTER UPDATE ===")

        after = list(
            collection.find(
                {},
                {"_id": 0, "title": 1, "year": 1, "price": 1}
            ).sort("year", 1)
        )

        for book in after:
            print(
                f"{book['title']:<40} "
                f"Year: {book['year']} "
                f"Price: ${book['price']:.2f}"
            )

        print("\n=== VERIFICATION ===")

        old_books = list(
            collection.find({"year": {"$lt": 2010}})
        )

        recent_books = list(
            collection.find({"year": {"$gte": 2010}})
        )

        print(f"Books published before 2010: {len(old_books)}")
        print(f"Books published from 2010 onward: {len(recent_books)}")

        print("\n[OK] Price update completed successfully.")
        print(f"Database: {DATABASE_NAME}")
        print(f"Collection: {COLLECTION_NAME}")
        print("\nOpen MongoDB Compass to verify the collection.")

    except (PyMongoError, OSError, ValueError, KeyError) as error:
        print(f"\n[ERROR] {error}")

    finally:
        if client:
            client.close()


if __name__ == "__main__":
    main()

