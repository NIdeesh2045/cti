import time
from datetime import datetime, timezone

from pymongo import MongoClient, WriteConcern
from pymongo.errors import PyMongoError

URI = "mongodb://localhost:27118/?directConnection=true"
DATABASE = "lab09_write_concern"
DOCUMENT_COUNT = 1000

write_concerns = [
    ("w:1", 1),
    ("w:majority", "majority"),
    ("w:3 (all data nodes)", 3),
]

client = MongoClient(
    URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000
)

try:
    client.admin.command("ping")
    print("Connected to MongoDB.")
    print(f"Inserting {DOCUMENT_COUNT} documents per write concern.\n")

    results = []

    for label, w_value in write_concerns:
        collection_name = f"benchmark_{str(w_value).replace(' ', '_')}"
        collection = client[DATABASE].get_collection(
            collection_name,
            write_concern=WriteConcern(w=w_value, wtimeout=15000)
        )

        start = time.perf_counter()
        successful = 0
        errors = 0

        for i in range(DOCUMENT_COUNT):
            document = {
                "sequence": i + 1,
                "writeConcern": label,
                "createdAt": datetime.now(timezone.utc)
            }

            try:
                collection.insert_one(document)
                successful += 1
            except PyMongoError as error:
                errors += 1
                if errors <= 3:
                    print(f"{label}: insert {i + 1} failed: {error}")

        elapsed = time.perf_counter() - start
        average_ms = (elapsed / DOCUMENT_COUNT) * 1000

        results.append({
            "concern": label,
            "successful": successful,
            "errors": errors,
            "total_seconds": elapsed,
            "average_ms": average_ms
        })

    print("\n========== WRITE CONCERN RESULTS ==========")
    print(f"{'Concern':<24} {'Success':>8} {'Errors':>8} {'Total (s)':>12} {'Avg (ms)':>12}")

    for result in results:
        print(
            f"{result['concern']:<24}"
            f"{result['successful']:>8}"
            f"{result['errors']:>8}"
            f"{result['total_seconds']:>12.3f}"
            f"{result['average_ms']:>12.3f}"
        )

    print("\nAverage latency = total elapsed time / 1000 inserts.")
    print("Note: w:3 requires acknowledgment from all three data-bearing nodes.")

finally:
    client.close()
