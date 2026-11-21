
import json
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from cassandra.cluster import Cluster

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "threats_100k.jsonl"

HOST = os.getenv("CASSANDRA_HOST", "localhost")
PORT = int(os.getenv("CASSANDRA_PORT", "9042"))

MAX_PENDING = 200

cluster = Cluster([HOST], port=PORT)
session = cluster.connect("lab18")

print("Connected to Cassandra successfully!")

source_stmt = session.prepare("""
    INSERT INTO threats_by_source (
        source, published_date, published_at, threat_id,
        title, threat_type, severity, status, target,
        technique, campaign_id, is_synthetic
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""")

type_stmt = session.prepare("""
    INSERT INTO threats_by_type (
        threat_type, published_date, published_at, threat_id,
        title, source, severity, status, target,
        technique, campaign_id, is_synthetic
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""")

pending = []
total = 0

def wait_for_writes():
    global pending

    for future in pending:
        future.result()

    pending.clear()

try:
    print("Resuming/updating all 100,000 records...")

    with DATA_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)

            published_at = datetime.fromisoformat(
                record["published_at"]
            ).replace(tzinfo=None)

            published_date = published_at.date()

            pending.append(session.execute_async(
                source_stmt,
                (
                    record["source"], published_date, published_at,
                    record["threat_id"], record["title"],
                    record["type"], record["severity"],
                    record["status"], record["target"],
                    record["technique"], record["campaign_id"],
                    record["is_synthetic"]
                )
            ))

            pending.append(session.execute_async(
                type_stmt,
                (
                    record["type"], published_date, published_at,
                    record["threat_id"], record["title"],
                    record["source"], record["severity"],
                    record["status"], record["target"],
                    record["technique"], record["campaign_id"],
                    record["is_synthetic"]
                )
            ))

            total += 1

            if len(pending) >= MAX_PENDING:
                wait_for_writes()

            if total % 10000 == 0:
                print(f"Processed: {total:,}")

    wait_for_writes()

    print("\nAll Cassandra writes completed successfully.")

    source_count = session.execute(
        "SELECT COUNT(*) FROM threats_by_source"
    ).one()[0]

    type_count = session.execute(
        "SELECT COUNT(*) FROM threats_by_type"
    ).one()[0]

    print(f"Threats by source: {source_count:,}")
    print(f"Threats by type: {type_count:,}")

finally:
    cluster.shutdown()
