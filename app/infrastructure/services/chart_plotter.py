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

        # Price panel
        ax_price.plot(dates, df["close"], label="Close", color="#1f77b4")
        ax_price.plot(dates, df["low"], label="Low", color="#2ca02c", alpha=0.6)
        ax_price.set_title(f"{symbol} weekly MACD")
        ax_price.set_ylabel("Price")
        ax_price.grid(True, alpha=0.3)
        ax_price.legend(loc="best")

        # MACD panel
        ax_macd.plot(dates, macd_series, label="MACD", color="#9467bd")
        try:
            signal = macd_series.ewm(span=9, adjust=False, min_periods=9).mean()
            ax_macd.plot(dates, signal, label="Signal (9)", color="#ff7f0e")
        except Exception:
            pass
        ax_macd.set_ylabel("MACD")
        ax_macd.grid(True, alpha=0.3)
        ax_macd.legend(loc="best")

        plt.xlabel("Date")
        plt.tight_layout()

        # Save to bytes buffer instead of file
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        return buf.read()

