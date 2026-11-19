
#!/bin/bash

set -Eeuo pipefail

mkdir -p /data/db

LOG=/var/log/mongodb.log

wait_mongo() {
    echo "Waiting for MongoDB..."

    for i in $(seq 1 40); do
        if mongosh --quiet "$@" --eval \
            "db.runCommand({ping:1})" >/dev/null 2>&1; then
            echo "MongoDB is ready."
            return 0
        fi

        sleep 1
    done

    echo "ERROR: MongoDB failed to start."
    cat "$LOG" || true
    return 1
}

echo "========================================="
echo "       CTI PLATFORM STARTUP"
echo "========================================="

# 1. Start MongoDB without authentication
echo "[1/5] Starting MongoDB setup mode..."

mongod \
    --fork \
    --logpath "$LOG" \
    --bind_ip 127.0.0.1 \
    --dbpath /data/db

wait_mongo

# 2. Create MongoDB root user
echo "[2/5] Configuring MongoDB authentication..."

: "${MONGO_ROOT_USER:=root}"
: "${MONGO_ROOT_PASSWORD:?MONGO_ROOT_PASSWORD must be supplied at runtime}"

mongosh --quiet admin --eval "
if (!db.getUser('${MONGO_ROOT_USER}')) {
    db.createUser({
        user: '${MONGO_ROOT_USER}',
        pwd: '${MONGO_ROOT_PASSWORD}',
        roles: ['root']
    });
}
"

# 3. Restart MongoDB with authentication
echo "[3/5] Restarting MongoDB with authentication..."

mongod --shutdown >/dev/null 2>&1 || true

sleep 2

mongod \
    --fork \
    --auth \
    --logpath "$LOG" \
    --bind_ip 127.0.0.1 \
    --dbpath /data/db

wait_mongo \
    -u "$MONGO_ROOT_USER" \
    -p "$MONGO_ROOT_PASSWORD" \
    --authenticationDatabase admin

# 4. Check host Ollama
echo "[4/5] Checking host Ollama..."

OLLAMA_URL="${OLLAMA_URL:-http://host.docker.internal:11434}"

if curl --connect-timeout 5 -fsS "$OLLAMA_URL/api/tags" >/dev/null; then
    echo "Ollama is reachable."

    echo "Configured chat model: ${OLLAMA_CHAT_MODEL:-llama3.2:3b}"
    echo "Configured embedding model: ${OLLAMA_EMBEDDING_MODEL:-nomic-embed-text}"
else
    echo "WARNING: Host Ollama is not reachable."
    echo "The CTI API will still start."
    echo "AI features require Ollama to be available."
fi

# 5. Start FastAPI
echo "[5/5] Starting CTI FastAPI application..."

cd /app

exec uvicorn main:app \
    --app-dir /app/app \
    --host 0.0.0.0 \
    --port 8000
