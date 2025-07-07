import pandas as pd
import pandas_ta as ta
import numpy as np
import yfinance as yf

print(np.nan)

def fetch_5min_candles(n=100, symbol="EURUSD=X"):
    df = yf.download(symbol, interval="5m", period="7d")

    # Flatten possible MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    df = df.tail(n).reset_index(drop=True)

    # Enforce columns as pure Series
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)

    return df

def add_ma_signals(df):
    df['EMA_8'] = ta.ema(df['Close'], length=8)
    df['SMA_13'] = ta.sma(df['Close'], length=13)

    # Rolling recent high/low
    df['recent_high'] = df['High'].rolling(window=20, min_periods=1).max().astype(float)
    df['recent_low'] = df['Low'].rolling(window=20, min_periods=1).min().astype(float)

    df['signal'] = 0

    buy_condition = (df['EMA_8'] > df['SMA_13']) & (df['EMA_8'].shift(1) <= df['SMA_13'].shift(1))
    sell_condition = (df['EMA_8'] < df['SMA_13']) & (df['EMA_8'].shift(1) >= df['SMA_13'].shift(1))

    df.loc[buy_condition, 'signal'] = 1
    df.loc[sell_condition, 'signal'] = -1

    # Ensure everything is a clean Series
    close = df['Close'].astype(float).reset_index(drop=True)
    recent_high = df['recent_high'].shift(1).astype(float).reset_index(drop=True)
    recent_low = df['recent_low'].shift(1).astype(float).reset_index(drop=True)
    signal = df['signal'].astype(int).reset_index(drop=True)

    # Now apply logic with guaranteed aligned Series
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
    df = fetch_5min_candles(100)
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
