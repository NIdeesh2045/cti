import os
import time
from pathlib import Path

from pymongo import MongoClient
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

URI = os.getenv("MONGODB_LOCAL_URI")

if not URI:
    raise RuntimeError("MONGODB_LOCAL_URI not found")

client = MongoClient(URI)
db = client["lab07_cti_schema"]

iocs = db["iocs"]
sources = db["sources"]
embedded = db["iocs_embedded_source"]

embedded.drop()

# Build source lookup dictionary
source_map = {
    str(source["_id"]): {
        "name": source["name"],
        "source_type": source.get("source_type", "CTI Feed")
    }
    for source in sources.find()
}

print("=" * 65)
print("LAB 7.1 - TRY IT YOURSELF")
print("EMBEDDING VS REFERENCING")
print("=" * 65)

# --------------------------------------------------
# Create embedded IOC documents
# --------------------------------------------------

batch = []

for ioc in iocs.find():
    source_id = ioc.get("source_id")

    source_details = source_map.get(str(source_id), {
        "name": ioc.get("source_name", "Unknown"),
        "source_type": "CTI Feed"
    })

    document = {
        "value": ioc.get("value"),
        "type": ioc.get("type"),
        "confidence": ioc.get("confidence"),
        "category": ioc.get("category"),
        "description": ioc.get("description"),
        "first_seen": ioc.get("first_seen"),
        "source": source_details
    }

    batch.append(document)

    if len(batch) >= 1000:
        embedded.insert_many(batch)
        batch = []

if batch:
    embedded.insert_many(batch)

print("\nEmbedded IOC documents:", embedded.count_documents({}))

# --------------------------------------------------
# Query 1: Referencing with $lookup
# Find IOCs from IPsum
# --------------------------------------------------

reference_pipeline = [
    {
        "$lookup": {
            "from": "sources",
            "localField": "source_id",
            "foreignField": "_id",
            "as": "source_details"
        }
    },
    {"$unwind": "$source_details"},
    {"$match": {"source_details.name": "IPsum"}}
]

start = time.perf_counter()
reference_results = list(iocs.aggregate(reference_pipeline))
reference_time = time.perf_counter() - start

# --------------------------------------------------
# Query 2: Embedded source
# --------------------------------------------------

start = time.perf_counter()
embedded_results = list(
    embedded.find({"source.name": "IPsum"})
)
embedded_time = time.perf_counter() - start

# --------------------------------------------------
# Results
# --------------------------------------------------

print("\n" + "=" * 65)
print("QUERY PERFORMANCE COMPARISON")
print("=" * 65)

print("\nReferencing with $lookup:")
print("Matching documents:", len(reference_results))
print(f"Execution time: {reference_time:.6f} seconds")

print("\nEmbedding source details:")
print("Matching documents:", len(embedded_results))
print(f"Execution time: {embedded_time:.6f} seconds")

print("\n" + "=" * 65)
print("DESIGN ANALYSIS")
print("=" * 65)

print("""
EMBEDDING ADVANTAGES:
1. Source details are available directly in the IOC document.
2. No $lookup operation is needed.
3. Source-based IOC queries become simpler.
4. Source information is available in one read.

EMBEDDING DISADVANTAGES:
1. Source information is duplicated across IOC documents.
2. Updating a source requires updating many IOC documents.
3. Storage usage increases.
4. Data consistency becomes harder to maintain.

REFERENCING ADVANTAGES:
1. Source information is stored only once.
2. Updating a source is easier.
3. Less duplication.
4. Better for sources shared by many IOCs.

REFERENCING DISADVANTAGES:
1. Related source information requires $lookup.
2. Queries become more complex.
3. Joining collections can add query overhead.

CONCLUSION:
Embedding is useful when source details are frequently read
with IOC records and change infrequently.

Referencing is preferable when source records are shared,
frequently updated, or need independent management.
""")

client.close()
