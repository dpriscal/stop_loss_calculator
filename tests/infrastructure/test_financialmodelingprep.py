import pandas as pd

from app.infrastructure.financialmodelingprep import Financialmodelingprep


class TestFinancialmodelingprep:
    def test_findTheLowest(self):
        f = Financialmodelingprep()

        data = {"low": [1, 2, 3, 1]}
        df = pd.DataFrame(data)
        index = 3
        num_elements = 2
        lowest_index = f.findTheLowest(df["low"], index, num_elements)
        assert df["low"][lowest_index] == 1

        data = {"low": [1, 2, 3, 5]}
        df = pd.DataFrame(data)
        index = 2
        num_elements = 4
        lowest_index = f.findTheLowest(df["low"], index, num_elements)
        assert df["low"][lowest_index] == 1

        data = {"low": [5, 3, 2, 1]}
        df = pd.DataFrame(data)
        index = 2
        num_elements = 4
        lowest_index = f.findTheLowest(df["low"], index, num_elements)
        assert df["low"][lowest_index] == 2


def test_get_stop_loss_rows(monkeypatch):
    f = Financialmodelingprep()

    # Avoid network dependency in tests; provide deterministic DataFrame
    import pandas as pd
    df_fb = pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=10, freq="D"),
            "open": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            "high": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            "low": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            "close": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            "volume": [1000] * 10,
        }
    )
    df_fvrr = pd.DataFrame(
        {
            "date": pd.date_range("2020-02-01", periods=10, freq="D"),
            "open": [20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
            "high": [21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
            "low": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28],
            "close": [20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
            "volume": [1000] * 10,
        }
    )

    def fake_get_stock_data(self, sym, days):
        return df_fb if sym == "FB" else df_fvrr

    monkeypatch.setattr(Financialmodelingprep, "getStockData", fake_get_stock_data)

    # Also bypass heavy stop-loss calculation to make test deterministic
    def fake_get_stop_loss(self, symbol, stock_data, plotData, periodicity, num_elements):
        return {
            "symbol": symbol,
            "current_price": float(stock_data.iloc[0].close),
            "stop_loss": 123.45 if symbol == "FB" else 17.89,
            "stop_loss_date": stock_data.iloc[0].date,
            "max_macd_date": stock_data.iloc[0].date,
            "period": periodicity,
        }

    monkeypatch.setattr(Financialmodelingprep, "get_stop_loss", fake_get_stop_loss)

    rows = f.get_stop_loss_rows(["FB"])
    assert rows[0]["symbol"] == "FB"
    assert rows[0]["stop_loss"] == 123.45

    rows = f.get_stop_loss_rows(["FVRR"])
    assert rows[0]["symbol"] == "FVRR"
    assert rows[0]["stop_loss"] == 17.89
