import argparse
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Ensure project root is importable when running in Docker or locally
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.infrastructure.financialmodelingprep import Financialmodelingprep


def plot_stop_loss(symbol: str, days: int, period: str, num_elements: int, output: str) -> str:
    f = Financialmodelingprep()

    # Fetch raw historical data and compute stop loss using existing logic
    df_raw = f.getStockData(symbol, days)
    result = f.get_stop_loss(symbol, df_raw, plotData=False, periodicity=period, num_elements=num_elements)

    stop_loss_price = float(result["stop_loss"])
    stop_loss_date = pd.to_datetime(result["stop_loss_date"])  # in case it's not already
    max_macd_date = pd.to_datetime(result["max_macd_date"])  # context on where MACD max was

    # Build weekly data for plotting (chronological)
    df_weekly = f.resample(df_raw.copy(), period)
    macd = f.getMacd(df_weekly)

    dates = pd.to_datetime(df_weekly["date"])  # ensure datetime

    Path(os.path.dirname(output)).mkdir(parents=True, exist_ok=True)

    fig, (ax_price, ax_macd) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Price panel
    ax_price.plot(dates, df_weekly["close"], label="Close", color="#1f77b4")
    ax_price.plot(dates, df_weekly["low"], label="Low", color="#2ca02c", alpha=0.6)
    ax_price.axhline(stop_loss_price, color="#d62728", linestyle="--", linewidth=1.5, label="Stop loss")
    ax_price.axvline(stop_loss_date, color="#d62728", linestyle=":", linewidth=1.0, alpha=0.8)
    ax_price.set_title(f"{symbol} {period} stop loss")
    ax_price.set_ylabel("Price")
    ax_price.grid(True, alpha=0.3)
    ax_price.legend(loc="best")

    # MACD panel
    ax_macd.plot(dates, macd, label="MACD", color="#9467bd")
    try:
        signal = f.getExp(macd, 9)
        ax_macd.plot(dates, signal, label="Signal (9)", color="#ff7f0e")
    except Exception:
        pass
    ax_macd.axvline(max_macd_date, color="#8c564b", linestyle=":", linewidth=1.0, alpha=0.8, label="Max MACD")
    ax_macd.axvline(stop_loss_date, color="#d62728", linestyle=":", linewidth=1.0, alpha=0.8, label="Stop loss date")
    ax_macd.set_ylabel("MACD")
    ax_macd.grid(True, alpha=0.3)
    ax_macd.legend(loc="best")

    plt.xlabel("Date")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()

    return output


def main():
    parser = argparse.ArgumentParser(description="QA plot: Stop loss for a symbol")
    parser.add_argument("--symbol", required=True, help="Ticker symbol, e.g., AAPL")
    parser.add_argument("--days", type=int, default=3650, help="Days of history to fetch")
    parser.add_argument("--period", default="W", help="Resampling period, e.g., W for weekly")
    parser.add_argument("--num-elements", type=int, default=20, dest="num_elements", help="Neighborhood elements for lowest search")
    parser.add_argument("--output", default="plots/stop_loss.png", help="Path to save the PNG plot")
    args = parser.parse_args()

    out_path = plot_stop_loss(args.symbol, args.days, args.period, args.num_elements, args.output)
    print(f"Saved plot to: {out_path}")


if __name__ == "__main__":
    main()


