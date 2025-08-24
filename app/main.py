import os
from typing import List

from fastapi import Depends, FastAPI

from app.application.use_cases.get_macd_minima import \
    get_macd_minima as uc_get_macd_minima
from app.application.use_cases.get_stop_loss import get_stop_loss as uc_get_stop_loss
from app.infrastructure.adapters.fmp_price_data_repository import FmpPriceDataRepository
from app.infrastructure.financialmodelingprep import Financialmodelingprep
from app.interface.deps import get_repo, get_stop_loss_strategy
from app.schemas import MacdMinimaRow, StopLossResponse

api = FastAPI()


@api.get("/stocks/{symbol}", response_model=StopLossResponse)
async def root(
    symbol: str,
    repo=Depends(get_repo),
    strategy=Depends(get_stop_loss_strategy),
):
    if os.environ.get("USE_LEGACY_STACK") == "1":
        f = Financialmodelingprep()
        rows = f.get_stop_loss_rows([symbol])
        first = rows[0] if rows else {"stop_loss": None, "stop_loss_date": None}
        return StopLossResponse(
            symbol=symbol,
            stop_loss=first.get("stop_loss"),
            stop_loss_date=first.get("stop_loss_date"),
        )
    # Default: DDD path
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


@api.get("/stocks/{symbol}/macd-minima", response_model=List[MacdMinimaRow])
async def macd_minima(
    symbol: str,
    period: str = "W",
    window: int = 1,
    days: int = 3650,
    repo=Depends(get_repo),
):
    if os.environ.get("USE_LEGACY_STACK") == "1":
        f = Financialmodelingprep()
        rows = f.get_macd_minima_rows(symbol, days=days, periodicity=period, window=window)
        return [MacdMinimaRow(**r) for r in rows]
    # Default: DDD path
    rows = uc_get_macd_minima(repo, symbol=symbol, days=days, periodicity=period, window=window)
    return [MacdMinimaRow(**r) for r in rows]
