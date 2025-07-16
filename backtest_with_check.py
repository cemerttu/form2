from pkg_resources import get_distribution, DistributionNotFound
import pandas as pd
import pandas_ta as ta
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# === Check required packages ===
required_packages = ['pandas', 'pandas_ta', 'numpy', 'yfinance', 'matplotlib']
print("🔍 Checking required package versions...\n")
for pkg in required_packages:
    try:
        version = get_distribution(pkg).version
        print(f"✅ {pkg}: v{version}")
    except DistributionNotFound:
        print(f"❌ {pkg} is NOT installed. Please run: pip install {pkg}")
        exit(1)

# === Strategy Parameters ===
STOP_LOSS_PIPS = 0.0020
TAKE_PROFIT_PIPS = 0.0040
SPREAD = 0.0005
TRADE_SIZE = 1.0
MAX_HOLD = 12
MARKET_OPEN_HOUR = 6
MARKET_CLOSE_HOUR = 20

# ---
# === Fetch candles ===
def fetch_and_prepare_data(symbol="EURUSD=X", min_valid_rows=150):
    # Try multiple interval/period combinations
    attempts = [
        ("5m", "7d"),
        ("5m", "14d"),
        ("15m", "14d"),
        ("15m", "30d"),
        ("1h", "30d"),
        ("1h", "60d")
    ]

    for interval, period in attempts:
        print(f"📦 Trying {symbol} | Interval: {interval} | Period: {period}")
        # Use auto_adjust=False for consistent 'Open', 'High', 'Low', 'Close' values
        # We will handle 'Adj Close' if it appears, but for forex, 'Close' is typically the one.
        df = yf.download(symbol, interval=interval, period=period, auto_adjust=False, progress=False)

        if df.empty or len(df) < min_valid_rows:
            print(f"⚠️ Not enough data: {len(df)} rows. Trying next option...")
            continue

        # Handle potential MultiIndex columns from yfinance, common with FX data
        if isinstance(df.columns, pd.MultiIndex):
            # Flatten MultiIndex by taking the last level (e.g., 'Close' from ('EURUSD=X', 'Close'))
            df.columns = [col[-1] if isinstance(col, tuple) else col for col in df.columns]

        df = df.reset_index()

        # Standardize Datetime column name
        if 'Datetime' not in df.columns:
            # yfinance uses 'index' for intraday and 'Date' for daily data
            if 'index' in df.columns:
                df['Datetime'] = pd.to_datetime(df['index'])
            elif 'Date' in df.columns:
                df['Datetime'] = pd.to_datetime(df['Date'])
            else:
                # Fallback: if neither, assume the first column is the datetime index
                print("Warning: Datetime column not found as 'index' or 'Date'. Assuming first column is datetime.")
                df['Datetime'] = pd.to_datetime(df.iloc[:, 0])

        # Ensure essential columns are present and numeric
        required_ohlc = ['Open', 'High', 'Low', 'Close']
        if not all(col in df.columns for col in required_ohlc):
            print(f"❌ Missing one or more OHLC columns ({required_ohlc}). Skipping this attempt.")
            continue

        for col in required_ohlc:
            df[col] = pd.to_numeric(df[col], errors='coerce') # Coerce non-numeric to NaN

        df['Hour'] = df['Datetime'].dt.hour

        # Select only the necessary columns BEFORE indicator calculation
        # This prevents issues if there are other unexpected columns
        df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Hour']].copy()

        # Compute indicators
        df['EMA_9'] = ta.ema(df['Close'], length=9)
        df['SMA_21'] = ta.sma(df['Close'], length=21)
        df['RSI'] = ta.rsi(df['Close'], length=14)

        # Drop rows with NaN values introduced by indicators
        # Now we are certain the columns exist if the above steps were successful
        df.dropna(subset=['EMA_9', 'SMA_21', 'RSI'], inplace=True)

        if len(df) >= min_valid_rows:
            print(f"✅ Successfully prepared data with {len(df)} valid candles.")
            return df, interval
        else:
            print(f"⚠️ Indicators dropped too many rows. Left with {len(df)} candles. Trying next option...")

    print(f"❌ All attempts failed. No valid data for {symbol}.")
    return None, None

# ---
# === Add signals with stricter rules ===
def add_ma_signals(df):
    # Check for precomputed indicators (added as a safeguard, but should be handled by fetch_and_prepare_data)
    for col in ['EMA_9', 'SMA_21', 'RSI']:
        if col not in df.columns:
            raise KeyError(f"Missing expected column: {col}. Indicator calculation failed upstream.")

    # Drop any remaining NaNs after calculations if any, though ideally handled by fetch_and_prepare_data
    df.dropna(subset=['EMA_9', 'SMA_21', 'RSI'], inplace=True) # Redundant if fetch_and_prepare_data works, but harmless

    # Calculate recent high/low BEFORE current row to prevent look-ahead bias
    df['recent_high_before'] = df['High'].rolling(window=10).max().shift(1)
    df['recent_low_before'] = df['Low'].rolling(window=10).min().shift(1)

    df['signal'] = 0
    df['signal_text'] = "Hold"

    # Define strong buy/sell conditions
    breakout_buy = (
        (df['EMA_9'] > df['SMA_21']) &
        (df['EMA_9'].shift(1) <= df['SMA_21'].shift(1)) & # Crossover condition
        (df['Close'] > df['recent_high_before']) & # Breakout condition
        (df['Open'] < df['recent_high_before']) & # Ensure candle opened below breakout level
        (df['RSI'] > 55) # RSI confirmation for strength
    )

    breakout_sell = (
        (df['EMA_9'] < df['SMA_21']) &
        (df['EMA_9'].shift(1) >= df['SMA_21'].shift(1)) & # Crossover condition
        (df['Close'] < df['recent_low_before']) & # Breakout condition
        (df['Open'] > df['recent_low_before']) & # Ensure candle opened above breakout level
        (df['RSI'] < 45) # RSI confirmation for strength
    )

    df.loc[breakout_buy, 'signal'] = 2
    df.loc[breakout_buy, 'signal_text'] = "Strong Buy"
    df.loc[breakout_sell, 'signal'] = -2
    df.loc[breakout_sell, 'signal_text'] = "Strong Sell"
    return df

# ---
# === Backtest engine ===
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
        
        # Check if current time is within market hours
        if hour < MARKET_OPEN_HOUR or hour >= MARKET_CLOSE_HOUR:
            # If a position is open, consider closing it at the end of market hours
            if position is not None:
                # Close at current close price as market is closing for strategy
                exit_price = row['Close']
                profit = 0
                if position == 'long':
                    profit = (exit_price - entry_price) * TRADE_SIZE
                    trades.append(f"MARKET CLOSE EXIT (LONG) @ {exit_price:.5f} | PROFIT = {profit:.5f} | Time: {row['Datetime']}")
                elif position == 'short':
                    profit = (entry_price - exit_price) * TRADE_SIZE
                    trades.append(f"MARKET CLOSE EXIT (SHORT) @ {exit_price:.5f} | PROFIT = {profit:.5f} | Time: {row['Datetime']}")
                balance += profit
                position = None # Close position
            equity_curve.append(balance)
            i += 1
            continue # Skip trade logic outside market hours

        price = row['Close']
        signal = row['signal']
        signal_text = row['signal_text']

        if position is None:
            # Only enter on Strong Buy/Sell signals within market hours
            if signal == 2:
                position = 'long'
                entry_price = price + SPREAD
                trades.append(f"STRONG BUY @ {entry_price:.5f} | Time: {row['Datetime']}")
                # No increment here, loop will increment i
            elif signal == -2:
                position = 'short'
                entry_price = price - SPREAD
                trades.append(f"STRONG SELL @ {entry_price:.5f} | Time: {row['Datetime']}")
                # No increment here, loop will increment i
        else: # If a position is open, check for exits
            # We look ahead MAX_HOLD candles or until end of df,
            # but only consider candles within market hours for SL/TP
            # The 'j' loop will find the first candle that triggers an exit or the end of MAX_HOLD
            # and that candle must be within market hours.
            exit_triggered = False
            for j in range(i, min(i + MAX_HOLD + 1, len(df))): # Start from current candle 'i' for exits
                future_row = df.iloc[j]
                if future_row['Hour'] < MARKET_OPEN_HOUR or future_row['Hour'] >= MARKET_CLOSE_HOUR:
                    continue # Skip checking SL/TP if outside market hours

                high = future_row['High']
                low = future_row['Low']
                current_candle_close = future_row['Close'] # For time-based exit

                if position == 'long':
                    if low <= entry_price - STOP_LOSS_PIPS:
                        exit_price = entry_price - STOP_LOSS_PIPS
                        profit = (exit_price - entry_price) * TRADE_SIZE
                        trades.append(f"SL HIT (LONG) @ {exit_price:.5f} | PROFIT = {profit:.5f} | Time: {future_row['Datetime']}")
                        balance += profit
                        position = None
                        i = j # Move main loop index to the exit candle
                        exit_triggered = True
                        break
                    elif high >= entry_price + TAKE_PROFIT_PIPS:
                        exit_price = entry_price + TAKE_PROFIT_PIPS
                        profit = (exit_price - entry_price) * TRADE_SIZE
                        trades.append(f"TP HIT (LONG) @ {exit_price:.5f} | PROFIT = {profit:.5f} | Time: {future_row['Datetime']}")
                        balance += profit
                        position = None
                        i = j # Move main loop index to the exit candle
                        exit_triggered = True
                        break

                elif position == 'short':
                    if high >= entry_price + STOP_LOSS_PIPS:
                        exit_price = entry_price + STOP_LOSS_PIPS # Corrected for short SL calculation
                        profit = (entry_price - exit_price) * TRADE_SIZE # Profit calculation for short
                        trades.append(f"SL HIT (SHORT) @ {exit_price:.5f} | PROFIT = {profit:.5f} | Time: {future_row['Datetime']}")
                        balance += profit
                        position = None
                        i = j # Move main loop index to the exit candle
                        exit_triggered = True
                        break
                    elif low <= entry_price - TAKE_PROFIT_PIPS:
                        exit_price = entry_price - TAKE_PROFIT_PIPS
                        profit = (entry_price - exit_price) * TRADE_SIZE # Profit calculation for short
                        trades.append(f"TP HIT (SHORT) @ {exit_price:.5f} | PROFIT = {profit:.5f} | Time: {future_row['Datetime']}")
                        balance += profit
                        position = None
                        i = j # Move main loop index to the exit candle
                        exit_triggered = True
                        break

            # If no SL/TP was hit within MAX_HOLD (or until end of data within market hours)
            if not exit_triggered and position is not None:
                # Use the close of the last considered candle in the MAX_HOLD window (or the last valid candle if less than MAX_HOLD candles remain)
                exit_price = df.iloc[min(i + MAX_HOLD, len(df) - 1)]['Close']
                if position == 'long':
                    profit = (exit_price - entry_price) * TRADE_SIZE
                    trades.append(f"TIME EXIT (LONG) @ {exit_price:.5f} | PROFIT = {profit:.5f} | Time: {df.iloc[min(i + MAX_HOLD, len(df) - 1)]['Datetime']}")
                elif position == 'short':
                    profit = (entry_price - exit_price) * TRADE_SIZE
                    trades.append(f"TIME EXIT (SHORT) @ {exit_price:.5f} | PROFIT = {profit:.5f} | Time: {df.iloc[min(i + MAX_HOLD, len(df) - 1)]['Datetime']}")
                balance += profit
                position = None
                i = min(i + MAX_HOLD, len(df) - 1) # Advance index to the point where the trade would have closed

        equity_curve.append(balance)
        i += 1

    return trades, balance, equity_curve, df

# ---
# === Reporting ===
def report(trades, balance, equity_curve, df, symbol, start=1000):
    print(f"\n📊 BACKTEST RESULT FOR {symbol}")
    print("="*60)
    if not trades:
        print("No trades were executed during this backtest period.")
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
    # Collect points for trades only if there are trades
    if trades:
        for t in trades:
            if "PROFIT = " in t:
                try:
                    profit = float(t.split("PROFIT = ")[1].split(' | Time:')[0]) # Extract profit before ' | Time:'
                    equity += profit
                    equity_points.append(equity)
                    colors.append("green" if profit > 0 else "red")
                except IndexError:
                    # Handle cases where "PROFIT =" might not be fully parsed (e.g., initial entries)
                    pass

    if equity_points: # Only plot scatter if there are actual trade profit points
        plt.scatter(range(len(equity_points)), equity_points, c=colors, s=60, label="Trades", edgecolor='black', zorder=5) # zorder to ensure points are on top
    plt.axhline(y=start, color='gray', linestyle='--', label='Initial Balance')
    plt.title(f"Equity Curve for {symbol} (Green = Win, Red = Loss)")
    plt.xlabel("Trade Number (or Candle Index for Equity Curve)")
    plt.ylabel("Balance")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# ---
# === MAIN ===
if __name__ == "__main__":
    # Hardcode the symbol to EURUSD=X
    user_symbol = "EURUSD=X"

    df, interval = fetch_and_prepare_data(symbol=user_symbol)
    if df is not None:
        try:
            df = add_ma_signals(df)
            trades, final_balance, equity_curve, df = run_backtest(df)
            report(trades, final_balance, equity_curve, df, f"{user_symbol} [{interval}]")
            print("\n✅ Backtest completed successfully!")
        except Exception as e:
            print(f"❌ ERROR in processing {user_symbol}: {e}")