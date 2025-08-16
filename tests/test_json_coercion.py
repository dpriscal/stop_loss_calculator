import numpy as np
from starlette.testclient import TestClient

from app.infrastructure.financialmodelingprep import Financialmodelingprep


def test_root_endpoint_coerces_non_finite_stop_loss(testclient: TestClient, monkeypatch):
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


def test_macd_minima_endpoint_coerces_non_finite_fields(testclient: TestClient, monkeypatch):
    # Avoid API key and network
    monkeypatch.setattr(Financialmodelingprep, "__init__", lambda self: None)
    # Return rows with NaN/Inf that should be present with null fields
    monkeypatch.setattr(
        Financialmodelingprep,
        "get_macd_minima_rows",
        lambda self, symbol, days, periodicity, window: [
            {
                "symbol": symbol,
                "date": "2020-01-19T00:00:00",
                "macd": np.nan,
                "price": 100.0,
                "period": periodicity,
            },
            {
                "symbol": symbol,
                "date": "2020-02-02T00:00:00",
                "macd": 2.5,
                "price": np.inf,
                "period": periodicity,
            },
        ],
    )

    r = testclient.get("/stocks/ABC/macd-minima?period=W&window=2&days=100")
    # Expect success and presence of both rows with nulls for non-finite values
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) == 2
    assert data[0]["symbol"] == "ABC" and data[0]["date"] == "2020-01-19T00:00:00"
    assert data[0]["macd"] is None and data[0]["price"] == 100.0
    assert data[1]["symbol"] == "ABC" and data[1]["date"] == "2020-02-02T00:00:00"
    assert data[1]["macd"] == 2.5 and data[1]["price"] is None


