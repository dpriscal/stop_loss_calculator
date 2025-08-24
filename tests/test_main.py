import os

import pandas as pd
from starlette.testclient import TestClient

from app.infrastructure.adapters.fmp_price_data_repository import FmpPriceDataRepository
from app.infrastructure.financialmodelingprep import Financialmodelingprep


def test_root_endpoint(testclient: TestClient, monkeypatch):
    # Force legacy path
    os.environ["USE_LEGACY_STACK"] = "1"
    try:
        r = testclient.get("/stocks/FB")
        assert r.status_code == 200
    finally:
        os.environ.pop("USE_LEGACY_STACK", None)


def test_root_endpoint_ddd_stack(testclient: TestClient, monkeypatch):
    os.environ["USE_DDD_STACK"] = "1"
    try:

        def _make_daily_df(
            values: list[float], start: str = "2020-01-01"
        ) -> pd.DataFrame:
            n = len(values)
            dates = pd.date_range(start, periods=n, freq="D")
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

        df_fb = _make_daily_df([10, 11, 12], start="2020-01-01")
        monkeypatch.setattr(
            FmpPriceDataRepository,
            "get_stock_data",
            lambda self, symbol, days: df_fb,
        )

        # Stub the underlying stop-loss policy to avoid MACD requirements
        monkeypatch.setattr(Financialmodelingprep, "__init__", lambda self: None)
        monkeypatch.setattr(
            Financialmodelingprep,
            "get_stop_loss",
            lambda self, symbol, stock_data, plotData, periodicity, num_elements: {
                "symbol": symbol,
                "current_price": float(stock_data.iloc[0].close),
                "stop_loss": 123.45,
                "stop_loss_date": stock_data.iloc[0].date,
                "max_macd_date": stock_data.iloc[0].date,
                "period": periodicity,
            },
        )

        r = testclient.get("/stocks/FB")
        assert r.status_code == 200
        data = r.json()
        assert data["symbol"] == "FB"
        assert "stop_loss" in data
        assert "stop_loss_date" in data
    finally:
        os.environ.pop("USE_DDD_STACK", None)
