import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
)

def assert_unique_grain(df: pd.DataFrame, key: str = "visit_id") -> None:
    if df[key].duplicated().any():
        raise ValueError("visit_id is not unique — aggregation/join error")

def preprocess_features(
    df: pd.DataFrame,
    features: list[str],
    z_clip: float = 5.0,
):
    X = df[features].fillna(0)

    mu = X.mean()
    sigma = X.std().replace(0, np.nan)
    z = (X - mu) / sigma

    X = X.clip(mu - z_clip * sigma, mu + z_clip * sigma, axis=1)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, scaler

def k_diagnostics(X, k_min=2, k_max=12, seed=42) -> pd.DataFrame:
    rows = []
    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, n_init="auto", random_state=seed)
        labels = km.fit_predict(X)
        rows.append({
            "k": k,
            "silhouette": silhouette_score(X, labels),
            "davies_bouldin": davies_bouldin_score(X, labels),
            "calinski_harabasz": calinski_harabasz_score(X, labels),
        })
    return pd.DataFrame(rows)

