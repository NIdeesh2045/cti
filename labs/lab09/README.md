# Lab 09 - Write Concern and Network Partition

## Technologies
- MongoDB 7.0
- Python
- PyMongo
- Docker

## Activity 9.1 - Measure Write Concern Latency

Measured 1,000 individual inserts for each write concern.

| Write Concern | Total Time | Average Latency |
|---|---:|---:|
| w:1 | 0.864 s | 0.864 ms |
| w:majority | 1.390 s | 1.390 ms |
| w:3 | 0.910 s | 0.910 ms |

All 3,000 writes succeeded.

### Try It Yourself - Journaling

Tested j:true and j:false for all three write concerns.

| Concern | Journal | Average Latency |
|---|---|---:|
| w:1 | true | 0.867 ms |
| w:1 | false | 0.447 ms |
| w:majority | true | 1.153 ms |
| w:majority | false | 101.983 ms |
| w:3 | true | 1.129 ms |
| w:3 | false | 0.883 ms |

All 6,000 writes succeeded. The unusually high majority result should be repeated before drawing conclusions.

Note: MongoDB does not support literal w:"all". w:3 was used to request acknowledgment from all three data-bearing members.

## Activity 9.2 - Simulate a Network Partition

Used Docker network manipulation to disconnect secondary members.

### Experiment 1
Disconnected mongo1.

- mongo2 remained PRIMARY.
- mongo3 remained SECONDARY.
- w:1 insert succeeded.
- w:majority insert succeeded.

### Experiment 2
Disconnected mongo3 as well.

- The replica set lost its majority.
- mongo2 stepped down and became SECONDARY.
- A w:1 write attempt failed with "not primary".
- The w:majority test was not executed in that command.

### Experiment 3 - Recovery

- Reconnected mongo3.
- mongo2 regained PRIMARY status.
- Reconnected mongo1.
- All three data-bearing members became healthy.

The arbiter was restored to the original Lab 08 replica set after the experiment.

## Conclusion

The experiments demonstrated how write concern and journaling affect write latency, and how network partitions affect replica set elections and write availability. A MongoDB replica set needs a voting majority to maintain a PRIMARY. Once connectivity was restored, the replica set recovered successfully.
