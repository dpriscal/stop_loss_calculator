from __future__ import annotations

import pandas as pd

from app.domain.repositories.macd_calculator import MacdCalculator  # noqa: F401


class EmaMacdCalculator:
    """Compute MACD as the difference between fast and slow EMAs on close.

    Defaults to fast=12, slow=26 periods using exponential weighted moving average.
    """

    def __init__(self, fast_period: int = 12, slow_period: int = 26) -> None:
        if fast_period <= 0 or slow_period <= 0:
            raise ValueError("EMA periods must be positive integers")
        if fast_period >= slow_period:
            raise ValueError("Fast period must be less than slow period")
        self.fast_period = fast_period
        self.slow_period = slow_period

    def get_macd(self, df: pd.DataFrame) -> pd.Series:  # type: ignore[override]
        """Return MACD series aligned to df's index.

        Expects a 'close' column in df. Uses pandas ewm with adjust=False.
        """
        if "close" not in df.columns:
            raise KeyError(
                "DataFrame must contain a 'close' column for MACD computation"
            )

        close = df["close"].astype(float)
        fast_ema = close.ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = close.ewm(span=self.slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        return macd
