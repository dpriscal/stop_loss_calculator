from __future__ import annotations

import io

import matplotlib.pyplot as plt
import pandas as pd


class ChartPlotter:
    """Service for generating MACD and price charts as PNG images."""

    def plot_macd_with_prices(
        self, symbol: str, df: pd.DataFrame, macd_series: pd.Series
    ) -> bytes:
        """Generate a chart with price and MACD panels, returning PNG bytes.

        Args:
            symbol: Stock symbol for the chart title
            df: DataFrame with columns: date, close, low (and optionally high, open, volume)
            macd_series: MACD series aligned with df's index

        Returns:
            PNG image bytes
        """
        dates = pd.to_datetime(df["date"])

        fig, (ax_price, ax_macd) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        self._plot_price_panel(ax_price, dates, df, symbol)
        self._plot_macd_panel(ax_macd, dates, macd_series)

        plt.xlabel("Date")
        plt.tight_layout()

        return self._save_to_bytes()

    def _plot_price_panel(
        self, ax: plt.Axes, dates: pd.Series, df: pd.DataFrame, symbol: str
    ) -> None:
        """Plot the price panel with close and low prices."""
        ax.plot(dates, df["close"], label="Close", color="#1f77b4")
        ax.plot(dates, df["low"], label="Low", color="#2ca02c", alpha=0.6)
        ax.set_title(f"{symbol} weekly MACD")
        ax.set_ylabel("Price")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")

    def _plot_macd_panel(
        self, ax: plt.Axes, dates: pd.Series, macd_series: pd.Series
    ) -> None:
        """Plot the MACD panel with MACD line and signal line."""
        ax.plot(dates, macd_series, label="MACD", color="#9467bd")
        try:
            signal = macd_series.ewm(span=9, adjust=False, min_periods=9).mean()
            ax.plot(dates, signal, label="Signal (9)", color="#ff7f0e")
        except Exception:
            pass
        ax.set_ylabel("MACD")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")

    def _save_to_bytes(self) -> bytes:
        """Save the current matplotlib figure to PNG bytes."""
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        return buf.read()

