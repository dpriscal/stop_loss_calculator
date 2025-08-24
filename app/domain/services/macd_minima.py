from __future__ import annotations

import pandas as pd

from .local_minima import find_local_minima


def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if not pd.api.types.is_datetime64_any_dtype(df.get("date")):
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])  # type: ignore[arg-type]
    return df


def _select_indices(df: pd.DataFrame, indices: list[int]) -> pd.DataFrame:
    out = df.iloc[indices][["date", "close"]].copy()
    out.rename(columns={"close": "price"}, inplace=True)
    return out


def get_macd_minima_from_macd(
    df: pd.DataFrame,
    macd: pd.Series,
    window: int = 1,
) -> pd.DataFrame:
    """Return a DataFrame of minima rows with columns: date, macd, price.

    The function expects one MACD value per row of ``df``. It finds local minima
    indices on the MACD series using ``window`` and maps those indices back to
    dates and closing prices from ``df``. The resulting rows are sorted by date.
    """
    df_local = _ensure_datetime_index(df.copy()).reset_index(drop=True)

    minima_indices = find_local_minima(macd.reset_index(drop=True), window=window)
    selected = _select_indices(df_local, minima_indices)
    selected["macd"] = macd.reset_index(drop=True).iloc[minima_indices].values
    selected = selected.sort_values(by="date").reset_index(drop=True)
    return selected


