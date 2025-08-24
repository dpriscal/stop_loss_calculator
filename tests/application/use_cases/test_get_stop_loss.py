import pandas as pd


class FakeRepo:
    def __init__(self, mapping):
        self._mapping = mapping

    def get_stock_data(self, symbol: str, days: int) -> pd.DataFrame:  # type: ignore[name-defined]
        return self._mapping[symbol]


def _make_daily_df(values: list[float], start: str = "2020-01-01") -> pd.DataFrame:  # type: ignore[name-defined]
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


def test_use_case_get_stop_loss_with_strategy_callable():
    from app.application.use_cases.get_stop_loss import get_stop_loss

    df_fb = _make_daily_df([10, 11, 12], start="2020-01-01")
    df_abc = _make_daily_df([20, 21, 22], start="2020-02-01")

    repo = FakeRepo({"FB": df_fb, "ABC": df_abc})

    def fake_strategy(symbol, stock_data, periodicity, num_elements):
        return {
            "stop_loss": 123.45 if symbol == "FB" else 67.89,
            "stop_loss_date": stock_data.iloc[0].date,
            "max_macd_date": stock_data.iloc[0].date,
        }

    rows = get_stop_loss(
        repo,
        symbols=["FB", "ABC"],
        periodicity="W",
        num_elements=10,
        strategy=fake_strategy,
    )

    assert rows[0]["symbol"] == "FB"
    assert rows[0]["current_price"] == float(df_fb.iloc[0].close)
    assert rows[0]["stop_loss"] == 123.45
    assert rows[0]["period"] == "W"

    assert rows[1]["symbol"] == "ABC"
    assert rows[1]["current_price"] == float(df_abc.iloc[0].close)
    assert rows[1]["stop_loss"] == 67.89
    assert rows[1]["period"] == "W"
