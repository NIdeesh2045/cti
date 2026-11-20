
import os
import json
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

CONNECTIONS = {
    "Docker MongoDB": os.getenv("MONGODB_LOCAL_URI"),
    "MongoDB Atlas": os.getenv("MONGODB_ATLAS_URI"),
}

FIELDS = [
    "version",
    "gitVersion",
    "platform",
    "bits",
    "allocator",
    "javascriptEngine",
    "maxBsonObjectSize",
    "storageEngines",
    "modules",
]


def get_details(name, uri):
    if not uri:
        print(f"\n{name}: URI not configured")
        return {"server": name, "connected": False}

    client = None

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=10000)
        info = client.server_info()

        details = {
            field: info.get(field, "Not provided by server")
            for field in FIELDS
        }

        print(f"\n{name}")
        print("-" * 45)

        for field, value in details.items():
            print(f"{field}: {value}")

        return {
            "server": name,
            "connected": True,
            "details": details,
        }

    except PyMongoError as error:
        print(f"\n{name}: Connection failed - {error}")
        return {
            "server": name,
            "connected": False,
            "error": str(error),
        }

    finally:
        if client:
            client.close()


def main():
    print("=" * 55)
    print("MONGODB SERVER DETAILS COMPARISON")
    print("=" * 55)

    results = [
        get_details(name, uri)
        for name, uri in CONNECTIONS.items()
    ]

    report = {
        "activity": "2.1 - Try It Yourself",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }

    output_path = "activity-2.1-try-it-yourself/mongodb_details.json"

    with open(output_path, "w") as file:
        json.dump(report, file, indent=4, default=str)

    print("\nResults saved to", output_path)


if __name__ == "__main__":
    main()

