from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class PriceDataRepository(ABC):
    """Port for obtaining price time series data.

    Adapters (e.g., Financial Modeling Prep) should implement this.
    """

    @abstractmethod
    def get_stock_data(self, symbol: str, days: int) -> pd.DataFrame:  # pragma: no cover - interface
        """Return a DataFrame of OHLCV rows for the given symbol.

        Expected columns include: date, open, high, low, close, volume.
        """
        raise NotImplementedError


