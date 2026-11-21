
flowchart TD
    A["Synthetic Threat Dataset<br/>100,000 Records"] --> B["Data Ingestion Pipeline"]

    B --> C["MongoDB"]
    B --> D["Apache Cassandra"]
    B --> E["Neo4j"]

    C --> C1["full_threats"]
    C --> C2["Dashboard / Recent Threats"]

    D --> D1["threats_by_source"]
    D --> D2["threats_by_type"]
    D --> D3["threats_by_target"]
    D --> D4["daily_threat_volume"]

    E --> E1["Lab18Threat Nodes"]
    E --> E2["Lab18Source Nodes"]
    E --> E3["Lab18Campaign Nodes"]

    C --> F["Comparative Analysis"]
    D --> F
    E --> F

    F --> G["Query Performance"]
    F --> H["Insert Throughput"]
    F --> I["Graph Analysis"]
    G --> J["Final Database Recommendation"]
    H --> J
    I --> J
