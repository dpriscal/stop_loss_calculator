import pandas as pd
import pytest


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):  # mimic requests.Response.json()
        return self._payload


def test_get_stock_data(monkeypatch):
    from app.infrastructure.adapters.fmp_price_data_repository import FmpPriceDataRepository

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

    def fake_get(url):
        return DummyResponse(payload)

    import requests

    monkeypatch.setattr(requests, "get", fake_get)

    repo = FmpPriceDataRepository(api_key="dummy")
    df = repo.get_stock_data("FB", days=2)

    assert isinstance(df, pd.DataFrame)
    assert set(["date", "open", "high", "low", "close", "volume"]) <= set(df.columns)
    assert len(df) == 2


