
import os
import time
from pymongo import MongoClient
from cassandra.cluster import Cluster
from neo4j import GraphDatabase


class CircuitBreaker:
    def __init__(self, threshold=3, reset_timeout=30):
        self.threshold = threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.opened_at = None

    def call(self, function, *args):
        if self.opened_at and time.time() - self.opened_at < self.reset_timeout:
            raise RuntimeError("Circuit breaker OPEN")

        if self.opened_at:
            self.opened_at = None
            self.failures = 0

        try:
            result = function(*args)
            self.failures = 0
            return result
        except Exception:
            self.failures += 1
            if self.failures >= self.threshold:
                self.opened_at = time.time()
            raise


class FraudQueryService:
    def __init__(self):
        self.mongo = MongoClient(
            "localhost", 27317,
            username="lab13_admin",
            password=os.environ["MONGO_PASSWORD"],
            authSource="admin",
            directConnection=True,
            maxPoolSize=10
        )
        self.mongo_db = self.mongo["fraud_detection"]

        self.cassandra_cluster = Cluster(["127.0.0.1"], port=9042)
        self.cassandra = self.cassandra_cluster.connect("fraud_detection")

        self.neo4j = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", os.getenv("NEO4J_PASSWORD", "lab16password")),
            max_connection_pool_size=10
        )

        self.breakers = {
            name: CircuitBreaker()
            for name in ("mongo", "cassandra", "neo4j")
        }

    def get_transaction(self, txn_id):
        return self.breakers["mongo"].call(
            lambda: self.mongo_db.transactions.find_one(
                {"txn_id": txn_id}, {"_id": 0}
            )
        )

    def get_user_profile(self, user_id):
        return self.breakers["cassandra"].call(
            lambda: list(self.cassandra.execute(
                """
                SELECT * FROM user_profiles
                WHERE user_id = %s LIMIT 10
                """,
                [user_id]
            ))
        )

    def detect_fraud_rings(self, user_id, max_hops=3):
        if not 1 <= max_hops <= 5:
            raise ValueError("max_hops must be between 1 and 5")

        def query():
            cypher = f"""
            MATCH path =
            (u:User {{id: $uid}})-[:TRANSFERRED_TO*1..{max_hops}]-
            (connected:User)
            RETURN path LIMIT 50
            """
            with self.neo4j.session() as session:
                return list(session.run(cypher, uid=user_id))

        return self.breakers["neo4j"].call(query)

    def analyze_fraud(self, txn_id, user_id):
        start = time.perf_counter()

        transaction = self.get_transaction(txn_id)
        profile = self.get_user_profile(user_id)
        connections = self.detect_fraud_rings(user_id)

        return {
            "transaction": transaction,
            "user_events": profile,
            "fraud_connections": len(connections),
            "latency_ms": round((time.perf_counter() - start) * 1000, 2)
        }

    def close(self):
        self.mongo.close()
        self.cassandra_cluster.shutdown()
        self.neo4j.close()


if __name__ == "__main__":
    service = FraudQueryService()
    try:
        result = service.analyze_fraud("TXN001", "U001")
        print("HYBRID FRAUD ANALYSIS")
        print("Transaction:", result["transaction"])
        print("User events:", len(result["user_events"]))
        print("Fraud connections:", result["fraud_connections"])
        print("Latency:", result["latency_ms"], "ms")
    finally:
        service.close()
