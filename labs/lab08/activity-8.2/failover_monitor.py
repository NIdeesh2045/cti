import time
from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.errors import PyMongoError

NODES = {
    "mongo1": "mongodb://localhost:27117/?directConnection=true",
    "mongo2": "mongodb://localhost:27118/?directConnection=true",
    "mongo3": "mongodb://localhost:27119/?directConnection=true",
}

clients = {
    name: MongoClient(
        uri,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
    )
    for name, uri in NODES.items()
}

database = "lab08_replication"
collection_name = "replication_test"
last_primary = None
cycle = 1

print("=" * 65)
print("LAB 8.2 - REPLICA SET FAILOVER MONITOR")
print("=" * 65)
print("Monitoring interval: 2 seconds")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        timestamp = datetime.now(timezone.utc).isoformat()
        primary_found = False

        for name, client in clients.items():
            try:
                hello = client.admin.command("hello")

                if hello.get("isWritablePrimary"):
                    primary_found = True
                    address = hello.get("me", name)

                    document = client[database][collection_name].find_one()

                    if last_primary != address:
                        print(f"\n*** PRIMARY CHANGE DETECTED: {address} ***\n")
                        last_primary = address

                    print(f"[{timestamp}] Cycle {cycle}")
                    print(f"Connected member: {address}")
                    print("Role: PRIMARY")
                    print(f"Read successful: {document is not None}")
                    print("-" * 65)
                    break

            except PyMongoError as error:
                print(f"{name}: temporarily unavailable ({error})")

        if not primary_found:
            print(f"[{timestamp}] Cycle {cycle}: Election in progress or no primary available.")
            print("-" * 65)

        cycle += 1
        time.sleep(2)

except KeyboardInterrupt:
    print("\nMonitoring stopped.")

finally:
    for client in clients.values():
        client.close()
