
from datetime import datetime, timezone

MAX_BSON_SIZE = 16 * 1024 * 1024

# Simulate a post containing 10,000 comments
comments = [
    {
        "comment_id": i,
        "author": f"User{i}",
        "text": f"This is comment number {i}",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    for i in range(1, 10001)
]

post = {
    "title": "MongoDB Embedding vs Referencing",
    "comments": comments
}

estimated_size = len(str(post).encode("utf-8"))

print("=== 10,000 COMMENTS DESIGN ANALYSIS ===")
print(f"Total comments: {len(comments)}")
print(f"Estimated document size: {estimated_size / 1024:.2f} KB")
print(f"MongoDB BSON document limit: {MAX_BSON_SIZE / (1024 * 1024)} MB")

print("\n=== WHY EMBEDDING IS PROBLEMATIC ===")
print("1. Document can grow excessively large.")
print("2. MongoDB has a 16 MB document size limit.")
print("3. Updating a large comments array can be expensive.")
print("4. Pagination and independent comment queries become harder.")
print("5. Concurrent updates to the same post document can create contention.")

print("\n=== ALTERNATIVE DESIGN ===")
print("Use a separate comments collection with post_id references.")
print("Create an index on post_id.")
print("Retrieve comments in pages using skip/limit or range-based pagination.")
print("Keep post data separate from the large comments collection.")

print("\n[OK] Try It Yourself completed")
