import os
import requests
from pathlib import Path
from datetime import datetime, timezone

from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv

# --------------------------------------------------
# Configuration
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

MONGODB_URI = os.getenv("MONGODB_LOCAL_URI")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_LOCAL_URI not found in project .env file")

BASE_URL = "https://ctidigest.com/"
ARTICLES_URL = BASE_URL + "articles.json"
IOCS_URL = BASE_URL + "iocs.json"

DB_NAME = "lab07_cti_schema"

# --------------------------------------------------
# Download actual CTI Digest data
# --------------------------------------------------

def download_json(url):
    print(f"\nDownloading: {url}")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list from {url}")

    print(f"Downloaded records: {len(data):,}")
    return data


# --------------------------------------------------
# Main execution
# --------------------------------------------------

def main():
    print("=" * 65)
    print("MONGODB LAB 07.1 - PRODUCTION SCHEMA ANALYSIS")
    print("=" * 65)

    articles = download_json(ARTICLES_URL)
    iocs = download_json(IOCS_URL)

    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")

    db = client[DB_NAME]

    # Fresh lab dataset only
    db.articles.drop()
    db.iocs.drop()
    db.sources.drop()

    sources = db.sources
    article_collection = db.articles
    ioc_collection = db.iocs

    # --------------------------------------------------
    # Create unique source documents
    # --------------------------------------------------

    source_names = set()

    for article in articles:
        if article.get("source"):
            source_names.add(article["source"].strip())

    for ioc in iocs:
        if ioc.get("source"):
            source_names.add(ioc["source"].strip())

    source_documents = []

    for name in sorted(source_names):
        source_documents.append({
            "name": name,
            "created_at": datetime.now(timezone.utc),
            "source_type": "CTI Feed"
        })

    if source_documents:
        sources.insert_many(source_documents)

    source_map = {
        doc["name"]: doc["_id"]
        for doc in sources.find({}, {"name": 1})
    }

    print(f"\nUnique sources created: {len(source_map):,}")

    # --------------------------------------------------
    # Prepare article documents
    # --------------------------------------------------

    article_documents = []

    for article in articles:
        source_name = (article.get("source") or "").strip()

        document = {
            "title": article.get("title", ""),
            "link": article.get("link", ""),
            "description": article.get("desc", ""),
            "published_at": article.get("date"),
            "category": article.get("category", "uncategorized"),
            "source_id": source_map.get(source_name),
            "source_name": source_name,
            "collected_at": datetime.now(timezone.utc)
        }

        article_documents.append(document)

    if article_documents:
        article_collection.insert_many(
            article_documents,
            ordered=False
        )

    # --------------------------------------------------
    # Prepare IOC documents
    # --------------------------------------------------

    ioc_documents = []

    for ioc in iocs:
        source_name = (ioc.get("source") or "").strip()

        document = {
            "value": ioc.get("value"),
            "type": ioc.get("type"),
            "confidence": ioc.get("confidence"),
            "category": ioc.get("category"),
            "description": ioc.get("description"),
            "first_seen": ioc.get("first_seen"),
            "source_id": source_map.get(source_name),
            "source_name": source_name,
            "collected_at": datetime.now(timezone.utc)
        }

        ioc_documents.append(document)

    if ioc_documents:
        ioc_collection.insert_many(
            ioc_documents,
            ordered=False
        )

    # --------------------------------------------------
    # Create useful indexes
    # --------------------------------------------------

    article_collection.create_index("source_id")
    article_collection.create_index("category")
    article_collection.create_index("published_at")

    ioc_collection.create_index("source_id")
    ioc_collection.create_index("type")
    ioc_collection.create_index("value")

    sources.create_index("name", unique=True)

    # --------------------------------------------------
    # BSON document size analysis
    # --------------------------------------------------

    print("\n" + "=" * 65)
    print("BSON DOCUMENT SIZE ANALYSIS")
    print("=" * 65)

    for collection_name in ["articles", "iocs", "sources"]:
        collection = db[collection_name]

        pipeline = [
            {
                "$project": {
                    "size": {"$bsonSize": "$$ROOT"}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "average_size": {"$avg": "$size"},
                    "maximum_size": {"$max": "$size"},
                    "minimum_size": {"$min": "$size"},
                    "total_documents": {"$sum": 1}
                }
            }
        ]

        result = list(collection.aggregate(pipeline))

        if result:
            stats = result[0]

            average = stats["average_size"]
            maximum = stats["maximum_size"]

            print(f"\nCollection: {collection_name}")
            print(f"Documents: {stats['total_documents']:,}")
            print(f"Average BSON size: {average:,.2f} bytes")
            print(f"Maximum BSON size: {maximum:,} bytes")
            print(f"Minimum BSON size: {stats['minimum_size']:,} bytes")
            print(f"Average size: {average / 1024:.2f} KB")
            print(f"Maximum size: {maximum / 1024:.2f} KB")

            limit = 16 * 1024 * 1024
            percentage = (maximum / limit) * 100

            print(f"16 MB limit usage: {percentage:.6f}%")

            if maximum < limit:
                print("Status: SAFE - below 16 MB limit")
            else:
                print("Status: WARNING - document reached 16 MB limit")

    # --------------------------------------------------
    # Final database summary
    # --------------------------------------------------

    print("\n" + "=" * 65)
    print("DATABASE SUMMARY")
    print("=" * 65)

    print("Database:", DB_NAME)
    print("Sources:", sources.count_documents({}))
    print("Articles:", article_collection.count_documents({}))
    print("IOCs:", ioc_collection.count_documents({}))

    print("\nCollections:")
    for name in db.list_collection_names():
        print("-", name)

    print("\nLab 07.1 dataset created successfully.")

    client.close()


if __name__ == "__main__":
    main()
