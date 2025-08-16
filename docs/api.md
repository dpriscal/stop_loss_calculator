# Api

This document describes the HTTP endpoints exposed by the service.

## Base url

- Local (docker): `http://127.0.0.1:8000`

## Authentication

- Set the `FINANCIALMODELINGPREP_API_KEY` environment variable (or provide it via `.env`).

## Endpoints

### Get stop loss for a symbol

- Method: `GET`
- Path: `/stocks/{symbol}`
- Path params:
  - `symbol` (string): the ticker, e.g., `AAPL`
- Response body (200):
```json
{
  "symbol": "AAPL",
  "stop_loss": 137.12,
  "stop_loss_date": "2020-06-01T00:00:00"
}
```

### Get macd minima for a symbol

- Method: `GET`
- Path: `/stocks/{symbol}/macd-minima`
- Path params:
  - `symbol` (string): the ticker, e.g., `AAPL`
- Query params:
  - `period` (string, default `W`): aggregation period. Supported: `D` (daily), `W` (weekly), `M` (monthly)
  - `window` (integer, default `1`): local-minima neighborhood size used to detect minima (higher filters more)
  - `days` (integer, default `3650`): number of historical days to fetch
- Response body (200): list of minima ordered by date.
```json
[
  {
    "symbol": "AAPL",
    "date": "2020-01-19T00:00:00",
    "macd": 1.23,
    "price": 78.15,
    "period": "W"
  },
  {
    "symbol": "AAPL",
    "date": "2020-02-02T00:00:00",
    "macd": 0.98,
    "price": 80.55,
    "period": "W"
  }
]
```

## Notes

- Responses use ISO 8601 for dates.
- MACD is computed as `EMA(12) - EMA(26)` on the resampled close series; a 9-period EMA is the signal line (used in QA plots).

