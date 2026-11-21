
import os
import json
import time
import statistics
import uuid
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient
from cassandra.cluster import Cluster
from neo4j import GraphDatabase

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "activity-18.1"
OUTPUT_DIR.mkdir(exist_ok=True)

RUNS = 10
INSERT_BATCH_SIZE = 1000

SOURCE = "CISA KEV"
TARGET = "Healthcare"

# Connections
mongo_client = MongoClient(
    os.getenv("MONGO_URI", "mongodb://localhost:27017/")
)
mdb = mongo_client["lab18_threats"]
threats = mdb["full_threats"]
benchmark_mongo = mdb["benchmark_inserts"]

cluster = Cluster([
    os.getenv("CASSANDRA_HOST", "localhost")
], port=int(os.getenv("CASSANDRA_PORT", "9042")))
cs = cluster.connect("lab18")

neo = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(
        os.getenv("NEO4J_USER", "neo4j"),
        os.getenv("NEO4J_PASSWORD")
    )
)

neo.verify_connectivity()

results = []


def measure(label, database, function):
    timings = []

    for _ in range(RUNS):
        start = time.perf_counter()
        function()
        elapsed = (time.perf_counter() - start) * 1000
        timings.append(elapsed)

    median = statistics.median(timings)

    results.append({
        "test": label,
        "database": database,
        "runs": RUNS,
        "median_ms": round(median, 3),
        "min_ms": round(min(timings), 3),
        "max_ms": round(max(timings), 3)
    })

    print(
        f"{label:25} | {database:10} | "
        f"Median: {median:.3f} ms"
    )


def mongo_history():
    list(
        threats.find(
            {"source": SOURCE},
            {"_id": 0, "threat_id": 1, "title": 1,
             "published_at": 1, "severity": 1}
        ).sort("published_at", -1).limit(100)
    )


def cassandra_history():
    return list(cs.execute(
        """
        SELECT threat_id, title, published_at, severity
        FROM threats_by_source
        WHERE source = %s
        LIMIT 100
        """,
        (SOURCE,)
    ))


def neo_history():
    with neo.session() as session:
        return list(session.run("""
            MATCH (t:Lab18Threat)-[:REPORTED_BY]->
                  (s:Lab18Source {name: $source})
            RETURN t.threat_id AS threat_id,
                   t.title AS title,
                   t.published_at AS published_at,
                   t.severity AS severity
            ORDER BY t.published_at DESC
            LIMIT 100
        """, source=SOURCE))


def mongo_target():
    return list(
        threats.find(
            {"target": TARGET},
            {"_id": 0, "threat_id": 1, "title": 1,
             "source": 1, "severity": 1}
        ).sort("published_at", -1).limit(100)
    )


def cassandra_target():
    return list(cs.execute(
        """
        SELECT threat_id, title, source, severity
        FROM threats_by_target
        WHERE target = %s
        LIMIT 100
        """,
        (TARGET,)
    ))


def neo_target():
    with neo.session() as session:
        return list(session.run("""
            MATCH (t:Lab18Threat)
            WHERE t.target = $target
            RETURN t.threat_id AS threat_id,
                   t.title AS title,
                   t.severity AS severity
            ORDER BY t.published_at DESC
            LIMIT 100
        """, target=TARGET))


def mongo_daily():
    return list(threats.aggregate([
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$published_at"
                    }
                },
                "total": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]))


def cassandra_daily():
    return list(cs.execute(
        "SELECT published_date, total_threats FROM daily_threat_volume"
    ))


def neo_daily():
    with neo.session() as session:
        return list(session.run("""
            MATCH (t:Lab18Threat)
            WITH date(t.published_at) AS day, count(*) AS total
            RETURN day, total
            ORDER BY day
        """))


def benchmark_mongo_insert(run_number):
    docs = [{
        "benchmark_id": f"M-{run_number}-{i}",
        "run": run_number,
        "created_at": datetime.now(timezone.utc),
        "is_benchmark": True
    } for i in range(INSERT_BATCH_SIZE)]

    benchmark_mongo.insert_many(docs, ordered=False)


def benchmark_cassandra_insert(run_number):
    stmt = cs.prepare("""
        INSERT INTO benchmark_inserts
        (run_id, benchmark_id, created_at)
        VALUES (?, ?, ?)
    """)

    pending = []

    for i in range(INSERT_BATCH_SIZE):
        pending.append(cs.execute_async(
            stmt,
            (
                str(run_number),
                f"C-{run_number}-{i}",
                datetime.now(timezone.utc).replace(tzinfo=None)
            )
        ))

        if len(pending) >= 100:
            for future in pending:
                future.result()
            pending.clear()

    for future in pending:
        future.result()


def benchmark_neo_insert(run_number):
    rows = [{
        "benchmark_id": f"N-{run_number}-{i}",
        "run": run_number
    } for i in range(INSERT_BATCH_SIZE)]

    with neo.session() as session:
        session.run("""
            UNWIND $rows AS row
            CREATE (:Lab18BenchmarkInsert {
                benchmark_id: row.benchmark_id,
                run: row.run,
                is_benchmark: true
            })
        """, rows=rows).consume()


def run_insert_benchmark(database, function):
    for run_number in range(1, RUNS + 1):
        start = time.perf_counter()
        function(run_number)
        elapsed = time.perf_counter() - start

        throughput = INSERT_BATCH_SIZE / elapsed

        results.append({
            "test": "Insert throughput",
            "database": database,
            "runs": 1,
            "batch_size": INSERT_BATCH_SIZE,
            "run": run_number,
            "elapsed_seconds": round(elapsed, 4),
            "throughput_records_per_second": round(throughput, 2)
        })

        print(
            f"Insert run {run_number:02d} | {database:10} | "
            f"{throughput:,.2f} records/sec"
        )


try:
    print("\nLAB18.1 DATABASE PERFORMANCE BENCHMARK")
    print("=" * 75)
    print(f"Query repetitions: {RUNS}")
    print(f"History source: {SOURCE}")
    print(f"Target: {TARGET}")

    # Create isolated Cassandra benchmark table.
    cs.execute("""
        CREATE TABLE IF NOT EXISTS benchmark_inserts (
            run_id text,
            benchmark_id text,
            created_at timestamp,
            PRIMARY KEY ((run_id), benchmark_id)
        )
    """)

    # 1. Threat history retrieval
    print("\n1. THREAT HISTORY RETRIEVAL")
    measure("Threat history", "MongoDB", mongo_history)
    measure("Threat history", "Cassandra", cassandra_history)
    measure("Threat history", "Neo4j", neo_history)

    # 2. Target and spread analysis
    print("\n2. TARGET AND SPREAD ANALYSIS")
    measure("Target analysis", "MongoDB", mongo_target)
    measure("Target analysis", "Cassandra", cassandra_target)
    measure("Target analysis", "Neo4j", neo_target)

    # 3. Daily threat volume analytics
    print("\n3. DAILY THREAT VOLUME")
    measure("Daily volume", "MongoDB", mongo_daily)
    measure("Daily volume", "Cassandra", cassandra_daily)
    measure("Daily volume", "Neo4j", neo_daily)

    # 4. Insert throughput
    print("\n4. INSERT THROUGHPUT")
    run_insert_benchmark("MongoDB", benchmark_mongo_insert)
    run_insert_benchmark("Cassandra", benchmark_cassandra_insert)
    run_insert_benchmark("Neo4j", benchmark_neo_insert)

    # Summarize insert throughput with median.
    print("\nINSERT THROUGHPUT MEDIANS")
    for database in ["MongoDB", "Cassandra", "Neo4j"]:
        values = [
            row["throughput_records_per_second"]
            for row in results
            if row["test"] == "Insert throughput"
            and row["database"] == database
        ]

        print(
            f"{database}: "
            f"{statistics.median(values):,.2f} records/sec"
        )

    # Save all results.
    output_file = OUTPUT_DIR / "benchmark_results.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, default=str)

    print("\n" + "=" * 75)
    print("BENCHMARKS COMPLETED")
    print(f"Results saved to: {output_file}")

finally:
    neo.close()
    mongo_client.close()
    cluster.shutdown()
