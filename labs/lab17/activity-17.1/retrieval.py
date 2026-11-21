
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from voyageai import Client

load_dotenv()

mongo = MongoClient(os.getenv("MONGO_URI"))
collection = mongo["rag_demo"]["documents"]
voyage = Client(api_key=os.getenv("VOYAGE_API_KEY"))


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

    return list(collection.aggregate(pipeline))


if __name__ == "__main__":
    question = "How can organizations protect themselves against ransomware?"

    results = retrieve_documents(question)

    print("\nQUESTION:", question)
    print("\nRETRIEVED DOCUMENTS:")

    for item in results:
        print(f"\nSource: {item['source']}")
        print(f"Score: {item['score']:.4f}")
        print(f"Text: {item['text']}")

    mongo.close()
