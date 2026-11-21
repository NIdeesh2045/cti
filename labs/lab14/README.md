# Lab 14 – MongoDB Monitoring, Backup and Recovery

## Overview

Lab 14 focuses on MongoDB database monitoring, automated backups, restore verification, and performance benchmarking.

The lab contains two activities:

- **Activity 14.1:** Build a Monitoring Dashboard
- **Activity 14.2:** Automated Backup and Restore Verification

---

# Activity 14.1 – Build a Monitoring Dashboard

## Objective

To monitor MongoDB server performance, collect important database metrics, detect potential issues, and generate alerts based on predefined thresholds.

## Technologies Used

- Python
- PyMongo
- MongoDB
- Docker
- Webhook integration

## Implementation

The Python monitoring script connects to the MongoDB replica set and collects the following metrics:

1. **Connection Statistics**
   - Current number of connections.

2. **Operation Counters**
   - Insert operations
   - Query operations
   - Update operations
   - Delete operations

3. **WiredTiger Cache Statistics**
   - Cache hit ratio
   - Cache memory usage
   - Maximum cache size

4. **Replica Set Monitoring**
   - Member health
   - Primary and secondary status
   - Replication lag

The collected metrics are displayed in a formatted table and written to `metrics.log` every 30 seconds.

## Alert Configuration

The monitoring script checks the following thresholds:

| Metric | Warning Condition |
|---|---|
| Cache hit ratio | Below 80% |
| Replication lag | Above 10 seconds |

Webhook notification support is implemented for Slack/Discord-compatible endpoints. Notifications are sent when configured; webhook delivery was not tested.

## Actual Results

| Metric | Observed Result |
|---|---:|
| Connections | 26 |
| Insert operations | 4 |
| Query operations | 79 |
| Update operations | 5 |
| Delete operations | 5 |
| Cache hit ratio | 100% |
| Cache used | Approximately 0.30 MB |
| Maximum cache | 3455 MB |
| Replica set health | Healthy |
| Replication lag | 0 seconds |

Two monitoring reports were generated at 30-second intervals.

No threshold warnings were triggered during the test.

---

# Activity 14.2 – Automated Backup and Restore Verification

## Objective

To implement automated MongoDB backups, maintain backup retention, verify data recovery, and benchmark backup and restore performance.

## Technologies Used

- Python
- PyMongo
- MongoDB Database Tools
- Docker
- Subprocess
- Time and Datetime modules

## Implementation

The `backup_verify.py` script provides the following functionality:

### 1. Automated Backup

- Uses `mongodump` to create MongoDB backups.
- Generates timestamped backup archive files.
- Stores backups in the `backups/` directory.

### 2. Backup Scheduling

- Supports hourly backup scheduling.
- Uses a 3600-second interval.
- Can be stopped using `Ctrl+C`.

### 3. Backup Retention

- Implements a seven-day retention policy.
- Removes backup archive files older than seven days.

### 4. Restore Verification

The verification process:

1. Inserts 1,000 test documents.
2. Creates a backup of the test database.
3. Modifies the original documents.
4. Restores the backup using `mongorestore`.
5. Checks whether all original documents are recovered.

### 5. Performance Benchmarking

Backup and restore performance was measured using three dataset sizes.

## Restore Verification Results

| Parameter | Result |
|---|---:|
| Documents backed up | 1,000 |
| Documents restored | 1,000 |
| Original documents verified | 1,000 |
| Backup time | 0.07 seconds |
| Restore time | 0.09 seconds |
| Verification status | PASSED |

## Performance Benchmark Results

| Documents | Backup Time | Restore Time |
|---:|---:|---:|
| 1,000 | 0.06 seconds | 0.12 seconds |
| 10,000 | 0.07 seconds | 0.21 seconds |
| 100,000 | 0.14 seconds | 1.08 seconds |

The results show that backup and restore times increase with dataset size.

## Backup Archive Verification

A timestamped backup archive was successfully generated:

`backup_20261121_082827.archive`

- Backup directory: `backups/`
- Archive size: 3.9 MB
- Backup execution time: 0.22 seconds

## Recovery Objectives

**Recovery Point Objective (RPO):**

1 hour, based on the configured hourly backup interval.

**Recovery Time Objective (RTO):**

The time required to restore the database and restart the application. Actual recovery time depends on the database size and deployment environment.

---

# Conclusion

Lab 14 successfully demonstrates MongoDB monitoring, performance metric collection, threshold-based alerting, automated backup creation, backup retention, restore verification, and performance benchmarking.

The monitoring dashboard successfully collected database metrics and confirmed healthy replica set operation.

The backup and restore verification successfully recovered all 1,000 original test documents. Performance benchmarking was also completed for datasets containing 1,000, 10,000, and 100,000 documents.

Both activities demonstrate practical database administration, monitoring, backup, and recovery techniques using Python and MongoDB.