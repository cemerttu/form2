import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pandas_ta")
from fastapi import FastAPI
import pandas as pd
import numpy as np
import pandas_ta as ta
import oandapyV20
import oandapyV20.endpoints.instruments as instruments

# === CONFIGURATION ===
ACCESS_TOKEN = "your_actual_token_here"  # 🔒 Replace with your real OANDA token
ACCOUNT_TYPE = "practice"                # "practice" or "live"
INSTRUMENT = "EUR_USD"
GRANULARITY = "M5"
CANDLE_COUNT = 100

# === FASTAPI APP ===
app = FastAPI()

# === OANDA CLIENT ===
def get_client():
    env = "practice" if ACCOUNT_TYPE == "practice" else "live"
    return oandapyV20.API(access_token=ACCESS_TOKEN, environment=env)

# === FETCH CANDLE DATA ===
def fetch_candles():
    client = get_client()
    params = {
        "count": CANDLE_COUNT,
        "granularity": GRANULARITY,
        "price": "M"
    }
    r = instruments.InstrumentsCandles(instrument=INSTRUMENT, params=params)
    client.request(r)
    candles = r.response.get("candles")

    data = []
    for candle in candles:
        if candle["complete"]:
            data.append({
                "time": candle["time"],
                "Open": float(candle["mid"]["o"]),
                "High": float(candle["mid"]["h"]),
                "Low": float(candle["mid"]["l"]),
                "Close": float(candle["mid"]["c"]),
            })

    return pd.DataFrame(data)

# === STRATEGY CALCULATION ===
def add_signals(df):
    df['EMA_8'] = ta.ema(df['Close'], length=8)
    df['SMA_13'] = ta.sma(df['Close'], length=13)
    df['recent_high'] = df['High'].rolling(20).max().shift(1)
    df['recent_low'] = df['Low'].rolling(20).min().shift(1)
    df['signal'] = 0

    buy = (df['EMA_8'] > df['SMA_13']) & (df['EMA_8'].shift(1) <= df['SMA_13'].shift(1))
    sell = (df['EMA_8'] < df['SMA_13']) & (df['EMA_8'].shift(1) >= df['SMA_13'].shift(1))

    df.loc[buy, 'signal'] = 1
    df.loc[sell, 'signal'] = -1

    breakout_buy = (df['Close'] > df['recent_high']) & (df['signal'] == 1)
    breakout_sell = (df['Close'] < df['recent_low']) & (df['signal'] == -1)

    df.loc[breakout_buy, 'signal'] = 2
    df.loc[breakout_sell, 'signal'] = -2

    return df

# === API ENDPOINT ===
@app.get("/signal")
def get_latest_signal():
    try:
        df = fetch_candles()
        df = add_signals(df)
        latest = df.iloc[-1]

        signal_map = {
            2: "STRONG BUY",
            1: "BUY",
            0: "HOLD",
            -1: "SELL",
            -2: "STRONG SELL"
        }

        return {
            "time": latest["time"],
            "close": round(latest["Close"], 5),
            "ema_8": round(latest["EMA_8"], 5),
            "sma_13": round(latest["SMA_13"], 5),
            "signal": signal_map.get(latest["signal"], "UNKNOWN")
        }

    except Exception as e:
        return {"error": str(e)}




