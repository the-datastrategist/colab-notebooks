# Sample Data Science & ML Systems

This repository contains **production-minded data science systems** built on publicly available data.
The focus is on **correct data modeling, scalable architectures, and defensible tradeoffs**, not
toy notebooks or algorithm demos.

Each project demonstrates how exploratory analysis evolves into **batchable, monitorable, and
extensible systems** suitable for real organizations.

---

## Project 1: Memory-Based Collaborative Filtering
**Notebook:** `tds_memory_collaborative_filtering_01_load_matrix.ipynb`

### Problem
Generate personalized recommendations from historical user–item interactions in settings where:
- labeled outcomes are sparse
- interpretability matters
- latency and simplicity are priorities

This is a common baseline for marketplaces, media platforms, gaming catalogs, and e-commerce.

### System Design
**Ingestion → Feature Engineering → Similarity Computation → Artifacts**

- Input: MovieLens-style ratings (`userId`, `movieId`, `rating`, `timestamp`)
- Core representation: **sparse user–item matrix (CSR)**
  - avoids dense pivots that do not scale
- Modeling approach:
  - **item–item collaborative filtering**
  - cosine similarity
  - **Top-K neighbors only** (no full N×N similarity matrix)

### Why these choices
- Item–item CF scales better than user–user as user count grows
- Sparse matrices reduce memory and enable efficient retrieval
- Top-K neighbors are sufficient for candidate generation in production
- Results are explainable (“similar due to shared consumption patterns”)

### Evaluation & Limitations
- Offline ranking checks (e.g., HitRate@K)
- Known failure modes:
  - cold start users/items
  - popularity bias
  - static preferences (no temporal decay)

### Production Path
- Batch retraining (daily/hourly)
- Store artifacts:
  - sparse interaction matrix
  - item → top-K neighbors
- Serve via:
  - cache / feature store
  - downstream ranking or re-ranking layer
- Natural extension to embeddings or hybrid systems

---

## Project 2: E-commerce Session Clustering
**Notebook:** `tds_session_clustering.ipynb`

### Problem
Segment **visits (sessions)** into interpretable behavioral types to understand:
- traffic quality
- purchase intent
- behavioral drift over time

The unit of analysis is the **session**, not the user.

### System Design
**Warehouse → Visit-Level Feature Table → Clustering → Artifacts**

- Data source: Google Analytics demo data (Google Merchandise Store)
- Critical constraint: **strict visit-level grain**
  - hit/page data aggregated before joins
  - explicit uniqueness checks to prevent metric inflation

### Feature Engineering
- Engagement: pageviews, time on site
- Navigation depth: unique pages, hits
- Commerce: transactions, revenue
- Rate features (per-pageview) used to:
  - reduce correlation
  - stabilize clustering geometry
- Outlier control via winsorization before scaling

### Modeling
- **K-Means** on standardized numeric features
- K selected using multiple diagnostics:
  - inertia (SSD)
  - silhouette
  - Davies–Bouldin
  - Calinski–Harabasz

This is a **baseline by design**: fast, interpretable, and operationally simple.

### Evaluation & Limitations
- Emphasis on:
  - cluster size balance
  - centroid sanity
  - temporal stability
- Known limitations:
  - assumes roughly spherical clusters
  - sensitive to feature scaling
  - no cross-session user context

### Production Path
- Scheduled batch execution
- Persist artifacts:
  - session → cluster labels
  - cluster centroids (original units)
  - diagnostics + run metadata
- Monitor:
  - cluster mix drift
  - conversion rate by cluster
  - feature distribution shifts

---

## Shared Design Principles

Across both projects:

- **Correct data grain is enforced**, not assumed
- Prefer **simple, interpretable baselines** with clear failure modes
- Separate:
  - extraction
  - feature engineering
  - modeling
  - artifact generation
- Outputs are **artifact-shaped**, not just plots
- Clear upgrade paths to:
  - orchestration (Airflow / Prefect)
  - feature stores
  - online serving
  - advanced models

These projects are meant to demonstrate how data science work fits into a
**real ML/analytics lifecycle**, not just how to train a model.

---

## Notes on Data
- All datasets are public and anonymized.
- No PII or user-identifiable data is used.
