
import json
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "threats_100k.jsonl"

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD")

BATCH_SIZE = 1000

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

if not PASSWORD:
    raise ValueError("NEO4J_PASSWORD is missing from .env")


def import_batch(tx, rows):
    tx.run("""
        UNWIND $rows AS row

        MERGE (s:Lab18Source {name: row.source})

        MERGE (c:Lab18Campaign {
            campaign_id: row.campaign_id
        })
        SET c.family = row.campaign_family

        MERGE (t:Lab18Threat {
            threat_id: row.threat_id
        })
        SET
            t.title = row.title,
            t.summary = row.summary,
            t.type = row.type,
            t.severity = row.severity,
            t.status = row.status,
            t.target = row.target,
            t.technique = row.technique,
            t.published_at = datetime(row.published_at),
            t.is_synthetic = row.is_synthetic

        MERGE (t)-[:REPORTED_BY]->(s)
        MERGE (t)-[:HAS_CAMPAIGN]->(c)
    """, rows=rows).consume()


driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD)
)

driver.verify_connectivity()
print("Connected to Lab18 Neo4j successfully!")

# Prevent accidental duplicate imports.
with driver.session() as session:
    existing = session.run("""
        MATCH (t:Lab18Threat)
        RETURN count(t) AS total
    """).single()["total"]

if existing > 0:
    driver.close()
    raise RuntimeError(
        f"Import stopped: {existing} Lab18 threat nodes already exist. "
        "No records were imported."
    )

print("Starting Neo4j import...")

total = 0
batch = []

try:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)
            batch.append(record)

            if len(batch) >= BATCH_SIZE:
                with driver.session() as session:
                    session.execute_write(import_batch, batch)

                total += len(batch)
                batch.clear()

                if total % 10000 == 0:
                    print(f"Imported: {total:,}")

    if batch:
        with driver.session() as session:
            session.execute_write(import_batch, batch)

        total += len(batch)

    with driver.session() as session:
        threat_count = session.run("""
            MATCH (t:Lab18Threat)
            RETURN count(t) AS total
        """).single()["total"]

        source_count = session.run("""
            MATCH (s:Lab18Source)
            RETURN count(s) AS total
        """).single()["total"]

        campaign_count = session.run("""
            MATCH (c:Lab18Campaign)
            RETURN count(c) AS total
        """).single()["total"]

        relationship_count = session.run("""
            MATCH (:Lab18Threat)-[r:REPORTED_BY|HAS_CAMPAIGN]->()
            RETURN count(r) AS total
        """).single()["total"]

    print("\nNeo4j import completed!")
    print(f"Records processed: {total:,}")
    print(f"Verified threat nodes: {threat_count:,}")
    print(f"Source nodes: {source_count:,}")
    print(f"Campaign nodes: {campaign_count:,}")
    print(f"Relationships: {relationship_count:,}")

finally:
    driver.close()

print("\nDatabase: Lab18 Neo4j")
print("All imported records are synthetic.")
