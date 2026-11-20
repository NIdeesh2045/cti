import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from pymongo import MongoClient
from pymongo.errors import PyMongoError

URI = "mongodb://localhost:27118/?directConnection=true"
DATABASE = "lab10_inventory"
PRODUCT_ID = "PROD001"
INITIAL_STOCK = 5
REQUESTS = 8

client = MongoClient(URI)
db = client[DATABASE]
inventory = db.inventory
orders = db.orders


def setup():
    inventory.delete_many({})
    orders.delete_many({})
    inventory.insert_one({
        "product_id": PRODUCT_ID,
        "name": "Wireless Mouse",
        "stock": INITIAL_STOCK,
        "version": 1,
        "price": 500.0
    })
    print(f"Inventory initialized with {INITIAL_STOCK} units.")


def reserve_inventory(customer_id, retry_limit=5):
    for attempt in range(retry_limit):
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    product = inventory.find_one(
                        {"product_id": PRODUCT_ID}, session=session
                    )

                    if not product or product["stock"] < 1:
                        raise ValueError("Insufficient stock")

                    update = inventory.update_one(
                        {
                            "product_id": PRODUCT_ID,
                            "stock": {"$gte": 1},
                            "version": product["version"]
                        },
                        {"$inc": {"stock": -1, "version": 1}},
                        session=session
                    )

                    if update.modified_count != 1:
                        raise RuntimeError("Inventory update conflict")

                    orders.insert_one({
                        "order_id": str(uuid.uuid4()),
                        "customer_id": customer_id,
                        "items": [{
                            "product_id": PRODUCT_ID,
                            "qty": 1,
                            "price": product["price"]
                        }],
                        "status": "PENDING",
                        "total": product["price"]
                    }, session=session)

            return True, None

        except ValueError as error:
            return False, str(error)

        except PyMongoError as error:
            if (
                error.has_error_label("TransientTransactionError")
                and attempt < retry_limit - 1
            ):
                time.sleep(0.1 * (2 ** attempt))
                continue
            return False, str(error)

        except RuntimeError as error:
            if attempt < retry_limit - 1:
                time.sleep(0.1 * (2 ** attempt))
                continue
            return False, str(error)

    return False, "Maximum retries reached"


def run_concurrency_test(workers):
    setup()
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(reserve_inventory, f"CUSTOMER{i + 1}")
            for i in range(REQUESTS)
        ]
        results = [future.result() for future in as_completed(futures)]

    elapsed = time.perf_counter() - start
    successful = sum(1 for success, _ in results if success)
    failed = REQUESTS - successful
    remaining = inventory.find_one(
        {"product_id": PRODUCT_ID}
    )["stock"]
    order_count = orders.count_documents({})

    print(f"\nConcurrency level: {workers}")
    print(f"Successful reservations: {successful}")
    print(f"Failed reservations: {failed}")
    print(f"Remaining stock: {remaining}")
    print(f"Orders created: {order_count}")
    print(f"Elapsed time: {elapsed:.4f} seconds")
    print(f"Throughput: {successful / elapsed:.2f} successful orders/second")


if __name__ == "__main__":
    try:
        client.admin.command("ping")
        print("Connected to MongoDB replica set.")
        print("\n========== CONCURRENCY TESTS ==========")

        for workers in (1, 4, 8, 16):
            run_concurrency_test(workers)

    finally:
        client.close()
