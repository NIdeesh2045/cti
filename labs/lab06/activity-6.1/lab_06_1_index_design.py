import os
import random
import time
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

MONGO_URI = os.getenv("MONGODB_LOCAL_URI")

if not MONGO_URI:
    raise ValueError("MONGODB_LOCAL_URI not found in .env")

DB_NAME = "lab06_indexing"
COLLECTION_NAME = "products"
TOTAL_PRODUCTS = 50000
BATCH_SIZE = 1000

random.seed(42)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")

db = client[DB_NAME]
products = db[COLLECTION_NAME]

# Reset collection for a repeatable experiment
products.drop()

# --------------------------------------------------
# PRODUCT DATA GENERATION
# --------------------------------------------------

categories = [
    "Electronics",
    "Clothing",
    "Books",
    "Home",
    "Sports",
    "Beauty",
    "Toys",
    "Automotive"
]

tags_pool = [
    "premium", "budget", "sale", "new", "popular",
    "wireless", "portable", "durable", "lightweight",
    "gaming", "office", "outdoor", "smart", "accessory"
]

adjectives = [
    "Smart", "Premium", "Portable", "Advanced",
    "Classic", "Modern", "Compact", "Professional",
    "Wireless", "Digital"
]

nouns = [
    "Phone", "Laptop", "Watch", "Camera", "Speaker",
    "Keyboard", "Monitor", "Headphones", "Tablet",
    "Charger", "Bottle", "Shoes", "Backpack", "Book"
]


def generate_product(product_number):
    return {
        "name": f"{random.choice(adjectives)} "
                f"{random.choice(nouns)} Model {product_number}",
        "category": random.choice(categories),
        "price": round(random.uniform(10, 2000), 2),
        "rating": random.choice([1, 2, 3, 4, 4.5, 5]),
        "stock": random.randint(0, 500),
        "tags": random.sample(tags_pool, random.randint(2, 5))
    }


def generate_dataset():
    print("\n[1] Generating 50,000 product documents...")

    batch = []
    inserted = 0

    for number in range(1, TOTAL_PRODUCTS + 1):
        batch.append(generate_product(number))

        if len(batch) == BATCH_SIZE:
            products.insert_many(batch)
            inserted += len(batch)
            batch = []
            print(f"Inserted {inserted:,}/{TOTAL_PRODUCTS:,} documents")

    if batch:
        products.insert_many(batch)
        inserted += len(batch)

    print(f"Dataset generation completed: {inserted:,} products")


# --------------------------------------------------
# FIVE REPRESENTATIVE QUERIES
# --------------------------------------------------

queries = [
    {
        "name": "Q1 - Category filter, sorted by price",
        "filter": lambda: products.find(
            {"category": "Electronics"}
        ).sort("price", ASCENDING)
    },
    {
        "name": "Q2 - Price range",
        "filter": lambda: products.find(
            {"price": {"$gte": 100, "$lte": 500}}
        )
    },
    {
        "name": "Q3 - Search by tag",
        "filter": lambda: products.find(
            {"tags": "wireless"}
        )
    },
    {
        "name": "Q4 - Text search on product name",
        "filter": lambda: products.find(
            {"$text": {"$search": "Smart Phone"}}
        )
    },
    {
        "name": "Q5 - Rating filter, sorted by stock",
        "filter": lambda: products.find(
            {"rating": 5}
        ).sort("stock", DESCENDING)
    }
]


# --------------------------------------------------
# EXPLAIN QUERY PLANS
# --------------------------------------------------

def find_stages(value, stages=None):
    if stages is None:
        stages = []

    if isinstance(value, dict):
        if "stage" in value:
            stages.append(value["stage"])

        for child in value.values():
            find_stages(child, stages)

    elif isinstance(value, list):
        for child in value:
            find_stages(child, stages)

    return stages


def run_explain(title):
    print(f"\n[{title}]")

    for query in queries:
        print(f"\n{query['name']}")

        try:
            explanation = query["filter"]().explain()

            stages = find_stages(
                explanation.get("queryPlanner", {}).get("winningPlan", {})
            )

            execution = explanation.get("executionStats", {})

            print("Execution stages:", " -> ".join(stages) or "Not reported")
            print("Total documents examined:",
                  execution.get("totalDocsExamined", "N/A"))
            print("Total keys examined:",
                  execution.get("totalKeysExamined", "N/A"))
            print("Documents returned:",
                  execution.get("nReturned", "N/A"))

        except Exception as error:
            print("Could not execute before indexing:", error)
            print("Reason: MongoDB $text requires a text index.")


# --------------------------------------------------
# INDEX DESIGN
# --------------------------------------------------

def create_indexes():
    print("\n[3] Creating indexes for the five query patterns...")

    indexes = [
        (
            [("category", ASCENDING), ("price", ASCENDING)],
            "category_price_idx"
        ),
        (
            [("price", ASCENDING)],
            "price_idx"
        ),
        (
            [("tags", ASCENDING)],
            "tags_idx"
        ),
        (
            [("name", TEXT)],
            "name_text_idx"
        ),
        (
            [("rating", ASCENDING), ("stock", DESCENDING)],
            "rating_stock_idx"
        )
    ]

    for keys, index_name in indexes:
        products.create_index(keys, name=index_name)
        print("Created index:", index_name)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

try:
    print("=" * 65)
    print("LAB 6.1 - INDEX DESIGN FOR A QUERY WORKLOAD")
    print("=" * 65)

    generate_dataset()

    print("\nTotal documents:", products.count_documents({}))
    print("Existing indexes:", list(products.index_information().keys()))

    run_explain("2 - QUERY EXECUTION BEFORE INDEXES")

    create_indexes()

    run_explain("4 - QUERY EXECUTION AFTER INDEXES")

    print("\n[5] Index information")

    for index_name, details in products.index_information().items():
        print(index_name, ":", details["key"])

    print("\nLab 6.1 completed successfully.")

except Exception as error:
    print("\nERROR:", error)
    raise

finally:
    client.close()
