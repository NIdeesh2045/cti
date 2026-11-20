from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import PyMongoError

URI = "mongodb://localhost:27118/?directConnection=true"
DATABASE = "lab10_bank"

client = MongoClient(URI)
db = client[DATABASE]

accounts = db.accounts
history = db.transaction_history

def setup_accounts():
    accounts.delete_many({})
    history.delete_many({})

    accounts.insert_many([
        {"account_id": "ACC001", "balance": 5000.0, "version": 1},
        {"account_id": "ACC002", "balance": 2000.0, "version": 1}
    ])

    print("Initial accounts created.")

def transfer_money(source_id, destination_id, amount):
    with client.start_session() as session:
        try:
            with session.start_transaction():
                source = accounts.find_one(
                    {"account_id": source_id},
                    session=session
                )

                if source is None:
                    raise ValueError("Source account not found.")

                if source["balance"] < amount:
                    raise ValueError("Insufficient funds.")

                debit = accounts.update_one(
                    {
                        "account_id": source_id,
                        "balance": {"$gte": amount}
                    },
                    {
                        "$inc": {
                            "balance": -amount,
                            "version": 1
                        }
                    },
                    session=session
                )

                if debit.modified_count != 1:
                    raise ValueError("Debit failed.")

                credit = accounts.update_one(
                    {"account_id": destination_id},
                    {
                        "$inc": {
                            "balance": amount,
                            "version": 1
                        }
                    },
                    session=session
                )

                if credit.modified_count != 1:
                    raise ValueError("Destination account not found.")

                history.insert_one({
                    "source": source_id,
                    "destination": destination_id,
                    "amount": amount,
                    "status": "SUCCESS",
                    "createdAt": datetime.now(timezone.utc)
                }, session=session)

            print(f"Transfer successful: {source_id} -> {destination_id}, amount: {amount}")
            return True

        except (ValueError, PyMongoError) as error:
            print(f"Transfer failed: {error}")
            return False

def display_accounts():
    print("\nAccount balances:")
    for account in accounts.find().sort("account_id", 1):
        print(account)

    print("\nTransaction history:")
    for transaction in history.find():
        print(transaction)

if __name__ == "__main__":
    try:
        client.admin.command("ping")
        setup_accounts()

        print("\n--- Successful transfer test ---")
        transfer_money("ACC001", "ACC002", 1000)

        display_accounts()

        print("\n--- Insufficient funds test ---")
        transfer_money("ACC002", "ACC001", 10000)

        display_accounts()

    finally:
        client.close()
