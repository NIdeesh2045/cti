
import os
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, DESCENDING

# Load configuration
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Connect to MongoDB
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")

# Separate Lab18 database
db = client["lab18_threats"]

print("MongoDB connected successfully!")

# Create collections if they do not exist
existing = db.list_collection_names()

if "threats" not in existing:
    db.create_collection("threats")

if "full_threats" not in existing:
    db.create_collection("full_threats")

threats = db["threats"]
full_threats = db["full_threats"]

# Indexes for threat history queries
full_threats.create_index(
    [("source", ASCENDING), ("published_at", DESCENDING)],
    name="source_timestamp_idx"
)

full_threats.create_index(
    [("type", ASCENDING)],
    name="threat_type_idx"
)

full_threats.create_index(
    [("severity", ASCENDING)],
    name="severity_idx"
)

full_threats.create_index(
    [("target", ASCENDING), ("published_at", DESCENDING)],
    name="target_timestamp_idx"
)

full_threats.create_index(
    [("threat_id", ASCENDING)],
    unique=True,
    name="threat_id_unique_idx"
)

# Dashboard document with embedded recent threats.
# The importer will maintain the latest 50 records here.
threats.update_one(
    {"_id": "lab18_dashboard"},
    {
        "$setOnInsert": {
            "name": "Lab18 Threat Intelligence Dashboard",
            "recent_threats": [],
            "description": "Dashboard summary containing the latest 50 threats"
        }
    },
    upsert=True
)

print("\nLab18 MongoDB schema created successfully!")

print("\nDatabase:", db.name)
print("Collections:", db.list_collection_names())

print("\nIndexes on full_threats:")
for index in full_threats.list_indexes():
    print(index["name"])

print("\nExisting threat records:", full_threats.count_documents({}))
print("Dashboard document:", threats.count_documents({}))

client.close()
