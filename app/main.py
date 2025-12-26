import logging
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import Response

from app.application.use_cases.get_macd_minima import (
    get_macd_minima as uc_get_macd_minima,
)
from app.application.use_cases.get_stop_loss import get_stop_loss as uc_get_stop_loss
from app.interface.deps import (
    get_data_repository,
    get_macd_chart_use_case,
    get_stop_loss_strategy,
)
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


@api.get("/stocks/{symbol}/macd-chart")
async def get_macd_chart_endpoint(
    symbol: str,
    days: int,
    periodicity: str = "W",
    use_case=Depends(get_macd_chart_use_case),
):
    """
    Retrieve a chart image showing stock prices and MACD for the last N days.

    Returns a PNG image with two panels:
    - Top panel: Stock prices (close and low)
    - Bottom panel: MACD indicator with signal line
    """
    try:
        image_bytes = use_case.execute(
            symbol=symbol, days=days, periodicity=periodicity
        )
        return Response(content=image_bytes, media_type="image/png")
    except RuntimeError as exc:
        # Handle cases where symbol is invalid or data is unavailable
        error_msg = str(exc)
        if "No historical data" in error_msg or "symbol" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg
        )
