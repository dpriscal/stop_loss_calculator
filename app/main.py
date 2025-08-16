from fastapi import FastAPI

from app.infrastructure.financialmodelingprep import Financialmodelingprep

api = FastAPI()


@api.get("/stocks/{symbol}")
async def root(symbol: str):
    f = Financialmodelingprep()
    rows = f.get_stop_loss_rows([symbol])
    return {
        "symbol": symbol,
        "stop_loss": rows[0]["stop_loss"],
        "stop_loss_date": rows[0]["stop_loss_date"],
    }


@api.get("/stocks/{symbol}/macd-minima")
async def macd_minima(symbol: str, period: str = "W", window: int = 1, days: int = 3650):
    f = Financialmodelingprep()
    rows = f.get_macd_minima_rows(symbol, days=days, periodicity=period, window=window)
    # Ensure JSON-serializable values
    out = []
    for r in rows:
        out.append(
            {
                "symbol": r["symbol"],
                "date": r["date"].isoformat() if hasattr(r["date"], "isoformat") else str(r["date"]),
                "macd": float(r["macd"]),
                "price": float(r["price"]),
                "period": r["period"],
            }
        )
    return out
