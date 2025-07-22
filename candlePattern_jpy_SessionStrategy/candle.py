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

# ========== Backtest Strategy ==========
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

plot_candlestick_with_signals(df, start_index=0, num_rows=150)

bt = Backtest(df, MyStrategy, cash=5000, margin=1/5, commission=0.0002)
results = bt.run()
bt.plot()

# ========== Print Summary ==========
print("\n📈 Backtest Results Summary:")
for key, value in results.items():
    print(f"{key}: {value}")
