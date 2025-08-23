from __future__ import annotations

from typing import Optional

import pandas as pd
import requests
from requests import Response, RequestException

from app.domain.repositories import PriceDataRepository


class FmpPriceDataRepository(PriceDataRepository):
    BASE_URL = "https://financialmodelingprep.com/api/v3/historical-price-full"

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("FINANCIALMODELINGPREP_API_KEY is not set")
        self._api_key = api_key

    def get_stock_data(self, symbol: str, days: int) -> pd.DataFrame:
        url = f"{self.BASE_URL}/{symbol}"
        params = {
            "timeseries": days,
            "apikey": self._api_key,
        }
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
        except RequestException as exc:
            raise RuntimeError(f"FMP request failed: {exc}")

        try:
            payload = response.json()
        except ValueError as exc:
            raise RuntimeError(f"FMP invalid JSON: {exc}")

        historical = payload.get("historical")
        if historical is None:
            # Common when key is invalid or rate-limited; surface concise detail
            msg = payload if isinstance(payload, str) else str(payload)[:200]
            raise RuntimeError(f"FMP response missing 'historical': {msg}")

        df = pd.DataFrame(historical)
        if df.empty:
            raise RuntimeError(f"No historical data returned for symbol '{symbol}'")
        return df

