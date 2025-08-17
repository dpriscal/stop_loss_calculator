from __future__ import annotations

from typing import Iterable, List, Dict

import pandas as pd

from app.domain.repositories import PriceDataRepository
from app.domain.services.macd_minima import get_macd_minima_from_macd


def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if not pd.api.types.is_datetime64_any_dtype(df.get("date")):
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])  # type: ignore[arg-type]
    return df


def _resample(df: pd.DataFrame, periodicity: str) -> pd.DataFrame:
    logic = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    df_local = df.set_index("date").resample(periodicity).apply(logic)
    df_local["date"] = df_local.index
    df_local.index = range(1, len(df_local) + 1)
    return df_local


def get_macd_minima(
    repo: PriceDataRepository,
    symbol: str,
    days: int,
    periodicity: str = "W",
    window: int = 1,
) -> List[Dict]:
    """Application use case to compute MACD minima rows for a symbol.

    Fetches data via repository, computes a MACD-like series, delegates minima
    detection to the domain service, and returns a list of dict rows.

    Note: For test-driven simplicity, we set MACD to the close series. This can
    later be replaced with a pluggable MACD calculator.
    """
    df = repo.get_stock_data(symbol, days)
    df = _ensure_datetime_index(df).reset_index(drop=True)
    df_resampled = _resample(df, periodicity)

    macd_series = df_resampled["close"]
    minima_df = get_macd_minima_from_macd(df_resampled, macd_series, window=window)

    rows: List[Dict] = []
    for _, row in minima_df.iterrows():
        rows.append(
            {
                "symbol": symbol,
                "date": row["date"],
                "macd": float(row["macd"]) if row.get("macd") is not None else None,
                "price": float(row["price"]) if row.get("price") is not None else None,
                "period": periodicity,
            }
        )

    return rows


