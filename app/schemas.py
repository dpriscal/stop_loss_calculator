from __future__ import annotations

import math
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator


def _coerce_non_finite(value: Optional[float]) -> Optional[float]:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


class StopLossResponse(BaseModel):
    symbol: str
    stop_loss: Optional[float]
    stop_loss_date: Optional[datetime]

    @validator("stop_loss", pre=True)
    def _coerce_stop_loss(cls, v):
        return _coerce_non_finite(v)


class MacdMinimaRow(BaseModel):
    symbol: str
    date: datetime
    macd: Optional[float]
    price: Optional[float]
    period: str

    @validator("macd", "price", pre=True)
    def _coerce_non_finite_fields(cls, v):
        return _coerce_non_finite(v)
