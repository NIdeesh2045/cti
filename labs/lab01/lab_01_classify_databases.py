
"""
Experiment 1.1: Classify Database Products
Course: 23CSE528 - NoSQL Databases using MongoDB

Objective:
Identify NoSQL database families and justify their
classification, use cases, and limitations.
"""


def display_products():
    products = [
        {
            "name": "Amazon S3",
            "family": "Key-Value (Object Storage)",
            "reason": "Objects are stored and retrieved using unique object keys.",
            "best_for": "Storing images, videos, backups and data lakes.",
            "limitation": "Does not support database-style queries on object contents."
        },
        {
            "name": "Couchbase",
            "family": "Document",
            "reason": "Stores JSON documents and supports queries and indexes on fields.",
            "best_for": "User profiles, product catalogs and session management.",
            "limitation": "Requires careful indexing and memory management."
        },
        {
            "name": "Apache HBase",
            "family": "Wide-Column",
            "reason": "Organizes distributed data into column families and supports wide rows.",
            "best_for": "Large-scale log storage and time-series workloads.",
            "limitation": "Complex administration and limited relational-style querying."
        },
        {
            "name": "Amazon Neptune",
            "family": "Graph",
            "reason": "Stores relationships as graph structures and supports graph queries.",
            "best_for": "Fraud detection, recommendation engines and social networks.",
            "limitation": "Not ideal for simple key-based lookups or ordinary tabular workloads."
        },
        {
            "name": "Memcached",
            "family": "Key-Value",
            "reason": "Stores values as byte arrays accessed through unique string keys.",
            "best_for": "Caching web sessions and frequently requested database results.",
            "limitation": "In-memory cache with no built-in durable data storage."
        }
    ]

    print("\n" + "=" * 90)
    print("ACTIVITY 1.1 - CLASSIFY DATABASE PRODUCTS")
    print("=" * 90)

    for product in products:
        print(f"\nProduct     : {product['name']}")
        print(f"Family      : {product['family']}")
        print(f"Reason      : {product['reason']}")
        print(f"Best For    : {product['best_for']}")
        print(f"Limitation  : {product['limitation']}")
        print("-" * 90)


def classify_extra_product():
    print("\nTRY IT YOURSELF - ADDITIONAL PRODUCT")
    print("=" * 90)

    product = {
        "name": "ScyllaDB",
        "family": "Wide-Column",
        "reason": (
            "ScyllaDB uses a distributed wide-column data model "
            "compatible with Apache Cassandra."
        ),
        "best_for": "High-throughput workloads such as IoT data and event storage.",
        "limitation": (
            "Requires data modelling around partition keys and query patterns."
        )
    }

    print(f"Product     : {product['name']}")
    print(f"Family      : {product['family']}")
    print(f"Reason      : {product['reason']}")
    print(f"Best For    : {product['best_for']}")
    print(f"Limitation  : {product['limitation']}")


def main():
    print("\n23CSE528 - NoSQL DATABASES USING MONGODB")
    print("EXPERIMENT 1.1")

    display_products()
    classify_extra_product()

    print("\nExperiment 1.1 completed successfully.")
    print("=" * 90)


if __name__ == "__main__":
    main()
