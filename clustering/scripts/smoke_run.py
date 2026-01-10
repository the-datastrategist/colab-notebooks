import json
from pathlib import Path
import numpy as np
import pandas as pd

from session_clustering.pipeline import (
    assert_unique_grain,
    preprocess_features,
    k_diagnostics,
)

def main():
    rng = np.random.default_rng(42)

    df = pd.DataFrame({
        "visit_id": [f"v{i}" for i in range(2000)],
        "pageviews": rng.poisson(6, 2000),
        "hits": rng.poisson(12, 2000),
        "unique_pages": rng.poisson(4, 2000),
        "time_on_site_sec": rng.gamma(2, 120, 2000),
        "transactions": rng.binomial(1, 0.05, 2000),
        "transaction_revenue": rng.gamma(2, 50000, 2000),
    })

    df["time_on_site_sec_per_pageview"] = df["time_on_site_sec"] / df["pageviews"].clip(lower=1)
    df["hits_per_pageview"] = df["hits"] / df["pageviews"].clip(lower=1)

    assert_unique_grain(df)

    FEATURES = [
        "pageviews",
        "hits",
        "unique_pages",
        "time_on_site_sec",
        "time_on_site_sec_per_pageview",
        "hits_per_pageview",
        "transactions",
        "transaction_revenue",
    ]

    X, _ = preprocess_features(df, FEATURES)
    diag = k_diagnostics(X)

    Path("artifacts").mkdir(exist_ok=True)
    diag.to_parquet("artifacts/k_diagnostics.parquet")

    Path("artifacts/report.json").write_text(
        json.dumps({"ok": True, "n_sessions": len(df)}, indent=2)
    )

if __name__ == "__main__":
    main()
