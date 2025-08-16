import pandas as pd

from app.infrastructure.financialmodelingprep import Financialmodelingprep


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


def test_get_macd_minima_rows_returns_minima_list(monkeypatch):
    prices = [3, 2, 1, 1, 2, 3]
    df = _make_weekly_df(prices)

    f = Financialmodelingprep()

    # Avoid network; supply data and MACD directly
    monkeypatch.setattr(Financialmodelingprep, "getStockData", lambda self, s, d: df)
    monkeypatch.setattr(
        Financialmodelingprep,
        "getMacd",
        lambda self, x: pd.Series([3, 2, 1, 1, 2, 3], index=x.index),
    )

    rows = f.get_macd_minima_rows("SYM", days=100, periodicity="W", window=1)

    # Expect only the first index of the plateau kept
    assert isinstance(rows, list)
    assert len(rows) == 1
    assert rows[0]["symbol"] == "SYM"
    assert rows[0]["date"] == df.loc[2, "date"]
    assert rows[0]["macd"] == 1
    assert rows[0]["price"] == df.loc[2, "close"]
    assert rows[0]["period"] == "W"


def test_get_macd_minima_rows_is_sorted_by_date(monkeypatch):
    prices = [5, 4, 3, 4, 3, 4, 5]
    df = _make_weekly_df(prices)

    f = Financialmodelingprep()

    monkeypatch.setattr(Financialmodelingprep, "getStockData", lambda self, s, d: df)
    monkeypatch.setattr(
        Financialmodelingprep,
        "getMacd",
        lambda self, x: pd.Series([5, 4, 3, 4, 3, 4, 5], index=x.index),
    )

    rows = f.get_macd_minima_rows("ABC", days=100, periodicity="W", window=1)

    assert [r["date"] for r in rows] == [df.loc[2, "date"], df.loc[4, "date"]]
    assert [r["macd"] for r in rows] == [3, 3]
    assert [r["price"] for r in rows] == [df.loc[2, "close"], df.loc[4, "close"]]
    assert all(r["symbol"] == "ABC" for r in rows)
    assert all(r["period"] == "W" for r in rows)


