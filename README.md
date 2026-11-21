# Threat Intelligence Platform & NoSQL Integrated Laboratory

```{=html}
<p align="center">
```
`<strong>`{=html}An integrated collection of Cyber Threat Intelligence
application development and hands-on NoSQL database engineering
experiments.`</strong>`{=html}
```{=html}
</p>
```
```{=html}
<p align="center">
```
`<img src="https://img.shields.io/badge/CTI%20Platform-FastAPI%20%7C%20MongoDB%20%7C%20Ollama-2563eb?style=for-the-badge" alt="CTI stack">`{=html}
`<img src="https://img.shields.io/badge/NoSQL%20Labs-18%20Experiments-16a34a?style=for-the-badge" alt="18 experiments">`{=html}
`<img src="https://img.shields.io/badge/Databases-MongoDB%20%7C%20Cassandra%20%7C%20Neo4j-0d9488?style=for-the-badge" alt="Databases">`{=html}
`<img src="https://img.shields.io/badge/Deployment-Docker-2496ed?style=for-the-badge" alt="Docker">`{=html}
```{=html}
</p>
```
## About This Repository

This repository brings together two connected areas of work:

1.  **Cyber Threat Intelligence (CTI) Platform** --- a containerized web
    application for viewing and managing threat intelligence, backed by
    MongoDB and supported by a locally hosted AI assistant.
2.  **NoSQL Integrated Laboratory** --- 18 practical experiments
    covering NoSQL data modelling, MongoDB operations, distributed
    systems, security, high availability, monitoring, multi-tenancy,
    polyglot persistence, vector retrieval and database benchmarking.

The CTI application provides an applied cybersecurity data-management
project, while the laboratory explores the database technologies,
architectures and engineering practices used to build and operate
data-intensive systems.

## Repository Contents

  -----------------------------------------------------------------------
  Directory                           Description
  ----------------------------------- -----------------------------------
  [`cti-app/`](./cti-app/)            Cyber Threat Intelligence web
                                      application, backend, frontend and
                                      deployment files

  [`labs/`](./labs/)                  NoSQL laboratory experiments
                                      01--18, with individual
                                      documentation and saved results
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 1. Cyber Threat Intelligence Platform

## Overview

The **Cyber Threat Intelligence (CTI) Platform** is a containerized
application designed to collect, store, browse and analyze cyber threat
intelligence through a web-based interface. It combines a FastAPI
backend, MongoDB database and an AI-powered chatbot connected to Ollama
running on the host machine.

The platform is packaged as a Docker image so that the application and
its MongoDB service can be deployed without separately installing Python
dependencies or MongoDB on the target laptop.

## Key Features

-   **Threat Intelligence Dashboard** --- view and monitor collected
    threat intelligence.
-   **Threat Management** --- browse, search and filter threat records.
-   **AI-Powered Chatbot** --- ask questions about threat intelligence
    using a locally hosted language model.
-   **Authentication** --- login and user registration.
-   **MongoDB Storage** --- persist threat intelligence and application
    data.
-   **Containerized Deployment** --- run the application and MongoDB
    from a single Docker image/container.
-   **Local AI Runtime** --- connect to Ollama on the host for chat and
    embedding functionality.

## CTI Technology Stack

  Component          Technology
  ------------------ -----------------------
  Backend            Python, FastAPI
  Database           MongoDB 8.0
  Frontend           HTML, CSS, JavaScript
  AI runtime         Ollama
  Chat model         `llama3.2:3b`
  Embedding model    `nomic-embed-text`
  Containerization   Docker

## CTI Architecture

``` text
                   User / Web Browser
                           |
                           v
                  CTI Web Interface
                           |
                           v
                    FastAPI Backend
                      /         \
                     /           \
                    v             v
                MongoDB         Ollama
                Database    (Host Machine)
                                  |
                           +------+------+
                           |             |
                           v             v
                      llama3.2:3b  nomic-embed-text
```

**Deployment note:** The Docker image contains the CTI application and
MongoDB. Ollama and its models run separately on the host machine. On
Docker Desktop for macOS and Windows, the container connects to the host
Ollama service using `host.docker.internal`.

## Docker Image

-   **Docker Hub:**
    [laddu2045/cti-platform](https://hub.docker.com/r/laddu2045/cti-platform)
-   **Image:** `laddu2045/cti-platform:2.1`
-   **Application port:** `8000`
-   **Database:** MongoDB 8.0
-   **Database persistence:** Docker named volume `cti-mongodb-data`
-   **AI runtime:** Ollama on the host

### Prerequisites

-   Docker Desktop or Docker Engine
-   Ollama installed on the host machine
-   The following Ollama models:

``` bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
ollama list
```

Make sure the Ollama service is running before using the chatbot
features.

### Run the Published Image

Pull the image:

``` bash
docker pull laddu2045/cti-platform:2.1
```

Start the container:

``` bash
docker run -d \
  --name cti-platform \
  -p 8000:8000 \
  -v cti-mongodb-data:/data/db \
  -e MONGO_ROOT_USER=root \
  -e MONGO_ROOT_PASSWORD='YOUR_STRONG_PASSWORD' \
  -e ADMIN_PASSWORD='YOUR_ADMIN_PASSWORD' \
  -e JWT_SECRET='YOUR_LONG_RANDOM_SECRET' \
  -e OLLAMA_URL=http://host.docker.internal:11434 \
  -e OLLAMA_CHAT_MODEL=llama3.2:3b \
  -e OLLAMA_EMBEDDING_MODEL=nomic-embed-text \
  laddu2045/cti-platform:2.1
```

Replace the example credentials and secret with secure values. Keep
secrets out of source control.

Open the application:

**http://localhost:8000**

### Useful CTI Commands

  Task                       Command
  -------------------------- -------------------------------
  Start existing container   `docker start cti-platform`
  Stop container             `docker stop cti-platform`
  Restart container          `docker restart cti-platform`
  Check running containers   `docker ps`
  View container logs        `docker logs -f cti-platform`
  View all containers        `docker ps -a`
  List Docker volumes        `docker volume ls`

The MongoDB named volume preserves database data when the container is
stopped or recreated. A newly deployed laptop starts with a fresh
database unless data is migrated separately.

### Deploying on Another Laptop

1.  Install Docker.
2.  Install Ollama.
3.  Pull `llama3.2:3b` and `nomic-embed-text`.
4.  Pull `laddu2045/cti-platform:2.1`.
5.  Start the container using the command above, with secure
    credentials.
6.  Open `http://localhost:8000`.

Ollama and its models are not included in the Docker image and must be
installed separately. For Linux Docker Engine, host access may require
`--add-host=host.docker.internal:host-gateway` and suitable Ollama
network configuration.

------------------------------------------------------------------------

# 2. NoSQL Integrated Laboratory

## Overview

The **NoSQL Integrated Laboratory** is a collection of 18 hands-on
experiments exploring NoSQL database technologies and their use in
real-world systems.

The experiments progress from database families and document modelling
to replication, sharding, transactions, security, high availability,
backup and restore, multi-tenancy, polyglot persistence,
Retrieval-Augmented Generation (RAG), vector search and cross-database
performance analysis.

## Laboratory Highlights

-   18 documented practical experiments.
-   MongoDB document modelling, CRUD, indexing, replication,
    transactions and sharding.
-   Apache Cassandra wide-column modelling and query-driven tables.
-   Neo4j graph modelling and relationship analysis.
-   Python automation and FastAPI-based services.
-   Docker and Docker Compose-based experiment environments.
-   Authentication, RBAC, TLS and tenant isolation.
-   Monitoring, backup, restore and operational verification.
-   Vector embeddings, retrieval and local LLM integration.
-   Comparative benchmarking using a synthetic threat-intelligence
    dataset.

## Laboratory Technology Stack

  -----------------------------------------------------------------------
  Area                                Technologies
  ----------------------------------- -----------------------------------
  Programming                         Python

  Document database                   MongoDB

  Wide-column database                Apache Cassandra

  Graph database                      Neo4j

  Backend and APIs                    FastAPI, REST

  Database drivers                    PyMongo, Cassandra Python Driver,
                                      Neo4j Python Driver

  Containers                          Docker, Docker Compose

  Orchestration                       Kubernetes

  Security                            JWT, MongoDB RBAC, TLS,
                                      certificates, key-file
                                      authentication

  Monitoring                          MongoDB metrics, exporters,
                                      operational scripts

  AI and retrieval                    FastEmbed, MongoDB Atlas Vector
                                      Search, Ollama

  Documentation                       Markdown, Mermaid
  -----------------------------------------------------------------------

## Experiment Roadmap

  ------------------------------------------------------------------------
  Stage                                  Experiments Main focus
  --------------------- ---------------------------- ---------------------
  NoSQL Foundations                           01--06 Database families,
                                                     data modelling, CRUD
                                                     and indexing

  Distributed MongoDB                         07--11 Schema design,
                                                     working sets,
                                                     replication,
                                                     consistency,
                                                     transactions and
                                                     sharding

  Production                                  12--15 Security, high
  Engineering                                        availability,
                                                     Kubernetes,
                                                     monitoring, backup
                                                     and multi-tenancy

  Advanced Data Systems                       16--18 Polyglot persistence,
                                                     RAG, vector search
                                                     and comparative
                                                     benchmarking
  ------------------------------------------------------------------------

## Experiment Catalogue

### Stage 1 --- NoSQL Foundations

  -----------------------------------------------------------------------
  Experiment              Topic                   What it covers
  ----------------------- ----------------------- -----------------------
  **01**                  Database Classification Document, key-value,
                          and NoSQL Families      wide-column and graph
                                                  database models; use
                                                  cases and technology
                                                  selection.

  **02**                  Application Data-Domain Mapping application
                          Mapping                 domains and access
                                                  patterns to suitable
                                                  NoSQL database
                                                  families. Six domain
                                                  mappings were recorded.

  **03**                  Embedded and Referenced Comparing embedded and
                          Document Modelling      referenced
                                                  relationships,
                                                  including one-to-one,
                                                  one-to-many and
                                                  many-to-many
                                                  structures.

  **04**                  Product Query API and   Python and MongoDB CRUD
                          Inventory CRUD          operations, filters,
                                                  comparison operators,
                                                  upserts and bulk
                                                  updates.

  **05**                  Order and Product Data  Order-oriented document
                          Modelling               structures, product
                                                  data, grouping and
                                                  query-driven modelling.

  **06**                  Index Design and Index  Single-field and
                          Strategies              compound indexes, index
                                                  ordering, query plans
                                                  and read/write
                                                  trade-offs.
  -----------------------------------------------------------------------

### Stage 2 --- Distributed MongoDB Systems

  -----------------------------------------------------------------------
  Experiment              Topic                   What it covers
  ----------------------- ----------------------- -----------------------
  **07**                  Production Schema       CTI document modelling,
                          Design and Working-Set  embedding versus
                          Analysis                referencing, BSON size,
                                                  a 100,000-document
                                                  working set and
                                                  WiredTiger cache
                                                  behaviour.

  **08**                  Replica-Set Monitoring, Replica-set members,
                          Failover and Priority   primary/secondary
                                                  roles, election
                                                  priority, arbiter
                                                  configuration and
                                                  failover observation.

  **09**                  Write Concern and       Comparing `w=1` and
                          Network Partition       majority
                                                  acknowledgement,
                                                  observing partition
                                                  behaviour and verifying
                                                  cluster recovery.

  **10**                  Transactions and        Multi-document
                          Concurrent Inventory    transactions,
                          Reservation             commit/rollback,
                                                  consistency and
                                                  concurrent inventory
                                                  updates.

  **11**                  Shard-Key Analysis and  Range and hashed shard
                          Hotspot Demonstration   keys, shard
                                                  distribution, query
                                                  targeting and
                                                  monotonically
                                                  increasing-key
                                                  hotspots.
  -----------------------------------------------------------------------

### Stage 3 --- Production Engineering and Security

  -----------------------------------------------------------------------
  Experiment              Topic                   What it covers
  ----------------------- ----------------------- -----------------------
  **12**                  MongoDB RBAC and TLS    Database
                          Security                authentication,
                                                  role-based permissions,
                                                  certificates and
                                                  encrypted client
                                                  connections.

  **13**                  Authenticated High      Key-file authenticated
                          Availability and        replica sets, metrics
                          Kubernetes              exporter, Kubernetes
                                                  StatefulSets and
                                                  persistent volume
                                                  claims.

  **14**                  MongoDB Monitoring and  Operational metrics,
                          Automated               timestamped backups,
                          Backup/Restore          restore workflows and
                                                  data verification.

  **15**                  Multi-Tenant API,       FastAPI task service,
                          Access Control and      JWT, role permissions,
                          Migration               tenant isolation, rate
                                                  limiting, TTL and
                                                  tenant-specific
                                                  migration.
  -----------------------------------------------------------------------

### Stage 4 --- Advanced Data Systems

  -----------------------------------------------------------------------
  Experiment              Topic                   What it covers
  ----------------------- ----------------------- -----------------------
  **16**                  Polyglot Persistence    Integrating MongoDB,
                          and Hybrid Query        Cassandra and Neo4j
                          Service                 through a unified
                                                  service, including
                                                  hybrid queries and
                                                  resilience patterns.

  **17**                  RAG Pipeline and Vector Cybersecurity
                          Index Benchmarking      knowledge-base
                                                  chunking,
                                                  384-dimensional
                                                  embeddings, vector
                                                  retrieval, MongoDB
                                                  Atlas and Qwen3:4B
                                                  through Ollama.

  **18**                  Cross-Database Threat   Comparing MongoDB,
                          Intelligence Benchmark  Cassandra and Neo4j
                                                  with 100,000 synthetic
                                                  threat records, query
                                                  benchmarks, insert
                                                  throughput and
                                                  graph-based campaign
                                                  analysis.
  -----------------------------------------------------------------------

Individual experiment documentation, implementation files and saved
outputs are maintained under [`labs/`](./labs/). Refer to each lab's
README for its detailed setup, commands, observations and results.

## Selected Laboratory Results

The following are recorded results from specific experiment runs. They
are not universal performance guarantees.

### Lab 11 --- Shard-Key Distribution

In the recorded two-shard hotspot test:

  Strategy                                   Shard 1   Shard 2
  ---------------------------------------- --------- ---------
  Monotonically increasing timestamp key      10,000         0
  Hashed key                                   5,027     4,973

This illustrates how a monotonically increasing key can concentrate
writes, while hashing can distribute records more evenly. Hashed keys
can make range queries less efficient because the original key order is
not preserved.

### Lab 14 --- Backup and Restore

  Measurement              Recorded result
  ---------------------- -----------------
  Documents restored                 1,000
  Backup time                0.004 seconds
  Restore time               0.030 seconds
  Restore verification                True

### Lab 15 --- Multi-Tenant API

  Measurement                     Recorded result
  ----------------------------- -----------------
  Tasks seeded                                500
  Users                                        10
  Cross-tenant leaks observed                   0

### Lab 18 --- Comparative Database Benchmark

Lab 18 uses a generated dataset containing 100,000 synthetic threat
records, 16 sources, seven threat types and 10,000 synthetic campaigns.

**Median query latency (lower is faster for the tested query):**

  Query category            MongoDB   Cassandra       Neo4j
  --------------------- ----------- ----------- -----------
  Threat history           0.454 ms    2.023 ms   15.139 ms
  Target analysis          0.451 ms    1.866 ms   28.889 ms
  Daily threat volume     58.088 ms    4.316 ms   67.996 ms

**Median insert throughput:**

  Database      Records per second
  ----------- --------------------
  MongoDB               242,739.95
  Cassandra              23,648.29
  Neo4j                  60,957.13

**Graph model recorded in the experiment:**

-   100,000 threat nodes
-   16 source nodes
-   10,000 campaign nodes
-   200,000 relationships

**Interpretation:** MongoDB performed strongly for the tested
threat-history and target queries. Cassandra performed strongly for
daily threat volume because the experiment used a pre-aggregated table.
Neo4j represented source, threat and campaign relationships directly for
graph analysis.

**Important limitations:** Lab 18's records and campaign associations
are synthetic, not verified real-world threat intelligence. Shared
campaign membership is a generated association, not proof of attribution
or a false positive. The benchmark ran in one local environment, and
database write methods differed. Larger-scale scenarios are projections,
not measured capacity guarantees.

## Laboratory Deployment

The integrated lab deployment launcher supports the following experiment
groups:

  Profile    Experiments
  ---------- --------------
  `demo-a`   7--10 and 12
  `demo-b`   11
  `demo-c`   13--14
  `demo-d`   15--16
  `demo-e`   17--18

The launcher also provides status and stop operations:

``` bash
./demo.sh demo-status
./demo.sh demo-stop
```

Run the commands from the directory containing the launcher. Check the
relevant lab README and configuration before starting an experiment
group.

**Resource note:** These environments have different CPU and memory
requirements. Do not assume all groups should run simultaneously. Some
experiments also require external services, credentials or a Kubernetes
environment.

## General Laboratory Setup

Clone the repository:

``` bash
git clone https://github.com/NIdeesh2045/threat-intelligence-platform.git
cd threat-intelligence-platform
```

Review the relevant experiment's README and environment template.
Configure database connection strings, credentials, ports and
application settings for that experiment.

Start only the required database services using that experiment's
documented Docker Compose file or launcher. A generic Compose command
may look like:

``` bash
docker compose up -d
```

This is a general example; individual labs may use different Compose
files, profiles or startup scripts.

Verify containers:

``` bash
docker ps
```

Do not commit `.env` files, passwords, private keys, certificates or
other secrets.

------------------------------------------------------------------------

# 3. Running the Two Main Components

## Start the CTI Application

If the CTI container has already been created:

``` bash
docker start cti-platform
```

Open:

http://localhost:8000

Stop it when finished:

``` bash
docker stop cti-platform
```

The chatbot also requires the Ollama service and its configured models
to be available on the host.

## Run the NoSQL Labs

There is no single command that starts every lab. Each experiment has
its own services, configuration and workflow. Start the required lab
environment using its own README and launcher instructions.

For the grouped deployment launcher, use the appropriate `demo-a`
through `demo-e` profile and check its status before and after use.

------------------------------------------------------------------------

# 4. Engineering Practices and Key Learnings

This repository demonstrates practical engineering concepts across
application development and database systems:

1.  **Workload-driven data modelling:** select document structures and
    database models based on application access patterns.
2.  **Performance-aware indexing:** evaluate query plans and balance
    read performance against index storage and write costs.
3.  **Distributed database behaviour:** understand replication,
    elections, write concern, transactions and sharding.
4.  **Security by design:** apply authentication, RBAC, TLS and
    tenant-level data isolation.
5.  **Operational reliability:** monitor services and validate backup
    and restore operations.
6.  **Polyglot persistence:** use different databases for document,
    wide-column and graph-oriented workloads.
7.  **AI-assisted retrieval:** combine embeddings, vector search and a
    language model to retrieve relevant cybersecurity context.
8.  **Evidence-based benchmarking:** interpret measured results with
    their workload, environment and methodology limitations.

## Limitations and Responsible Interpretation

-   Lab results are specific to the recorded configuration and workload.
-   Synthetic threat data must not be represented as verified live
    threat intelligence.
-   Local benchmark results do not establish production or
    distributed-cluster performance.
-   Project documentation does not imply that all services are running
    at the same time.
-   Some labs require separate database services, external credentials,
    Ollama or Kubernetes.
-   Keep credentials and private configuration outside version control.

------------------------------------------------------------------------

# 5. Author

**K. Nideesh Reddy**\
**USN:** 24BTRCL095\
**Department:** Computer Science and Engineering\
**Institution:** JAIN (Deemed-to-be University)\
**GitHub:** [NIdeesh2045](https://github.com/NIdeesh2045)\
**Repository:**
[threat-intelligence-platform](https://github.com/NIdeesh2045/threat-intelligence-platform)\
**Docker Hub:** [laddu2045](https://hub.docker.com/u/laddu2045)

------------------------------------------------------------------------

```{=html}
<p align="center">
```
`<strong>`{=html}Building. Experimenting. Comparing.
Learning.`</strong>`{=html}
```{=html}
</p>
```
