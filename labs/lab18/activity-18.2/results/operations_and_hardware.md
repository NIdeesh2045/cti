
# Hardware and Operational Analysis

## Suggested Starting Hardware

These are planning estimates for a small lab deployment, not measured requirements.

| Database | CPU | RAM | Storage |
|---|---:|---:|---|
| MongoDB | 4–8 vCPU | 16–32 GB | SSD |
| Cassandra | 4–8 vCPU per node | 16–32 GB per node | SSD |
| Neo4j | 4–8 vCPU | 16–32 GB | SSD |

## Operational Complexity

### MongoDB
- Index management
- Replica-set monitoring
- Backup and restore
- Shard-key planning

### Cassandra
- Cluster monitoring
- Compaction and repair
- Partition management
- Replication and consistency configuration

### Neo4j
- Graph query optimization
- Memory and page-cache monitoring
- Index management
- Graph backup and restore

## Backup and Monitoring

| Database | Backup | Important monitoring |
|---|---|---|
| MongoDB | Database-aware backups and snapshots | Replication lag, slow queries, disk |
| Cassandra | Snapshots and commit-log procedures | Compaction, repair, node health |
| Neo4j | Neo4j-supported backup tools | Memory, page cache, transactions |

All deployments should have tested restore procedures, retention policies and monitoring alerts.
