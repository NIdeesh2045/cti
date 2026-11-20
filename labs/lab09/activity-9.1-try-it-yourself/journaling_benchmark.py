import time
from datetime import datetime, timezone

from pymongo import MongoClient, WriteConcern
from pymongo.errors import PyMongoError

URI = "mongodb://localhost:27118/?directConnection=true"
DATABASE = "lab09_journaling"
DOCUMENT_COUNT = 1000

write_concerns = [
    ("w:1", 1),
    ("w:majority", "majority"),
    ("w:3", 3),
]

client = MongoClient(
    URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000
)

try:
    client.admin.command("ping")
    print("Connected to MongoDB.")
    print(f"Testing {DOCUMENT_COUNT} inserts per combination.\n")

    print(
        f"{'Write Concern':<18} {'Journal':<10} "
        f"{'Success':>8} {'Errors':>8} {'Total (s)':>12} {'Avg (ms)':>12}"
    )

    for label, w_value in write_concerns:
        for journal in (True, False):
            collection_name = (
                f"benchmark_w{str(w_value).replace(' ', '_')}_j{journal}"
            )

            collection = client[DATABASE].get_collection(
                collection_name,
                write_concern=WriteConcern(
                    w=w_value,
                    j=journal,
                    wtimeout=15000
                )
            )

            start = time.perf_counter()
            successful = 0
            errors = 0

            for i in range(DOCUMENT_COUNT):
                document = {
                    "sequence": i + 1,
                    "writeConcern": label,
                    "journal": journal,
                    "createdAt": datetime.now(timezone.utc)
                }

                try:
                    collection.insert_one(document)
                    successful += 1
                except PyMongoError as error:
                    errors += 1
                    if errors <= 3:
                        print(f"\n{label}, j={journal}: {error}")

            elapsed = time.perf_counter() - start
            average_ms = elapsed * 1000 / DOCUMENT_COUNT

            print(
                f"{label:<18} {str(journal):<10} "
                f"{successful:>8} {errors:>8} "
                f"{elapsed:>12.3f} {average_ms:>12.3f}"
            )

    print("\nAverage latency = total elapsed time / 1000 inserts.")

finally:
    client.close()
