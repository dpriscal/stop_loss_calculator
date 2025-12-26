import pandas as pd
from starlette.testclient import TestClient

from app.infrastructure.adapters.fmp_price_data_repository import FmpPriceDataRepository


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


def test_macd_chart_endpoint_returns_png_image(testclient: TestClient, monkeypatch):
    """Test that MACD chart endpoint returns valid PNG image."""
    prices = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0]
    df = _make_weekly_df(prices)

    monkeypatch.setattr(
        FmpPriceDataRepository,
        "get_stock_data",
        lambda self, symbol, days: df,
    )

    r = testclient.get("/stocks/ABC/macd-chart?days=100&periodicity=W")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert isinstance(r.content, bytes)
    assert len(r.content) > 0
    # PNG files start with PNG signature
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_macd_chart_endpoint_uses_default_periodicity(
    testclient: TestClient, monkeypatch
):
    """Test that MACD chart endpoint uses default periodicity (W) when not specified."""
    prices = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0]
    df = _make_weekly_df(prices)

    monkeypatch.setattr(
        FmpPriceDataRepository,
        "get_stock_data",
        lambda self, symbol, days: df,
    )

    r = testclient.get("/stocks/ABC/macd-chart?days=100")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_macd_chart_endpoint_handles_different_periodicity(
    testclient: TestClient, monkeypatch
):
    """Test that MACD chart endpoint handles different periodicity values."""
    # Create daily data
    dates = pd.date_range("2020-01-01", periods=30, freq="D")
    df = pd.DataFrame(
        {
            "date": dates,
            "open": [100.0] * 30,
            "high": [105.0] * 30,
            "low": [95.0] * 30,
            "close": [100.0 + i * 0.1 for i in range(30)],
            "volume": [1000] * 30,
        }
    )

    monkeypatch.setattr(
        FmpPriceDataRepository,
        "get_stock_data",
        lambda self, symbol, days: df,
    )

    r = testclient.get("/stocks/ABC/macd-chart?days=100&periodicity=D")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_macd_chart_endpoint_returns_404_for_invalid_symbol(
    testclient: TestClient, monkeypatch
):
    """Test that MACD chart endpoint returns 404 for invalid symbol."""

    def raise_runtime_error(self, symbol, days):
        raise RuntimeError(f"No historical data returned for symbol '{symbol}'")

    monkeypatch.setattr(
        FmpPriceDataRepository,
        "get_stock_data",
        raise_runtime_error,
    )

    r = testclient.get("/stocks/INVALID/macd-chart?days=100")
    assert r.status_code == 404
