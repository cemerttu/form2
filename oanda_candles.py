import pandas as pd
import pandas_ta as ta
import numpy as np
import yfinance as yf

print(np.nan)

def fetch_5min_candles(n=100, symbol="EURUSD=X"):
    df = yf.download(symbol, interval="5m", period="7d")
    df = df.tail(n).rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close"})
    df = df.reset_index(drop=True)  # Reset index to avoid hidden datetime misalignments
    return df

def add_ma_signals(df):
    df['EMA_8'] = ta.ema(df['Close'], length=8)
    df['SMA_13'] = ta.sma(df['Close'], length=13)

    df['recent_high'] = df['High'].rolling(window=20, min_periods=1).max()
    df['recent_low'] = df['Low'].rolling(window=20, min_periods=1).min()

    # Convert to Series if somehow 2D
    if isinstance(df['recent_high'], pd.DataFrame):
        df['recent_high'] = df['recent_high'].iloc[:, 0]
    if isinstance(df['recent_low'], pd.DataFrame):
        df['recent_low'] = df['recent_low'].iloc[:, 0]

    df['signal'] = 0

    buy_condition = (df['EMA_8'] > df['SMA_13']) & (df['EMA_8'].shift(1) <= df['SMA_13'].shift(1))
    sell_condition = (df['EMA_8'] < df['SMA_13']) & (df['EMA_8'].shift(1) >= df['SMA_13'].shift(1))

    df.loc[buy_condition, 'signal'] = 1
    df.loc[sell_condition, 'signal'] = -1

    # Guaranteed alignment using .align() on Series
    close_aligned, high_shift_aligned = df['Close'].align(df['recent_high'].shift(1), axis=0, join='inner')
    close_aligned2, low_shift_aligned = df['Close'].align(df['recent_low'].shift(1), axis=0, join='inner')
    signal_aligned, _ = df['signal'].align(close_aligned, axis=0, join='inner')

    breakout_buy = (close_aligned > high_shift_aligned) & (signal_aligned == 1)
    breakout_sell = (close_aligned2 < low_shift_aligned) & (signal_aligned == -1)

    # Update signals only where aligned
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
