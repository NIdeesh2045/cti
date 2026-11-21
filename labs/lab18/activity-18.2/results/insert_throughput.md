
# Insert Throughput Comparison

## Benchmark Configuration
- 10 runs per database
- 1,000 benchmark records per run
- Metric: Median records inserted per second

## Results

| Database | Median Throughput |
|---|---:|
| MongoDB | 242,739.95 records/sec |
| Cassandra | 23,648.29 records/sec |
| Neo4j | 60,957.13 records/sec |

## Analysis

MongoDB achieved the highest measured throughput, followed by Neo4j and Cassandra.

The implementations used different write methods:
- MongoDB: Bulk insert
- Cassandra: Asynchronous prepared inserts
- Neo4j: UNWIND with CREATE

Therefore, these results compare the implemented workflows rather than providing a perfectly controlled database-engine comparison.

## Conclusion

MongoDB delivered the highest measured insert throughput in this experiment. Further standardized benchmarking is required for a fair engine-level comparison.
