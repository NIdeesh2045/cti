
import os
from pymongo import MongoClient

client = MongoClient(
    "localhost",
    27317,
    username="lab13_admin",
    password=os.environ["MONGO_PASSWORD"],
    authSource="admin",
    directConnection=True
)

db = client["fraud_detection"]

db.transactions.delete_many({})

transactions = [
    {
        "txn_id": "TXN001",
        "user_id": "U001",
        "receiver_id": "U002",
        "amount": 5000,
        "status": "completed",
        "risk": "low"
    },
    {
        "txn_id": "TXN002",
        "user_id": "U001",
        "receiver_id": "U003",
        "amount": 7500,
        "status": "completed",
        "risk": "high"
    },
    {
        "txn_id": "TXN003",
        "user_id": "U002",
        "receiver_id": "U004",
        "amount": 12000,
        "status": "pending",
        "risk": "high"
    }
]

db.transactions.insert_many(transactions)

print("MongoDB fraud database created!")
print("Database:", db.name)
print("Transactions:", db.transactions.count_documents({}))

client.close()
