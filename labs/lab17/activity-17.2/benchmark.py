
import time
import json
import random
import os

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

NUM_DOCUMENTS = 5000
NUM_QUERIES = 100
TOP_K = 20
DIMENSIONS = 384
RANDOM_SEED = 42

OUTPUT_DIR = "activity-17.2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# --------------------------------------------------
# 1. GENERATE 5000 THREAT INTELLIGENCE DOCUMENTS
# --------------------------------------------------

threats = [
    "phishing attacks", "ransomware attacks", "malware infections",
    "SQL injection", "cross-site scripting", "DDoS attacks",
    "brute force attacks", "zero-day vulnerabilities",
    "credential theft", "insider threats"
]

targets = [
    "enterprise networks", "cloud infrastructure",
    "database servers", "web applications", "email systems",
    "financial systems", "endpoint devices", "IoT devices",
    "government systems", "healthcare networks"
]

techniques = [
    "using malicious email attachments",
    "through stolen login credentials",
    "by exploiting unpatched software",
    "using command and control servers",
    "through vulnerable network services",
    "by abusing privilege escalation",
    "using malicious scripts",
    "through compromised third-party software",
    "by exploiting weak authentication",
    "using social engineering techniques"
]

impacts = [
    "data theft and information disclosure",
    "unauthorized access to sensitive systems",
    "financial losses and operational disruption",
    "data encryption and service unavailability",
    "network compromise and lateral movement",
    "loss of confidential information",
    "system damage and business interruption",
    "identity theft and account compromise"
]

def generate_documents(count):
    documents = []

    for i in range(count):
        threat = random.choice(threats)
        target = random.choice(targets)
        technique = random.choice(techniques)
        impact = random.choice(impacts)

        text = (
            f"Threat Report {i + 1}. "
            f"The incident involves {threat} targeting {target}. "
            f"Attackers operate {technique}. "
            f"The potential impact includes {impact}. "
            f"Organizations should apply security monitoring, "
            f"regular patching, access controls and incident response "
            f"procedures to reduce the risk."
        )

        documents.append(text)

    return documents


print("Generating threat intelligence documents...")
documents = generate_documents(NUM_DOCUMENTS)

print("Total documents:", len(documents))

# --------------------------------------------------
# 2. LOAD EMBEDDING MODEL
# --------------------------------------------------

print("\nLoading embedding model...")

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

print("Model loaded successfully.")
print("Embedding dimensions:", model.get_sentence_embedding_dimension())

# --------------------------------------------------
# 3. GENERATE 384-DIMENSIONAL EMBEDDINGS
# --------------------------------------------------

print("\nGenerating document embeddings...")

document_embeddings = model.encode(
    documents,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True
)

document_embeddings = np.asarray(
    document_embeddings, dtype=np.float32
)

assert document_embeddings.shape == (NUM_DOCUMENTS, DIMENSIONS)

print("Embedding shape:", document_embeddings.shape)

# --------------------------------------------------
# 4. GENERATE 100 TEST QUERIES
# --------------------------------------------------

queries = []

for i in range(NUM_QUERIES):
    threat = random.choice(threats)
    target = random.choice(targets)
    technique = random.choice(techniques)

    query = (
        f"What security measures can protect against {threat} "
        f"targeting {target} {technique}?"
    )

    queries.append(query)

print("\nTotal test queries:", len(queries))

query_embeddings = model.encode(
    queries,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True
)

query_embeddings = np.asarray(
    query_embeddings, dtype=np.float32
)

# --------------------------------------------------
# 5. EXACT SEARCH BASELINE
# --------------------------------------------------

print("\nBuilding exact search baseline...")

exact_index = faiss.IndexFlatIP(DIMENSIONS)

exact_start = time.perf_counter()
exact_index.add(document_embeddings)
exact_build_time = time.perf_counter() - exact_start

print("Exact index built successfully.")
print(f"Exact index build time: {exact_build_time:.4f} seconds")

print("\nCalculating exact top-20 results...")

exact_distances, exact_indices = exact_index.search(
    query_embeddings, TOP_K
)

# --------------------------------------------------
# 6. HNSW INDEX
# --------------------------------------------------

print("\nBuilding HNSW index...")

hnsw_start = time.perf_counter()

hnsw_index = faiss.IndexHNSWFlat(
    DIMENSIONS, 32, faiss.METRIC_INNER_PRODUCT
)

hnsw_index.hnsw.efConstruction = 200
hnsw_index.hnsw.efSearch = 64

hnsw_index.add(document_embeddings)

hnsw_build_time = time.perf_counter() - hnsw_start

print("HNSW index built successfully.")
print(f"HNSW build time: {hnsw_build_time:.4f} seconds")

# --------------------------------------------------
# 7. IVF INDEX
# --------------------------------------------------

print("\nBuilding IVF index...")

nlist = 100
nprobe = 10

quantizer = faiss.IndexFlatIP(DIMENSIONS)

ivf_index = faiss.IndexIVFFlat(
    quantizer,
    DIMENSIONS,
    nlist,
    faiss.METRIC_INNER_PRODUCT
)

ivf_start = time.perf_counter()

ivf_index.train(document_embeddings)
ivf_index.add(document_embeddings)

ivf_build_time = time.perf_counter() - ivf_start

ivf_index.nprobe = nprobe

print("IVF index built successfully.")
print(f"IVF build time: {ivf_build_time:.4f} seconds")

# --------------------------------------------------
# 8. BENCHMARK FUNCTION
# --------------------------------------------------

def benchmark_index(index, index_name):
    print(f"\nBenchmarking {index_name}...")

    # Warm-up search
    index.search(query_embeddings[:5], TOP_K)

    latencies = []
    recalls = []

    for i in range(NUM_QUERIES):
        query_vector = query_embeddings[i:i + 1]

        start = time.perf_counter()

        distances, indices = index.search(query_vector, TOP_K)

        elapsed = time.perf_counter() - start

        latencies.append(elapsed * 1000)

        exact_set = set(exact_indices[i])
        retrieved_set = set(indices[0])

        recall = len(exact_set.intersection(retrieved_set)) / TOP_K

        recalls.append(recall)

    return {
        "Index": index_name,
        "Build Time (seconds)": round(
            hnsw_build_time if index_name == "HNSW"
            else ivf_build_time, 4
        ),
        "Average Latency (ms)": round(float(np.mean(latencies)), 4),
        "Recall@20 (%)": round(float(np.mean(recalls)) * 100, 2),
        "Queries": NUM_QUERIES
    }


# --------------------------------------------------
# 9. RUN BOTH BENCHMARKS
# --------------------------------------------------

hnsw_results = benchmark_index(hnsw_index, "HNSW")
ivf_results = benchmark_index(ivf_index, "IVF")

results = pd.DataFrame([hnsw_results, ivf_results])

# --------------------------------------------------
# 10. DISPLAY AND SAVE RESULTS
# --------------------------------------------------

print("\n==============================================")
print("       HNSW vs IVF BENCHMARK RESULTS")
print("==============================================")

print(results.to_string(index=False))

csv_path = os.path.join(OUTPUT_DIR, "benchmark_results.csv")
json_path = os.path.join(OUTPUT_DIR, "benchmark_results.json")

results.to_csv(csv_path, index=False)

with open(json_path, "w") as file:
    json.dump(results.to_dict(orient="records"), file, indent=4)

print("\nResults saved:")
print(csv_path)
print(json_path)

# --------------------------------------------------
# 11. AUTOMATIC COMPARISON
# --------------------------------------------------

print("\n==============================================")
print("             COMPARISON")
print("==============================================")

fastest = results.loc[
    results["Average Latency (ms)"].idxmin(), "Index"
]

best_recall = results.loc[
    results["Recall@20 (%)"].idxmax(), "Index"
]

fastest_build = results.loc[
    results["Build Time (seconds)"].idxmin(), "Index"
]

print("Fastest query search:", fastest)
print("Highest recall:", best_recall)
print("Fastest index construction:", fastest_build)

print("\nBenchmark completed successfully!")
