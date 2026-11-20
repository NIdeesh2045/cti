# Lab 08 - MongoDB Replication, Replica Sets and Failover

## Objective
Deploy a MongoDB replica set, verify data replication, add an arbiter, observe failover and elections, and configure member priorities.

## Technologies
- MongoDB 7.0
- Docker and Docker Compose
- mongosh
- Python
- PyMongo

## Activity 8.1 - Deploy a Local Replica Set

Three MongoDB nodes were deployed using Docker Compose:
- mongo1 - PRIMARY
- mongo2 - SECONDARY
- mongo3 - SECONDARY

The replica set `rs0` was initialized successfully. A test document was inserted into the `lab08_replication` database and verified on both secondary nodes.

## Activity 8.1 - Try It Yourself: Add an Arbiter

An arbiter was added as `lab08-arbiter:27017`.

Final members:
- mongo1 - PRIMARY
- mongo2 - SECONDARY
- mongo3 - SECONDARY
- arbiter - ARBITER

There were four voting members, with three votes required for a majority. The arbiter participates in elections but does not store application data.

## Activity 8.2 - Observe Failover and Election

The `rs.stepDown(60)` command was used to force the primary to step down.

First election:
- mongo1 stepped down.
- mongo2 became PRIMARY.

Second election:
- mongo2 stepped down.
- mongo1 became PRIMARY.

The Python monitoring script detected the primary change and successfully read data from the new primary.

## Activity 8.2 - Try It Yourself: Configure Member Priorities

Configured priorities:
- mongo1: 1
- mongo2: 3
- mongo3: 2
- arbiter: 0

Prediction: mongo2 would become PRIMARY because it had the highest priority among the data-bearing members.

Observed result:
- mongo2 - PRIMARY
- mongo1 - SECONDARY
- mongo3 - SECONDARY
- arbiter - ARBITER

The prediction was correct.

## Conclusion

The lab demonstrated MongoDB replica set deployment, data replication, arbiter voting, automatic failover, primary elections, and member priority configuration.
