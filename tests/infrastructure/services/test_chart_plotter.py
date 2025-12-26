import pandas as pd
import pytest

from app.infrastructure.services.chart_plotter import ChartPlotter


@pytest.fixture
def sample_price_data():
    """Create sample price data for testing."""
    dates = pd.date_range("2020-01-01", periods=20, freq="W")
    return pd.DataFrame(
        {
            "date": dates,
            "open": [100.0] * 20,
            "high": [105.0] * 20,
            "low": [95.0] * 20,
            "close": [100.0 + i * 0.5 for i in range(20)],
            "volume": [1000] * 20,
        }
    )


@pytest.fixture
def sample_macd_series(sample_price_data):
    """Create sample MACD series aligned with price data."""
    return pd.Series([0.1 + i * 0.05 for i in range(20)], index=sample_price_data.index)


def test_chart_plotter_plot_macd_with_prices_returns_bytes(
    sample_price_data, sample_macd_series
):
    """Test that ChartPlotter returns valid PNG bytes."""
    plotter = ChartPlotter()
    symbol = "AAPL"

    result = plotter.plot_macd_with_prices(
        symbol, sample_price_data, sample_macd_series
    )

    assert isinstance(result, bytes)
    assert len(result) > 0
    # PNG files start with PNG signature
    assert result[:8] == b"\x89PNG\r\n\x1a\n"


def test_chart_plotter_plot_macd_with_prices_handles_empty_data():
    """Test that ChartPlotter handles empty data gracefully."""
    plotter = ChartPlotter()
    symbol = "AAPL"
    empty_df = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
    empty_series = pd.Series(dtype=float)

    result = plotter.plot_macd_with_prices(symbol, empty_df, empty_series)

    assert isinstance(result, bytes)
    assert len(result) > 0


def test_chart_plotter_plot_macd_with_prices_handles_missing_signal_line(
    sample_price_data, sample_macd_series
):
    """Test that ChartPlotter handles cases where signal line cannot be computed."""
    plotter = ChartPlotter()
    symbol = "AAPL"
    # Use very short series that might not have enough data for signal line
    short_df = sample_price_data.head(5)
    short_macd = sample_macd_series.head(5)

    result = plotter.plot_macd_with_prices(symbol, short_df, short_macd)

    assert isinstance(result, bytes)
    assert len(result) > 0
    assert result[:8] == b"\x89PNG\r\n\x1a\n"
