
# Query Performance Comparison

## Benchmark Configuration
- Dataset: 100,000 synthetic threat records
- Repetitions: 10 runs per query
- Metric: Median execution time
- Lower execution time indicates better performance.

## Measured Results

| Query | MongoDB | Cassandra | Neo4j |
|---|---:|---:|---:|
| Threat History | 0.454 ms | 2.023 ms | 15.139 ms |
| Target Analysis | 0.451 ms | 1.866 ms | 28.889 ms |
| Daily Threat Volume | 58.088 ms | 4.316 ms | 67.996 ms |

## Performance Analysis

### Threat History
MongoDB achieved the lowest median execution time of 0.454 ms.

### Target Analysis
MongoDB performed best with 0.451 ms, followed by Cassandra at 1.866 ms.

### Daily Threat Volume
Cassandra performed best with 4.316 ms because the daily counts were pre-aggregated in a dedicated table.

## Conclusion

MongoDB performed best for the tested retrieval queries, while Cassandra performed best for daily-volume analytics. Neo4j provides graph relationship capabilities, although its measured query times were higher in these tests.

These results represent the implemented queries in the local test environment.
