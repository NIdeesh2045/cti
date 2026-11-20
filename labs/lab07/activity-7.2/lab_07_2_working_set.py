import os
import re
import time
import requests
from pathlib import Path
from datetime import datetime, timezone

from pymongo import MongoClient
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

MONGODB_URI = os.getenv("MONGODB_LOCAL_URI")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_LOCAL_URI not found")

REPO_README = (
    "https://raw.githubusercontent.com/"
    "jacobdjwilson/awesome-annual-security-reports/main/README.md"
)

DB_NAME = "lab07_working_set"
COLLECTION_NAME = "security_reports_working_set"

TOTAL_DOCUMENTS = 100_000
BATCH_SIZE = 2_000

# --------------------------------------------------
# Download actual annual security report metadata
# --------------------------------------------------

def download_report_catalog():
    print("Downloading annual security reports catalog...")

    response = requests.get(REPO_README, timeout=60)
    response.raise_for_status()

    pattern = re.compile(
        r"- \[([^\]]+)\]\(([^)]+)\)\s*-\s*"
        r"\[([^\]]+)\]\(([^)]+)\)"
        r"(?:\s*\((\d{4})\))?\s*-\s*(.*)"
    )

    reports = []

    for line in response.text.splitlines():
        match = pattern.match(line.strip())

        if not match:
            continue

        organization, website, title, report_path, year, summary = (
            match.groups()
        )

        reports.append({
            "organization": organization,
            "organization_url": website,
            "title": title,
            "report_path": report_path,
            "year": int(year) if year else None,
            "summary": summary.strip()
        })

    if not reports:
        raise RuntimeError("No report records found in repository README")

    print(f"Report catalog entries found: {len(reports):,}")
    return reports


# --------------------------------------------------
# Generate approximately 2 KB workload documents
# --------------------------------------------------

def create_document(number, report):
    payload = (
        f"Annual cybersecurity research report. "
        f"Organization: {report['organization']}. "
        f"Report: {report['title']}. "
        f"Research summary: {report['summary']}. "
    )

    # Additional workload payload to reach approximately 2 KB.
    payload = (payload * 100)[:1600]

    return {
        "document_number": number,
        "organization": report["organization"],
        "organization_url": report["organization_url"],
        "report_title": report["title"],
        "report_path": report["report_path"],
        "report_year": report["year"],
        "summary": report["summary"],
        "payload": payload,
        "dataset": "awesome-annual-security-reports",
        "created_at": datetime.now(timezone.utc)
    }


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    print("=" * 65)
    print("MONGODB LAB 07.2 - WORKING SET ANALYSIS")
    print("=" * 65)

    reports = download_report_catalog()

    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000
    )

    client.admin.command("ping")

    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Only reset this experiment's collection.
    collection.drop()

    print(f"\nDatabase: {DB_NAME}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Target documents: {TOTAL_DOCUMENTS:,}")

    start = time.perf_counter()
    batch = []

    for number in range(TOTAL_DOCUMENTS):
        report = reports[number % len(reports)]
        batch.append(create_document(number, report))

        if len(batch) >= BATCH_SIZE:
            collection.insert_many(batch, ordered=False)
            batch.clear()

            inserted = collection.count_documents({})
            print(f"Inserted: {inserted:,}/{TOTAL_DOCUMENTS:,}")

    if batch:
        collection.insert_many(batch, ordered=False)

    elapsed = time.perf_counter() - start

    # --------------------------------------------------
    # BSON size analysis
    # --------------------------------------------------

    size_result = list(collection.aggregate([
        {
            "$project": {
                "size": {"$bsonSize": "$$ROOT"}
            }
        },
        {
            "$group": {
                "_id": None,
                "average_size": {"$avg": "$size"},
                "minimum_size": {"$min": "$size"},
                "maximum_size": {"$max": "$size"},
                "total_size": {"$sum": "$size"}
            }
        }
    ]))

    stats = size_result[0]

    print("\n" + "=" * 65)
    print("DATASET CREATION RESULTS")
    print("=" * 65)

    print("Documents:", f"{collection.count_documents({}):,}")
    print(f"Average BSON size: {stats['average_size']:,.2f} bytes")
    print(f"Minimum BSON size: {stats['minimum_size']:,} bytes")
    print(f"Maximum BSON size: {stats['maximum_size']:,} bytes")
    print(f"Total BSON size: {stats['total_size'] / (1024**2):.2f} MB")
    print(f"Insertion time: {elapsed:.2f} seconds")

    print("\nDataset source:")
    print("https://github.com/jacobdjwilson/awesome-annual-security-reports/")

    print("\nWorking-set dataset created successfully.")

    client.close()


if __name__ == "__main__":
    main()
