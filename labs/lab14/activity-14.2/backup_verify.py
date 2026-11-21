
import argparse
import getpass
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

from pymongo import MongoClient

CONTAINER = "lab13-mongo1"
BACKUP_ROOT = Path("backups")
RETENTION_DAYS = 7


def docker_tool(tool, username, password, archive=None):
    from urllib.parse import quote_plus

    uri = (
        f"mongodb://{quote_plus(username)}:{quote_plus(password)}"
        "@localhost:27017/?authSource=admin"
    )

    command = [
        "docker", "exec", "-i", CONTAINER,
        tool, "--uri", uri, "--archive"
    ]

    if tool == "mongorestore":
        command.append("--drop")

    return subprocess.run(
        command,
        input=archive,
        capture_output=True,
        check=True
    )


def create_backup(username, password):
    BACKUP_ROOT.mkdir(exist_ok=True)
    filename = datetime.now().strftime("backup_%Y%m%d_%H%M%S.archive")
    path = BACKUP_ROOT / filename

    start = time.time()
    result = docker_tool("mongodump", username, password)
    path.write_bytes(result.stdout)

    print(f"Backup created: {path}")
    print(f"Backup time: {time.time() - start:.2f} seconds")
    return path


def apply_retention():
    cutoff = time.time() - RETENTION_DAYS * 86400

    for file in BACKUP_ROOT.glob("*.archive"):
        if file.stat().st_mtime < cutoff:
            file.unlink()
            print(f"Deleted expired backup: {file}")


def verify_restore(username, password):
    client = MongoClient(
        "mongodb://localhost:27317",
        directConnection=True,
        username=username,
        password=password,
        authSource="admin"
    )

    collection = client.backup_test.records
    collection.drop()

    collection.insert_many([
        {"_id": i, "value": f"original_{i}", "verified": True}
        for i in range(1000)
    ])

    from urllib.parse import quote_plus

    uri = (
        f"mongodb://{quote_plus(username)}:{quote_plus(password)}"
        "@localhost:27017/?authSource=admin"
    )

    start = time.time()
    backup = subprocess.run(
        ["docker", "exec", "-i", CONTAINER,
         "mongodump", "--uri", uri, "--db", "backup_test", "--archive"],
        capture_output=True, check=True
    )
    backup_time = time.time() - start

    collection.update_many({}, {"$set": {"verified": False}})

    start = time.time()
    subprocess.run(
        ["docker", "exec", "-i", CONTAINER,
         "mongorestore", "--uri", uri, "--archive",
         "--drop", "--nsInclude=backup_test.*"],
        input=backup.stdout,
        capture_output=True,
        check=True
    )
    restore_time = time.time() - start

    restored = client.backup_test.records
    count = restored.count_documents({})
    valid = restored.count_documents({"verified": True})

    print(f"Restored documents: {count}")
    print(f"Original documents verified: {valid}")
    print(f"Backup time: {backup_time:.2f}s")
    print(f"Restore time: {restore_time:.2f}s")
    print("Restore verification:", "PASSED" if count == 1000 and valid == 1000 else "FAILED")

    client.close()


def benchmark(username, password):
    client = MongoClient(
        "mongodb://localhost:27317",
        directConnection=True,
        username=username,
        password=password,
        authSource="admin"
    )

    collection = client.backup_benchmark.records

    from urllib.parse import quote_plus
    uri = (
        f"mongodb://{quote_plus(username)}:{quote_plus(password)}"
        "@localhost:27017/?authSource=admin"
    )

    for size in (1000, 10000, 100000):
        collection.drop()

        for start_id in range(0, size, 5000):
            batch = [
                {"_id": i, "value": f"benchmark_{i}"}
                for i in range(start_id, min(start_id + 5000, size))
            ]
            collection.insert_many(batch)

        start = time.time()
        backup = subprocess.run(
            ["docker", "exec", "-i", CONTAINER,
             "mongodump", "--uri", uri,
             "--db", "backup_benchmark", "--archive"],
            capture_output=True, check=True
        )
        backup_time = time.time() - start

        start = time.time()
        subprocess.run(
            ["docker", "exec", "-i", CONTAINER,
             "mongorestore", "--uri", uri, "--archive",
             "--drop", "--nsInclude=backup_benchmark.*"],
            input=backup.stdout,
            capture_output=True,
            check=True
        )
        restore_time = time.time() - start

        print(
            f"{size:,} documents | "
            f"Backup: {backup_time:.2f}s | "
            f"Restore: {restore_time:.2f}s"
        )

    client.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--schedule", action="store_true")
    args = parser.parse_args()

    username = input("MongoDB username [lab13_admin]: ").strip() or "lab13_admin"
    password = getpass.getpass("MongoDB password: ")

    if args.verify:
        verify_restore(username, password)
    elif args.benchmark:
        benchmark(username, password)
    elif args.schedule:
        print("Hourly backup scheduler started. Press Ctrl+C to stop.")
        try:
            while True:
                create_backup(username, password)
                apply_retention()
                time.sleep(3600)
        except KeyboardInterrupt:
            print("Scheduler stopped.")
    else:
        create_backup(username, password)
        apply_retention()


if __name__ == "__main__":
    main()
