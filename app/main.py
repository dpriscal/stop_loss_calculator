from fastapi import FastAPI
from typing import List

from app.infrastructure.financialmodelingprep import Financialmodelingprep
from app.schemas import StopLossResponse, MacdMinimaRow

api = FastAPI()


@api.get("/stocks/{symbol}", response_model=StopLossResponse)
async def root(symbol: str):
    f = Financialmodelingprep()
    rows = f.get_stop_loss_rows([symbol])
    first = rows[0] if rows else {"stop_loss": None, "stop_loss_date": None}
    return StopLossResponse(
        symbol=symbol,
        stop_loss=first.get("stop_loss"),
        stop_loss_date=first.get("stop_loss_date"),
    )


@api.get("/stocks/{symbol}/macd-minima", response_model=List[MacdMinimaRow])
async def macd_minima(symbol: str, period: str = "W", window: int = 1, days: int = 3650):
    f = Financialmodelingprep()
    rows = f.get_macd_minima_rows(symbol, days=days, periodicity=period, window=window)
    return [MacdMinimaRow(**r) for r in rows]
