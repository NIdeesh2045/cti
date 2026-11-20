# MongoDB Lab 07 – Schema Design and Working Set Analysis

## Overview

This lab explores MongoDB schema design, embedding and referencing, BSON document size, WiredTiger cache behaviour, and working-set performance.

The lab uses two datasets:
- CTI Digest: https://ctidigest.com/
- Annual Security Reports: https://github.com/jacobdjwilson/awesome-annual-security-reports/

---

# Activity 7.1 – Analyze a Production Schema

## Objective

Analyze a real-world threat intelligence dataset, identify relationships between documents, compare embedding and referencing, and calculate BSON document sizes.

## Data Collection

Data was collected from CTI Digest using its publicly available JSON endpoints:

- Articles: https://ctidigest.com/articles.json
- Indicators of Compromise (IOCs): https://ctidigest.com/iocs.json

The collected data was stored in the MongoDB database `lab07_cti_schema`.

## Database Collections

| Collection | Documents |
|---|---:|
| articles | 23,874 |
| iocs | 68,835 |
| sources | 37 |

## Schema Design

The database uses three collections:

1. **articles:** Stores threat intelligence articles and references their source using `source_id`.
2. **iocs:** Stores Indicators of Compromise such as IP addresses and references their source using `source_id`.
3. **sources:** Stores canonical source information such as source names.

The article and IOC documents also contain `source_name` as a denormalized display field.

## Embedding vs Referencing

Referencing was selected for the source relationship because:

- Multiple articles and IOCs can belong to the same source.
- Source information can be maintained in one place.
- It avoids duplicating the complete source document.
- It supports relationships between independent collections.

Embedding is suitable for small, bounded information that is normally accessed together with its parent document.

An embedded alternative was implemented in the try-it-yourself activity by storing source information directly inside IOC documents.

## BSON Document Size Analysis

The `$bsonSize` aggregation operator was used to calculate document sizes.

| Collection | Average BSON Size | Maximum BSON Size |
|---|---:|---:|
| articles | 553.77 bytes | 814 bytes |
| iocs | 252.10 bytes | 365 bytes |
| sources | 94.05 bytes | 105 bytes |

All documents are safely below MongoDB's 16 MB BSON document size limit.

## Activity 7.1 – Try It Yourself

The referencing design was compared with an embedded-source design.

Both designs returned 44,330 matching IOC documents in the tested query.

| Design | Execution Time |
|---|---:|
| Referencing with `$lookup` | 1.041857 seconds |
| Embedded source | 0.126001 seconds |

In this test, the embedded design was approximately 8.27 times faster.

**Observation:** Embedding reduced the need for a lookup operation. However, embedding duplicates source information and can make updates more difficult. These timings are from one local test and are not universal performance guarantees.

## Threat Identification

An IOC is an indicator that may be associated with malicious activity, but an indicator alone does not prove that a system is compromised. Confidence, source reliability, context, and corroborating evidence should be considered before classifying an indicator as an actual threat.

---

# Activity 7.2 – Working Set Analysis

## Objective

Create a large MongoDB working set, inspect WiredTiger cache statistics, perform random reads, and observe cache behaviour.

## Dataset

Source: https://github.com/jacobdjwilson/awesome-annual-security-reports/

The GitHub repository catalog was used to obtain report metadata. A working-set dataset of 100,000 documents was generated, with each document containing report metadata and an additional payload.

## Dataset Creation Results

| Measurement | Result |
|---|---:|
| Catalog entries found | 502 |
| Documents inserted | 100,000 |
| Average BSON size | 2,486.56 bytes |
| Minimum BSON size | 2,289 bytes |
| Maximum BSON size | 2,700 bytes |
| Total logical BSON size | 237.14 MB |
| MongoDB storage size | 42.98 MB |
| Insertion time | 3.32 seconds |

The generated documents average approximately 2.43 KiB, which is slightly above the approximate 2 KB target.

## WiredTiger Cache Analysis

MongoDB `serverStatus` was used to inspect WiredTiger cache statistics.

The test performed five rounds of random reads, with 10,000 reads in each round.

### Final Cache Results

| Metric | Result |
|---|---:|
| Cache used | 267.87 MB |
| Configured cache | 3,455 MB |
| Cache occupancy | 7.75% |
| Pages requested | 2,057,728 |
| Pages read into cache | 702 |
| Approximate counter-based hit ratio | 99.97% |

### Random Read Performance

| Round | Reads | Time (seconds) | Reads/second |
|---|---:|---:|---:|
| 1 | 10,000 | 1.844 | 5,423.93 |
| 2 | 10,000 | 1.920 | 5,209.47 |
| 3 | 10,000 | 1.999 | 5,003.59 |
| 4 | 10,000 | 1.968 | 5,080.34 |
| 5 | 10,000 | 2.043 | 4,895.63 |

### Observation

The approximate cache hit ratio remained around 99.96–99.97% during the random-read test.

The working set was relatively small compared with the configured WiredTiger cache, which helps explain the high cache hit ratio.

Cache occupancy represents the portion of configured cache currently used. It does not represent the percentage of the complete collection held in memory.

The counter-based hit ratio is an approximation, not an exact per-query cache hit measurement.

---

# Activity 7.2 – Try It Yourself

## Objective

Build a monitoring script that periodically checks the annual security report catalog for new entries and reports WiredTiger cache statistics.

## Implementation

The `cache_monitor.py` script:

1. Reads the annual security report catalog from GitHub.
2. Compares catalog entries with records already stored in MongoDB.
3. Identifies and stores newly discovered report metadata.
4. Reads WiredTiger cache statistics using `serverStatus`.
5. Reports cache usage, occupancy, page counters, and an approximate cache hit ratio.
6. Repeats the monitoring process every 10 seconds.

## Monitoring Results

Three monitoring cycles were completed.

| Metric | Observed Result |
|---|---:|
| Source catalog entries | 502 |
| Newly discovered reports | 0 |
| Cache used | 264.68 MB |
| Configured cache | 3,455 MB |
| Cache occupancy | 7.66% |
| Approximate cache hit ratio | 99.97% |

No new reports were discovered during the three monitoring cycles.

## Conclusion

The monitoring script successfully checked the external report catalog and monitored WiredTiger cache statistics at 10-second intervals.

---

# Overall Conclusion

This lab demonstrated how MongoDB schema design affects data organization and query performance. Referencing provides better normalization for shared source information, while embedding can improve read performance when related data is frequently accessed together.

The BSON size analysis confirmed that all CTI documents were far below the 16 MB document limit.

The working-set experiment demonstrated how to inspect WiredTiger cache metrics and evaluate random-read behaviour. The monitoring script extended this analysis by periodically checking external report catalog updates and database cache statistics.

## Project Structure

- `activity-7.1/` – Production schema analysis.
- `activity-7.1-try-it-yourself/` – Embedded source design comparison.
- `activity-7.2/` – Working-set creation and cache analysis.
- `activity-7.2-try-it-yourself/` – Periodic report and cache monitoring.

