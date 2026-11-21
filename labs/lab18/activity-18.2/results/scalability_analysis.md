
# Scalability Analysis

## Dataset Scaling Scenarios

The experiment directly tested 100,000 synthetic threat records. The following 1M, 10M and 100M scenarios are qualitative projections, not measured results.

| Database | 1 Million | 10 Million | 100 Million |
|---|---|---|---|
| MongoDB | Optimize indexes and storage | Consider sharding | Distributed sharded deployment |
| Cassandra | Add nodes and tune partitions | Expand cluster and replication | Large distributed cluster |
| Neo4j | Tune memory and indexes | Optimize graph traversals | Evaluate graph segmentation and workload distribution |

## MongoDB
- Use replica sets for availability.
- Introduce sharding when storage or throughput demands it.
- Select shard keys based on query patterns.
- Monitor indexes, replication lag and storage.

## Cassandra
- Add nodes to increase cluster capacity.
- Distribute data using appropriate partition keys.
- Configure replication across nodes.
- Monitor compaction, repair, disk usage and latency.

## Neo4j
- Optimize graph indexes and traversal queries.
- Monitor memory, page cache and relationship growth.
- Evaluate clustering options based on deployment edition.
- Consider graph segmentation for very large workloads.

## Conclusion

Cassandra is designed for distributed horizontal scaling. MongoDB provides replication and sharding options. Neo4j is valuable for connected-data workloads but requires careful graph and memory planning.

Actual capacity depends on hardware, workload, record size, indexes, concurrency and deployment configuration.
