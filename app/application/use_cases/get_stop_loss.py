from __future__ import annotations

from typing import Callable, Dict, List

import pandas as pd

from app.domain.repositories import PriceDataRepository


def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if not pd.api.types.is_datetime64_any_dtype(df.get("date")):
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])  # type: ignore[arg-type]
    return df


def get_stop_loss(
    repo: PriceDataRepository,
    symbols: List[str],
    periodicity: str = "W",
    num_elements: int = 20,
    strategy: Callable[[str, pd.DataFrame, str, int], Dict] | None = None,
    days: int = 3650,
) -> List[Dict]:
    """Application use case to compute stop-loss rows for a list of symbols.

    A strategy callable must be provided to encapsulate the stop-loss policy.
    The callable receives: (symbol, stock_data, periodicity, num_elements)
    and returns a mapping containing at least keys: stop_loss, stop_loss_date,
    max_macd_date.
    """
    if strategy is None:
        raise ValueError("strategy callable must be provided")

    results: List[Dict] = []
    for symbol in symbols:
        df = repo.get_stock_data(symbol, days)
        df = _ensure_datetime_index(df)
        current_price = float(df.iloc[0].close)

        data = strategy(symbol, df, periodicity, num_elements)

        results.append(
            {
                "symbol": symbol,
                "current_price": current_price,
                "stop_loss": data.get("stop_loss"),
                "stop_loss_date": data.get("stop_loss_date"),
                "max_macd_date": data.get("max_macd_date"),
                "period": periodicity,
            }
        )

    return results
