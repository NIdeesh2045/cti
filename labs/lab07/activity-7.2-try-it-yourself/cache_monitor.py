import os
import re
import time
import requests
from pathlib import Path
from datetime import datetime, timezone

from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

URI = os.getenv("MONGODB_LOCAL_URI")

if not URI:
    raise RuntimeError("MONGODB_LOCAL_URI not found")

README_URL = (
    "https://raw.githubusercontent.com/"
    "jacobdjwilson/awesome-annual-security-reports/main/README.md"
)

DB_NAME = "lab07_working_set"
WORKLOAD_COLLECTION = "security_reports_working_set"
DISCOVERY_COLLECTION = "new_report_discoveries"

CHECK_INTERVAL = 10


def fetch_reports():
    response = requests.get(README_URL, timeout=30)
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

    return reports


def get_cache_metrics(client):
    status = client.admin.command("serverStatus")
    cache = status.get("wiredTiger", {}).get("cache", {})

    current = cache.get("bytes currently in the cache", 0)
    maximum = cache.get("maximum bytes configured", 0)
    requested = cache.get("pages requested from the cache", 0)
    pages_read = cache.get("pages read into cache", 0)

    occupancy = current / maximum * 100 if maximum else 0

    # Approximate cache hit ratio from cumulative counters.
    hit_ratio = (
        max(0, 1 - pages_read / requested) * 100
        if requested else 0
    )

    return {
        "current_mb": current / (1024 ** 2),
        "maximum_mb": maximum / (1024 ** 2),
        "occupancy": occupancy,
        "pages_requested": requested,
        "pages_read": pages_read,
        "hit_ratio": hit_ratio
    }


def main():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")

    db = client[DB_NAME]
    workload = db[WORKLOAD_COLLECTION]
    discoveries = db[DISCOVERY_COLLECTION]

    print("=" * 70)
    print("LAB 7.2 - WIREDTIGER CACHE & NEW REPORT MONITOR")
    print("=" * 70)
    print("Monitoring interval:", CHECK_INTERVAL, "seconds")
    print("Press Ctrl+C to stop.")

    cycle = 0

    try:
        while True:
            cycle += 1
            timestamp = datetime.now(timezone.utc)

            print("\n" + "=" * 70)
            print("MONITORING CYCLE:", cycle)
            print("UTC time:", timestamp.isoformat())

            # Check for new reports in the source repository.
            try:
                reports = fetch_reports()

                known_paths = set(
                    workload.distinct("report_path")
                )

                known_paths.update(
                    discoveries.distinct("report_path")
                )

                new_reports = [
                    report for report in reports
                    if report["report_path"] not in known_paths
                ]

                if new_reports:
                    operations = []

                    for report in new_reports:
                        operations.append(
                            UpdateOne(
                                {"report_path": report["report_path"]},
                                {
                                    "$setOnInsert": {
                                        **report,
                                        "discovered_at": timestamp,
                                        "source": "awesome-annual-security-reports"
                                    }
                                },
                                upsert=True
                            )
                        )

                    result = discoveries.bulk_write(operations)

                    print("New reports discovered:", len(new_reports))
                    print("New records inserted:", result.upserted_count)

                    for report in new_reports[:5]:
                        print("-", report["title"], "|", report["organization"])
                else:
                    print("New reports discovered: 0")

                print("Current source catalog entries:", len(reports))

            except Exception as error:
                print("Report check failed:", error)

            # Report WiredTiger cache metrics.
            try:
                metrics = get_cache_metrics(client)

                print("\nWIREDTIGER CACHE")
                print("-" * 50)
                print(f"Cache used: {metrics['current_mb']:.2f} MB")
                print(f"Cache configured: {metrics['maximum_mb']:.2f} MB")
                print(f"Cache occupancy: {metrics['occupancy']:.2f}%")
                print(f"Pages requested: {metrics['pages_requested']:,}")
                print(f"Pages read into cache: {metrics['pages_read']:,}")
                print(
                    "Approximate cache hit ratio: "
                    f"{metrics['hit_ratio']:.2f}%"
                )

            except Exception as error:
                print("Cache metrics unavailable:", error)

            print("\nNext check in", CHECK_INTERVAL, "seconds...")
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")

    finally:
        print(
            "Total newly discovered reports:",
            discoveries.count_documents({})
        )
        client.close()


if __name__ == "__main__":
    main()
