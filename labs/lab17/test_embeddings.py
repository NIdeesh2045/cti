
import os
import numpy as np
from dotenv import load_dotenv
from voyageai import Client

load_dotenv()

client = Client(api_key=os.getenv("VOYAGE_API_KEY"))

texts = [
    "MongoDB is a document database.",
    "MongoDB stores data in BSON format."
]

result = client.embed(texts, model="voyage-3")

embeddings = result.embeddings

def cosine_similarity(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )

similarity = cosine_similarity(
    embeddings[0], embeddings[1]
)

print("Embedding dimensions:", len(embeddings[0]))
print(f"Cosine similarity: {similarity:.4f}")
print("Voyage AI embedding test successful!")
