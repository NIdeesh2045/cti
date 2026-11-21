
import os
import time
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from bson.errors import InvalidId

load_dotenv()

# Configuration
MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
TOKEN_MINUTES = 60
RATE_LIMIT = 100
RATE_WINDOW_SECONDS = 60

if not MONGO_URI or not JWT_SECRET:
    raise RuntimeError("MONGO_URI and JWT_SECRET must be configured in .env")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["tasktracker"]

# HTTP Bearer authentication for Swagger
bearer_scheme = HTTPBearer()


# Database initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    client.admin.command("ping")

    db.tasks.create_index(
        [("tenant_id", 1), ("created_at", -1)]
    )

    db.tasks.create_index(
        [("tenant_id", 1), ("owner_id", 1)]
    )

    db.users.create_index(
        [("tenant_id", 1), ("username", 1)],
        unique=True
    )

    # MongoDB-backed rate limiter
    db.rate_limits.create_index(
        [("key", 1), ("window_start", 1)],
        unique=True
    )

    db.rate_limits.create_index(
        "expires_at",
        expireAfterSeconds=0
    )

    yield
    client.close()


# FastAPI application
app = FastAPI(
    title="TaskTracker Multi-Tenant API",
    description="SaaS Task Management API with tenant isolation and RBAC",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# Request models
class LoginRequest(BaseModel):
    tenant_id: str
    username: str
    password: str


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str = Field(default="", max_length=2000)
    priority: str = "medium"


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None


# Password utilities
def hash_password(password: str, salt: str | None = None):
    salt = salt or secrets.token_hex(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        200000
    ).hex()

    return f"{salt}${digest}"


def verify_password(password: str, stored_hash: str):
    try:
        salt, expected = stored_hash.split("$", 1)
        actual = hash_password(password, salt).split("$", 1)[1]
        return secrets.compare_digest(actual, expected)
    except ValueError:
        return False


# Authentication and JWT verification
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        role = payload.get("role")

        if not user_id or not tenant_id or role not in ("admin", "user"):
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

        user = db.users.find_one({
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "role": role
        })

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User no longer exists or is inactive"
            )

        return {
            "user_id": str(user["_id"]),
            "tenant_id": tenant_id,
            "role": role
        }

    except (jwt.InvalidTokenError, InvalidId, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )


# MongoDB-backed rate limiter
def enforce_rate_limit(user: dict):
    now = int(time.time())
    window_start = now - (now % RATE_WINDOW_SECONDS)

    key = f"{user['tenant_id']}:{user['user_id']}"

    try:
        record = db.rate_limits.find_one_and_update(
            {
                "key": key,
                "window_start": window_start
            },
            {
                "$inc": {"count": 1},
                "$setOnInsert": {
                    "expires_at": datetime.now(timezone.utc)
                    + timedelta(seconds=RATE_WINDOW_SECONDS * 2)
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

    except DuplicateKeyError:
        record = db.rate_limits.find_one_and_update(
            {
                "key": key,
                "window_start": window_start
            },
            {"$inc": {"count": 1}},
            return_document=ReturnDocument.AFTER
        )

    if record["count"] > RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )


def get_user_with_rate_limit(
    user: dict = Depends(get_current_user)
):
    enforce_rate_limit(user)
    return user


# Tenant and role filtering
def task_filter(user: dict):
    query = {"tenant_id": user["tenant_id"]}

    if user["role"] != "admin":
        query["owner_id"] = user["user_id"]

    return query


# MongoDB document serialization
def serialize_task(task):
    task["id"] = str(task.pop("_id"))
    return task


# Health endpoint
@app.get("/")
def home():
    return {
        "message": "TaskTracker Multi-Tenant API",
        "status": "running"
    }


@app.get("/health")
def health():
    client.admin.command("ping")
    return {
        "status": "healthy",
        "database": "connected"
    }


# Login endpoint
@app.post("/auth/token")
def login(data: LoginRequest):
    user = db.users.find_one({
        "tenant_id": data.tenant_id,
        "username": data.username
    })

    if not user or not verify_password(
        data.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect tenant, username or password"
        )

    token = jwt.encode(
        {
            "sub": str(user["_id"]),
            "tenant_id": user["tenant_id"],
            "role": user["role"],
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=TOKEN_MINUTES)
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": TOKEN_MINUTES * 60
    }


# CREATE task
@app.post("/tasks/", status_code=201)
def create_task(
    task: TaskCreate,
    user: dict = Depends(get_user_with_rate_limit)
):
    if task.priority not in ("low", "medium", "high"):
        raise HTTPException(400, "Invalid priority")

    doc = {
        "tenant_id": user["tenant_id"],
        "owner_id": user["user_id"],
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": "open",
        "created_at": datetime.now(timezone.utc)
    }

    result = db.tasks.insert_one(doc)
    doc["_id"] = result.inserted_id

    return serialize_task(doc)


# READ all accessible tasks
@app.get("/tasks/")
def list_tasks(
    user: dict = Depends(get_user_with_rate_limit)
):
    tasks = db.tasks.find(task_filter(user)).sort(
        "created_at", -1
    )

    return [serialize_task(task) for task in tasks]


# READ one task
@app.get("/tasks/{task_id}")
def get_task(
    task_id: str,
    user: dict = Depends(get_user_with_rate_limit)
):
    try:
        oid = ObjectId(task_id)
    except InvalidId:
        raise HTTPException(400, "Invalid task ID")

    task = db.tasks.find_one({
        "_id": oid,
        **task_filter(user)
    })

    if not task:
        raise HTTPException(404, "Task not found")

    return serialize_task(task)


# UPDATE task
@app.put("/tasks/{task_id}")
def update_task(
    task_id: str,
    data: TaskUpdate,
    user: dict = Depends(get_user_with_rate_limit)
):
    try:
        oid = ObjectId(task_id)
    except InvalidId:
        raise HTTPException(400, "Invalid task ID")

    updates = data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(400, "No update fields provided")

    if "priority" in updates and updates["priority"] not in (
        "low", "medium", "high"
    ):
        raise HTTPException(400, "Invalid priority")

    if "status" in updates and updates["status"] not in (
        "open", "in_progress", "completed"
    ):
        raise HTTPException(400, "Invalid status")

    result = db.tasks.update_one(
        {
            "_id": oid,
            **task_filter(user)
        },
        {"$set": updates}
    )

    if result.matched_count == 0:
        raise HTTPException(404, "Task not found")

    task = db.tasks.find_one({
        "_id": oid,
        **task_filter(user)
    })

    return serialize_task(task)


# DELETE task
@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: str,
    user: dict = Depends(get_user_with_rate_limit)
):
    try:
        oid = ObjectId(task_id)
    except InvalidId:
        raise HTTPException(400, "Invalid task ID")

    result = db.tasks.delete_one({
        "_id": oid,
        **task_filter(user)
    })

    if result.deleted_count == 0:
        raise HTTPException(404, "Task not found")

    return {
        "message": "Task deleted successfully"
    }


# Admin-only endpoint
@app.get("/admin/users")
def list_tenant_users(
    user: dict = Depends(get_user_with_rate_limit)
):
    if user["role"] != "admin":
        raise HTTPException(403, "Admin access required")

    users = db.users.find(
        {"tenant_id": user["tenant_id"]},
        {"password_hash": 0}
    )

    return [
        {
            "id": str(u["_id"]),
            "username": u["username"],
            "role": u["role"],
            "tenant_id": u["tenant_id"]
        }
        for u in users
    ]
