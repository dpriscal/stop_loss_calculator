from __future__ import annotations

import pandas as pd

from app.domain.repositories import PriceDataRepository
from app.domain.services.ema_macd_calculator import EmaMacdCalculator
from app.infrastructure.services.chart_plotter import ChartPlotter


class GetMacdChart:
    """Application use case to generate MACD and price chart as PNG bytes."""

    def __init__(
        self,
        repo: PriceDataRepository,
        plotter: ChartPlotter,
    ) -> None:
        """Initialize the use case with required dependencies.

        Args:
            repo: Repository for fetching stock price data
            plotter: Service for generating charts
        """
        self._repo = repo
        self._plotter = plotter

    def execute(
        self,
        symbol: str,
        days: int,
        periodicity: str = "W",
    ) -> bytes:
        """Execute the use case to generate MACD and price chart.

        Fetches data via repository, resamples according to periodicity, computes MACD,
        and generates a chart with price and MACD panels.

        Args:
            symbol: Stock symbol
            days: Number of historical days to fetch
            periodicity: Resampling period (e.g., 'W' for weekly, 'D' for daily)

        Returns:
            PNG image bytes
        """
        stock_data     = self._repo.get_stock_data(symbol, days)
        stock_data     = self._ensure_datetime_index(stock_data).reset_index(drop=True)
        resampled_data = self._resample(stock_data, periodicity)

        macd_series = EmaMacdCalculator().get_macd(resampled_data)

        return self._plotter.plot_macd_with_prices(symbol, resampled_data, macd_series)

    def _ensure_datetime_index(self, stock_data: pd.DataFrame) -> pd.DataFrame:
        """Ensure the date column is datetime type."""
        if not pd.api.types.is_datetime64_any_dtype(stock_data.get("date")):
            stock_data = stock_data.copy()
            stock_data["date"] = pd.to_datetime(stock_data["date"])  # type: ignore[arg-type]
        return stock_data

    def _resample(self, stock_data: pd.DataFrame, periodicity: str) -> pd.DataFrame:
        """Resample DataFrame according to the specified periodicity."""
        aggregation_logic = {
            "open":   "first",
            "high":   "max",
            "low":    "min",
            "close":  "last",
            "volume": "sum",
        }
        resampled_data = (
            stock_data.set_index("date")
            .resample(periodicity)
            .apply(aggregation_logic)
        )
        resampled_data["date"] = resampled_data.index
        resampled_data.index   = range(1, len(resampled_data) + 1)
        return resampled_data

