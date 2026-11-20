
import json

from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "lab02_bookstore"
COLLECTION_NAME = "books_extra"


def main():
    client = None

    try:
        print("=" * 55)
        print("ACTIVITY 2.2 - TRY IT YOURSELF")
        print("Machine Learning Books: 5% Price Increase")
        print("=" * 55)

        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=10000
        )
        client.admin.command("ping")
        print("\n[OK] Connected to Docker MongoDB")

        collection = client[DATABASE_NAME][COLLECTION_NAME]

        # Load the JSON dataset
        with open(
            "activity-2.2-try-it-yourself/books_extra.json",
            "r"
        ) as file:
            books = json.load(file)

        # Reset collection for repeatable execution
        collection.drop()
        collection.insert_many(books)

        print(f"[OK] Inserted {len(books)} books")

        # Display prices before update
        print("\n=== BEFORE UPDATE ===")

        for book in collection.find(
            {},
            {"_id": 0, "title": 1, "genre": 1, "price": 1}
        ):
            print(
                f"{book['title']:<40} "
                f"${book['price']:.2f}"
            )

        # Increase Machine Learning book prices by 5%
        print("\n=== UPDATE: 5% INCREASE ===")

        result = collection.update_many(
            {"genre": "Machine Learning"},
            {"$mul": {"price": 1.05}}
        )

        print(f"Matched: {result.matched_count}")
        print(f"Modified: {result.modified_count}")

        # Display prices after update
        print("\n=== AFTER UPDATE ===")

        for book in collection.find(
            {},
            {"_id": 0, "title": 1, "genre": 1, "price": 1}
        ):
            print(
                f"{book['title']:<40} "
                f"${book['price']:.2f}"
            )

        print("\n[OK] Try It Yourself completed successfully.")
        print(f"Database: {DATABASE_NAME}")
        print(f"Collection: {COLLECTION_NAME}")

    except (PyMongoError, OSError, ValueError, KeyError) as error:
        print(f"\n[ERROR] {error}")

    finally:
        if client:
            client.close()


if __name__ == "__main__":
    main()

