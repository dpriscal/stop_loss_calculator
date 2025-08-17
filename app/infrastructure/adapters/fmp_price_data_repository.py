from __future__ import annotations

from typing import Optional

import pandas as pd
import requests

from app.domain.repositories import PriceDataRepository


class FmpPriceDataRepository(PriceDataRepository):
    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise RuntimeError("FINANCIALMODELINGPREP_API_KEY is not set")
        self._api_key = api_key

    def get_stock_data(self, symbol: str, days: int) -> pd.DataFrame:
        r = requests.get(
            f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?timeseries={days}&apikey={self._api_key}"
        )
        data = r.json()["historical"]
        return pd.DataFrame(data)


