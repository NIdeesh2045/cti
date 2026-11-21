
import json
import os
from pathlib import Path
from collections import Counter
from datetime import datetime

from dotenv import load_dotenv
from cassandra.cluster import Cluster
from neo4j import GraphDatabase
from pymongo import MongoClient, ASCENDING

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "threats_100k.jsonl"

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

# Database connections
cassandra = Cluster(
    [os.getenv("CASSANDRA_HOST", "localhost")],
    port=int(os.getenv("CASSANDRA_PORT", "9042"))
)
cs = cassandra.connect("lab18")

mongo = MongoClient(
    os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
    serverSelectionTimeoutMS=5000
)
mongo.admin.command("ping")
mongo_db = mongo["lab18_threats"]

neo = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(
        os.getenv("NEO4J_USER", "neo4j"),
        os.getenv("NEO4J_PASSWORD")
    )
)

try:
    neo.verify_connectivity()

    print("Connected to all three databases.")
    print("Preparing Lab18 benchmark structures...")

    # --------------------------------------------------
    # 1. MongoDB indexes
    # --------------------------------------------------

    # target_timestamp_idx already exists from the original
    # MongoDB schema. Do not create a duplicate index.

    # Create only the daily-volume index if missing.
    existing_indexes = mongo_db.full_threats.index_information()

    daily_index_exists = any(
        index.get("key") == [("published_at", ASCENDING)]
        for index in existing_indexes.values()
    )

    if not daily_index_exists:
        mongo_db.full_threats.create_index(
            [("published_at", ASCENDING)],
            name="lab18_daily_volume_idx"
        )

    print("MongoDB indexes checked.")

    # --------------------------------------------------
    # 2. Cassandra query-driven tables
    # --------------------------------------------------

    cs.execute("""
        CREATE TABLE IF NOT EXISTS threats_by_target (
            target text,
            published_date date,
            published_at timestamp,
            threat_id text,
            title text,
            source text,
            threat_type text,
            severity text,
            campaign_id text,
            is_synthetic boolean,
            PRIMARY KEY (
                (target), published_date, published_at, threat_id
            )
        ) WITH CLUSTERING ORDER BY (
            published_date DESC,
            published_at DESC,
            threat_id ASC
        )
    """)

    cs.execute("""
        CREATE TABLE IF NOT EXISTS daily_threat_volume (
            published_date date PRIMARY KEY,
            total_threats int
        )
    """)

    print("Cassandra benchmark tables checked.")

    # --------------------------------------------------
    # 3. Neo4j target index
    # --------------------------------------------------

    with neo.session() as session:
        session.run("""
            CREATE INDEX lab18_target_date_idx IF NOT EXISTS
            FOR (t:Lab18Threat)
            ON (t.target, t.published_at)
        """).consume()

    print("Neo4j target index checked.")

    # --------------------------------------------------
    # 4. Populate Cassandra target table
    # --------------------------------------------------

    existing = cs.execute(
        "SELECT COUNT(*) FROM threats_by_target"
    ).one()[0]

    if existing == 0:

        print("\nImporting 100,000 target records into Cassandra...")

        target_stmt = cs.prepare("""
            INSERT INTO threats_by_target (
                target, published_date, published_at, threat_id,
                title, source, threat_type, severity,
                campaign_id, is_synthetic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """)

        daily_counts = Counter()
        pending = []
        total = 0

        with DATA_FILE.open("r", encoding="utf-8") as file:

            for line in file:
                if not line.strip():
                    continue

                record = json.loads(line)

                published_at = datetime.fromisoformat(
                    record["published_at"]
                ).replace(tzinfo=None)

                published_date = published_at.date()

                daily_counts[published_date] += 1

                future = cs.execute_async(
                    target_stmt,
                    (
                        record["target"],
                        published_date,
                        published_at,
                        record["threat_id"],
                        record["title"],
                        record["source"],
                        record["type"],
                        record["severity"],
                        record["campaign_id"],
                        record["is_synthetic"]
                    )
                )

                pending.append(future)
                total += 1

                # Limit concurrent writes.
                if len(pending) >= 200:
                    for result in pending:
                        result.result()

                    pending.clear()

                if total % 20000 == 0:
                    print(f"Processed: {total:,}")

        # Wait for remaining writes.
        for result in pending:
            result.result()

        print("\nWriting daily volume aggregates...")

        daily_stmt = cs.prepare("""
            INSERT INTO daily_threat_volume (
                published_date, total_threats
            ) VALUES (?, ?)
        """)

        for day, count in daily_counts.items():
            cs.execute(daily_stmt, (day, count))

        print(f"Target records imported: {total:,}")
        print(f"Daily aggregate rows written: {len(daily_counts):,}")

    else:
        print(
            f"\nTarget table already contains approximately "
            f"{existing:,} records. Import skipped."
        )

    # --------------------------------------------------
    # 5. Verify Cassandra tables
    # --------------------------------------------------

    target_count = cs.execute(
        "SELECT COUNT(*) FROM threats_by_target"
    ).one()[0]

    daily_count = cs.execute(
        "SELECT COUNT(*) FROM daily_threat_volume"
    ).one()[0]

    # --------------------------------------------------
    # 6. Final verification
    # --------------------------------------------------

    mongo_count = mongo_db.full_threats.count_documents({})

    with neo.session() as session:
        neo_count = session.run("""
            MATCH (t:Lab18Threat)
            RETURN count(t) AS total
        """).single()["total"]

    print("\n" + "=" * 50)
    print("LAB18 BENCHMARK PREPARATION COMPLETED")
    print("=" * 50)

    print(f"MongoDB threat records: {mongo_count:,}")
    print(f"Cassandra target records: {target_count:,}")
    print(f"Cassandra daily aggregate rows: {daily_count:,}")
    print(f"Neo4j threat nodes: {neo_count:,}")

    if target_count != 100000:
        print("WARNING: Cassandra target count is not 100,000.")

    if mongo_count != 100000:
        print("WARNING: MongoDB count is not 100,000.")

    if neo_count != 100000:
        print("WARNING: Neo4j count is not 100,000.")

finally:
    neo.close()
    mongo.close()
    cassandra.shutdown()

print("\nAll database connections closed.")
