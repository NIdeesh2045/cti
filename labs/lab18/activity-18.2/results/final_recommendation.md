
# Final Database Recommendation

Based on the Lab18.1 implementation and benchmark results:

## MongoDB — Primary Threat Storage
Recommended for storing threat documents, application integration, flexible schemas and fast retrieval in the tested queries.

## Cassandra — High-Volume Distributed Workloads
Recommended for predictable source, type and time-based access patterns and distributed data storage.

## Neo4j — Threat Relationship Analysis
Recommended for investigating relationships among threats, sources and campaigns using graph traversal.

## Overall Recommendation

A polyglot persistence architecture is suitable when all three workload types are important:

- MongoDB: primary operational threat database.
- Cassandra: query-driven distributed data storage.
- Neo4j: graph-based threat correlation.

If the project must use only one database, MongoDB is the most balanced choice for the workloads tested in this experiment.

The recommendation is based on a 100,000-record synthetic experiment. Larger-scale deployment decisions require further testing.
