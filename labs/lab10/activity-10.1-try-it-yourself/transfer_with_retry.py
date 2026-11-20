import time
from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.errors import PyMongoError

URI = "mongodb://localhost:27118/?directConnection=true"
DATABASE = "lab10_bank"
MAX_RETRIES = 5

client = MongoClient(URI)
db = client[DATABASE]
accounts = db.accounts
history = db.transaction_history


def transfer_with_retry(source_id, destination_id, amount):
    for attempt in range(MAX_RETRIES):
        try:
            with client.start_session() as session:
                session.start_transaction()

                source = accounts.find_one(
                    {"account_id": source_id},
                    session=session
                )

                if source is None or source["balance"] < amount:
                    session.abort_transaction()
                    print("Transfer rejected: insufficient funds.")
                    return False

                debit = accounts.update_one(
                    {
                        "account_id": source_id,
                        "balance": {"$gte": amount}
                    },
                    {"$inc": {"balance": -amount, "version": 1}},
                    session=session
                )

                if debit.modified_count != 1:
                    session.abort_transaction()
                    raise RuntimeError("Debit failed.")

                credit = accounts.update_one(
                    {"account_id": destination_id},
                    {"$inc": {"balance": amount, "version": 1}},
                    session=session
                )

                if credit.modified_count != 1:
                    session.abort_transaction()
                    raise RuntimeError("Destination account not found.")

                history.insert_one({
                    "source": source_id,
                    "destination": destination_id,
                    "amount": amount,
                    "status": "SUCCESS",
                    "createdAt": datetime.now(timezone.utc)
                }, session=session)

                session.commit_transaction()

                print(f"Transfer successful on attempt {attempt + 1}.")
                return True

        except PyMongoError as error:
            if error.has_error_label("TransientTransactionError"):
                delay = 0.1 * (2 ** attempt)
                print(
                    f"Transient transaction error. "
                    f"Retry {attempt + 1}/{MAX_RETRIES} "
                    f"after {delay:.2f} seconds."
                )
                if attempt < MAX_RETRIES - 1:
                    time.sleep(delay)
                    continue

            print(f"Transfer failed: {error}")
            return False

    print("Maximum retries reached.")
    return False


if __name__ == "__main__":
    try:
        client.admin.command("ping")

        accounts.delete_many({})
        history.delete_many({})

        accounts.insert_many([
            {"account_id": "ACC001", "balance": 5000.0, "version": 1},
            {"account_id": "ACC002", "balance": 2000.0, "version": 1}
        ])

        print("Testing transfer with retry logic...")
        transfer_with_retry("ACC001", "ACC002", 1000)

        print("\nFinal account balances:")
        for account in accounts.find().sort("account_id", 1):
            print(account)

        print("\nTransaction history:")
        for record in history.find():
            print(record)

    finally:
        client.close()
