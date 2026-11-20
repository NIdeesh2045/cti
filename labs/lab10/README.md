# Lab 10 – MongoDB Transactions and Inventory Reservation

## Activity 10.1 – Bank Transfer Transaction

### Objective
Implement a bank transfer using MongoDB sessions and transactions.

### Implementation
- Created two bank accounts: ACC001 and ACC002.
- Used a MongoDB session and transaction.
- Debited the source account and credited the destination account.
- Recorded successful transfers in transaction history.
- Tested insufficient funds and verified rollback.

### Results

Initial balances:
- ACC001: 5000
- ACC002: 2000

Transfer:
- Source: ACC001
- Destination: ACC002
- Amount: 1000

Final balances:
- ACC001: 4000
- ACC002: 3000

The successful transfer created one transaction history record.

The insufficient-funds test failed as expected. Account balances and
transaction history remained unchanged.

## Activity 10.1 – Try It Yourself: Retry Logic

### Objective
Implement retry logic for transient transaction errors using
exponential backoff.

### Configuration
- Maximum attempts: 5
- Initial delay: 0.1 seconds
- Backoff formula: 0.1 * (2 ** attempt)

### Result
The transfer of 1000 from ACC001 to ACC002 succeeded on attempt 1.

No transient transaction error occurred, so the retry path was not
triggered during this run.

## Activity 10.2 – Inventory Reservation with Deadlock Handling

### Objective
Reserve product inventory and create pending orders using transactions
while handling concurrent requests.

### Inventory
- Product: Wireless Mouse
- Product ID: PROD001
- Initial stock: 5
- Total requests: 8

### Transactional Concurrency Results

| Threads | Successful | Failed | Remaining Stock | Throughput |
|---:|---:|---:|---:|---:|
| 1 | 5 | 3 | 0 | 40.72 orders/sec |
| 4 | 5 | 3 | 0 | 44.48 orders/sec |
| 8 | 5 | 3 | 0 | 15.92 orders/sec |
| 16 | 5 | 3 | 0 | 3.22 orders/sec |

Exactly five orders were created in each test. Three requests failed
because the inventory was exhausted.

## Non-Transactional Comparison

The inventory reservation was also implemented using
MongoDB's find_one_and_update() method.

| Threads | Successful | Failed | Throughput |
|---:|---:|---:|---:|
| 1 | 5 | 3 | 317.91 orders/sec |
| 4 | 5 | 3 | 446.10 orders/sec |
| 8 | 5 | 3 | 472.88 orders/sec |
| 16 | 5 | 3 | 619.04 orders/sec |

### Observation
The non-transactional approach achieved higher throughput in these
tests because it avoided transaction overhead.

However, inventory decrement and order creation are separate operations.
If order insertion fails after stock is decremented, the two collections
can become inconsistent.

The transactional approach provides atomicity across inventory updates
and order creation.

## Conclusion

This lab demonstrated MongoDB transactions, session management,
rollback, retry logic, and concurrent inventory reservation.

Transactions maintained consistency during concurrent reservations.
The non-transactional approach was faster in this experiment but does
not provide atomicity across multiple document operations.

## Files

- activity-10.1/bank_transfer.py
- activity-10.1/output.txt
- activity-10.1-try-it-yourself/transfer_with_retry.py
- activity-10.1-try-it-yourself/output.txt
- activity-10.2/inventory_reservation.py
- activity-10.2/output.txt
- activity-10.2/non_transactional_comparison.py
- activity-10.2/comparison_output.txt
