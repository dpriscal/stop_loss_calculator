# Qa for macd minima

Use this guide to generate MACD plots annotated with detected minima for visual verification.

## Prerequisites

- Set `FINANCIALMODELINGPREP_API_KEY` in your shell or `.env`.
- Build the development Docker image:
```shell
docker build --target development -t stop_loss_calculator:dev .
```

## Generate a plot

- Create a local output folder and run the QA script for a symbol (example: AAPL, ~10yr history, window=1):
```shell
mkdir -p plots

docker run --rm -t \
  -w /stop_loss_calculator \
  -e FINANCIALMODELINGPREP_API_KEY=${FINANCIALMODELINGPREP_API_KEY} \
  -v $(pwd)/plots:/stop_loss_calculator/plots \
  stop_loss_calculator:dev \
  python scripts/qa_plot_macd_minima.py \
    --symbol AAPL \
    --days 3650 \
    --window 1 \
    --output plots/aapl_macd_minima.png
```

- For a more conservative minima selection (larger neighborhood), try a wider window, e.g. `window=20`:
```shell
docker run --rm -t \
  -w /stop_loss_calculator \
  -e FINANCIALMODELINGPREP_API_KEY=${FINANCIALMODELINGPREP_API_KEY} \
  -v $(pwd)/plots:/stop_loss_calculator/plots \
  stop_loss_calculator:dev \
  python scripts/qa_plot_macd_minima.py \
    --symbol AAPL \
    --days 3650 \
    --window 20 \
    --output plots/aapl_macd_minima_w20.png
```

The generated PNG files will appear in the local `plots/` directory.
