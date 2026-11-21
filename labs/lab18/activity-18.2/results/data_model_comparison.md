
# Data Modelling Comparison

## 1. MongoDB

**Data model:** Document-oriented database.

- Stores threat information as flexible JSON-like documents.
- Uses collections such as `full_threats` and `threats`.
- Supports indexes for source, timestamp, severity, type and target.
- Embeds recent threat records in the dashboard document.

**Advantages:**
- Flexible schema.
- Easy application integration.
- Supports filtering and aggregation.
- Suitable for operational threat storage.

**Limitations:**
- Relationship-heavy queries can require complex aggregation or application-side processing.

## 2. Apache Cassandra

**Data model:** Wide-column database.

Lab18 uses:
- `threats_by_source`
- `threats_by_type`
- `threats_by_target`
- `daily_threat_volume`

**Advantages:**
- Designed for distributed data storage.
- Supports query-driven data modelling.
- Provides horizontal scalability.
- Suitable for high-volume workloads.

**Limitations:**
- Requires denormalization.
- Additional tables are needed for different query patterns.
- Ad-hoc queries are less flexible.

## 3. Neo4j

**Data model:** Graph database.

Lab18 uses:
- `Lab18Threat`
- `Lab18Source`
- `Lab18Campaign`

Relationships:
- `REPORTED_BY`
- `HAS_CAMPAIGN`

**Advantages:**
- Represents relationships directly.
- Supports graph traversal and campaign correlation.
- Useful for identifying connected threat communities.

**Limitations:**
- Requires graph modelling knowledge.
- Complex graph traversals need careful optimization.
- Memory and relationship growth must be monitored.

## Comparison Summary

| Feature | MongoDB | Cassandra | Neo4j |
|---|---|---|---|
| Data model | Document | Wide-column | Graph |
| Schema | Flexible | Query-driven | Relationship-based |
| Main strength | Flexible storage | Distributed workloads | Relationship analysis |
| Query language | MongoDB Query API | CQL | Cypher |
| Best Lab18 use | Threat records | Source and time queries | Threat correlation |

## Conclusion

MongoDB is suitable for flexible threat storage, Cassandra for distributed query-driven workloads, and Neo4j for relationship-based threat investigation. The best choice depends on the application's workload.
