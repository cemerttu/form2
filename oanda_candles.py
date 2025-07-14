import pandas as pd
import pandas_ta as ta
import numpy as np
import yfinance as yf


def fetch_1min_candles(n=500, symbol="EURUSD=X"):
    df = yf.download(symbol, interval="5m", period="6d")

    # Flatten MultiIndex if exists
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    df = df.tail(n).reset_index(drop=True)

    # Ensure numeric types
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)

    return df


def add_ma_signals(df):
    # Indicators
    df['EMA_9'] = ta.ema(df['Close'], length=9)
    df['SMA_21'] = ta.sma(df['Close'], length=21)

    # Rolling high/low for breakout detection
    df['recent_high_before'] = df['High'].rolling(window=10, min_periods=1).max()
    df['recent_low_before'] = df['Low'].rolling(window=10, min_periods=1).min()

    # Future high/low (with lookahead)
    look_forward_window = 10
    df['future_high_after'] = np.nan
    df['future_low_after'] = np.nan

    for i in range(len(df)):
        future_slice = df['High'].iloc[i : i + look_forward_window]
        if not future_slice.empty:
            df.loc[i, 'future_high_after'] = future_slice.max()
            df.loc[i, 'future_low_after'] = df['Low'].iloc[i : i + look_forward_window].min()

    # Signal encoding
    df['signal'] = 0

    # Crossovers
    buy = (df['EMA_9'] > df['SMA_21']) & (df['EMA_9'].shift(1) <= df['SMA_21'].shift(1))
    sell = (df['EMA_9'] < df['SMA_21']) & (df['EMA_9'].shift(1) >= df['SMA_21'].shift(1))
    df.loc[buy, 'signal'] = 1
    df.loc[sell, 'signal'] = -1

    # Strong signals (breakouts)
    breakout_buy = (df['Close'] > df['recent_high_before'].shift(1)) & (df['signal'] == 1)
    breakout_sell = (df['Close'] < df['recent_low_before'].shift(1)) & (df['signal'] == -1)
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
    print("\n📊 SIGNAL FOLLOW-UP (last 20 candles):")
    print("----------------------------------------------------------------------------------------")

    df = fetch_1min_candles(500)
    df = add_ma_signals(df)

    signal_labels = {
        2: "STRONG BUY",
        1: "BUY",
        0: "HOLD (no signal)",
        -1: "SELL",
        -2: "STRONG SELL"
    }

    # Signal summary
    print("\n🔔 SIGNAL SUMMARY (with explanation):")
    signal_counts = df['signal'].value_counts().sort_index()
    for sig_value in sorted(signal_labels.keys(), reverse=True):
        count = signal_counts.get(sig_value, 0)
        label = signal_labels[sig_value]
        print(f" {sig_value:>2} = {label:<15} --> {count} signals")

    # Show last 20 candles
    print("\n📈 LAST 20 CANDLES:\n")
    for idx, row in df.tail(20).iterrows():
        signal = row['signal']
        close = safe_fmt(row['Close'])
        ema = safe_fmt(row['EMA_9'])
        sma = safe_fmt(row['SMA_21'])
        fut_high = safe_fmt(row['future_high_after'])
        fut_low = safe_fmt(row['future_low_after'])

        sig_str = {
            2: "STRONG BUY (2)",
            1: "BUY (1)",
            0: "HOLD (0)",
            -1: "SELL (-1)",
            -2: "STRONG SELL (-2)"
        }.get(signal, f"UNKNOWN ({signal})")

        print(f"Candle {idx}: {sig_str} | Close={close} | EMA_9={ema} | SMA_21={sma} | Future High(10)={fut_high} | Future Low(10)={fut_low}")

    # Most recent candle
    print("\n📍 MOST RECENT CANDLE:\n")
    row = df.iloc[-1]
    signal = row['signal']
    close = safe_fmt(row['Close']_
