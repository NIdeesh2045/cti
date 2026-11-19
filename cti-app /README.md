# 🛡️ CTI Platform – Cyber Threat Intelligence Platform

A containerized Cyber Threat Intelligence (CTI) platform that collects, stores, analyzes, and presents cyber threat intelligence through a web-based dashboard and an AI-powered chatbot.

The platform uses **FastAPI, MongoDB, and Ollama** to provide threat intelligence management and AI-assisted analysis.

## 🚀 Features

- **Threat Intelligence Dashboard** – View and monitor collected threat intelligence.
- **Threat Management** – Browse, search, and filter threat records.
- **AI-Powered Chatbot** – Ask questions about threat intelligence using a locally hosted LLM.
- **Authentication** – Login and user registration.
- **MongoDB Database** – Store threat intelligence and application data.
- **Docker Deployment** – Run the platform inside a single Docker container.

## 🧰 Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | MongoDB 8.0 |
| AI Integration | Ollama |
| Chat Model | llama3.2:3b |
| Embedding Model | nomic-embed-text |
| Frontend | HTML, CSS, JavaScript |
| Containerization | Docker |

## 📦 Docker Image

**Docker Hub Repository:**  
https://hub.docker.com/r/laddu2045/cti-platform

Pull the image:

```bash
docker pull laddu2045/cti-platform:2.1
```

## ⚙️ Prerequisites

Before running the platform, install:

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine.
2. [Ollama](https://ollama.com/) installed on the host machine.

### Install AI Models

Ollama runs on the host machine, outside the Docker container.

Download the required models:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Verify the installed models:

```bash
ollama list
```

Make sure Ollama is running before using the AI features.

## 🐳 Run the Platform

### 1. Pull the Docker Image

```bash
docker pull laddu2045/cti-platform:2.1
```

### 2. Start the Container

```bash
docker run -d \
  --name cti-platform \
  -p 8000:8000 \
  -v cti-mongodb-data:/data/db \
  -e MONGO_ROOT_USER=root \
  -e MONGO_ROOT_PASSWORD='YOUR_STRONG_PASSWORD' \
  -e ADMIN_PASSWORD='YOUR_ADMIN_PASSWORD' \
  -e JWT_SECRET='YOUR_LONG_RANDOM_SECRET' \
  -e OLLAMA_URL=http://host.docker.internal:11434 \
  -e OLLAMA_CHAT_MODEL=llama3.2:3b \
  -e OLLAMA_EMBEDDING_MODEL=nomic-embed-text \
  laddu2045/cti-platform:2.1
```

Replace the example passwords and secret with your own secure values.

### 3. Access the Application

Open your browser:

**http://localhost:8000**

### 4. Verify the Container

Check the running container:

```bash
docker ps
```

View application logs:

```bash
docker logs -f cti-platform
```

## 🖥️ Deployment on Another Laptop

The platform can be deployed on another laptop without manually installing Python, FastAPI, or MongoDB.

Follow these steps:

1. Install Docker.
2. Install Ollama.
3. Download the required Ollama models.
4. Pull the CTI Docker image.
5. Run the container using the command above.
6. Open `http://localhost:8000`.

**Important:** Ollama and its models must be installed separately on each laptop. The Docker image contains the application and MongoDB, but does not include Ollama or its models.

For Docker Desktop on macOS and Windows, `host.docker.internal` allows the container to connect to Ollama running on the host.

For Linux Docker Engine, you may need to add:

```bash
--add-host=host.docker.internal:host-gateway
```

You must also configure Ollama to accept connections from the Docker container.

## 💾 Database Persistence

MongoDB data is stored in a Docker named volume:

```bash
-v cti-mongodb-data:/data/db
```

This ensures database data persists when the container is stopped or recreated.

To view Docker volumes:

```bash
docker volume ls
```

**Note:** A new laptop starts with a fresh database. Existing MongoDB records are not included in the Docker image. Use a database backup and restore process to migrate existing data.

## 🔧 Useful Docker Commands

| Operation | Command |
|---|---|
| Stop container | `docker stop cti-platform` |
| Start container | `docker start cti-platform` |
| Restart container | `docker restart cti-platform` |
| View logs | `docker logs -f cti-platform` |
| Remove container | `docker rm -f cti-platform` |
| Check containers | `docker ps -a` |

Removing the container does not remove the named MongoDB volume.

## 🏗️ Architecture

```text
                 User / Web Browser
                         |
                         v
                  CTI Web Interface
                         |
                         v
                   FastAPI Backend
                    /          \
                   /            \
                  v              v
             MongoDB           Ollama
             Database       (Host Machine)
                                |
                         +------+------+
                         |             |
                         v             v
                    llama3.2:3b   nomic-embed-text
```

## ⚠️ Troubleshooting

**1. Container fails to start**

```bash
docker logs cti-platform
```

Check the logs for MongoDB startup or configuration errors.

**2. AI chatbot is not responding**

- Make sure Ollama is running.
- Verify both models are installed using `ollama list`.
- Check the `OLLAMA_URL` environment variable.
- Ensure the Docker container can access the host Ollama service.

**3. Port 8000 is already in use**

Run the container using another host port:

```bash
-p 8080:8000
```

Then access:

`http://localhost:8080`

**4. MongoDB authentication errors**

Ensure that the MongoDB credentials match the credentials configured when the database volume was initialized. Changing the environment password does not automatically change an existing MongoDB user's password.

## 📌 Image Information

- **Image:** `laddu2045/cti-platform`
- **Version:** `2.1`
- **Container Port:** `8000`
- **Database:** MongoDB 8.0
- **AI Runtime:** External Ollama
- **Database Storage:** Docker Named Volume
- **Architecture:** `linux/amd64`

---

## 👨‍💻 Author

**GitHub:** https://github.com/NIdeesh2045

**Docker Hub:** https://hub.docker.com/u/laddu2045

---

*CTI Platform – Containerized Cyber Threat Intelligence with AI-powered analysis.*