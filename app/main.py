import matplotlib.pyplot as plt
import pandas as pd
import requests
from dotenv import dotenv_values
from fastapi import FastAPI
import os

working_directory = os.path.abspath(os.getcwd())
config = dotenv_values(".env")
financial_api_key = config["FINANCIALMODELINGPREP_API_KEY"]

api = FastAPI()


def monthly(df):
    return resample(df, "MS")


def weekly(df):
    return resample(df, "W")


def resample(df, periodicity):
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


def addDayOfWeek(df):
    df["day_of_week"] = pd.to_datetime(df["date"]).dt.day_name()
    df = df.loc[df["day_of_week"] == "Monday"]
    df = df.reset_index()
    return df


def isTheLower(df, index, num_elements):
    for i in range(1, num_elements):
        if not (df[index] < df[index - i]):
            return False
    return True


def getStockData(symbol, days):
    r = requests.get(
        f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?timeseries={days}&apikey={financial_api_key}"
    )
    r = r.json()
    stockdata = r["historical"]
    return pd.DataFrame(stockdata)


def plotStockData(df, symbol):
    plt.plot(df.date, df.close, label=symbol)
    plt.show()


def plotMacd(df, macd):
    exp9 = getExp(macd, 9)
    plt.plot(df.date, macd, label="MACD", color="#EBD2BE")
    plt.plot(df.date, exp9, label="Signal Line")
    plt.legend(loc="upper left")
    plt.show()


def getExp(df, periods):
    return df.ewm(span=periods, adjust=False, min_periods=periods).mean()


def getMacd(df):
    exp12 = getExp(df.close, 12)
    exp26 = getExp(df.close, 26)
    return exp12 - exp26


def findTheLowest(df, index, num_elements):
    while index > num_elements:
        if isTheLower(df, index, num_elements):
            return index
        index = index - 1
        num_elements = min(index, num_elements)
    return index


def choseStopLoss(sp1, sp2, price):
    if sp1 >= sp2 and sp1 < price:
        return sp1
    if sp2 >= sp1 and sp2 < price:
        return sp2
    return price


# *****************************


def get_stop_loss(symbol, stock_data, plotData=False, periodicity="W", num_elements=20):
    current_price = stock_data.iloc[0].close
    df = resample(stock_data, periodicity)
    macd = getMacd(df)

    df = df.reindex(index=df.index[::-1])
    macd = macd.reindex(index=macd.index[::-1])

    if plotData:
        print(symbol)
        plotStockData(df, symbol)
        plotMacd(df, macd)

    # max_macd_value = max(macd)
    max_macd_index = macd.idxmax()
    index = findTheLowest(macd, max_macd_index, 5)
    index = findTheLowest(df["low"], index, num_elements)

    return {
        "symbol": symbol,
        "current_price": current_price,
        "stop_loss": df["low"][index],
        "stop_loss_date": df["date"][index],
        "max_macd_date": df["date"][max_macd_index],
        "period": periodicity,
    }


def get_stop_loss_rows(symbols):
    rows = []

    for symbol in symbols:
        try:
            days = 365 * 10
            df = getStockData(symbol, days)
            rows.append(get_stop_loss(symbol, df, False, "MS", 10))
            return rows
        except Exception as e:
            print("Problem with: " + symbol)
            print(e)


@api.get("/stocks/{symbol}")
async def root(symbol: str):
    rows = get_stop_loss_rows([symbol])
    return {"symbol": symbol, "stop_loss": rows[0]["stop_loss"], "stop_loss_date": rows[0]["stop_loss_date"]}
