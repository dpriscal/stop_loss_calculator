import argparse
import os
import sys
from pathlib import Path

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.qa_plot_macd_minima import plot_macd_with_minima
from scripts.qa_plot_stop_loss import plot_stop_loss


def main():
    parser = argparse.ArgumentParser(description="Batch QA plots for multiple symbols")
    parser.add_argument(
        "--symbols",
        type=str,
        default="AAPL,MSFT,AMZN,GOOGL,META,TSLA,NVDA,JPM,BAC,NFLX",
        help="Comma-separated list of tickers",
    )
    parser.add_argument(
        "--days", type=int, default=3650, help="Days of history to fetch"
    )
    parser.add_argument(
        "--period", default="W", help="Resampling period for stop loss plot"
    )
    parser.add_argument(
        "--window", type=int, default=1, help="Local-minima window size"
    )
    parser.add_argument(
        "--outdir", default="plots", help="Directory to save PNG outputs"
    )
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]

    for sym in symbols:
        macd_path = outdir / f"{sym.lower()}_macd_minima_w{args.window}.png"
        stop_path = outdir / f"{sym.lower()}_stop_loss.png"

        try:
            p1 = plot_macd_with_minima(sym, args.days, args.window, str(macd_path))
            print(f"Saved: {p1}")
        except Exception as e:
            print(f"Failed macd minima for {sym}: {e}")

        try:
            p2 = plot_stop_loss(sym, args.days, args.period, 20, str(stop_path))
            print(f"Saved: {p2}")
        except Exception as e:
            print(f"Failed stop loss for {sym}: {e}")


if __name__ == "__main__":
    main()
