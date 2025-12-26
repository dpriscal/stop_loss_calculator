import pandas as pd

from app.infrastructure.services.chart_plotter import ChartPlotter


class FakeRepo:
    def __init__(self, df):
        self._df = df

    def get_stock_data(self, symbol: str, days: int) -> pd.DataFrame:
        return self._df


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


def test_get_macd_chart_returns_png_bytes():
    """Test that GetMacdChart use case returns valid PNG bytes."""
    from app.application.use_cases.get_macd_chart import GetMacdChart

    prices = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0]
    df = _make_weekly_df(prices)

    repo = FakeRepo(df)
    plotter = ChartPlotter()
    use_case = GetMacdChart(repo, plotter)

    result = use_case.execute(symbol="ABC", days=100, periodicity="W")

    assert isinstance(result, bytes)
    assert len(result) > 0
    # PNG files start with PNG signature
    assert result[:8] == b"\x89PNG\r\n\x1a\n"


def test_get_macd_chart_handles_empty_data():
    """Test that GetMacdChart handles empty data gracefully."""
    from app.application.use_cases.get_macd_chart import GetMacdChart

    empty_df = pd.DataFrame(
        columns=["date", "open", "high", "low", "close", "volume"]
    )

    repo = FakeRepo(empty_df)
    plotter = ChartPlotter()
    use_case = GetMacdChart(repo, plotter)

    result = use_case.execute(symbol="ABC", days=100, periodicity="W")

    assert isinstance(result, bytes)
    assert len(result) > 0


def test_get_macd_chart_uses_correct_periodicity():
    """Test that GetMacdChart respects periodicity parameter."""
    from app.application.use_cases.get_macd_chart import GetMacdChart

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

    repo = FakeRepo(df)
    plotter = ChartPlotter()
    use_case = GetMacdChart(repo, plotter)

    # Request weekly resampling
    result = use_case.execute(symbol="ABC", days=100, periodicity="W")

    assert isinstance(result, bytes)
    assert len(result) > 0
    assert result[:8] == b"\x89PNG\r\n\x1a\n"

