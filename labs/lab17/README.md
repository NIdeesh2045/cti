
# Lab 17 – Vector Databases and RAG

## Overview

This lab explores Retrieval-Augmented Generation (RAG), semantic search, conversation memory, and vector indexing techniques.

## Technologies Used

- Python
- MongoDB Atlas
- Voyage AI
- Atlas Vector Search
- Ollama
- Llama 3.2 (3B)
- FAISS
- Sentence Transformers
- NumPy and Pandas

## Activity 17.1 – RAG Pipeline

### Objective
Build a RAG pipeline that retrieves relevant threat intelligence documents and generates context-aware answers using a local LLM.

### Implementation
- Created five threat intelligence documents.
- Divided documents into smaller chunks.
- Generated 1024-dimensional embeddings using Voyage AI.
- Stored documents and embeddings in MongoDB Atlas.
- Created an Atlas Vector Search index.
- Retrieved the top three relevant documents.
- Generated responses using Ollama and Llama 3.2 (3B).
- Implemented conversation memory using MongoDB.

### Files
- `activity-17.1/rag_pipeline.py`
- `activity-17.1/retrieval.py`
- `activity-17.1/generate_answer.py`
- `activity-17.1/output.txt`

## Activity 17.2 – HNSW vs IVF

### Objective
Compare HNSW and IVF vector indexes based on index construction time, query latency, and retrieval recall.

### Dataset and Configuration
- Documents: 5,000
- Test queries: 100
- Embedding dimensions: 384
- Embedding model: `all-MiniLM-L6-v2`
- Retrieval size: Top 20
- HNSW M: 32
- HNSW efConstruction: 200
- HNSW efSearch: 64
- IVF nlist: 100
- IVF nprobe: 10

### Benchmark Results

| Metric | HNSW | IVF |
|---|---:|---:|
| Build Time (seconds) | 0.3567 | 0.0109 |
| Average Latency (ms) | 0.0333 | 0.0212 |
| Recall@20 (%) | 99.80 | 99.55 |

### Files
- `activity-17.2/benchmark.py`
- `activity-17.2/benchmark_results.csv`
- `activity-17.2/benchmark_results.json`
- `activity-17.2/output.txt`

## How to Run

Install dependencies:

```bash
python3 -m pip install pymongo python-dotenv numpy voyageai faiss-cpu sentence-transformers pandas matplotlib
```

Run Activity 17.1:

```bash
python3 activity-17.1/rag_pipeline.py
```

Run Activity 17.1 retrieval:

```bash
python3 activity-17.1/retrieval.py
```

Run Activity 17.1 generation and conversation memory:

```bash
python3 activity-17.1/generate_answer.py
```

Run Activity 17.2:

```bash
python3 activity-17.2/benchmark.py
```

## Configuration

Activity 17.1 requires a `.env` file containing:

```env
MONGO_URI=your_mongodb_atlas_connection_string
VOYAGE_API_KEY=your_voyage_api_key
```

Do not commit `.env` or expose API credentials.

## Conclusion

Both activities demonstrate semantic retrieval and vector search.

Activity 17.1 implements a complete RAG workflow with conversation memory.

Activity 17.2 experimentally compares HNSW and IVF using FAISS, showing the trade-offs between index construction time, query latency, and recall.
