
import os
import time
import json
import urllib.request
from datetime import datetime
from getpass import getpass

from pymongo import MongoClient
from pymongo.errors import PyMongoError

# ==========================================
# CONFIGURATION
# ==========================================

USERNAME = "lab13_admin"
LOG_FILE = "metrics.log"
INTERVAL = 30

WEBHOOK_URL = os.getenv("MONGODB_WEBHOOK_URL")

password = getpass("MongoDB admin password: ")

client = MongoClient(
    "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/",
    username=USERNAME,
    password=password,
    authSource="admin",
    replicaSet="rs0",
    serverSelectionTimeoutMS=10000
)


# ==========================================
# WEBHOOK ALERT
# ==========================================

def send_webhook_alert(message):
    if not WEBHOOK_URL:
        return

    try:
        if "discord.com" in WEBHOOK_URL:
            payload = {"content": message}
        else:
            payload = {"text": message}

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            WEBHOOK_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            print("Webhook alert sent:", response.status)

    except Exception as error:
        print("Webhook delivery failed:", error)


# ==========================================
# CACHE HIT RATIO
# ==========================================

def calculate_cache_hit_ratio(cache):
    """
    Calculate cache hit ratio using WiredTiger page counters.

    Formula:
    Cache hits = pages requested - pages read from disk

    Cache hit ratio = cache hits / pages requested * 100
    """

    pages_requested = cache.get(
        "pages requested from the cache", 0
    )

    pages_read = cache.get(
        "pages read into cache", 0
    )

    if pages_requested <= 0:
        return None

    hits = max(pages_requested - pages_read, 0)

    return (hits / pages_requested) * 100


# ==========================================
# REPLICA SET METRICS
# ==========================================

def get_replica_metrics():

    try:
        result = client.admin.command("replSetGetStatus")

        members = result.get("members", [])

        primary = next(
            (
                member for member in members
                if member.get("stateStr") == "PRIMARY"
            ),
            None
        )

        if not primary:
            return "No PRIMARY", None

        primary_time = primary.get("optimeDate")

        if not primary_time:
            return "Unknown", None

        secondary_lags = []

        for member in members:

            if member.get("stateStr") != "SECONDARY":
                continue

            if member.get("health") != 1:
                continue

            secondary_time = member.get("optimeDate")

            if secondary_time:
                lag = (
                    primary_time - secondary_time
                ).total_seconds()

                secondary_lags.append(max(lag, 0))

        replication_lag = (
            max(secondary_lags)
            if secondary_lags else None
        )

        unhealthy = [
            member for member in members
            if member.get("health") != 1
        ]

        status = (
            "Healthy"
            if not unhealthy
            else "Unhealthy member detected"
        )

        return status, replication_lag

    except PyMongoError:
        return "Not a replica set / unavailable", None


# ==========================================
# COLLECT MONGODB METRICS
# ==========================================

def get_metrics():

    server = client.admin.command("serverStatus")

    # Connection count
    connections = server.get("connections", {})

    current_connections = connections.get(
        "current", 0
    )

    # Operation counters
    operations = server.get("opcounters", {})

    # WiredTiger cache statistics
    cache = (
        server.get("wiredTiger", {})
        .get("cache", {})
    )

    cache_hit_ratio = calculate_cache_hit_ratio(cache)

    cache_used = cache.get(
        "bytes currently in the cache", 0
    )

    cache_max = cache.get(
        "maximum bytes configured", 0
    )

    # Replica set status and lag
    replica_status, replication_lag = get_replica_metrics()

    return {
        "connections": current_connections,

        "insert": operations.get("insert", 0),
        "query": operations.get("query", 0),
        "update": operations.get("update", 0),
        "delete": operations.get("delete", 0),

        "cache_hit": cache_hit_ratio,
        "cache_used": cache_used,
        "cache_max": cache_max,

        "replica_status": replica_status,
        "replication_lag": replication_lag
    }


# ==========================================
# DISPLAY AND LOG METRICS
# ==========================================

def display_and_log(metrics):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cache_hit = metrics["cache_hit"]

    cache_display = (
        f"{cache_hit:.2f}%"
        if cache_hit is not None
        else "N/A (no page requests)"
    )

    lag = metrics["replication_lag"]

    lag_display = (
        f"{lag:.2f} seconds"
        if lag is not None
        else "N/A"
    )

    rows = [
        ("Connections", metrics["connections"]),
        ("Insert operations", metrics["insert"]),
        ("Query operations", metrics["query"]),
        ("Update operations", metrics["update"]),
        ("Delete operations", metrics["delete"]),
        ("Cache hit ratio", cache_display),
        (
            "Cache used",
            f'{metrics["cache_used"] / 1024 / 1024:.2f} MB'
        ),
        (
            "Cache maximum",
            f'{metrics["cache_max"] / 1024 / 1024:.2f} MB'
        ),
        ("Replica set", metrics["replica_status"]),
        ("Replication lag", lag_display)
    ]

    table = [
        f"\nMONGODB MONITORING REPORT - {timestamp}",
        "-" * 70,
        f"{'METRIC':<30} | {'VALUE':<35}",
        "-" * 70
    ]

    for name, value in rows:
        table.append(
            f"{name:<30} | {str(value):<35}"
        )

    table.append("-" * 70)

    report = "\n".join(table)

    print(report)

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(report + "\n")

    # Cache threshold alert
    if cache_hit is not None and cache_hit < 80:

        message = (
            f"WARNING: MongoDB cache hit ratio is "
            f"{cache_hit:.2f}% (below 80%)"
        )

        print(message)
        send_webhook_alert(message)

    # Replication lag threshold alert
    if lag is not None and lag > 10:

        message = (
            f"WARNING: MongoDB replication lag is "
            f"{lag:.2f} seconds (above 10 seconds)"
        )

        print(message)
        send_webhook_alert(message)


# ==========================================
# MAIN MONITORING LOOP
# ==========================================

def main():

    print("\nMongoDB Monitoring Dashboard Started")
    print("Monitoring interval:", INTERVAL, "seconds")
    print("Log file:", LOG_FILE)

    print(
        "Webhook:",
        "Enabled" if WEBHOOK_URL else "Not configured"
    )

    print("Press Ctrl+C to stop.\n")

    try:

        while True:

            try:
                metrics = get_metrics()
                display_and_log(metrics)

            except PyMongoError as error:
                print("MongoDB monitoring error:", error)

            time.sleep(INTERVAL)

    except KeyboardInterrupt:

        print("\nMonitoring stopped.")

    finally:

        client.close()


if __name__ == "__main__":
    main()
