import pandas as pd

from app.application.use_cases.get_macd_minima import get_macd_minima
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


def test_get_macd_minima_rows_returns_minima_list(monkeypatch):
    prices = [3, 2, 1, 1, 2, 3]
    df = _make_weekly_df(prices)

    # Avoid network; supply repo data directly
    monkeypatch.setattr(
        FmpPriceDataRepository,
        "get_stock_data",
        lambda self, s, d: df,
    )
    rows = get_macd_minima(FmpPriceDataRepository(api_key="dummy"), symbol="SYM", days=100, periodicity="W", window=1)

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

    monkeypatch.setattr(FmpPriceDataRepository, "get_stock_data", lambda self, s, d: df)
    rows = get_macd_minima(FmpPriceDataRepository(api_key="dummy"), symbol="ABC", days=100, periodicity="W", window=1)

    assert [r["date"] for r in rows] == [df.loc[2, "date"], df.loc[4, "date"]]
    assert [r["macd"] for r in rows] == [3, 3]
    assert [r["price"] for r in rows] == [df.loc[2, "close"], df.loc[4, "close"]]
    assert all(r["symbol"] == "ABC" for r in rows)
    assert all(r["period"] == "W" for r in rows)


def _make_daily_df(values: list[float], start: str = "2020-01-01") -> pd.DataFrame:
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


def test_get_macd_minima_rows_daily_period(monkeypatch):
    prices = [5, 4, 3, 4, 3, 4, 5]
    df = _make_daily_df(prices, start="2020-01-01")

    monkeypatch.setattr(FmpPriceDataRepository, "get_stock_data", lambda self, s, d: df)
    rows = get_macd_minima(FmpPriceDataRepository(api_key="dummy"), symbol="DLY", days=100, periodicity="D", window=1)

    assert [r["date"] for r in rows] == [df.loc[2, "date"], df.loc[4, "date"]]
    assert [r["macd"] for r in rows] == [3, 3]
    assert [r["price"] for r in rows] == [df.loc[2, "close"], df.loc[4, "close"]]
    assert all(r["period"] == "D" for r in rows)


def _make_daily_over_months(month_end_values: list[float]) -> pd.DataFrame:
    # Build daily df from first to last month end, setting month-end closes
    month_ends = pd.date_range("2020-01-31", periods=len(month_end_values), freq="M")
    start = (month_ends[0] - pd.offsets.MonthBegin(1)).date().isoformat()
    end = month_ends[-1].date().isoformat()
    all_days = pd.date_range(start, end, freq="D")
    # Start with zeros
    close = pd.Series([1.0] * len(all_days), index=all_days)
    for me, val in zip(month_ends, month_end_values):
        close.loc[me] = val
    df = pd.DataFrame(
        {
            "date": close.index,
            "open": close.values,
            "high": close.values + 1,
            "low": (close.values - 1).clip(min=0.0),
            "close": close.values,
            "volume": [1000] * len(close),
        }
    )
    return df


def test_get_macd_minima_rows_monthly_period(monkeypatch):
    # Month-end macd values shape; minima at index 2 only
    month_end_vals = [5, 4, 3, 4, 5]
    df = _make_daily_over_months(month_end_vals)

    monkeypatch.setattr(FmpPriceDataRepository, "get_stock_data", lambda self, s, d: df)
    rows = get_macd_minima(FmpPriceDataRepository(api_key="dummy"), symbol="MON", days=1000, periodicity="M", window=1)

    # Expect single minimum at the third month
    # Resampling will set the date to month-end
    expected_date = pd.date_range("2020-01-31", periods=len(month_end_vals), freq="M")[2]
    assert len(rows) == 1
    assert rows[0]["date"] == expected_date
    assert rows[0]["macd"] == 3
    assert rows[0]["period"] == "M"


