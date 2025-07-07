


import pandas as pd
import pandas_ta as ta
import numpy as np

print(np.nan)

# Set your OANDA access token (not used in this demo)
access_token = "YOUR_OANDA_ACCESS_TOKEN"

from oandapyV20 import API
import oandapyV20.endpoints.instruments as instruments

def fetch_5min_candles(n=100, instrument="EUR_USD"):
    # Fetch last n 5-minute candles from OANDA
    client = API(access_token=access_token)
    params = {
        "granularity": "M5",
        "count": n
    }
    r = instruments.InstrumentsCandles(instrument=instrument, params=params)
    response = client.request(r)
    candles = response['candles']
    df = pd.DataFrame({
        'Open': [float(c['mid']['o']) for c in candles],
        'High': [float(c['mid']['h']) for c in candles],
        'Low': [float(c['mid']['l']) for c in candles],
        'Close': [float(c['mid']['c']) for c in candles]
    })
    return df

def add_ma_signals(df):
    # Calculate 12 EMA and 15 SMA
    df['EMA_12'] = ta.ema(df['Close'], length=12)
    df['SMA_15'] = ta.sma(df['Close'], length=15)
    # Generate signals: 1 for buy, -1 for sell, 0 for hold
    df['signal'] = 0
    df.loc[(df['EMA_12'] > df['SMA_15']) & (df['EMA_12'].shift(1) <= df['SMA_15'].shift(1)), 'signal'] = 1
    df.loc[(df['EMA_12'] < df['SMA_15']) & (df['EMA_12'].shift(1) >= df['SMA_15'].shift(1)), 'signal'] = -1
    return df

# Example usage: print last 10 signals
if __name__ == "__main__":
    df = fetch_5min_candles(100)
    df = add_ma_signals(df)
    for idx, row in df.tail(10).iterrows():
        if row['signal'] == 1:
            print(f"Candle {idx}: BUY signal | Close={row['Close']:.2f} | EMA_12={row['EMA_12']:.2f} | SMA_15={row['SMA_15']:.2f}")
        elif row['signal'] == -1:
            print(f"Candle {idx}: SELL signal | Close={row['Close']:.2f} | EMA_12={row['EMA_12']:.2f} | SMA_15={row['SMA_15']:.2f}")
        else:
            print(f"Candle {idx}: HOLD | Close={row['Close']:.2f} | EMA_12={row['EMA_12']:.2f} | SMA_15={row['SMA_15']:.2f}")




