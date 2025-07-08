import pandas as pd
import pandas_ta as ta
import numpy as np
import yfinance as yf

def fetch_5min_candles(n=500, symbol="EURUSD=X"):
    df = yf.download(symbol, interval="5m", period="7d")

    # Flatten MultiIndex if exists
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    df = df.tail(n).reset_index(drop=True)

    # Ensure types
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)

    return df

def add_ma_signals(df):
    df['EMA_5'] = ta.ema(df['Close'], length=5)
    df['SMA_10'] = ta.sma(df['Close'], length=10)

    # Rolling high/low for breakout logic (less strict)
    df['recent_high'] = df['High'].rolling(window=10, min_periods=1).max()
    df['recent_low'] = df['Low'].rolling(window=10, min_periods=1).min()

    df['signal'] = 0  # 0 = HOLD

    # Basic crossover logic
    buy = (df['EMA_5'] > df['SMA_10']) & (df['EMA_5'].shift(1) <= df['SMA_10'].shift(1))
    sell = (df['EMA_5'] < df['SMA_10']) & (df['EMA_5'].shift(1) >= df['SMA_10'].shift(1))

    df.loc[buy, 'signal'] = 1
    df.loc[sell, 'signal'] = -1

    # Breakout logic
    breakout_buy = (df['Close'] > df['recent_high'].shift(1)) & (df['signal'] == 1)
    breakout_sell = (df['Close'] < df['recent_low'].shift(1)) & (df['signal'] == -1)

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
    df = fetch_5min_candles(500)
    df = add_ma_signals(df)

    print("\n🔔 SIGNAL SUMMARY:")
    print(df['signal'].value_counts().to_string())
    print("\n📈 LAST 20 CANDLES:\n")

    for idx, row in df.tail(20).iterrows():
        signal = row['signal']
        close = safe_fmt(row['Close'])
        ema5 = safe_fmt(row['EMA_5'])
        sma10 = safe_fmt(row['SMA_10'])

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

        print(f"Candle {idx}: {sig_str} | Close={close} | EMA_5={ema5} | SMA_10={sma10}")





# This code fetches 5-minute candles for a given symbol, calculates moving averages,
# and generates buy/sell signals based on EMA/SMA crossovers and breakout conditions.


# from oandapyV20 import API
# from oandapyV20.endpoints import instruments
# import pandas as pd
# import pandas_ta as ta    


    