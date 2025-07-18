# === Package Version Check ===
from pkg_resources import get_distribution, DistributionNotFound

required_packages = ['pandas', 'pandas_ta', 'numpy', 'yfinance', 'matplotlib']
print("🔍 Checking required package versions...\n")

for pkg in required_packages:
    try:
        version = get_distribution(pkg).version
        print(f"✅ {pkg}: v{version}")
    except DistributionNotFound:
        print(f"❌ {pkg} is NOT installed. Please run: pip install {pkg}")
        exit(1)

# === Strategy Code ===
import pandas as pd
import pandas_ta as ta
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

STOP_LOSS_PIPS = 0.0020
TAKE_PROFIT_PIPS = 0.0040
SPREAD = 0.0005
TRADE_SIZE = 1.0
MAX_HOLD = 12
MARKET_OPEN_HOUR = 6
MARKET_CLOSE_HOUR = 20

symbols_to_test = ["EURUSD=X", "GBPUSD=X", "USDJPY=X"]

def fetch_candles(symbol="EURUSD=X", interval="5m", period="7d"):
    df = yf.download(symbol, interval=interval, period=period)
    if df.empty or len(df) < 50:
        print(f"❌ ERROR: No data or too few candles for {symbol}. Skipping...")
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df = df.reset_index()

    if 'Datetime' not in df.columns:
        if 'index' in df.columns:
            df['Datetime'] = pd.to_datetime(df['index'])
        elif 'Date' in df.columns:
            df['Datetime'] = pd.to_datetime(df['Date'])

    df['Hour'] = df['Datetime'].dt.hour
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    return df

def add_ma_signals(df):
    df['EMA_9'] = ta.ema(df['Close'], length=9)
    df['SMA_21'] = ta.sma(df['Close'], length=21)

    if df['EMA_9'].isnull().all() or df['SMA_21'].isnull().all():
        raise ValueError("EMA or SMA not calculated. Check pandas_ta.")

    df.dropna(subset=['EMA_9', 'SMA_21'], inplace=True)

    df['recent_high_before'] = df['High'].rolling(window=10, min_periods=1).max()
    df['recent_low_before'] = df['Low'].rolling(window=10, min_periods=1).min()

    df['signal'] = 0
    df['signal_text'] = "Hold"

    buy = (df['EMA_9'] > df['SMA_21']) & (df['EMA_9'].shift(1) <= df['SMA_21'].shift(1))
    sell = (df['EMA_9'] < df['SMA_21']) & (df['EMA_9'].shift(1) >= df['SMA_21'].shift(1))
    df.loc[buy, 'signal'] = 1
    df.loc[buy, 'signal_text'] = "Buy"
    df.loc[sell, 'signal'] = -1
    df.loc[sell, 'signal_text'] = "Sell"

    breakout_buy = (df['Close'] > df['recent_high_before'].shift(1)) & (df['signal'] == 1)
    breakout_sell = (df['Close'] < df['recent_low_before'].shift(1)) & (df['signal'] == -1)
    df.loc[breakout_buy, 'signal'] = 2
    df.loc[breakout_buy, 'signal_text'] = "Strong Buy"
    df.loc[breakout_sell, 'signal'] = -2
    df.loc[breakout_sell, 'signal_text'] = "Strong Sell"

    return df

def run_backtest(df):
    balance = 1000.0
    position = None
    entry_price = 0
    trades = []
    equity_curve = []
    i = 0

    while i < len(df):
        row = df.iloc[i]
        hour = row['Hour']
        if hour < MARKET_OPEN_HOUR or hour >= MARKET_CLOSE_HOUR:
            equity_curve.append(balance)
            i += 1
            continue

        price = row['Close']
        signal = row['signal']
        signal_text = row['signal_text']

        if position is None:
            if signal == 2:
                position = 'long'
                entry_price = price + SPREAD
                trades.append(f"{signal_text.upper()} @ {entry_price:.5f}")
                i += 1
                continue
            elif signal == -2:
                position = 'short'
                entry_price = price - SPREAD
                trades.append(f"{signal_text.upper()} @ {entry_price:.5f}")
                i += 1
                continue

        if position:
            for j in range(i + 1, min(i + MAX_HOLD + 1, len(df))):
                future_row = df.iloc[j]
                if future_row['Hour'] < MARKET_OPEN_HOUR or future_row['Hour'] >= MARKET_CLOSE_HOUR:
                    continue

                high = future_row['High']
                low = future_row['Low']

                if position == 'long':
                    if low <= entry_price - STOP_LOSS_PIPS:
                        exit_price = entry_price - STOP_LOSS_PIPS
                        profit = (exit_price - entry_price) * TRADE_SIZE
                        trades.append(f"SL HIT (LONG) @ {exit_price:.5f} | PROFIT = {profit:.5f}")
                        balance += profit
                        position = None
                        i = j
                        break
                    elif high >= entry_price + TAKE_PROFIT_PIPS:
                        exit_price = entry_price + TAKE_PROFIT_PIPS
                        profit = (exit_price - entry_price) * TRADE_SIZE
                        trades.append(f"TP HIT (LONG) @ {exit_price:.5f} | PROFIT = {profit:.5f}")
                        balance += profit
                        position = None
                        i = j
                        break

                elif position == 'short':
                    if high >= entry_price + STOP_LOSS_PIPS:
                        exit_price = entry_price + STOP_LOSS_PIPS
                        profit = (entry_price - exit_price) * TRADE_SIZE
                        trades.append(f"SL HIT (SHORT) @ {exit_price:.5f} | PROFIT = {profit:.5f}")
                        balance += profit
                        position = None
                        i = j
                        break
                    elif low <= entry_price - TAKE_PROFIT_PIPS:
                        exit_price = entry_price - TAKE_PROFIT_PIPS
                        profit = (entry_price - exit_price) * TRADE_SIZE
                        trades.append(f"TP HIT (SHORT) @ {exit_price:.5f} | PROFIT = {profit:.5f}")
                        balance += profit
                        position = None
                        i = j
                        break
            else:
                exit_price = df.iloc[min(i + MAX_HOLD, len(df) - 1)]['Close']
                if position == 'long':
                    profit = (exit_price - entry_price) * TRADE_SIZE
                    trades.append(f"TIME EXIT (LONG) @ {exit_price:.5f} | PROFIT = {profit:.5f}")
                elif position == 'short':
                    profit = (entry_price - exit_price) * TRADE_SIZE
                    trades.append(f"TIME EXIT (SHORT) @ {exit_price:.5f} | PROFIT = {profit:.5f}")
                balance += profit
                position = None
                i = min(i + MAX_HOLD, len(df) - 1)

        equity_curve.append(balance)
        i += 1

    return trades, balance, equity_curve, df

def report(trades, balance, equity_curve, df, symbol, start=1000):
    print(f"\n📊 BACKTEST RESULT FOR {symbol}")
    print("="*60)
    for t in trades:
        print("•", t)
    print("\n💰 FINAL BALANCE:", round(balance, 2))
    print("📈 TOTAL PROFIT:", round(balance - start, 2))
    print("="*60)

    plt.figure(figsize=(12, 5))
    plt.plot(equity_curve, label='Equity Curve', color='blue', linewidth=1.5)

    equity_points = []
    colors = []
    equity = start
    for t in trades:
        if "PROFIT = " in t:
            profit = float(t.split("PROFIT = ")[1])
            equity += profit
            equity_points.append(equity)
            colors.append("green" if profit > 0 else "red")

    plt.scatter(range(len(equity_points)), equity_points, c=colors, s=60, label="Trades", edgecolor='black')
    plt.axhline(y=start, color='gray', linestyle='--')
    plt.title(f"Equity Curve for {symbol} (Green = Win, Red = Loss)")
    plt.xlabel("Trade Index")
    plt.ylabel("Balance")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# === MAIN ===
if __name__ == "__main__":
    for symbol in symbols_to_test:
        print(f"\n🔁 Running backtest for {symbol}...")
        df = fetch_candles(symbol=symbol, interval="5m", period="7d")
        if df is None:
            continue
        try:
            df = add_ma_signals(df)
            trades, final_balance, equity_curve, df = run_backtest(df)
            report(trades, final_balance, equity_curve, df, symbol)
            print("\n✅ Backtest completed successfully!")
        except Exception as e:
            print(f"❌ ERROR in processing {symbol}: {e}")

