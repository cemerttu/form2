import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from twelvedata import TDClient

# === Configuration ===
API_KEY = "9851f57e14cb45c9a1e71ece51bb93e4"
SYMBOL = "EUR/USD"
INTERVAL = "1day"
OUTPUTSIZE = 365
INITIAL_BALANCE = 1000.0
SPREAD = 0.0005
MAX_HOLD = 12

STOP_LOSS_PIPS = 20
TAKE_PROFIT_PIPS = 40
PIP_VALUE = 0.0001

# === Fetch data ===
def fetch_data():
    td = TDClient(apikey=API_KEY)
    ts = td.time_series(symbol=SYMBOL, interval=INTERVAL, outputsize=OUTPUTSIZE)
    df = ts.as_pandas()
    df.reset_index(inplace=True)
    df.rename(columns={"datetime": "Datetime", "open": "Open", "high": "High", "low": "Low", "close": "Close"}, inplace=True)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
    return df

# === Add indicators and signals ===
def add_signals(df):
    df['EMA_9'] = ta.ema(df['Close'], length=9)
    df['SMA_21'] = ta.sma(df['Close'], length=21)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['recent_high'] = df['High'].rolling(10).max().shift(1)
    df['recent_low'] = df['Low'].rolling(10).min().shift(1)
    df['signal'] = 0
    df['signal_text'] = 'Hold'

    buy = (df['EMA_9'] > df['SMA_21']) & (df['EMA_9'].shift(1) <= df['SMA_21'].shift(1)) & (df['Close'] > df['recent_high']) & (df['RSI'] > 50)
    sell = (df['EMA_9'] < df['SMA_21']) & (df['EMA_9'].shift(1) >= df['SMA_21'].shift(1)) & (df['Close'] < df['recent_low']) & (df['RSI'] < 50)

    df.loc[buy, 'signal'] = 2
    df.loc[buy, 'signal_text'] = 'Strong Buy'
    df.loc[sell, 'signal'] = -2
    df.loc[sell, 'signal_text'] = 'Strong Sell'
    return df

# === Assign dynamic risk mode based on market behavior ===
def assign_risk_mode(df):
    df['volatility'] = (df['High'] - df['Low']) / df['Close']
    df['trend_strength'] = abs(df['EMA_9'] - df['SMA_21']) / df['Close']

    df['risk_mode'] = 'Fixed'  # Default

    df.loc[
        (df['RSI'] > 65) & (df['trend_strength'] > 0.01) & (df['volatility'] > 0.01),
        'risk_mode'
    ] = 'Aggressive'

    df.loc[
        (df['RSI'].between(55, 65)) & (df['trend_strength'] > 0.005),
        'risk_mode'
    ] = 'Optimal'

    df.loc[
        (df['RSI'].between(45, 55)) | (df['trend_strength'] < 0.005),
        'risk_mode'
    ] = 'Conservative'

    return df

# === Dynamic trade size based on mode ===
def get_trade_size(balance, risk_mode):
    if risk_mode == "Fixed":
        return 1.0
    elif risk_mode == "Conservative":
        return balance * 0.005
    elif risk_mode == "Optimal":
        return balance * 0.01
    elif risk_mode == "Aggressive":
        return balance * 0.02
    else:
        return 1.0

# === Backtest ===
def backtest(df):
    balance = INITIAL_BALANCE
    equity = []
    position = None
    entry_price = 0
    trades = []

    for i in range(len(df)):
        row = df.iloc[i]
        signal = row['signal']
        price = row['Close']
        date = row['Datetime']
        risk_mode = row['risk_mode']

        if position is None:
            if signal == 2:
                entry_price = price + SPREAD
                position = 'long'
                entry_time = i
                size = get_trade_size(balance, risk_mode)
                trades.append((date, entry_price, f'BUY ({risk_mode})'))
            elif signal == -2:
                entry_price = price - SPREAD
                position = 'short'
                entry_time = i
                size = get_trade_size(balance, risk_mode)
                trades.append((date, entry_price, f'SELL ({risk_mode})'))
        else:
            for j in range(i+1, min(i + MAX_HOLD + 1, len(df))):
                r = df.iloc[j]
                high, low = r['High'], r['Low']
                exit_date = r['Datetime']

                if position == 'long':
                    sl = entry_price - STOP_LOSS_PIPS * PIP_VALUE
                    tp = entry_price + TAKE_PROFIT_PIPS * PIP_VALUE
                    if low <= sl:
                        pnl = (sl - entry_price) * size
                        balance += pnl
                        trades.append((exit_date, sl, f'SL LONG PnL={pnl:.2f}'))
                        position = None
                        break
                    elif high >= tp:
                        pnl = (tp - entry_price) * size
                        balance += pnl
                        trades.append((exit_date, tp, f'TP LONG PnL={pnl:.2f}'))
                        position = None
                        break

                elif position == 'short':
                    sl = entry_price + STOP_LOSS_PIPS * PIP_VALUE
                    tp = entry_price - TAKE_PROFIT_PIPS * PIP_VALUE
                    if high >= sl:
                        pnl = (entry_price - sl) * size
                        balance += pnl
                        trades.append((exit_date, sl, f'SL SHORT PnL={pnl:.2f}'))
                        position = None
                        break
                    elif low <= tp:
                        pnl = (entry_price - tp) * size
                        balance += pnl
                        trades.append((exit_date, tp, f'TP SHORT PnL={pnl:.2f}'))
                        position = None
                        break

            if position is not None and j == min(i + MAX_HOLD, len(df) - 1):
                final = df.iloc[j]
                exit_price = final['Close']
                if position == 'long':
                    pnl = (exit_price - entry_price) * size
                else:
                    pnl = (entry_price - exit_price) * size
                balance += pnl
                trades.append((final['Datetime'], exit_price, f'TIMEOUT PnL={pnl:.2f}'))
                position = None

        equity.append(balance)
    return trades, equity

# === Plotting ===
def plot(df, trades, equity):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    df_plot = df.set_index('Datetime')
    ax1.plot(df_plot['Close'], label='Close', color='black', alpha=0.6)

    for t in trades:
        if 'BUY' in t[2]:
            ax1.scatter(t[0], t[1], marker='^', color='green')
        elif 'SELL' in t[2]:
            ax1.scatter(t[0], t[1], marker='v', color='red')
        else:
            ax1.scatter(t[0], t[1], marker='x', color='blue')

    ax1.set_title("Price Chart with Trade Signals")
    ax1.set_ylabel("Price")
    ax1.legend()

    ax2 = ax1.twinx()
    ax2.plot(df['Datetime'], equity, label='Equity', color='blue', linestyle='--')
    ax2.axhline(INITIAL_BALANCE, color='gray', linestyle=':')
    ax2.set_ylabel("Balance")

    fig.tight_layout()
    plt.legend(loc="upper left")
    plt.show()

# === Run ===
if __name__ == "__main__":
    df = fetch_data()
    df = add_signals(df)
    df = assign_risk_mode(df)
    trades, equity = backtest(df)
    plot(df, trades, equity)
