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
