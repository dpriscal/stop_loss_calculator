import math
import pandas as pd

from app.domain.services.local_minima import find_local_minima


def test_find_local_minima_simple_valley():
    s = pd.Series([3, 2, 1, 2, 3])
    idxs = find_local_minima(s, window=1)
    assert idxs == [2]


def test_find_local_minima_plateau_chooses_first_index():
    s = pd.Series([3, 2, 1, 1, 2, 3])
    idxs = find_local_minima(s, window=1)
    assert idxs == [2]


def test_find_local_minima_ignores_boundaries():
    # Boundaries (positions 0 and last) are not considered minima
    s = pd.Series([1, 2, 1])
    idxs = find_local_minima(s, window=1)
    assert idxs == []


def test_find_local_minima_with_nans():
    s = pd.Series([3, math.nan, 2, 1, 2, math.nan, 3])
    idxs = find_local_minima(s, window=1)
    assert idxs == [3]


def test_find_local_minima_multiple_minima_in_order():
    s = pd.Series([5, 4, 3, 4, 3, 4, 5])
    idxs = find_local_minima(s, window=1)
    assert idxs == [2, 4]


