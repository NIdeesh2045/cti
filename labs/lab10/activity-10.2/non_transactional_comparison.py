import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from pymongo import MongoClient, ReturnDocument

URI = "mongodb://localhost:27118/?directConnection=true"
client = MongoClient(URI)
db = client["lab10_inventory"]
inventory = db.inventory
orders = db.orders

PRODUCT_ID = "PROD001"
INITIAL_STOCK = 5
REQUESTS = 8


def setup():
    inventory.delete_many({})
    orders.delete_many({})
    inventory.insert_one({
        "product_id": PRODUCT_ID,
        "name": "Wireless Mouse",
        "stock": INITIAL_STOCK,
        "price": 500.0
    })


def reserve(customer_id):
    product = inventory.find_one_and_update(
        {
            "product_id": PRODUCT_ID,
            "stock": {"$gte": 1}
        },
        {"$inc": {"stock": -1}},
        return_document=ReturnDocument.BEFORE
    )

    if product is None:
        return False

    orders.insert_one({
        "order_id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "product_id": PRODUCT_ID,
        "status": "PENDING",
        "total": product["price"]
    })

    return True


def run_test(workers):
    setup()
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(reserve, f"CUSTOMER{i + 1}")
            for i in range(REQUESTS)
        ]
        results = [future.result() for future in as_completed(futures)]

    elapsed = time.perf_counter() - start
    successful = sum(results)
    failed = REQUESTS - successful

    print(f"\nConcurrency level: {workers}")
    print(f"Successful reservations: {successful}")
    print(f"Failed reservations: {failed}")
    print("Remaining stock:", inventory.find_one(
        {"product_id": PRODUCT_ID}
    )["stock"])
    print("Orders created:", orders.count_documents({}))
    print(f"Elapsed time: {elapsed:.4f} seconds")
    print(f"Throughput: {successful / elapsed:.2f} orders/second")


if __name__ == "__main__":
    try:
        client.admin.command("ping")
        print("Non-transactional comparison")
        for workers in (1, 4, 8, 16):
            run_test(workers)
    finally:
        client.close()
