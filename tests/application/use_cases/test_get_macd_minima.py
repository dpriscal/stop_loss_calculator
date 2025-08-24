import pandas as pd


class FakeRepo:
    def __init__(self, df):
        self._df = df

    def get_stock_data(self, symbol: str, days: int) -> pd.DataFrame:  # type: ignore[name-defined]
        return self._df


def _make_weekly_df(values: list[float]) -> pd.DataFrame:  # type: ignore[name-defined]
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


def test_use_case_returns_rows_in_order_with_expected_fields():
    from app.application.use_cases.get_macd_minima import get_macd_minima

    prices = [5, 4, 3, 4, 3, 4, 5]
    df = _make_weekly_df(prices)

    repo = FakeRepo(df)
    rows = get_macd_minima(repo, symbol="ABC", days=100, periodicity="W", window=1)

    assert [r["date"] for r in rows] == [df.loc[2, "date"], df.loc[4, "date"]]
    assert [r["macd"] for r in rows] == [3, 3]
    assert [r["price"] for r in rows] == [df.loc[2, "close"], df.loc[4, "close"]]
    assert all(r["symbol"] == "ABC" and r["period"] == "W" for r in rows)
