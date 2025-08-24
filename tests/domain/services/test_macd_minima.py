import pandas as pd

from app.domain.services.local_minima import find_local_minima


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


def test_get_macd_minima_uses_minima_indices_and_maps_price():
    from app.domain.services.macd_minima import get_macd_minima_from_macd

    prices = [3, 2, 1, 1, 2, 3]
    df = _make_weekly_df(prices)

    # MACD series with plateau minimum at indices 2 and 3
    macd = pd.Series([3, 2, 1, 1, 2, 3], index=df.index)

    minima = get_macd_minima_from_macd(df, macd, window=1)

    assert list(minima["date"]) == [df.loc[2, "date"]]
    assert list(minima["macd"]) == [1]
    assert list(minima["price"]) == [df.loc[2, "close"]]


def test_get_macd_minima_sorted_by_date():
    from app.domain.services.macd_minima import get_macd_minima_from_macd

    prices = [5, 4, 3, 4, 3, 4, 5]
    df = _make_weekly_df(prices)

    macd = pd.Series([5, 4, 3, 4, 3, 4, 5], index=df.index)

    minima = get_macd_minima_from_macd(df, macd, window=1)

    assert list(minima["date"]) == [df.loc[2, "date"], df.loc[4, "date"]]
    assert list(minima["macd"]) == [3, 3]
    assert list(minima["price"]) == [df.loc[2, "close"], df.loc[4, "close"]]


