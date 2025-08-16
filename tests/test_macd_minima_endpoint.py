from starlette.testclient import TestClient

from app.infrastructure.financialmodelingprep import Financialmodelingprep


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


