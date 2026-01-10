# eCommerce Visit Segmentation (Session Clustering)

This repository implements a **production-minded baseline** for clustering e-commerce
sessions into interpretable behavioral segments using visit-level features and K-Means.

---

## Project Overview

### What problem this solves
E-commerce teams often need to understand **types of sessions**, not just users:

- Which visits show purchase intent vs casual browsing?
- How does traffic quality vary by campaign or channel?
- How do session behaviors shift over time?

This project produces:
- A **visit-level feature table**
- Stable **session clusters**
- Artifacts suitable for analytics, experimentation, and monitoring

### Who this would be used by
- Growth & Marketing Analytics teams
- Product Analytics / Data Science
- UX & Merchandising teams

---

## System Architecture

**Ingestion → Feature Engineering → Modeling → Outputs**

1. **Ingestion**
   - Google Analytics–style session + hit tables in BigQuery
   - Time-windowed via `_TABLE_SUFFIX`

2. **Data & Feature Engineering**
   - Enforced **visit-level grain**
   - Hit-level aggregates computed separately, then joined
   - Rate-based features to reduce correlation

3. **Modeling**
   - Standardized numeric feature matrix
   - K-Means clustering
   - K selected via multiple diagnostics

4. **Outputs**
   - `session_clusters.parquet`
   - `cluster_centers.parquet`
   - `k_diagnostics.parquet`
   - `model_report.json`

---

## Modeling / Analytics

### Model used
- **K-Means**
  - Fast, interpretable, scalable baseline
  - Easy to retrain and operationalize

### Evaluation approach
Multiple diagnostics (no single metric is decisive):
- Inertia / SSD (elbow)
- Silhouette score
- Davies–Bouldin
- Calinski–Harabasz

Operational checks:
- Cluster size distribution
- Centroid sanity checks
- Temporal stability of cluster mix

---

## Orchestration & Infrastructure

### Current state
- Notebook-driven batch execution
- Artifacts written to disk / object storage

### Production path
- Scheduled batch job (Airflow / Prefect / Dagster)
- Feature SQL materialized in BigQuery
- Versioned artifacts in GCS/S3
- Monitoring:
  - Feature drift
  - Cluster mix drift
  - Conversion rate by cluster

---

## How to Run Locally

```bash
make install
make test
make smoke
