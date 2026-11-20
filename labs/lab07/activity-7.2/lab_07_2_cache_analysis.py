import os
import random
import time
from pathlib import Path

from pymongo import MongoClient
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

URI = os.getenv("MONGODB_LOCAL_URI")

if not URI:
    raise RuntimeError("MONGODB_LOCAL_URI not found")

DB_NAME = "lab07_working_set"
COLLECTION_NAME = "security_reports_working_set"

TOTAL_DOCUMENTS = 100_000
READS_PER_ROUND = 10_000
ROUNDS = 5


def get_cache_stats(client):
    status = client.admin.command("serverStatus")
    wt = status.get("wiredTiger", {}).get("cache", {})

    current = wt.get("bytes currently in the cache", 0)
    maximum = wt.get("maximum bytes configured", 0)

    pages_requested = wt.get("pages requested from the cache", 0)
    pages_read = wt.get("pages read into cache", 0)

    occupancy = (current / maximum * 100) if maximum else 0

    # Approximate counter-based hit ratio.
    # Treat this as an estimate, not an exact per-query hit rate.
    denominator = pages_requested + pages_read
    hit_ratio = (
        (pages_requested / denominator) * 100
        if denominator else 0
    )

    return {
        "current": current,
        "maximum": maximum,
        "occupancy": occupancy,
        "pages_requested": pages_requested,
        "pages_read": pages_read,
        "hit_ratio": hit_ratio
    }


def display_cache(stats, label):
    print(f"\n{label}")
    print("-" * 60)
    print(f"Cache currently used: {stats['current'] / (1024**2):.2f} MB")
    print(f"Maximum cache configured: {stats['maximum'] / (1024**2):.2f} MB")
    print(f"Cache occupancy: {stats['occupancy']:.2f}%")
    print(f"Pages requested: {stats['pages_requested']:,}")
    print(f"Pages read into cache: {stats['pages_read']:,}")
    print(f"Approximate counter-based hit ratio: {stats['hit_ratio']:.2f}%")


def main():
    print("=" * 65)
    print("MONGODB LAB 07.2 - WIREDTIGER CACHE ANALYSIS")
    print("=" * 65)

    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")

    collection = client[DB_NAME][COLLECTION_NAME]

    count = collection.count_documents({})
    if count != TOTAL_DOCUMENTS:
        raise RuntimeError(
            f"Expected {TOTAL_DOCUMENTS} documents, found {count}"
        )

    # Index enables efficient random point lookups.
    collection.create_index("document_number")

    print(f"\nDatabase: {DB_NAME}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Documents: {count:,}")

    storage = client[DB_NAME].command("collStats", COLLECTION_NAME)
    print(f"Collection storage size: {storage.get('storageSize', 0) / (1024**2):.2f} MB")
    print(f"Logical data size: {storage.get('size', 0) / (1024**2):.2f} MB")

    # Initial cache measurement
    initial = get_cache_stats(client)
    display_cache(initial, "INITIAL WIREDTIGER CACHE")

    print("\nStarting random reads across the collection...")

    for round_number in range(1, ROUNDS + 1):
        start = time.perf_counter()

        for _ in range(READS_PER_ROUND):
            number = random.randrange(TOTAL_DOCUMENTS)
            result = collection.find_one(
                {"document_number": number},
                {"_id": 0, "document_number": 1, "report_title": 1}
            )

            if result is None:
                raise RuntimeError(f"Document {number} not found")

        elapsed = time.perf_counter() - start
        stats = get_cache_stats(client)

        print(f"\nROUND {round_number}")
        print("-" * 60)
        print(f"Random reads: {READS_PER_ROUND:,}")
        print(f"Read time: {elapsed:.3f} seconds")
        print(f"Reads per second: {READS_PER_ROUND / elapsed:,.2f}")
        print(f"Cache occupancy: {stats['occupancy']:.2f}%")
        print(f"Pages requested: {stats['pages_requested']:,}")
        print(f"Pages read into cache: {stats['pages_read']:,}")
        print(f"Approximate counter-based hit ratio: {stats['hit_ratio']:.2f}%")

        time.sleep(2)

    print("\n" + "=" * 65)
    print("FINAL CACHE ANALYSIS")
    print("=" * 65)

    final = get_cache_stats(client)
    display_cache(final, "FINAL WIREDTIGER CACHE")

    print("""
INTERPRETATION:
- Cache occupancy shows how much of the configured cache is used.
- Pages read into cache indicates disk/page reads into WiredTiger.
- Repeated random reads may benefit from pages already cached.
- Cache occupancy is not the same as the percentage of the
  complete collection held in memory.
- The displayed counter-based hit ratio is an approximation,
  not an exact per-query cache hit measurement.
""")

    client.close()


if __name__ == "__main__":
    main()
