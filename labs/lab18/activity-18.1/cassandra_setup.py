
import os
from dotenv import load_dotenv
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

load_dotenv()

HOST = os.getenv("CASSANDRA_HOST", "localhost")
PORT = int(os.getenv("CASSANDRA_PORT", "9042"))

# Connect to Cassandra
cluster = Cluster([HOST], port=PORT)
session = cluster.connect()

print("Connected to Cassandra successfully!")

# Create separate Lab18 keyspace
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS lab18
    WITH replication = {
        'class': 'SimpleStrategy',
        'replication_factor': 1
    }
""")

session.set_keyspace("lab18")

# Query-driven table: threats by source
session.execute("""
    CREATE TABLE IF NOT EXISTS threats_by_source (
        source text,
        published_date date,
        published_at timestamp,
        threat_id text,
        title text,
        threat_type text,
        severity text,
        status text,
        target text,
        technique text,
        campaign_id text,
        is_synthetic boolean,
        PRIMARY KEY ((source), published_date, published_at, threat_id)
    ) WITH CLUSTERING ORDER BY (
        published_date DESC,
        published_at DESC,
        threat_id ASC
    )
""")

# Query-driven table: threats by type
session.execute("""
    CREATE TABLE IF NOT EXISTS threats_by_type (
        threat_type text,
        published_date date,
        published_at timestamp,
        threat_id text,
        title text,
        source text,
        severity text,
        status text,
        target text,
        technique text,
        campaign_id text,
        is_synthetic boolean,
        PRIMARY KEY ((threat_type), published_date, published_at, threat_id)
    ) WITH CLUSTERING ORDER BY (
        published_date DESC,
        published_at DESC,
        threat_id ASC
    )
""")

print("\nLab18 Cassandra schema created successfully!")

print("\nKeyspace: lab18")
print("\nTables:")

for row in session.execute("""
    SELECT table_name
    FROM system_schema.tables
    WHERE keyspace_name = 'lab18'
"""):
    print("-", row.table_name)

cluster.shutdown()
