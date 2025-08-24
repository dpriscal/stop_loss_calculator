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

from app.infrastructure.financialmodelingprep import (
    Financialmodelingprep,
    find_local_minima,
)


def plot_macd_with_minima(symbol: str, days: int, window: int, output: str) -> str:
    f = Financialmodelingprep()

    df = f.getStockData(symbol, days)
    df_weekly = f.resample(df, "W")
    macd = f.getMacd(df_weekly)

    minima_indices = find_local_minima(macd, window=window)

    dates = df_weekly["date"]
    macd_vals = macd

    Path(os.path.dirname(output)).mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 6))
    plt.plot(dates, macd_vals, label="MACD", color="#1f77b4")

    # Optional signal line for context
    try:
        signal = f.getExp(macd_vals, 9)
        plt.plot(dates, signal, label="Signal (9)", color="#ff7f0e")
    except Exception:
        pass

    if minima_indices:
        plt.scatter(
            dates.iloc[minima_indices],
            macd_vals.iloc[minima_indices],
            color="#d62728",
            marker="v",
            s=60,
            label="Minima",
            zorder=3,
        )

        # Annotate with price
        for i in minima_indices:
            date_i = dates.iloc[i]
            macd_i = macd_vals.iloc[i]
            price_i = df_weekly.iloc[i]["close"]
            plt.annotate(
                f"{price_i:.2f}",
                (date_i, macd_i),
                textcoords="offset points",
                xytext=(0, -12),
                ha="center",
                fontsize=8,
                color="#d62728",
            )

    plt.title(f"{symbol} weekly MACD with minima")
    plt.xlabel("Date")
    plt.ylabel("MACD")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output)
    plt.close()

    return output


def main():
    parser = argparse.ArgumentParser(description="QA plot: MACD minima for a symbol")
    parser.add_argument("--symbol", required=True, help="Ticker symbol, e.g., AAPL")
    parser.add_argument(
        "--days", type=int, default=3650, help="Days of history to fetch"
    )
    parser.add_argument(
        "--window", type=int, default=1, help="Local minima window size"
    )
    parser.add_argument(
        "--output",
        default="plots/macd_minima.png",
        help="Path to save the PNG plot",
    )
    args = parser.parse_args()

    out_path = plot_macd_with_minima(args.symbol, args.days, args.window, args.output)
    print(f"Saved plot to: {out_path}")


if __name__ == "__main__":
    main()
