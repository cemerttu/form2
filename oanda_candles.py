import pandas as pd
import pandas_ta as ta
import numpy as np
import yfinance as yf
import time

# Fetch data every 1 minute for the symbol (and only the last few candles)
def fetch_1min_candles(symbol="EURUSD=X", interval="5m", period="1d", n=5):
    df = yf.download(symbol, interval=interval, period=period)

    # Flatten MultiIndex if exists
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    df = df.tail(n).reset_index(drop=True)  # Only keep the last n candles

    # Ensure numeric types
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)

    return df

# Add moving average signals
def add_ma_signals(df):
    # Indicators
    df['EMA_9'] = ta.ema(df['Close'], length=9)
    df['SMA_21'] = ta.sma(df['Close'], length=21)

    # Rolling high/low for breakout detection
    df['recent_high_before'] = df['High'].rolling(window=10, min_periods=1).max()
    df['recent_low_before'] = df['Low'].rolling(window=10, min_periods=1).min()

    # Future high/low (lookahead window)
    look_forward_window = 10
    df['future_high_after'] = np.nan
    df['future_low_after'] = np.nan

    for i in range(len(df)):
        future_slice_high = df['High'].iloc[i : i + look_forward_window]
        future_slice_low = df['Low'].iloc[i : i + look_forward_window]
        if not future_slice_high.empty:
            df.loc[i, 'future_high_after'] = future_slice_high.max()
            df.loc[i, 'future_low_after'] = future_slice_low.min()

    # Signal encoding
    df['signal'] = 0

    # Simple EMA/SMA crossover logic
    buy = (df['EMA_9'] > df['SMA_21']) & (df['EMA_9'].shift(1) <= df['SMA_21'].shift(1))
    sell = (df['EMA_9'] < df['SMA_21']) & (df['EMA_9'].shift(1) >= df['SMA_21'].shift(1))
    df.loc[buy, 'signal'] = 1
    df.loc[sell, 'signal'] = -1

    # Strong signals: breakout + crossover
    breakout_buy = (df['Close'] > df['recent_high_before'].shift(1)) & (df['signal'] == 1)
    breakout_sell = (df['Close'] < df['recent_low_before'].shift(1)) & (df['signal'] == -1)
    df.loc[breakout_buy, 'signal'] = 2
    df.loc[breakout_sell, 'signal'] = -2

    return df

# Function to format values with 5 decimals
def safe_fmt(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return 'nan'
    if hasattr(val, 'item'):
        val = val.item()
    return f"{val:.5f}"

# Print signal summary
def print_signal_summary(df, signal_labels):
    signal_counts = df['signal'].value_counts().sort_index()
    for sig_value in sorted(signal_labels.keys(), reverse=True):
        count = signal_counts.get(sig_value, 0)
        label = signal_labels[sig_value]
        print(f" {sig_value:>2} = {label:<15} --> {count} signals")

# Print last 20 candles
def print_last_20_candles(df, signal_labels):
    print("\n📈 LAST 20 CANDLES:\n")
    for idx, row in df.tail(20).iterrows():
        signal = row['signal']
        close = safe_fmt(row['Close'])
        ema = safe_fmt(row['EMA_9'])  # Format EMA with 5 decimals
        sma = safe_fmt(row['SMA_21'])  # Format SMA with 5 decimals
        fut_high = safe_fmt(row['future_high_after'])
        fut_low = safe_fmt(row['future_low_after'])
        
        sig_str = signal_labels.get(signal, f"UNKNOWN ({signal})") + f" ({signal})"
        print(f"Candle {idx}: {sig_str} | Close={close} | EMA_9={ema} | SMA_21={sma} | Future High(10)={fut_high} | Future Low(10)={fut_low}")

# Print most recent candle
def print_most_recent_candle(df, signal_labels):
    print("\n📍 MOST RECENT CANDLE:\n")
    row = df.iloc[-1]
    signal = row['signal']
    close = safe_fmt(row['Close'])
    ema = safe_fmt(row['EMA_9'])  # Format EMA with 5 decimals
    sma = safe_fmt(row['SMA_21'])  # Format SMA with 5 decimals
    fut_high = safe_fmt(row['future_high_after'])
    fut_low = safe_fmt(row['future_low_after'])

    sig_str = signal_labels.get(signal, f"UNKNOWN ({signal})") + f" ({signal})"
    print(f"Most Recent Candle: {sig_str} | Close={close} | EMA_9={ema} | SMA_21={sma} | Future High(10)={fut_high} | Future Low(10)={fut_low}")

# Main loop
if __name__ == "__main__":
    print("\n📊 SIGNAL FOLLOW-UP (last 20 candles):")
    print("----------------------------------------------------------------------------------------")

    signal_labels = {
        2: "STRONG BUY",
        1: "BUY",
        0: "HOLD (no signal)",
        -1: "SELL",
        -2: "STRONG SELL"
    }

    while True:
        # Fetch only the last 5 candles for speed
        df = fetch_1min_candles(symbol="EURUSD=X", interval="5m", period="1d", n=5)  # Reduced the period to 1 day and n to 5
        df = add_ma_signals(df)

        # Print signal summary and recent candles
        print_signal_summary(df, signal_labels)
        print_last_20_candles(df, signal_labels)

        # Wait for the next 5-second interval
        print("\nWaiting for the next 5-second interval...")
        time.sleep(5)  # Sleep for 5 seconds (adjusted from 300 seconds)





