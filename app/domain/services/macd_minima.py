from __future__ import annotations

import pandas as pd

from .local_minima import find_local_minima


# Ensure the 'date' column in the DataFrame is of datetime type.
def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if not pd.api.types.is_datetime64_any_dtype(df.get("date")):
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
    return df


def _select_indices(df: pd.DataFrame, indices: list[int]) -> pd.DataFrame:
    """
    Select rows from the DataFrame at the specified indices and return a new DataFrame
    with columns 'date' and 'price' (renamed from 'close').

    Args:
        df (pd.DataFrame): The input DataFrame containing at least 'date' and 'close' columns.
        indices (list[int]): List of integer indices to select from the DataFrame.

    Returns:
        pd.DataFrame: A DataFrame with selected rows, columns 'date' and 'price'.
    """
    # Select the rows at the given indices and only keep 'date' and 'close' columns
    out = df.iloc[indices][["date", "close"]].copy()
    # Rename 'close' column to 'price' for output consistency
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
