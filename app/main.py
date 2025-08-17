import os
from fastapi import FastAPI
from typing import List

from app.infrastructure.financialmodelingprep import Financialmodelingprep
from app.schemas import StopLossResponse, MacdMinimaRow
from app.infrastructure.adapters.fmp_price_data_repository import FmpPriceDataRepository
from app.application.use_cases.get_macd_minima import get_macd_minima as uc_get_macd_minima
from app.application.use_cases.get_stop_loss import get_stop_loss as uc_get_stop_loss

api = FastAPI()


@api.get("/stocks/{symbol}", response_model=StopLossResponse)
async def root(symbol: str):
    if os.environ.get("USE_DDD_STACK") == "1":
        repo = FmpPriceDataRepository()

        def strategy(sym, stock_df, periodicity, num_elements):
            # Reuse existing policy implementation for now
            f = Financialmodelingprep()
            return f.get_stop_loss(sym, stock_df, False, periodicity, num_elements)

        rows = uc_get_stop_loss(
            repo,
            symbols=[symbol],
            periodicity="MS",
            num_elements=10,
            strategy=strategy,
        )
        first = rows[0] if rows else {"stop_loss": None, "stop_loss_date": None}
        return StopLossResponse(
            symbol=symbol,
            stop_loss=first.get("stop_loss"),
            stop_loss_date=first.get("stop_loss_date"),
        )
    else:
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
    if os.environ.get("USE_DDD_STACK") == "1":
        repo = FmpPriceDataRepository()
        rows = uc_get_macd_minima(repo, symbol=symbol, days=days, periodicity=period, window=window)
        return [MacdMinimaRow(**r) for r in rows]
    else:
        f = Financialmodelingprep()
        rows = f.get_macd_minima_rows(symbol, days=days, periodicity=period, window=window)
        return [MacdMinimaRow(**r) for r in rows]
