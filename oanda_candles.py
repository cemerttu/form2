import pandas as pd
import pandas_ta as ta
import numpy as np
import yfinance as yf

# === Fetch 5-minute candles ===
def fetch_5min_candles(n=500, symbol="EURUSD=X"):
    df = yf.download(symbol, interval="5m", period="7d", progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    df = df.tail(n).reset_index(drop=True)
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)

    return df

# === Add Moving Average signals ===
def add_ma_signals(df):
    df['EMA_9'] = ta.ema(df['Close'], length=9)
    df['SMA_21'] = ta.sma(df['Close'], length=21)
    df['recent_high'] = df['High'].rolling(window=10, min_periods=1).max()
    df['recent_low'] = df['Low'].rolling(window=10, min_periods=1).min()
    df['signal'] = 0  # 0 = HOLD

    # Crossovers
    buy = (df['EMA_9'] > df['SMA_21']) & (df['EMA_9'].shift(1) <= df['SMA_21'].shift(1))
    sell = (df['EMA_9'] < df['SMA_21']) & (df['EMA_9'].shift(1) >= df['SMA_21'].shift(1))
    df.loc[buy, 'signal'] = 1
    df.loc[sell, 'signal'] = -1

    # Breakouts
    breakout_buy = (df['Close'] > df['recent_high'].shift(1)) & (df['signal'] == 1)
    breakout_sell = (df['Close'] < df['recent_low'].shift(1)) & (df['signal'] == -1)
    df.loc[breakout_buy, 'signal'] = 2
    df.loc[breakout_sell, 'signal'] = -2

    return df

# === Print candles before each signal ===
def print_before_signal(df, candles_before=3):
    print("\n📊 SIGNAL PREVIEW ({} candles before each signal):\n".format(candles_before))

    for i in range(len(df)):
        signal = df.loc[i, 'signal']
        if signal in [1, -1, 2, -2]:
            sig_type = {
                1: "BUY",
                -1: "SELL",
                2: "STRONG BUY",
                -2: "STRONG SELL"
            }[signal]

            print(f"\n🕒 Signal at candle {i} ({sig_type})")
            for j in range(candles_before, 0, -1):
                if i - j >= 0:
                    close = df.loc[i - j, 'Close']
                    print(f"   ⏪ {j} candle(s) before: Close = {close:.5f}")

# === MAIN ===
if __name__ == "__main__":
    df = fetch_5min_candles(500)
    df = add_ma_signals(df)

    print("\n🔔 SIGNAL COUNTS:")
    print(df['signal'].value_counts().to_string())

    print_before_signal(df, candles_before=3)



print("\n📊 SIGNAL FOLLOW-UP (next 3 candles after signal):\n")
print("------------------------------------------------------------------------------------------------------------------------------------------")


# import pandas as pd
# import pandas_ta as ta
# import numpy as np
# import yfinance as yf

# def fetch_5min_candles(n=500, symbol="EURUSD=X"):
#     df = yf.download(symbol, interval="5m", period="7d")

#     # Flatten MultiIndex if exists
#     if isinstance(df.columns, pd.MultiIndex):
#         df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

#     df = df.tail(n).reset_index(drop=True)

#     # Ensure types
#     df['Open'] = df['Open'].astype(float)
#     df['High'] = df['High'].astype(float)
#     df['Low'] = df['Low'].astype(float)
#     df['Close'] = df['Close'].astype(float)

#     return df

# def add_ma_signals(df):
#     df['EMA_9'] = ta.ema(df['Close'], length=9)
#     df['SMA_21'] = ta.sma(df['Close'], length=21)

#     # --- Original "candles before" calculations ---
#     df['recent_high_before'] = df['High'].rolling(window=10, min_periods=1).max()
#     df['recent_low_before'] = df['Low'].rolling(window=10, min_periods=1).min()

#     # --- NEW: "Candles After" (for research/analysis ONLY - introduces look-ahead bias) ---
#     # Define the look-forward window (e.g., 10 candles into the future)
#     look_forward_window = 10

#     # To calculate the max High in the *next* 'look_forward_window' candles
#     # we shift the High column by negative 'look_forward_window'
#     # and then apply a rolling max.
#     # The '.shift(-look_forward_window + 1).rolling(...).max()' logic is tricky.
#     # A simpler way to think about it for 'future high over next N candles' is:
#     # 1. Take the 'High' column.
#     # 2. For each row, calculate the max of 'High' from this row up to 'N' rows ahead.
#     # This can be done by reversing the series, applying rolling max, then reversing back.
#     # Or by using a `closed='right'` or `closed='both'` in conjunction with `shift`.

#     # A more common and robust way to get "future high/low within N candles"
#     # is to use a rolling window and then shift the result *backward*.

#     # For 'future_high_after_10': For each row 'i', what's the max High from row 'i' to 'i + 9'?
#     # This means the rolling window should operate on future data.
#     # We can create a reversed series, apply rolling max, then reverse again.
#     # df['future_high_after'] = df['High'][::-1].rolling(window=look_forward_window, min_periods=1).max()[::-1].shift(look_forward_window -1) # This is complicated.

#     # Let's use a simpler, more direct approach for future high/low
#     # This creates a Series where each value is the max/min of the next 'look_forward_window' values
#     df['future_high_after'] = np.nan
#     df['future_low_after'] = np.nan

#     for i in range(len(df) - look_forward_window):
#         df.loc[i, 'future_high_after'] = df['High'].iloc[i : i + look_forward_window].max()
#         df.loc[i, 'future_low_after'] = df['Low'].iloc[i : i + look_forward_window].min()


#     df['signal'] = 0 

#     # Crossover logic remains the same (based on past/current data)
#     buy = (df['EMA_9'] > df['SMA_21']) & (df['EMA_9'].shift(1) <= df['SMA_21'].shift(1))
#     sell = (df['EMA_9'] < df['SMA_21']) & (df['EMA_9'].shift(1) >= df['SMA_21'].shift(1))

#     df.loc[buy, 'signal'] = 1
#     df.loc[sell, 'signal'] = -1

#     # Breakout logic still uses 'recent_high_before' and 'recent_low_before'
#     # as these are based on past data and are suitable for real signals.
#     # If you were to use 'future_high_after' here, it would be look-ahead biased.
#     breakout_buy = (df['Close'] > df['recent_high_before'].shift(1)) & (df['signal'] == 1)
#     breakout_sell = (df['Close'] < df['recent_low_before'].shift(1)) & (df['signal'] == -1)

#     df.loc[breakout_buy, 'signal'] = 2
#     df.loc[breakout_sell, 'signal'] = -2

#     return df

# def safe_fmt(val):
#     if val is None or (isinstance(val, float) and np.isnan(val)):
#         return 'nan'
#     if hasattr(val, 'item'):
#         val = val.item()
#     return f"{val:.5f}"

# if __name__ == "__main__":
#     df = fetch_5min_candles(500)
#     df = add_ma_signals(df)

#     print("\n🔔 SIGNAL SUMMARY:")
#     print(df['signal'].value_counts().to_string())
#     print("\n📈 LAST 20 CANDLES:\n")

#     for idx, row in df.tail(20).iterrows():
#         signal = row['signal']
#         close = safe_fmt(row['Close'])
#         ema = safe_fmt(row['EMA_9'])
#         sma = safe_fmt(row['SMA_21'])
#         # Also print the new 'future' columns (will be NaN for last few rows)
#         fut_high = safe_fmt(row['future_high_after'])
#         fut_low = safe_fmt(row['future_low_after'])

#         if signal == 2:
#             sig_str = 'STRONG BUY'
#         elif signal == 1:
#             sig_str = 'BUY'
#         elif signal == -1:
#             sig_str = 'SELL'
#         elif signal == -2:
#             sig_str = 'STRONG SELL'
#         else:
#             sig_str = 'HOLD'

#         print(f"Candle {idx}: {sig_str} | Close={close} | EMA_9={ema} | SMA_21={sma} | Future High(10)={fut_high} | Future Low(10)={fut_low}")




