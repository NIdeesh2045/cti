
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

URI = os.getenv("MONGODB_LOCAL_URI", "mongodb://localhost:27017")
DB_NAME = "lab03_blog"


def main():
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("[OK] Connected to MongoDB")

    db = client[DB_NAME]

    # Reset collections for a repeatable experiment
    posts = db["posts"]
    comments = db["comments"]
    embedded_posts = db["posts_embedded"]

    posts.drop()
    comments.drop()
    embedded_posts.drop()

    # Load and insert 5 posts
    with open(Path(__file__).with_name("posts.json"), "r", encoding="utf-8") as file:
        post_data = json.load(file)

    post_result = posts.insert_many(post_data)
    post_ids = post_result.inserted_ids

    print(f"[OK] Inserted {len(post_ids)} posts")

    # Insert 2 comments for each post = 10 comments
    comment_data = [
        ("Excellent introduction!", "Reader1"),
        ("Very helpful explanation.", "Reader2"),
        ("Embedding makes sense here.", "Reader3"),
        ("Can you provide more examples?", "Reader4"),
        ("Aggregation is powerful.", "Reader1"),
        ("Great tutorial!", "Reader5"),
        ("Performance matters a lot.", "Reader2"),
        ("Useful optimization tips.", "Reader3"),
        ("Both databases have advantages.", "Reader4"),
        ("Nice comparison.", "Reader5")
    ]

    comments_to_insert = []

    for index, post_id in enumerate(post_ids):
        for offset in range(2):
            text, author = comment_data[index * 2 + offset]
            comments_to_insert.append({
                "post_id": post_id,
                "text": text,
                "author": author
            })

    comments.insert_many(comments_to_insert)
    print(f"[OK] Inserted {len(comments_to_insert)} comments")

    # Referenced design: retrieve post and comments using $lookup
    print("\n=== REFERENCED DESIGN ($lookup) ===")

    pipeline = [
        {"$match": {"_id": post_ids[0]}},
        {
            "$lookup": {
                "from": "comments",
                "localField": "_id",
                "foreignField": "post_id",
                "as": "comments"
            }
        }
    ]

    referenced_result = list(posts.aggregate(pipeline))
    referenced_post = referenced_result[0]

    print(f"Post: {referenced_post['title']}")
    print(f"Comments: {len(referenced_post['comments'])}")

    # Alternative referenced approach: two separate find operations
    print("\nReferenced design using separate queries:")
    separate_post = posts.find_one({"_id": post_ids[0]})
    separate_comments = list(comments.find({"post_id": post_ids[0]}))
    print(f"Post: {separate_post['title']}")
    print(f"Comments: {len(separate_comments)}")

    # Migrate referenced data into embedded design
    print("\n=== MIGRATING TO EMBEDDED DESIGN ===")

    migration_pipeline = [
        {
            "$lookup": {
                "from": "comments",
                "localField": "_id",
                "foreignField": "post_id",
                "as": "comments"
            }
        },
        {
            "$project": {
                "title": 1,
                "author": 1,
                "content": 1,
                "comments.text": 1,
                "comments.author": 1
            }
        },
        {
            "$out": "posts_embedded"
        }
    ]

    posts.aggregate(migration_pipeline)
    print("[OK] Migrated posts and comments into posts_embedded")

    # Verify embedded design
    print("\n=== EMBEDDED DESIGN ===")

    embedded_post = embedded_posts.find_one({"title": post_data[0]["title"]})

    print(f"Post: {embedded_post['title']}")
    print(f"Comments: {len(embedded_post['comments'])}")

    # Query count comparison
    print("\n=== QUERY COUNT COMPARISON ===")
    print("Referenced with separate find queries: 2 queries")
    print("Referenced with $lookup aggregation: 1 query")
    print("Embedded design with find_one(): 1 query")

    print("\n=== DESIGN COMPARISON ===")
    print("Referenced: Better for large or independently managed comments.")
    print("Embedded: Convenient when comments are limited and read with posts.")

    print("\n[OK] Lab 3.2 completed")
    client.close()


if __name__ == "__main__":
    main()
