
import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
from voyageai import Client

load_dotenv()

# Connections
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["rag_demo"]

documents = db["documents"]
conversations = db["conversations"]

voyage = Client(api_key=os.getenv("VOYAGE_API_KEY"))

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"


def retrieve_documents(question, limit=3):
    result = voyage.embed(
        [question],
        model="voyage-3"
    )

    query_vector = result.embeddings[0]

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 20,
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 0,
                "text": 1,
                "source": 1,
                "score": {
                    "$meta": "vectorSearchScore"
                }
            }
        }
    ]

    return list(documents.aggregate(pipeline))


def get_conversation_history(user_id):
    history = list(
        conversations.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(5)
    )

    return list(reversed(history))


def generate_answer(question, user_id="student001"):
    # Retrieve relevant documents
    retrieved = retrieve_documents(question)

    context = "\n\n".join(
        f"Source: {item['source']}\n{item['text']}"
        for item in retrieved
    )

    # Retrieve last five conversation messages
    history = get_conversation_history(user_id)

    history_text = "\n".join(
        f"{item['role']}: {item['content']}"
        for item in history
    )

    prompt = f"""
You are a helpful cybersecurity threat intelligence assistant.

Answer the user's question using the provided documents.
If the documents do not contain the answer, clearly say so.
Do not invent information.

Previous conversation:
{history_text}

Retrieved documents:
{context}

User question:
{question}

Provide a clear and simple answer.
"""

    # Generate response using Ollama
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=180
    )

    response.raise_for_status()
    answer = response.json()["response"]

    # Save user question
    conversations.insert_one({
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc),
        "role": "user",
        "content": question
    })

    # Save assistant response
    conversations.insert_one({
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc),
        "role": "assistant",
        "content": answer
    })

    return answer


if __name__ == "__main__":
    user_id = "student001"

    print("RAG SYSTEM - THREAT INTELLIGENCE")
    print("Type 'exit' to stop.\n")

    try:
        while True:
            question = input("You: ").strip()

            if question.lower() == "exit":
                break

            if not question:
                continue

            try:
                answer = generate_answer(question, user_id)

                print("\nAI Answer:")
                print(answer)
                print("\n" + "-" * 60 + "\n")

            except Exception as error:
                print("Error:", error)

    finally:
        mongo.close()
