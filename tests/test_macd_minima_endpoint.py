from starlette.testclient import TestClient
import os
import pandas as pd

from app.infrastructure.financialmodelingprep import Financialmodelingprep
from app.infrastructure.adapters.fmp_price_data_repository import FmpPriceDataRepository


def test_macd_minima_endpoint_returns_rows(testclient: TestClient, monkeypatch):
    # Bypass API key and network: no-op __init__ and mock service method
    monkeypatch.setattr(Financialmodelingprep, "__init__", lambda self: None)
    monkeypatch.setattr(
        Financialmodelingprep,
        "get_macd_minima_rows",
        lambda self, symbol, days, periodicity, window: [
            {
                "symbol": symbol,
                "date": "2020-01-19T00:00:00",
                "macd": 3.0,
                "price": 100.0,
                "period": periodicity,
            },
            {
                "symbol": symbol,
                "date": "2020-02-02T00:00:00",
                "macd": 2.5,
                "price": 105.0,
                "period": periodicity,
            },
        ],
    )

    r = testclient.get("/stocks/ABC/macd-minima?period=W&window=2&days=100")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert data[0]["symbol"] == "ABC"
    assert data[0]["date"] == "2020-01-19T00:00:00"
    assert data[0]["macd"] == 3.0
    assert data[0]["price"] == 100.0
    assert data[0]["period"] == "W"


def test_macd_minima_endpoint_returns_rows_ddd_stack(testclient: TestClient, monkeypatch):
    os.environ["USE_DDD_STACK"] = "1"
    try:
        # Provide deterministic data via repository to avoid network
        def _make_weekly_df(values: list[float]) -> pd.DataFrame:
            n = len(values)
            dates = pd.date_range("2020-01-05", periods=n, freq="W")
            df = pd.DataFrame(
                {
                    "date": dates,
                    "open": values,
                    "high": [v + 1 for v in values],
                    "low": [max(0.0, v - 1) for v in values],
                    "close": values,
                    "volume": [1000] * n,
                }
            )
            return df

        prices = [5, 4, 3, 4, 3, 4, 5]
        df = _make_weekly_df(prices)

        monkeypatch.setattr(
            FmpPriceDataRepository,
            "get_stock_data",
            lambda self, symbol, days: df,
        )

        r = testclient.get("/stocks/ABC/macd-minima?period=W&window=2&days=100")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert data[0]["symbol"] == "ABC"
        assert data[0]["date"] == "2020-01-19T00:00:00"
        assert data[0]["macd"] == 3.0
        assert data[0]["price"] == df.loc[2, "close"]
        assert data[0]["period"] == "W"
    finally:
        os.environ.pop("USE_DDD_STACK", None)

