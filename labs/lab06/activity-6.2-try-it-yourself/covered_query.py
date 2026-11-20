import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

MONGO_URI = os.getenv("MONGODB_LOCAL_URI")

if not MONGO_URI:
    raise ValueError("MONGODB_LOCAL_URI not found in .env")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")

db = client["lab06_indexing"]
products = db["index_benchmark"]

try:
    print("=" * 65)
    print("LAB 6.2 - TRY IT YOURSELF: COVERED QUERY")
    print("=" * 65)

    print("\n[1] Creating compound index")

    products.create_index(
        [("category", ASCENDING), ("name", ASCENDING)],
        name="category_name_covered_idx"
    )

    print("Created: category_name_covered_idx")

    print("\n[2] Executing covered query")

    query = {"category": "Electronics"}

    projection = {
        "_id": 0,
        "category": 1,
        "name": 1
    }

    explanation = products.find(
        query,
        projection
    ).explain()

    execution = explanation.get("executionStats", {})
    winning_plan = explanation.get("queryPlanner", {}).get(
        "winningPlan", {}
    )

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

    stages = find_stages(winning_plan)

    print("Execution stages:", " -> ".join(stages))
    print("Documents examined:",
          execution.get("totalDocsExamined", "N/A"))
    print("Keys examined:",
          execution.get("totalKeysExamined", "N/A"))
    print("Documents returned:",
          execution.get("nReturned", "N/A"))

    print("\n[3] Sample covered query results")

    results = list(products.find(
        query,
        projection
    ).limit(5))

    for document in results:
        print(document)

    if "FETCH" not in stages and execution.get(
        "totalDocsExamined"
    ) == 0:
        print("\nSUCCESS: Covered query verified.")
        print("FETCH stage eliminated.")
    else:
        print("\nCovered query requires further verification.")

    print("\nLab 6.2 covered query completed.")

finally:
    client.close()
