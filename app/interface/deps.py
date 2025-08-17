from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status

from app.domain.repositories import PriceDataRepository
from app.infrastructure.adapters.fmp_price_data_repository import FmpPriceDataRepository
from app.infrastructure.financialmodelingprep import Financialmodelingprep
from app.interface.settings import get_settings, AppSettings


def get_repo(settings: AppSettings = Depends(get_settings)) -> PriceDataRepository:
    api_key = settings.FINANCIALMODELINGPREP_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="FINANCIALMODELINGPREP_API_KEY not configured",
        )
    return FmpPriceDataRepository(api_key=api_key)


def get_stop_loss_strategy() -> Callable:
    def strategy(symbol, stock_df, periodicity, num_elements):
        f = Financialmodelingprep()
        return f.get_stop_loss(symbol, stock_df, False, periodicity, num_elements)

    return strategy


