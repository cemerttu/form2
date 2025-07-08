import pandas as pd
import numpy as np
import pandas_ta as ta
import oandapyV20
import oandapyV20.endpoints.instruments as instruments

# Replace with your OANDA API token
ACCESS_TOKEN = "YOUR_OANDA_API_KEY"
ACCOUNT_TYPE = "practice"  # or "live"
INSTRUMENT = "EUR_USD"
GRANULARITY = "M5"
CANDLE_COUNT = 100

def fetch_5min_candles():
    client = oandapyV20.API(access_token=ACCESS_TOKEN)
    params = {
        "count": CANDLE_COUNT,
        "granularity": GRANULARITY,
        "price": "M"  # Midpoint prices
    }

    r = instruments.InstrumentsCandles(instrument=INSTRUMENT, params=params)
    client.request(r)
    candles = r.response.get("candles")

    # Parse into DataFrame
    data = []
    for candle in candles:
        data.append({
            "time": candle["time"],
            "Open": float(candle["mid"]["o"]),
            "High": float(candle["mid"]["h"]),
            "Low": float(candle["mid"]["l"]),
            "Close": float(candle["mid"]["c"]),
        })

    df = pd.DataFrame(data)
    return df

def add_ma_signals(df):
    df['EMA_8'] = ta.ema(df['Close'], length=8)
    df['SMA_13'] = ta.sma(df['Close'], length=13)
    df['recent_high'] = df['High'].rolling(window=20, min_periods=1).max()
    df['recent_low'] = df['Low'].rolling(window=20, min_periods=1).min()
    df['signal'] = 0

    buy_condition = (df['EMA_8'] > df['SMA_13']) & (df['EMA_8'].shift(1) <= df['SMA_13'].shift(1))
    sell_condition = (df['EMA_8'] < df['SMA_13']) & (df['EMA_8'].shift(1) >= df['SMA_13'].shift(1))

    df.loc[buy_condition, 'signal'] = 1
    df.loc[sell_condition, 'signal'] = -1

    close = df['Close']
    recent_high = df['recent_high'].shift(1)
    recent_low = df['recent_low'].shift(1)
    signal = df['signal']

    breakout_buy = (close > recent_high) & (signal == 1)
    breakout_sell = (close < recent_low) & (signal == -1)

    df.loc[breakout_buy, 'signal'] = 2
    df.loc[breakout_sell, 'signal'] = -2

    return df

def safe_fmt(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return 'nan'
    if hasattr(val, 'item'):
        val = val.item()
    return f"{val:.5f}"

if __name__ == "__main__":
    df = fetch_5min_candles()
    df = add_ma_signals(df)

    for idx, row in df.tail(20).iterrows():
        signal = row['signal']
        close = safe_fmt(row['Close'])
        ema8 = safe_fmt(row['EMA_8'])
        sma13 = safe_fmt(row['SMA_13'])

        if signal == 2:
            sig_str = 'STRONG BUY'
        elif signal == 1:
            sig_str = 'BUY'
        elif signal == -1:
            sig_str = 'SELL'
        elif signal == -2:
            sig_str = 'STRONG SELL'
        else:
            sig_str = 'HOLD'

        print(f"Candle {idx}: {sig_str} | Close={close} | EMA_8={ema8} | SMA_13={sma13}")
