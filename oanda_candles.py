# File: oanda_candles.py
import pandas as pd
import pandas_ta as ta
import numpy as np
import yfinance as yf

print(np.nan)


def fetch_5min_candles(n=100, symbol="EURUSD=X"):
    # Fetch last n 5-minute candles from Yahoo Finance
    df = yf.download(symbol, interval="5m", period="7d")
    df = df.tail(n)
    df = df.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close"})
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
    # Print signals for the last 20 real 5-minute candles
    df = fetch_5min_candles(100)
    df = add_ma_signals(df)
    for idx, row in df.tail(20).iterrows():
        signal = row['signal']
        if hasattr(signal, 'item'):
            signal = signal.item()
        # Ensure all values are scalars for formatting and handle None/NaN
        def safe_fmt(val):
            try:
                if val is None or (isinstance(val, float) and np.isnan(val)):
                    return 'nan'
                if hasattr(val, 'item'):
                    val = val.item()
                return f"{val:.5f}"
            except Exception:
                return 'nan'

        close = safe_fmt(row['Close'])
        ema12 = safe_fmt(row['EMA_12'])
        sma15 = safe_fmt(row['SMA_15'])
        # Map signal to string
        if signal == 1:
            sig_str = 'BUY'
        elif signal == -1:
            sig_str = 'SELL'
        else:
            sig_str = 'HOLD'
        print(f"Candle {idx}: {sig_str} | Close={close} | EMA_12={ema12} | SMA_15={sma15}")




