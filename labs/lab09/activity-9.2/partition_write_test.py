from datetime import datetime, timezone
from pymongo import MongoClient, WriteConcern
from pymongo.errors import PyMongoError

URI = "mongodb://localhost:27118/?directConnection=true"
DATABASE = "lab09_partition"
COLLECTION = "partition_test"

client = MongoClient(
    URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000
)

def test_write(concern_name, write_concern):
    collection = client[DATABASE].get_collection(
        COLLECTION,
        write_concern=write_concern
    )

    document = {
        "test": "network_partition",
        "concern": concern_name,
        "createdAt": datetime.now(timezone.utc)
    }

    try:
        result = collection.insert_one(document)
        print(f"{concern_name}: SUCCESS")
        print(f"Inserted ID: {result.inserted_id}")
    except PyMongoError as error:
        print(f"{concern_name}: FAILED")
        print(f"Reason: {error}")

try:
    client.admin.command("ping")
    print("Connected to MongoDB.")
    print("Testing write concerns...\n")

    test_write("w:1", WriteConcern(w=1))

    test_write(
        "w:majority",
        WriteConcern(w="majority", wtimeout=10000)
    )

finally:
    client.close()
    print("\nConnection closed.")
