from __future__ import annotations

import numpy as np
import pandas as pd


def find_local_minima(series: pd.Series, window: int = 1) -> list[int]:
    """Return 0-based indices of local minima within a sliding neighborhood of size `window`.

    Rules:
    - Only consider interior points (exclude first and last index).
    - A point is a local minimum if it is <= all non-NaN neighbors within `window`
      AND strictly < at least one neighbor (to avoid selecting flat-only regions).
    - For flat plateaus that qualify as minima, return only the first index in the plateau.
    - NaNs are ignored in comparisons; if all neighbors are NaN, the point is not selected.
    """
    if series is None or len(series) < 3:
        return []

    values = series.to_numpy()
    n = len(values)
    minima_indices: list[int] = []

    for i in range(1, n - 1):
        center = values[i]
        if np.isnan(center):
            continue

        start = max(0, i - window)
        end = min(n - 1, i + window)

        neighbor_idxs = [j for j in range(start, end + 1) if j != i]
        neighbor_vals = [values[j] for j in neighbor_idxs if not np.isnan(values[j])]

        if len(neighbor_vals) == 0:
            continue

        is_not_greater_than_any = all(center <= v for v in neighbor_vals)
        is_strictly_less_than_some = any(center < v for v in neighbor_vals)

        if is_not_greater_than_any and is_strictly_less_than_some:
            minima_indices.append(i)

    deduped: list[int] = []
    for idx in minima_indices:
        if len(deduped) == 0:
            deduped.append(idx)
            continue
        prev = deduped[-1]
        if idx == prev + 1 and values[idx] == values[prev]:
            continue
        deduped.append(idx)

    return deduped
