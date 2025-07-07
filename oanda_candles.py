# File: oanda_candles.py
import pandas as pd
import pandas_ta as ta
import numpy as np
import yfinance as yf

print(np.nan)

def fetch_5min_candles(n=100, symbol="EURUSD=X"):
    df = yf.download(symbol, interval="5m", period="7d")
    df = df.tail(n).rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close"})
    return df

# Corrected version inside your add_ma_signals function

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

    # --- Robust alignment for breakout logic ---
    close_series = df['Close']
    recent_high_shifted = df['recent_high'].shift(1)
    recent_low_shifted = df['recent_low'].shift(1)
    signal_series = df['signal']

    # Find the intersection of all indices
    common_idx = close_series.index & recent_high_shifted.index & recent_low_shifted.index & signal_series.index

    # Reindex all Series to the common index
    close_series = close_series.reindex(common_idx)
    recent_high_shifted = recent_high_shifted.reindex(common_idx)
    recent_low_shifted = recent_low_shifted.reindex(common_idx)
    signal_series = signal_series.reindex(common_idx)

    breakout_buy = (close_series > recent_high_shifted) & (signal_series == 1)
    breakout_sell = (close_series < recent_low_shifted) & (signal_series == -1)

    # Only update the rows where the mask is True
    df.loc[breakout_buy[breakout_buy].index, 'signal'] = 2
    df.loc[breakout_sell[breakout_sell].index, 'signal'] = -2

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

        # Enhanced signal mapping
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
