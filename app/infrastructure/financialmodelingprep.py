import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import requests
from dotenv import dotenv_values


class Financialmodelingprep:
    def __init__(self):
        config = dotenv_values(".env")
        key_from_env = os.environ.get("FINANCIALMODELINGPREP_API_KEY")
        financial_api_key = key_from_env or config.get("FINANCIALMODELINGPREP_API_KEY")
        if not financial_api_key:
            raise RuntimeError("FINANCIALMODELINGPREP_API_KEY is not set in env or .env")

        self.financial_api_key = financial_api_key

    def get_stop_loss_rows(self, symbols):
        rows = []

        for symbol in symbols:
            try:
                days = 365 * 10
                df = self.getStockData(symbol, days)
                rows.append(self.get_stop_loss(symbol, df, False, "MS", 10))
                return rows
            except Exception as e:
                print("Problem with: " + symbol)
                print(e)

    def get_stop_loss(
        self, symbol, stock_data, plotData=False, periodicity="W", num_elements=20
    ):
        current_price = stock_data.iloc[0].close
        df = self.resample(stock_data, periodicity)
        macd = self.getMacd(df)

        df = df.reindex(index=df.index[::-1])
        macd = macd.reindex(index=macd.index[::-1])

        if plotData:
            self.plotStockData(df, symbol)
            self.plotMacd(df, macd)

        # max_macd_value = max(macd)
        max_macd_index = macd.idxmax()
        index = self.findTheLowest(macd, max_macd_index, 5)
        index = self.findTheLowest(df["low"], index, num_elements)

        return {
            "symbol": symbol,
            "current_price": current_price,
            "stop_loss": df["low"][index],
            "stop_loss_date": df["date"][index],
            "max_macd_date": df["date"][max_macd_index],
            "period": periodicity,
        }

    def resample(self, df, periodicity):
        df["date"] = pd.to_datetime(df["date"])
        logic = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
        df = df.set_index("date")
        df = df.resample(periodicity).apply(logic)
        df["date"] = df.index
        df.index = range(1, len(df) + 1)
        return df

    def getStockData(self, symbol, days):
        r = requests.get(
            f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?timeseries={days}&apikey={self.financial_api_key}"
        )
        r = r.json()
        stockdata = r["historical"]
        return pd.DataFrame(stockdata)

    def plotStockData(self, df, symbol):
        plt.plot(df.date, df.close, label=symbol)
        plt.show()

    def plotMacd(self, df, macd):
        exp9 = self.getExp(macd, 9)
        plt.plot(df.date, macd, label="MACD", color="#EBD2BE")
        plt.plot(df.date, exp9, label="Signal Line")
        plt.legend(loc="upper left")
        plt.show()

    def getMacd(self, df):
        exp12 = self.getExp(df.close, 12)
        exp26 = self.getExp(df.close, 26)
        return exp12 - exp26

    def getExp(self, df, periods):
        return df.ewm(span=periods, adjust=False, min_periods=periods).mean()

    def findTheLowest(self, df, index, num_elements):
        if index == 0:
            return index

        while index > 0:
            if self.isTheLower(df, index, num_elements):
                return index
            index = index - 1
        return index

    def isTheLower(self, df, index, num_elements):
        if index == 1:
            return df[index] < df[index - 1]
        rang = range(1, min(index, num_elements))
        for i in rang:
            if not (df[index] < df[index - i]) and not pd.isna(df[index - i]):
                return False
        return True

    # get_macd_minima removed in favor of application/domain use cases

    # get_macd_minima_rows removed; use application use case instead


def find_local_minima(series: pd.Series, window: int = 1) -> list[int]:
    """Compatibility wrapper delegating to the domain service implementation."""
    from app.domain.services.local_minima import (
        find_local_minima as _domain_find_local_minima,
    )
 
    return _domain_find_local_minima(series, window)


def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if not pd.api.types.is_datetime64_any_dtype(df.get("date")):
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])  # type: ignore[arg-type]
    return df


def _select_indices(df: pd.DataFrame, indices: list[int]) -> pd.DataFrame:
    out = df.iloc[indices][["date", "close"]].copy()
    out.rename(columns={"close": "price"}, inplace=True)
    return out


 
