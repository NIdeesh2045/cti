
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


def get_server_info(name, uri):
    if not uri:
        print(f"\n{name}: Connection URI is missing.")
        return None

    client = None

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=10000)

        # Verify connection and retrieve server information
        info = client.server_info()

        result = {
            "server": name,
            "version": info.get("version", "Unknown"),
            "gitVersion": info.get("gitVersion", "Unknown"),
            "ok": True,
        }

        print(f"\n{name}")
        print("-" * 35)
        print(f"Version: {result['version']}")
        print(f"Git Version: {result['gitVersion']}")
        print("Connection: Successful")

        return result

    except PyMongoError as error:
        print(f"\n{name}: Connection failed.")
        print(f"Error: {error}")
        return {
            "server": name,
            "ok": False,
            "error": str(error),
        }

    finally:
        if client:
            client.close()


def main():
    print("=" * 50)
    print("MONGODB SERVER VERSION COMPARISON")
    print("=" * 50)

    results = []

    for name, uri in CONNECTIONS.items():
        result = get_server_info(name, uri)
        if result:
            results.append(result)

    print("\n" + "=" * 50)
    print("COMPARISON SUMMARY")
    print("=" * 50)

    successful = [r for r in results if r["ok"]]

    for result in successful:
        print(f"{result['server']}: {result['version']}")

    if len(successful) == 2:
        if successful[0]["version"] == successful[1]["version"]:
            print("\nBoth servers are running the same MongoDB version.")
        else:
            print("\nThe MongoDB server versions are different.")

    report = {
        "activity": "2.1",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }

    with open("activity-2.1/mongodb_info.json", "w") as file:
        json.dump(report, file, indent=4)

    print("\nResults saved to activity-2.1/mongodb_info.json")


if __name__ == "__main__":
    main()

