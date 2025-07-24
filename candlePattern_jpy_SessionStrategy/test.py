import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from backtesting import Backtest, Strategy

tqdm.pandas()

# ========== Generate Dummy Data ==========
def generate_dummy_data(num_rows=500):
    date_rng = pd.date_range(start='2024-01-01', periods=num_rows, freq='5min')
    prices = np.cumsum(np.random.normal(0, 0.0005, size=num_rows)) + 1.1000
    high = prices + np.random.uniform(0.0003, 0.0008, size=num_rows)
    low = prices - np.random.uniform(0.0003, 0.0008, size=num_rows)
    open_ = prices + np.random.uniform(-0.0002, 0.0002, size=num_rows)
    close = prices + np.random.uniform(-0.0002, 0.0002, size=num_rows)

    df = pd.DataFrame({
        "Open": open_,
        "High": high,
        "Low": low,
        "Close": close
    }, index=date_rng)
    df.index.name = "Gmt time"
    return df

# ========== Signal Logic ==========
def total_signal(df, current_candle):
    try:
        current_pos = df.index.get_loc(current_candle)
        if current_pos < 2:
            return 0

        c1 = df['Low'].iloc[current_pos] > df['Low'].iloc[current_pos - 1]
        c2 = df['Low'].iloc[current_pos - 1] < df['Low'].iloc[current_pos - 2]
        c3 = ((df['Close'].iloc[current_pos] - df['Close'].iloc[current_pos - 1]) /
              df['Close'].iloc[current_pos - 1]) > 0.0001
        if c1 and c2 and c3:
            return 2

        c1 = df['High'].iloc[current_pos] < df['High'].iloc[current_pos - 1]
        c2 = df['High'].iloc[current_pos - 1] > df['High'].iloc[current_pos - 2]
        c3 = ((df['Close'].iloc[current_pos - 1] - df['Close'].iloc[current_pos]) /
              df['Close'].iloc[current_pos]) > 0.0001
        if c1 and c2 and c3:
            return 1

        return 0
    except:
        return 0

def add_total_signal(df):
    df['TotalSignal'] = df.progress_apply(lambda row: total_signal(df, row.name), axis=1)
    return df

def add_pointpos_column(df, signal_column):
    def pointpos(row):
        if row[signal_column] == 2:
            return row['Low'] - 0.0005
        elif row[signal_column] == 1:
            return row['High'] + 0.0005
        else:
            return np.nan
    df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)
    return df

# ========== Plotting ==========
def plot_candlestick_with_signals(df, start_index=0, num_rows=100):
    df_subset = df.iloc[start_index:start_index + num_rows]
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Candlestick(
        x=df_subset.index,
        open=df_subset['Open'],
        high=df_subset['High'],
        low=df_subset['Low'],
        close=df_subset['Close'],
        name='Candlesticks'), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df_subset.index,
        y=df_subset['pointpos'],
        mode='markers',
        marker=dict(size=10, color='MediumPurple', symbol='circle'),
        name='Signals'), row=1, col=1)
    fig.update_layout(
        width=1200, height=700,
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'))
    fig.show()

def plot_candlestick_with_equity_and_trades(df, equity_curve, trades, start_index=0, num_rows=100):
    df_subset = df.iloc[start_index:start_index + num_rows]
    eq_subset = equity_curve.iloc[start_index:start_index + num_rows]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df_subset.index,
        open=df_subset['Open'],
        high=df_subset['High'],
        low=df_subset['Low'],
        close=df_subset['Close'],
        name='Candlesticks'), row=1, col=1)
    # Signal markers
    fig.add_trace(go.Scatter(
        x=df_subset.index,
        y=df_subset['pointpos'],
        mode='markers',
        marker=dict(size=10, color='MediumPurple', symbol='circle'),
        name='Signals'), row=1, col=1)
    # Trade entry/exit markers
    if trades is not None and not trades.empty:
        # Buy entries (Size > 0)
        buy_entries = trades[(trades['Size'] > 0) & (trades['EntryTime'] >= df_subset.index[0]) & (trades['EntryTime'] <= df_subset.index[-1])]
        # Sell entries (Size < 0)
        sell_entries = trades[(trades['Size'] < 0) & (trades['EntryTime'] >= df_subset.index[0]) & (trades['EntryTime'] <= df_subset.index[-1])]
        exits = trades['ExitTime'][(trades['ExitTime'] >= df_subset.index[0]) & (trades['ExitTime'] <= df_subset.index[-1])]
        # Buy entry markers (white)
        fig.add_trace(go.Scatter(
            x=buy_entries['EntryTime'],
            y=df.loc[buy_entries['EntryTime'], 'Open'],
            mode='markers',
            marker=dict(size=12, color='white', symbol='triangle-up'),
            name='Buy Entry'), row=1, col=1)
        # Sell entry markers (yellow)
        fig.add_trace(go.Scatter(
            x=sell_entries['EntryTime'],
            y=df.loc[sell_entries['EntryTime'], 'Open'],
            mode='markers',
            marker=dict(size=12, color='yellow', symbol='triangle-up'),
            name='Sell Entry'), row=1, col=1)
        # Trade exit markers (red)
        fig.add_trace(go.Scatter(
            x=exits,
            y=df.loc[exits, 'Open'],
            mode='markers',
            marker=dict(size=12, color='red', symbol='triangle-down'),
            name='Trade Exit'), row=1, col=1)
    # Equity curve
    fig.add_trace(go.Scatter(
        x=eq_subset.index,
        y=eq_subset['Equity'],
        mode='lines',
        line=dict(color='deepskyblue', width=2),
        name='Equity Curve'), row=2, col=1)
    fig.update_layout(
        width=1200, height=900,
        plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    fig.show()

# ========== Strategy ==========
def SIGNAL():
    return df.TotalSignal

class MyStrategy(Strategy):
    mysize = 0.2
    def init(self):
        self.signal1 = self.I(SIGNAL)
        self.ordertime = []

    def next(self):
        self.cancel_old_orders()
        self.manage_trades()
        self.handle_signals()

    def cancel_old_orders(self):
        i = 0
        while i < len(self.orders):
            order_age = self.data.index[-1] - self.ordertime[i]
            if order_age > pd.Timedelta(days=2):
                self.orders[i].cancel()
                self.ordertime.pop(i)
            else:
                i += 1

    def manage_trades(self):
        for trade in self.trades:
            trade_duration = self.data.index[-1] - trade.entry_time
            if trade_duration >= pd.Timedelta(days=2) or trade.pl > 0:
                trade.close()

    def handle_signals(self):
        if self.signal1[-1] == 2 and not self.position:
            self.cancel_all_orders()
            self.buy(size=self.mysize, stop=self.data.High[-1])
            self.ordertime.append(self.data.index[-1])
        elif self.signal1[-1] == 1 and not self.position:
            self.cancel_all_orders()
            self.sell(size=self.mysize, stop=self.data.Low[-1])
            self.ordertime.append(self.data.index[-1])

    def cancel_all_orders(self):
        while self.orders:
            self.orders[0].cancel()
            self.ordertime.pop(0)

# ========== Run Everything ==========
df = generate_dummy_data()
df = add_total_signal(df)
df = add_pointpos_column(df, "TotalSignal")

print("✅ Signal counts:\n", df["TotalSignal"].value_counts())

bt = Backtest(df, MyStrategy, cash=5000, margin=1/5, commission=0.0002)
results = bt.run()

# 📊 Combined Candlestick + Equity + Trades plot
plot_candlestick_with_equity_and_trades(
    df,
    results['_equity_curve'],
    results['_trades'] if '_trades' in results else None,
    start_index=0,
    num_rows=150
)

# ========== 📈 Summary, 📊 Equity Curve, 📋 Trades ==========
def clean_value(val):
    if isinstance(val, pd.DataFrame):
        return "DataFrame"
    if val is None or val == "NaT":
        return "N/A"
    if isinstance(val, (float, int)):
        return f"{val:.4f}"
    if isinstance(val, pd.Timestamp):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(val, pd.Timedelta):
        return str(val)
    return str(val)

# 📈 Summary
print("\n📈 Backtest Results Summary:")
for key, value in results.items():
    if isinstance(value, pd.DataFrame):
        continue  # skip printing DataFrames in summary
    print(f"{key}: {clean_value(value)}")

# 📊 Equity Curve (last 5 rows)
print("\n📊 Equity Curve (last 5 rows):")
print(results['_equity_curve'].tail())

# 📋 Trade Log (last 5 trades)
print("\n📋 Trades (last 5):")
if '_trades' in results:
    print(results['_trades'][['EntryTime', 'ExitTime', 'Size', 'EntryPrice', 'ExitPrice', 'PnL']].tail())
    print(f"\n🔍 Total Closed Trades: {len(results['_trades'])}")
else:
    print("No trades executed.")

# Plot interactive backtest result
bt.plot()
