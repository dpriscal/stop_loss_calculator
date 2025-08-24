from __future__ import annotations

from typing import Protocol

import pandas as pd


class MacdCalculator(Protocol):
    """Protocol for computing MACD (or similar indicator) over a DataFrame."""

    def get_macd(self, df: pd.DataFrame) -> pd.Series:  # pragma: no cover - interface
        ...
