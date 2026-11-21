
import os
import hashlib
import secrets

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["tasktracker"]

db.users.create_index(
    [("tenant_id", ASCENDING), ("username", ASCENDING)],
    unique=True
)


def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        200000
    ).hex()
    return f"{salt}${digest}"


users = [
    {
        "tenant_id": "tenant_a",
        "username": "alice",
        "role": "admin"
    },
    {
        "tenant_id": "tenant_a",
        "username": "bob",
        "role": "user"
    },
    {
        "tenant_id": "tenant_b",
        "username": "charlie",
        "role": "admin"
    },
    {
        "tenant_id": "tenant_b",
        "username": "david",
        "role": "user"
    }
]

print("Creating TaskTracker test users...")

for user in users:
    password = secrets.token_urlsafe(12)

    db.users.update_one(
        {
            "tenant_id": user["tenant_id"],
            "username": user["username"]
        },
        {
            "$set": {
                **user,
                "password_hash": hash_password(password)
            }
        },
        upsert=True
    )

    print(
        f"Tenant: {user['tenant_id']} | "
        f"Username: {user['username']} | "
        f"Role: {user['role']} | "
        f"Password: {password}"
    )

print("\nUser seeding completed.")

client.close()
