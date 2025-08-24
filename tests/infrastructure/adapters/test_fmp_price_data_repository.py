import pandas as pd
import pytest


class DummyResponse:
    """
    A minimal mock of requests.Response for testing.
    Allows setting status_code and raising for status, and returns a payload via .json().
    """
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception(f"HTTP {self.status_code}")


def test_get_stock_data(monkeypatch):
    from app.infrastructure.adapters.fmp_price_data_repository import (
        FmpPriceDataRepository,
    )

    # Fake payload matching FMP shape
    payload = {
        "historical": [
            {
                "date": "2020-01-02",
                "open": 10.0,
                "high": 11.0,
                "low": 9.0,
                "close": 10.5,
                "volume": 1000,
            },
            {
                "date": "2020-01-01",
                "open": 9.0,
                "high": 10.0,
                "low": 8.0,
                "close": 9.5,
                "volume": 900,
            },
        ]
    }

    def fake_get(url, params=None, timeout=None):
        return DummyResponse(payload)

    import requests

    monkeypatch.setattr(requests, "get", fake_get)

    repo = FmpPriceDataRepository(api_key="dummy")
    df = repo.get_stock_data("FB", days=2)

    assert isinstance(df, pd.DataFrame)
    assert set(["date", "open", "high", "low", "close", "volume"]) <= set(df.columns)
    assert len(df) == 2

