# Lab 11 – Sharding and Horizontal Scalability

## Lab 11.1 – Evaluate Shard Key Choices

### Objective
Evaluate four candidate shard keys for an e-commerce order management system.

### Decision Matrix

| Shard Key | Cardinality | Distribution | Query Targeting |
|---|---|---|---|
| order_id | High | Generally even | Poor for customer-based queries; may require scatter-gather |
| customer_id | High | Potentially uneven due to customer activity | Good for customer-specific queries |
| order_date | High | Can become uneven due to monotonically increasing values | Good for date-range queries |
| Hashed customer_id | High | Generally even due to hashing | Good for equality queries on customer_id; range queries are inefficient |

### Recommendation

The recommended shard key is **hashed customer_id**.

Hashing customer IDs helps distribute writes and documents more evenly across shards. It also supports efficient targeting for queries that filter by customer ID.

### Try It Yourself – MongoDB 5.0+ Resharding

MongoDB 5.0 introduced the ability to change a collection's shard key using the reshardCollection command.

Example:

    db.adminCommand({
        reshardCollection: "sales.orders",
        key: { customer_id: "hashed" }
    })

### Main Resharding Steps

1. Select the collection and new shard key.
2. MongoDB initializes the resharding operation and determines the new data distribution.
3. Clone phase: copy existing documents into temporary collections on recipient shards.
4. Index phase: build the required indexes.
5. Catch-up phase: apply ongoing writes from the source collection.
6. Commit phase: switch to the new collection and remove the old collection.

### Limitations and Considerations

- Resharding requires additional storage, CPU, and I/O resources.
- Only one resharding, moveCollection, rewriteCollection, or unshardCollection operation can run at a time on a cluster.
- Writes may be briefly blocked during the final cutover.
- Existing unique indexes must satisfy the new shard key requirements.
- Collections using Queryable Encryption are not supported.
- Atlas Search indexes may need to be rebuilt after resharding.
- Resharding can take time depending on collection size and cluster resources.

### Conclusion

A good shard key should provide high cardinality, balanced distribution, and efficient query targeting. Hashed customer_id is a suitable choice for this workload because it balances distribution while supporting customer-specific equality queries.

References:
- https://www.mongodb.com/docs/manual/core/sharding-reshard-a-collection/
- https://www.mongodb.com/docs/manual/reference/command/reshardCollection/

## Lab 11.2: Shard Key Hotspot Detection

### Objective
Compare a monotonically increasing timestamp shard key with a hashed shard key and observe their data distribution and query routing behavior.

### Setup
- MongoDB 7.0 sharded cluster with two shards.
- `hotspot_data` uses `{ ts: 1 }`.
- `even_data` uses `{ user_id: "hashed" }`.
- Inserted 10,000 documents into each collection.

### Data Distribution Results

| Collection | Shard 1 | Shard 2 |
|---|---:|---:|
| hotspot_data | 10,000 | 0 |
| even_data | 5,027 | 4,973 |

The timestamp-based collection placed all documents on shard 1 in this experiment. The hashed collection distributed documents almost equally between both shards.

### Query Explain Results

| Metric | Timestamp Range Query | Hashed-Key Range Query |
|---|---:|---:|
| Winning plan | SINGLE_SHARD | SHARD_MERGE |
| Shards contacted | 1 | 2 |
| Documents returned | 10,000 | 10,000 |
| Documents examined | 10,000 | 10,000 |
| Execution time | 10 ms | 3 ms |

The timestamp query used the `ts_1` index (`IXSCAN`) and targeted shard 1.

The hashed-key range query contacted both shards (`SHARD_MERGE`) and used collection scans (`COLLSCAN`). A hashed shard key does not preserve the original ObjectId ordering, so a range query on the original values cannot be efficiently targeted to a shard.

Execution times should not be treated as a direct performance comparison because the two queries used different execution plans and access methods.

### Conclusion

The experiment demonstrates that a monotonically increasing shard key can concentrate writes on the shard owning the newest key range. Hashed shard keys provide more balanced data distribution, but range queries on the original hashed field may require scatter-gather operations across multiple shards.

Hashed keys are suitable when balanced distribution and equality-based lookups are important. Ranged keys are useful when range-query targeting is important and write distribution can be managed.
