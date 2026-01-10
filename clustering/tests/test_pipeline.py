import pandas as pd
import pytest
from session_clustering.pipeline import assert_unique_grain

def test_assert_unique_grain_raises():
    df = pd.DataFrame({"visit_id": ["a", "a"]})
    with pytest.raises(ValueError):
        assert_unique_grain(df)
