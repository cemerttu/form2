import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from twelvedata import TDClient

# === User Parameters ===
API_KEY = "9851f57e14cb45c9a1e71ece51bb93e4"  # Your TwelveData API key
SYMBOL = "EUR/USD"
INTERVAL = "1day"            # You can change this to "15min", "1h", etc.
OUTPUTSIZE = 365             # Number of candles to fetch
INITIAL_BALANCE = 1000.0
STOP_LOSS = 0.0020
TAKE_PROFIT = 0.0040
SPREAD = 0.0005
TRADE_SIZE = 1.0
MAX_HOLD = 12                # Max candles to hold a position

# === Fetch data from TwelveData ===
def fetch_data(api_key, symbol, interval, outputsize):
    td = TDClient(apikey=api_key)
    timeseries = td.time_series(
    symbol=symbol,
    interval=interval,
    outputsize=outputsize
)

    df = timeseries.as_pandas()
    df.reset_index(inplace=True)
    df.rename(columns={"datetime": "Datetime",
                       "open": "Open",
                       "high": "High",
                       "low": "Low",
                       "close": "Close"}, inplace=True)
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Hour'] = pd.to_datetime(df['Datetime']).dt.hour
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    return df

# === Add indicators & signals ===
def apply_indicators(df):
    df['EMA_9'] = ta.ema(df['Close'], length=9)
    df['SMA_21'] = ta.sma(df['Close'], length=21)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df.dropna(inplace=True)
    df['recent_high'] = df['High'].rolling(10).max().shift(1)
    df['recent_low'] = df['Low'].rolling(10).min().shift(1)
    df['signal'] = 0
    df['signal_text'] = "Hold"
    buy = (
        (df['EMA_9'] > df['SMA_21']) &
        (df['EMA_9'].shift(1) <= df['SMA_21'].shift(1)) &
        (df['Close'] > df['recent_high']) &
        (df['RSI'] > 55)
    )
    sell = (
        (df['EMA_9'] < df['SMA_21']) &
        (df['EMA_9'].shift(1) >= df['SMA_21'].shift(1)) &
        (df['Close'] < df['recent_low']) &
        (df['RSI'] < 45)
    )
    df.loc[buy, 'signal'] = 2
    df.loc[buy, 'signal_text'] = "Strong Buy"
    df.loc[sell, 'signal'] = -2
    df.loc[sell, 'signal_text'] = "Strong Sell"
    return df

# === Backtest engine ===
def run_backtest(df):
    balance = INITIAL_BALANCE
    position = None
    entry_price = 0.0
    trades = []
    equity_curve = []
    i = 0

    while i < len(df):
        row = df.iloc[i]
        hour = row['Hour']
        # Only trade during day session (optional)
        if hour < 6 or hour >= 20:
            equity_curve.append(balance)
            i += 1
            continue

        signal = row['signal']
        price = row['Close']

        if position is None and signal in (2, -2):
            if signal == 2:
                entry_price = price + SPREAD
                position = 'long'
                trades.append(f"BUY @ {entry_price:.5f} | {row['Datetime']}")
            else:
                entry_price = price - SPREAD
                position = 'short'
                trades.append(f"SELL @ {entry_price:.5f} | {row['Datetime']}")

        elif position is not None:
            exit_flag = False
            for j in range(i+1, min(i + MAX_HOLD + 1, len(df))):
                future = df.iloc[j]
                if future['Hour'] < 6 or future['Hour'] >= 20:
                    continue
                high, low = future['High'], future['Low']
                if position == 'long':
                    if low <= entry_price - STOP_LOSS:
                        exit_price = entry_price - STOP_LOSS
                        profit = (exit_price - entry_price) * TRADE_SIZE
                        trades.append(f"SL LONG @ {exit_price:.5f} | PnL = {profit:.2f}")
                        balance += profit
                        exit_flag = True
                    elif high >= entry_price + TAKE_PROFIT:
                        exit_price = entry_price + TAKE_PROFIT
                        profit = (exit_price - entry_price) * TRADE_SIZE
                        trades.append(f"TP LONG @ {exit_price:.5f} | PnL = {profit:.2f}")
                        balance += profit
                        exit_flag = True
                else:
                    if high >= entry_price + STOP_LOSS:
                        exit_price = entry_price + STOP_LOSS
                        profit = (entry_price - exit_price) * TRADE_SIZE
                        trades.append(f"SL SHORT @ {exit_price:.5f} | PnL = {profit:.2f}")
                        balance += profit
                        exit_flag = True
                    elif low <= entry_price - TAKE_PROFIT:
                        exit_price = entry_price - TAKE_PROFIT
                        profit = (entry_price - exit_price) * TRADE_SIZE
                        trades.append(f"TP SHORT @ {exit_price:.5f} | PnL = {profit:.2f}")
                        balance += profit
                        exit_flag = True

                if exit_flag:
                    position = None
                    i = j
                    break

            if not exit_flag and position is not None:
                final = df.iloc[min(i + MAX_HOLD, len(df)-1)]
                exit_price = final['Close']
                if position == 'long':
                    profit = (exit_price - entry_price) * TRADE_SIZE
                    trades.append(f"TIMEOUT LONG @ {exit_price:.5f} | PnL = {profit:.2f}")
                else:
                    profit = (entry_price - exit_price) * TRADE_SIZE
                    trades.append(f"TIMEOUT SHORT @ {exit_price:.5f} | PnL = {profit:.2f}")
                balance += profit
                position = None
                i = min(i + MAX_HOLD, len(df)-1)

        equity_curve.append(balance)
        i += 1

    return trades, balance, equity_curve

# === Report ===
def report(trades, final_balance, equity_curve):
    print("\n📊 TRADE LOG")
    for t in trades:
        print("•", t)
    print(f"\n💰 FINAL BALANCE: {final_balance:.2f}")
    print(f"📈 TOTAL PROFIT: {final_balance - INITIAL_BALANCE:.2f}")

    plt.figure(figsize=(10, 4))
    plt.plot(equity_curve, label="Equity Curve", linewidth=2)
    plt.axhline(INITIAL_BALANCE, linestyle="--", color="gray", label="Initial Balance")
    plt.title(f"Strategy Backtest ({SYMBOL})")
    plt.xlabel("Time Steps")
    plt.ylabel("Balance")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# === Main Execution ===
if __name__ == "__main__":
    df = fetch_data(API_KEY, SYMBOL, INTERVAL, OUTPUTSIZE)
    df = apply_indicators(df)
    trades, final_balance, equity = run_backtest(df)
    report(trades, final_balance, equity)
