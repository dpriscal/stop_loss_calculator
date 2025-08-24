import numpy as np
import os
import pandas as pd
from starlette.testclient import TestClient

from app.infrastructure.financialmodelingprep import Financialmodelingprep
from app.infrastructure.adapters.fmp_price_data_repository import FmpPriceDataRepository


def test_root_endpoint_coerces_non_finite_stop_loss(testclient: TestClient, monkeypatch):
    # Force legacy path for this test
    os.environ["USE_LEGACY_STACK"] = "1"
    try:
        # Avoid API key and network
        monkeypatch.setattr(Financialmodelingprep, "__init__", lambda self: None)
        # Return a NaN stop_loss that should be coerced to null in JSON
        monkeypatch.setattr(
            Financialmodelingprep,
            "get_stop_loss_rows",
            lambda self, symbols: [
                {
                    "symbol": symbols[0],
                    "stop_loss": float("nan"),
                    "stop_loss_date": "2020-01-19T00:00:00",
                }
            ],
        )

        r = testclient.get("/stocks/FOO")
        assert r.status_code == 200
        data = r.json()
        assert data["symbol"] == "FOO"
        assert data["stop_loss"] is None
        assert data["stop_loss_date"] == "2020-01-19T00:00:00"
    finally:
        os.environ.pop("USE_LEGACY_STACK", None)


def test_macd_minima_endpoint_coerces_non_finite_fields(testclient: TestClient, monkeypatch):
    # DDD path: avoid network and inject non-finite values via domain service
    # Provide a minimal deterministic DataFrame through the repository
    dates = pd.date_range("2020-01-05", periods=3, freq="W")
    df = pd.DataFrame(
        {
            "date": dates,
            "open": [1, 2, 3],
            "high": [2, 3, 4],
            "low": [0, 1, 2],
            "close": [1, 2, 3],
            "volume": [100] * 3,
        }
    )
    monkeypatch.setattr(FmpPriceDataRepository, "get_stock_data", lambda self, symbol, days: df)

    # Monkeypatch use case's imported minima function to include NaN and Inf
    import app.application.use_cases.get_macd_minima as uc_mod

    def fake_get_macd_minima_from_macd(local_df, macd_series, window):
        out = pd.DataFrame(
            {
                "date": [dates[0], dates[1]],
                "price": [100.0, np.inf],
                "macd": [np.nan, 2.5],
            }
        )
        return out

    monkeypatch.setattr(uc_mod, "get_macd_minima_from_macd", fake_get_macd_minima_from_macd)

    r = testclient.get("/stocks/ABC/macd-minima?period=W&window=2&days=100")
    # Expect success and presence of both rows with nulls for non-finite values
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) == 2
    assert data[0]["symbol"] == "ABC" and data[0]["date"] == dates[0].isoformat()
    assert data[0]["macd"] is None and data[0]["price"] == 100.0
    assert data[1]["symbol"] == "ABC" and data[1]["date"] == dates[1].isoformat()
    assert data[1]["macd"] == 2.5 and data[1]["price"] is None


