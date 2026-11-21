
import os
import json
from pathlib import Path
from collections import Counter

from dotenv import load_dotenv
from neo4j import GraphDatabase
from pymongo import MongoClient

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "activity-18.1"

neo = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(
        os.getenv("NEO4J_USER", "neo4j"),
        os.getenv("NEO4J_PASSWORD")
    )
)

mongo = MongoClient(
    os.getenv("MONGO_URI", "mongodb://localhost:27017/")
)

threats = mongo["lab18_threats"]["full_threats"]

try:
    neo.verify_connectivity()

    print("Starting Lab18 graph-based analysis...")

    with neo.session() as session:

        # Find campaigns reported by multiple sources.
        communities = list(session.run("""
            MATCH (t:Lab18Threat)-[:HAS_CAMPAIGN]->(c:Lab18Campaign)
            MATCH (t)-[:REPORTED_BY]->(s:Lab18Source)

            WITH c,
                 collect(DISTINCT s.name) AS sources,
                 collect(t.threat_id) AS threat_ids,
                 count(t) AS threat_count

            WHERE size(sources) > 1

            RETURN
                c.campaign_id AS campaign_id,
                c.family AS campaign_family,
                sources,
                threat_ids,
                threat_count,
                size(sources) AS source_count

            ORDER BY source_count DESC, threat_count DESC
            LIMIT 100
        """))

        # Aggregate source pairs sharing campaigns.
        source_pairs = list(session.run("""
            MATCH (t:Lab18Threat)-[:HAS_CAMPAIGN]->(c:Lab18Campaign)
            MATCH (t)-[:REPORTED_BY]->(s:Lab18Source)

            WITH c, collect(DISTINCT s.name) AS sources
            WHERE size(sources) > 1

            UNWIND sources AS source_a
            UNWIND sources AS source_b

            WITH c, source_a, source_b
            WHERE source_a < source_b

            RETURN
                source_a,
                source_b,
                count(c) AS shared_campaigns

            ORDER BY shared_campaigns DESC
            LIMIT 20
        """))

        # Overall graph statistics.
        stats = session.run("""
            MATCH (t:Lab18Threat)
            WITH count(t) AS threats

            MATCH (s:Lab18Source)
            WITH threats, count(s) AS sources

            MATCH (c:Lab18Campaign)
            RETURN
                threats,
                sources,
                count(c) AS campaigns
        """).single()

    community_results = []
    cross_reference_results = []

    for community in communities:

        threat_ids = community["threat_ids"]

        mongo_records = list(
            threats.find(
                {"threat_id": {"$in": threat_ids}},
                {
                    "_id": 0,
                    "threat_id": 1,
                    "title": 1,
                    "source": 1,
                    "type": 1,
                    "severity": 1,
                    "target": 1,
                    "campaign_id": 1,
                    "is_synthetic": 1
                }
            )
        )

        community_results.append({
            "campaign_id": community["campaign_id"],
            "campaign_family": community["campaign_family"],
            "sources": community["sources"],
            "source_count": community["source_count"],
            "threat_count": community["threat_count"],
            "threat_ids": threat_ids
        })

        cross_reference_results.extend(mongo_records)

    pair_results = [
        {
            "source_a": row["source_a"],
            "source_b": row["source_b"],
            "shared_campaigns": row["shared_campaigns"]
        }
        for row in source_pairs
    ]

    output = {
        "dataset": "100,000 synthetic threat records",
        "graph_statistics": {
            "threat_nodes": stats["threats"],
            "source_nodes": stats["sources"],
            "campaign_nodes": stats["campaigns"]
        },
        "cross_source_campaigns_found": len(community_results),
        "source_pair_analysis": pair_results,
        "communities": community_results,
        "mongodb_cross_reference": cross_reference_results
    }

    output_path = OUTPUT_DIR / "graph_analysis_results.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=4, default=str)

    print("\nGRAPH ANALYSIS RESULTS")
    print("=" * 55)

    print(f"Threat nodes: {stats['threats']:,}")
    print(f"Source nodes: {stats['sources']:,}")
    print(f"Campaign nodes: {stats['campaigns']:,}")

    print(
        f"Cross-source campaigns identified: "
        f"{len(community_results):,}"
    )

    print(
        f"MongoDB threat records cross-referenced: "
        f"{len(cross_reference_results):,}"
    )

    print("\nTOP SOURCE PAIRS")

    for pair in pair_results[:10]:
        print(
            f"{pair['source_a']} + {pair['source_b']}: "
            f"{pair['shared_campaigns']} shared campaigns"
        )

    print("\nSAMPLE CROSS-SOURCE CAMPAIGNS")

    for community in community_results[:5]:
        print(
            f"{community['campaign_id']} | "
            f"Sources: {', '.join(community['sources'])} | "
            f"Threats: {community['threat_count']}"
        )

    print("\nResults saved to:")
    print(output_path)

    print(
        "\nNote: Shared synthetic campaigns indicate "
        "potential relationships, not confirmed false positives."
    )

finally:
    neo.close()
    mongo.close()
