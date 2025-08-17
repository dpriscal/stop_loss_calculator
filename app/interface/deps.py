from __future__ import annotations

from typing import Callable

from app.domain.repositories import PriceDataRepository
from app.infrastructure.adapters.fmp_price_data_repository import FmpPriceDataRepository
from app.infrastructure.financialmodelingprep import Financialmodelingprep


def get_repo() -> PriceDataRepository:
    return FmpPriceDataRepository()


def get_stop_loss_strategy() -> Callable:
    def strategy(symbol, stock_df, periodicity, num_elements):
        f = Financialmodelingprep()
        return f.get_stop_loss(symbol, stock_df, False, periodicity, num_elements)

    return strategy


