
FROM --platform=linux/amd64 python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    OLLAMA_URL=http://host.docker.internal:11434 \
    OLLAMA_CHAT_MODEL=llama3.2:3b \
    OLLAMA_EMBEDDING_MODEL=nomic-embed-text \
    MONGO_DB=chatbot

# Install MongoDB 8.0 and required utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    curl \
    ca-certificates \
    && curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc \
       | gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" \
       > /etc/apt/sources.list.d/mongodb-org-8.0.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends mongodb-org \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /data/db

# Application directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Normalize shell script and set permissions
RUN sed -i 's/\r$//' /app/docker/start.sh \
    && chmod 755 /app/docker/start.sh

EXPOSE 8000

CMD ["/bin/bash", "/app/docker/start.sh"]
