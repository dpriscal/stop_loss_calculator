import logging
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status

from app.application.use_cases.get_macd_minima import (
    get_macd_minima as uc_get_macd_minima,
)
from app.application.use_cases.get_stop_loss import get_stop_loss as uc_get_stop_loss
from app.interface.deps import get_data_repository, get_stop_loss_strategy
from app.schemas import MacdMinimaRow, StopLossResponse

logger = logging.getLogger(__name__)

api = FastAPI()


@api.get("/stocks/{symbol}", response_model=StopLossResponse)
async def get_stop_loss_endpoint(
    symbol: str,
    data_repository=Depends(get_data_repository),
    strategy=Depends(get_stop_loss_strategy),
):
    """
    Retrieve stop loss information for a given stock symbol.
    """
    rows = uc_get_stop_loss(
        data_repository,
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
async def get_macd_minima_endpoint(
    symbol: str,
    period: str = "W",
    window: int = 1,
    days: int = 3650,
    data_repository=Depends(get_data_repository),
):
    """
    Retrieve MACD minima rows for a given stock symbol.
    """
    rows = uc_get_macd_minima(
        data_repository, symbol=symbol, days=days, periodicity=period, window=window
    )
    return [MacdMinimaRow(**r) for r in rows]
