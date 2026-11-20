
import time
from getpass import getpass

from pymongo import MongoClient
from pymongo.errors import PyMongoError

password = getpass("MongoDB admin password: ")

client = MongoClient(
    "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/",
    username="lab13_admin",
    password=password,
    authSource="admin",
    replicaSet="rs0",
    serverSelectionTimeoutMS=10000,
    retryWrites=True
)

try:
    # Verify initial primary
    hello = client.admin.command("hello")
    print("Initial primary:", hello.get("primary"))

    # Insert a test document
    db = client["lab13_test"]
    result = db.failover_records.insert_one({
        "message": "PyMongo failover test",
        "timestamp": time.time()
    })
    print("Inserted document:", result.inserted_id)

    # Trigger primary stepdown
    print("\nTriggering primary failover...")
    try:
        client.admin.command({"replSetStepDown": 30, "force": True})
    except PyMongoError as error:
        print("Connection interrupted during stepdown (expected).")

    # Wait for a new primary
    print("Waiting for new primary...")
    for attempt in range(30):
        try:
            hello = client.admin.command("hello")
            if hello.get("isWritablePrimary"):
                print("New primary elected:", hello.get("me"))
                break
        except PyMongoError:
            pass

        time.sleep(2)
    else:
        raise RuntimeError("New primary was not elected in time.")

    # Verify writes after failover
    db.failover_records.insert_one({
        "message": "Write after failover",
        "timestamp": time.time()
    })
    print("Write after failover: SUCCESS")

finally:
    client.close()
