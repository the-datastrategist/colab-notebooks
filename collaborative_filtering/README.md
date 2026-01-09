# Memory-Based Collaborative Filtering (MovieLens) — Production-Minded Notebook

This repo contains a **memory-based collaborative filtering** prototype that builds a user–item interaction matrix from MovieLens ratings and computes **item–item similarity** for fast, explainable recommendations.

> Reviewer note: The goal here is to show *systems + reasoning* (data model, scalability constraints, and productionization path), not a “toy recommender”.

---

## Project Overview

### What problem this solves
- Given historical user ratings/interactions, generate **personalized recommendations**:
  - “Users who liked what you liked also liked…”
  - “Items similar to this item…”
- Intended use cases in a real organization:
  - **Consumer products**: content feeds (video/music/articles), marketplaces, e-commerce, gaming item stores
  - **Internal tooling**: merchandising, editorial curation support, personalized notifications

### Why it matters
- Provides a **strong baseline** that is:
  - **Fast to compute** and easy to explain
  - Useful when labeled outcomes are scarce (no explicit conversion labels)
  - A practical “first model” before moving to embeddings / deep models

---

## System Architecture

### High-level flow (ingestion → processing → modeling → outputs)
1. **Ingestion**
   - Source: `ratings.csv` (MovieLens 25M format: `userId, movieId, rating, timestamp`)
   - In production: events arrive from app telemetry (Kafka/PubSub) into a data lake/warehouse

2. **Processing**
   - Data validation + type normalization
   - Feature construction:
     - explicit `rating`
     - optional implicit signal: `liked` (rating > user mean)
     - optional normalized signal: `wt_rating` (rating / user mean)

3. **Modeling**
   - Build **sparse** user–item matrix (CSR)
   - Compute **Top-K item neighbors** using cosine distance (NearestNeighbors)
   - (Optional) user–user similarity is supported but *not recommended at scale* (O(U²))

4. **Outputs**
   - `item_neighbors.parquet` (movie_id → [(neighbor_id, similarity)] top-K)
   - `user_item_matrix.npz` (sparse interactions)
   - These artifacts can be served from:
     - a feature store / object storage (GCS/S3)
     - a low-latency retrieval service (Redis, vector index, ANN service)

### Technologies used and why
- **Pandas**: ingest + quick EDA
- **SciPy CSR sparse matrices**: memory-efficient representation for large interaction data
- **scikit-learn NearestNeighbors (cosine)**: practical Top-K similarity without building a dense N×N matrix
- **(Optional) google-cloud-storage**: artifact upload to GCS

---

## Data & Feature Engineering

### Data sources
- MovieLens-style `ratings.csv`:
  - `userId`: integer
  - `movieId`: integer
  - `rating`: float (typically 0.5–5.0)
  - `timestamp`: unix epoch seconds

### Key transformations / feature logic
- `event_ts` = `pd.to_datetime(timestamp, unit="s")`
- **User-mean normalization**:
  - `avg_rating_user` = mean(rating) per user
  - `wt_rating` = rating / avg_rating_user  
    - Why: reduces user-specific scale bias (some users rate high/low)
- **Implicit preference flag**:
  - `liked` = rating > avg_rating_user  
    - Why: enables “implicit CF” style training from explicit ratings

### Assumptions and limitations
- Assumes user taste is stationary over the window (no temporal decay by default)
- Cold-start is not solved (new users/items need fallback strategies)
- MovieLens has clean IDs; production systems need robust ID mapping + de-dupe

---

## Modeling / Analytics

### Models used and why
- **Item–item collaborative filtering** with cosine similarity.
  - Output is interpretable (“similar because co-consumed by similar users”)
  - Scales better than user–user similarity (items typically smaller than users)

### Evaluation approach and metrics
- Notebook includes a **time-aware split** (leave-last-interaction-per-user):
  - Train on earlier interactions
  - Test on held-out last item per user
- Metrics:
  - **HitRate@K** (did we recommend the held-out item?)
  - **Precision@K** (optional for multi-item holdout)

### Known weaknesses / failure modes
- Popularity bias (blockbusters dominate) → mitigate via:
  - similarity shrinkage / co-occurrence thresholds
  - re-ranking with diversity / novelty constraints
- Sparse users (few interactions) → fallback to popularity / content-based

---

## Orchestration & Infrastructure (Production Path)

What exists in this repo:
- A notebook that can run end-to-end and write artifacts locally (and optionally upload to GCS).

What a real deployment would add:
- **Batch pipeline** (daily/hourly):
  - Orchestrator: Airflow / Prefect / Dagster
  - Compute: Spark / BigQuery / Ray (depending on scale)
  - Artifact versioning: timestamped paths + metadata table
- **Serving**:
  - Precompute Top-K neighbors for each item
  - Online layer ranks candidates for a user using recent interactions
  - Store neighbors in Redis/BigTable; or ANN index if using embeddings
- **Monitoring**:
  - Data drift: interaction volume, item/user churn, rating distribution shifts
  - Model health: coverage, latency, hitrate proxy, diversity metrics

---

## How to Run Locally

### 1) Create environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Minimal dependencies used by the notebook:
- pandas
- numpy
- scipy
- scikit-learn
- pyarrow (for parquet)
- (optional) google-cloud-storage

### 2) Provide data
Set the path to your ratings file:
- Local: `DATA_PATH=./data/ratings.csv`
- GCS:   `DATA_PATH=gs://<bucket>/<path>/ratings.csv`

### 3) Run the notebook
Open and run:
- `tds_memory_collaborative_filtering_01_load_matrix.ipynb`

---

## Design Tradeoffs & Future Improvements

### Key tradeoffs
- **Dense pivot vs sparse matrix**:
  - Dense pivot is simplest but explodes memory at scale  
  - Sparse CSR is production-appropriate and enables Top-K retrieval
- **Full similarity matrix vs Top-K neighbors**:
  - Full N×N is expensive and usually unnecessary for serving
  - Top-K neighbors are sufficient for candidate generation

### Improvements with more time
- Add:
  - popularity + cold-start fallback
  - temporal decay and session-based boosts
  - offline evaluation suite (Recall@K, MAP@K, coverage, novelty/diversity)
  - artifact registry + metadata tables (e.g., BigQuery model_runs)
- Scale path:
  - compute neighbors with Spark ALS or approximate neighbors
  - use embeddings (two-tower / item2vec) and ANN retrieval for large catalogs

---

## Repo Contents
- `tds_memory_collaborative_filtering_01_load_matrix.ipynb` — end-to-end CF baseline + Top-K neighbor generation
