Lab 18 — Comparative Database Implementation and Analysis
Overview
Lab 18 compares MongoDB, Apache Cassandra, and Neo4j for a
synthetic threat-intelligence workload.

It contains two activities:
- Lab 18.1: Database setup, synthetic data generation and import,
  performance benchmarking, and graph-based campaign analysis.
- Lab 18.2: Comparative analysis of data models, performance,
  scalability, hardware, operations, backup, monitoring, and database
  selection.
Dataset disclaimer: All records and campaign relationships in this
lab are synthetic. They are not verified real-world threat
intelligence. Shared campaign membership indicates a generated
association, not a confirmed attack or false positive.

Dataset
Property	Value
Total threat records	100,000
Sources	16
Threat types	7
Severity levels	3
Unique campaigns	10,000
Records per campaign	10


Generated files:
- data/threats_100k.jsonl
- data/threats_100k.csv
Generate the dataset from the Lab18 root:
python3 scripts/generate_dataset.py
Database namespaces
Lab18 uses separate namespaces to avoid modifying other lab databases or
the existing CTI platform.
Database	Lab18 namespace	Purpose
MongoDB	lab18_threats	Threat documents and dashboard data
Cassandra	lab18 keyspace	Query-driven threat tables and daily aggregates
Neo4j	Lab18Threat, Lab18Source, Lab18Campaign labels	Threat-source-campaign graph


The MongoDB database is lab18_threats; Cassandra keyspace is lab18.
Neo4j Lab18 data is distinguished by its Lab18-specific labels and
constraints.
Lab 18.1 — Implementation and benchmarking
MongoDB
Database: lab18_threats

Collections:
- full_threats — complete threat dataset.
- threats — dashboard document containing the latest 50 threats.
Verified import: 100,000 threat records.
Cassandra
Keyspace: lab18

Tables:
- threats_by_source
- threats_by_type
- threats_by_target
- daily_threat_volume
Verified counts:
- threats_by_source: 100,000
- threats_by_type: 100,000
- threats_by_target: 100,000
- daily_threat_volume: 695 daily aggregate rows
Neo4j
Lab18 labels:
- Lab18Threat
- Lab18Source
- Lab18Campaign
Relationships:
- REPORTED_BY
- HAS_CAMPAIGN
Verified graph:
- 100,000 threat nodes
- 16 source nodes
- 10,000 campaign nodes
- 200,000 relationships
Query performance
Median execution time from 10 repetitions; lower is faster for the
tested query.
Query	MongoDB	Cassandra	Neo4j
Threat history	0.454 ms	2.023 ms	15.139 ms
Target analysis	0.451 ms	1.866 ms	28.889 ms
Daily threat volume	58.088 ms	4.316 ms	67.996 ms


Insert throughput
Median throughput from 10 runs, each attempting to insert 1,000
benchmark records.
Database	Median throughput
MongoDB	242,739.95 records/sec
Cassandra	23,648.29 records/sec
Neo4j	60,957.13 records/sec


Benchmark caveat: The write methods differ: MongoDB uses bulk
insert, Cassandra uses asynchronous prepared individual inserts with
write completion waits, and Neo4j uses UNWIND with CREATE in a
transaction. These results compare the implemented workflows in the
local environment, not perfectly controlled engine limits.
Graph analysis
- Threat nodes: 100,000
- Source nodes: 16
- Campaign nodes: 10,000
- Cross-source campaigns returned: 100
- MongoDB threat records cross-referenced: 1,000
The graph analysis query has a LIMIT 100, so 100 is the number
returned, not necessarily the total number of matching campaigns. The
source-pair ranking is based on the generated campaign relationships.
These associations are synthetic and are not proof of real threat
attribution or false positives.
Lab 18.1 result files
- activity-18.1/benchmark_results.json
- activity-18.1/graph_analysis_results.json
Lab 18.2 — Comparative analysis
Lab18.2 contains the following authored analysis artifacts:
- activity-18.2/diagrams/system_architecture.md
- activity-18.2/results/query_performance.md
- activity-18.2/results/insert_throughput.md
- activity-18.2/results/data_model_comparison.md
- activity-18.2/results/scalability_analysis.md
- activity-18.2/results/operations_and_hardware.md
- activity-18.2/results/final_recommendation.md
Main findings
- MongoDB: Best measured median for threat-history and target
  retrieval; highest measured insert throughput in this implementation.
- Cassandra: Best measured daily-volume query because the daily
  counts are pre-aggregated in a dedicated table; suitable for
  query-driven distributed storage.
- Neo4j: Models threat/source/campaign relationships directly and
  supports graph traversal and correlation.
Recommendation
A polyglot architecture is suitable when all three workload types
matter:
- MongoDB as the primary operational threat store.
- Cassandra for query-driven distributed storage and analytical access.
- Neo4j for graph-based threat relationship analysis.
If only one database can be operated, MongoDB is the most balanced
choice for the workloads tested in this experiment.
Scalability note
The experiment measured 100,000 records. The 1M, 10M, and 100M scenarios
in the Lab18.2 analysis are qualitative projections, not measured
results or production capacity guarantees.
Project structure
lab18/
├── data/
│   ├── threats_100k.jsonl
│   └── threats_100k.csv
├── scripts/
│   └── generate_dataset.py
├── activity-18.1/
│   ├── mongodb_setup.py
│   ├── cassandra_setup.py
│   ├── neo4j_setup.py
│   ├── import_mongodb.py
│   ├── import_cassandra.py
│   ├── import_neo4j.py
│   ├── prepare_benchmarks.py
│   ├── benchmark.py
│   ├── graph_analysis.py
│   ├── benchmark_results.json
│   └── graph_analysis_results.json
├── activity-18.2/
│   ├── diagrams/
│   │   └── system_architecture.md
│   └── results/
│       ├── query_performance.md
│       ├── insert_throughput.md
│       ├── data_model_comparison.md
│       ├── scalability_analysis.md
│       ├── operations_and_hardware.md
│       └── final_recommendation.md
├── .env
├── .gitignore
├── output.txt
└── README.md
The tree lists the intended Lab18 deliverables. Keep .env private and
do not commit credentials.
Python dependencies
The Lab18 scripts use:
python3 -m pip install pymongo cassandra-driver neo4j python-dotenv
Database services must be running and reachable using the local settings
in .env.
Running the workflow
Run commands from the labs/lab18 directory.
1. Generate the synthetic dataset:
   python3 scripts/generate_dataset.py
2. Create each database schema:
   python3 activity-18.1/mongodb_setup.py
   python3 activity-18.1/cassandra_setup.py
   python3 activity-18.1/neo4j_setup.py
3. Import the dataset:
   python3 activity-18.1/import_mongodb.py
   python3 activity-18.1/import_cassandra.py
   python3 activity-18.1/import_neo4j.py
4. Prepare query-specific benchmark structures:
   python3 activity-18.1/prepare_benchmarks.py
5. Run performance benchmarks:
   python3 activity-18.1/benchmark.py
6. Run graph campaign analysis:
   python3 activity-18.1/graph_analysis.py
Caution: The import scripts are designed to avoid accidental
duplicate imports and may stop if records already exist. Do not rerun
imports blindly. The benchmark script creates separate benchmark-only
data. Review scripts before rerunning any operation.
Limitations
- All threat records and campaign associations are synthetic.
- Only the 100,000-record dataset was directly tested.
- The benchmarks were run in one local environment.
- Insert methods differ among databases, limiting strict comparability.
- Cassandra’s daily-volume query reads precomputed aggregates, whereas
  MongoDB and Neo4j calculate aggregation results during the query.
- Larger-scale capacity scenarios are estimates requiring validation
  with representative workloads.
Conclusion
Lab18 demonstrates that database selection should be based on workload
characteristics rather than a single performance number. MongoDB
provides flexible operational storage, Cassandra supports query-driven
distributed data access, and Neo4j supports relationship-centric
investigation. A combined architecture can use each database for the
workload it models best.