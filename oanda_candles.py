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
    import time
    print("Strategy started. Press Ctrl+C to stop.")
    try:
        while True:
            df = fetch_5min_candles(100)
            df = add_ma_signals(df)
            signal = df.iloc[-1]['signal']
            if hasattr(signal, 'item'):
                signal = signal.item()
            if signal == 1:
                print("Latest Candle: BUY")
            elif signal == -1:
                print("Latest Candle: SELL")
            else:
                print("Latest Candle: HOLD")
            time.sleep(60)  # Wait 1 minute before checking again
    except KeyboardInterrupt:
        print("\nStrategy stopped by user.")




