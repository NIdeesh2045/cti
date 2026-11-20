
"""
Experiment 1.2: Map a Real-World Application to NoSQL Families
Course: 23CSE528 - NoSQL Databases using MongoDB

Objective:
Identify the most appropriate NoSQL family for different
application data domains and justify the selection.
"""

import textwrap

def print_table(title, headers, rows):
    widths = [22, 22, 22, 42]

    print("\n" + "=" * 112)
    print(title.center(112))
    print("=" * 112)

    header = "".join(
        f"{headers[i]:<{widths[i]}}"
        for i in range(len(headers))
    )
    print(header)
    print("-" * 112)

    for row in rows:
        wrapped = [
            textwrap.wrap(str(row[i]), width=widths[i]) or [""]
            for i in range(len(row))
        ]

        row_height = max(len(cell) for cell in wrapped)

        for line in range(row_height):
            for col in range(len(row)):
                value = (
                    wrapped[col][line]
                    if line < len(wrapped[col])
                    else ""
                )
                print(f"{value:<{widths[col]}}", end="")
            print()

        print("-" * 112)

    print("=" * 112)



def ride_sharing_application():
    print("\nACTIVITY 1: RIDE-SHARING APPLICATION")
    print("Scenario: An application similar to Uber")
    print("-" * 110)

    domains = [
        {
            "domain": "Driver Locations",
            "family": "Key-Value",
            "database": "Redis",
            "reason": (
                "Driver locations are frequently updated and retrieved "
                "using driver IDs. Redis provides fast lookups and "
                "geospatial operations."
            )
        },
        {
            "domain": "User Profiles",
            "family": "Document",
            "database": "MongoDB",
            "reason": (
                "User profiles contain nested and flexible information "
                "such as addresses, preferences and payment details."
            )
        },
        {
            "domain": "Ride History",
            "family": "Wide-Column / Document",
            "database": "Cassandra / MongoDB",
            "reason": (
                "Ride records are frequently appended and retrieved "
                "by rider ID and date range. Cassandra supports "
                "high write throughput and time-based queries."
            )
        },
        {
            "domain": "Driver-Rider Relationships",
            "family": "Graph",
            "database": "Neo4j",
            "reason": (
                "Graph databases efficiently represent and traverse "
                "relationships, useful for referral networks, "
                "connections and fraud detection."
            )
        }
    ]

    rows = [
        (
            item["domain"],
            item["family"],
            item["database"],
            item["reason"]
        )
        for item in domains
    ]

    print_table(
        "RIDE-SHARING DATA DOMAIN MAPPING",
        ["Data Domain", "NoSQL Family", "Database", "Reason"],
        rows
    )


def social_media_analytics():
    print("\nACTIVITY 2: SOCIAL MEDIA ANALYTICS PLATFORM")
    print(
        "Scenario: A platform processing millions of posts daily "
        "and tracking trending topics in real time."
    )
    print("-" * 110)

    domains = [
        {
            "domain": "Raw Post Storage",
            "family": "Wide-Column",
            "database": "Apache Cassandra",
            "reason": (
                "Cassandra supports high write throughput and "
                "scalable storage for millions of incoming posts. "
                "It also supports partition-based access patterns."
            )
        },
        {
            "domain": "Real-Time Analytics",
            "family": "Key-Value",
            "database": "Redis",
            "reason": (
                "Redis provides fast in-memory counters and caching "
                "for trending topics, engagement statistics and "
                "real-time dashboard updates."
            )
        }
    ]

    rows = [
        (
            item["domain"],
            item["family"],
            item["database"],
            item["reason"]
        )
        for item in domains
    ]

    print_table(
        "SOCIAL MEDIA ANALYTICS DATA MAPPING",
        ["Data Domain", "NoSQL Family", "Database", "Reason"],
        rows
    )


def summary():
    print("\nFINAL SUMMARY")
    print("=" * 110)

    summary_data = [
        ("Driver Locations", "Key-Value", "Redis"),
        ("User Profiles", "Document", "MongoDB"),
        ("Ride History", "Wide-Column / Document", "Cassandra / MongoDB"),
        ("Driver-Rider Relationships", "Graph", "Neo4j"),
        ("Raw Social Media Posts", "Wide-Column", "Apache Cassandra"),
        ("Real-Time Analytics", "Key-Value", "Redis")
    ]

    for domain, family, database in summary_data:
        print(f"{domain:<35} | {family:<25} | {database}")

    print("=" * 110)


def main():
    print("\n23CSE528 - NOSQL DATABASES USING MONGODB")
    print("EXPERIMENT 1.2")
    print("=" * 110)

    ride_sharing_application()
    social_media_analytics()
    summary()

    print("\nExperiment 1.2 completed successfully.")
    print("=" * 110)


if __name__ == "__main__":
    main()
