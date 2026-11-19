
import os
import requests

URL = os.getenv(
    "OLLAMA_URL",
    "http://host.docker.internal:11434"
).rstrip("/")

CHAT = os.getenv("OLLAMA_CHAT_MODEL", "llama3.2:3b")
EMB = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")


def embed(texts):
    response = requests.post(
        f"{URL}/api/embed",
        json={
            "model": EMB,
            "input": texts,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()["embeddings"]


def chat(messages):
    response = requests.post(
        f"{URL}/api/chat",
        json={
            "model": CHAT,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 2048,
                "num_predict": 220,
            },
        },
        timeout=300,
    )

    response.raise_for_status()

    return response.json()["message"]["content"]
