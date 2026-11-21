
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
from voyageai import Client

load_dotenv()

mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["rag_demo"]
collection = db["documents"]

voyage = Client(api_key=os.getenv("VOYAGE_API_KEY"))

documents = [
    {
        "source": "Threat Intelligence",
        "text": """Threat intelligence is the process of collecting,
        analyzing and sharing information about cyber threats.
        It helps organizations understand attackers, their methods
        and potential security risks."""
    },
    {
        "source": "Phishing Attacks",
        "text": """Phishing is a cyberattack where attackers use
        fraudulent emails, messages or websites to steal sensitive
        information such as passwords and banking details."""
    },
    {
        "source": "Malware",
        "text": """Malware is malicious software designed to damage,
        disrupt or gain unauthorized access to computer systems.
        Common types include ransomware, spyware and trojans."""
    },
    {
        "source": "Ransomware",
        "text": """Ransomware encrypts a victim's files and demands
        payment to restore access. Organizations should maintain
        backups, patch systems and use endpoint protection."""
    },
    {
        "source": "Network Security",
        "text": """Network security protects computer networks
        against unauthorized access and cyberattacks through
        firewalls, intrusion detection and access controls."""
    }
]


def chunk_text(text, chunk_size=100):
    words = text.split()
    return [
        " ".join(words[i:i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]



def build_documents():
    collection.delete_many({})

    all_chunks = []

    for document in documents:
        chunks = chunk_text(document["text"])

        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "source": document["source"],
                "created_at": datetime.now(timezone.utc)
            })

    if not all_chunks:
        print("No document chunks found.")
        return

    # Generate all embeddings in one API request
    result = voyage.embed(
        [item["text"] for item in all_chunks],
        model="voyage-3"
    )

    for item, embedding in zip(all_chunks, result.embeddings):
        item["embedding"] = embedding

    collection.insert_many(all_chunks)

    print("Documents stored successfully!")
    print("Total chunks:", len(all_chunks))
    print("Embedding dimensions:", len(result.embeddings[0]))


if __name__ == "__main__":
    build_documents()
    mongo.close()
