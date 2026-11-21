
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD")

if not PASSWORD:
    raise ValueError("NEO4J_PASSWORD is missing from .env")

driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD)
)

driver.verify_connectivity()
print("Connected to Neo4j successfully!")

with driver.session() as session:

    # Lab18-specific constraints; existing graph data is preserved.
    session.run("""
        CREATE CONSTRAINT lab18_threat_id IF NOT EXISTS
        FOR (t:Lab18Threat)
        REQUIRE t.threat_id IS UNIQUE
    """)

    session.run("""
        CREATE CONSTRAINT lab18_source_name IF NOT EXISTS
        FOR (s:Lab18Source)
        REQUIRE s.name IS UNIQUE
    """)

    session.run("""
        CREATE CONSTRAINT lab18_campaign_id IF NOT EXISTS
        FOR (c:Lab18Campaign)
        REQUIRE c.campaign_id IS UNIQUE
    """)

    # Verify the Lab18 constraints.
    result = session.run("""
        SHOW CONSTRAINTS
        YIELD name
        WHERE name STARTS WITH 'lab18_'
        RETURN name
        ORDER BY name
    """)

    print("\nLab18 Neo4j constraints:")
    for record in result:
        print("-", record["name"])

driver.close()

print("\nLab18 Neo4j schema created successfully!")
