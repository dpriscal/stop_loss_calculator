from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status

from app.application.use_cases.get_macd_chart import GetMacdChart
from app.domain.repositories import PriceDataRepository
from app.infrastructure.adapters.fmp_price_data_repository import FmpPriceDataRepository
from app.infrastructure.financialmodelingprep import Financialmodelingprep
from app.infrastructure.services.chart_plotter import ChartPlotter
from app.interface.settings import AppSettings, get_settings


def get_data_repository(
    settings: AppSettings = Depends(get_settings),
) -> PriceDataRepository:
    api_key = settings.FINANCIALMODELINGPREP_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="FINANCIALMODELINGPREP_API_KEY not configured",
        )
    try:
        return FmpPriceDataRepository(api_key=api_key)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


def get_stop_loss_strategy() -> Callable:
    def strategy(symbol, stock_df, periodicity, num_elements):
        f = Financialmodelingprep()
        return f.get_stop_loss(symbol, stock_df, False, periodicity, num_elements)

    return strategy


def get_chart_plotter() -> ChartPlotter:
    """Dependency provider for ChartPlotter service."""
    return ChartPlotter()


def get_macd_chart_use_case(
    repo: PriceDataRepository = Depends(get_data_repository),
    plotter: ChartPlotter = Depends(get_chart_plotter),
) -> GetMacdChart:
    """Dependency provider for GetMacdChart use case."""
    return GetMacdChart(repo=repo, plotter=plotter)
