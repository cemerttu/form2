import os
import numpy as np
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from tqdm import tqdm
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from backtesting import Strategy, Backtest

tqdm.pandas()

# ===================== Data Reading =====================
def read_csv_to_dataframe(file_path):
    try:
        df = pd.read_csv(file_path)

        if df.empty or df.isnull().all().all():
            print(f"⚠️ Skipping empty or NaN-only file: {file_path}")
            return None

        if "Gmt time" not in df.columns:
            print(f"⚠️ Skipping file with missing 'Gmt time': {file_path}")
            return None

        df["Gmt time"] = df["Gmt time"].astype(str).str.replace(".000", "", regex=False)
        df["Gmt time"] = pd.to_datetime(df["Gmt time"], format='%d.%m.%Y %H:%M:%S', errors='coerce')
        df.dropna(subset=["Gmt time", "Open", "High", "Low", "Close"], inplace=True)

        df = df[df["High"] != df["Low"]]
        df.set_index("Gmt time", inplace=True)
        return df

    except pd.errors.EmptyDataError:
        print(f"❌ Skipping completely empty file: {file_path}")
        return None
    except Exception as e:
        print(f"🚨 Error reading {file_path}: {e}")
        return None


def read_data_folder(folder_path="./data"):
    dataframes = []
    file_names = []

    for file_name in tqdm(os.listdir(folder_path)):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            df = read_csv_to_dataframe(file_path)
            if df is not None:
                dataframes.append(df)
                file_names.append(file_name)
    return dataframes, file_names

# ===================== Signal Logic =====================
def total_signal(df, current_candle):
    try:
        current_pos = df.index.get_loc(current_candle)
        if current_pos < 2:
            return 0

        c1 = df['Low'].iloc[current_pos] > df['Low'].iloc[current_pos - 1]
        c2 = df['Low'].iloc[current_pos - 1] < df['Low'].iloc[current_pos - 2]
        c3 = ((df['Close'].iloc[current_pos] - df['Close'].iloc[current_pos - 1]) /
              df['Close'].iloc[current_pos - 1]) > 0.005
        if c1 and c2 and c3:
            return 2

        c1 = df['High'].iloc[current_pos] < df['High'].iloc[current_pos - 1]
        c2 = df['High'].iloc[current_pos - 1] > df['High'].iloc[current_pos - 2]
        c3 = ((df['Close'].iloc[current_pos - 1] - df['Close'].iloc[current_pos]) /
              df['Close'].iloc[current_pos]) > 0.005
        if c1 and c2 and c3:
            return 1

        return 0
    except Exception:
        return 0


def add_total_signal(df):
    if df is None or df.empty:
        print("⚠️ Cannot compute total signal: DataFrame is empty or None")
        return df
    df['TotalSignal'] = df.progress_apply(lambda row: total_signal(df, row.name), axis=1)
    return df


def add_pointpos_column(df, signal_column):
    def pointpos(row):
        if row[signal_column] == 2:
            return row['Low'] - 1e-4
        elif row[signal_column] == 1:
            return row['High'] + 1e-4
        else:
            return np.nan

    df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)
    return df

# ===================== Visualization =====================
def plot_candlestick_with_signals(df, start_index, num_rows):
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
        x=df_subset.index, y=df_subset['pointpos'], mode="markers",
        marker=dict(size=10, color="MediumPurple", symbol='circle'),
        name="Entry Points"), row=1, col=1)

    fig.update_layout(
        width=1200, height=800, plot_bgcolor='black', paper_bgcolor='black',
        font=dict(color='white'), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    fig.show()

# ===================== Strategy Definition =====================
def SIGNAL():
    return df.TotalSignal

class Strat_02(Strategy):
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

# ===================== Backtest & Analysis =====================
folder_path = "./data"
dataframes, file_names = read_data_folder(folder_path)

# ✅ Prevent crashing if folder is empty
if len(dataframes) == 0:
    print("❌ No data found in the './data' folder. Please add valid .csv files.")
    exit()

# Preprocess all files
for i, df in enumerate(dataframes):
    print(f"📊 Processing file: {file_names[i]}")
    df = add_total_signal(df)
    df = add_pointpos_column(df, "TotalSignal")
    dataframes[i] = df

# ✅ Now safe to plot
plot_candlestick_with_signals(dataframes[0], 0, 355)

# Run backtests
results = []
for df in dataframes:
    bt = Backtest(df, Strat_02, cash=5000, margin=1/5, commission=0.0002)
    stats = bt.run()
    results.append(stats)

# ===================== Aggregate Stats =====================
agg_returns = sum([r["Return [%]"] for r in results])
num_trades = sum([r["# Trades"] for r in results])
max_drawdown = min([r["Max. Drawdown [%]"] for r in results])
avg_drawdown = sum([r["Avg. Drawdown [%]"] for r in results]) / len(results)
win_rate = sum([r["Win Rate [%]"] for r in results]) / len(results)
best_trade = max([r["Best Trade [%]"] for r in results])
worst_trade = min([r["Worst Trade [%]"] for r in results])
avg_trade = sum([r["Avg. Trade [%]"] for r in results]) / len(results)

print(f"Aggregated Returns: {agg_returns:.2f}%")
print(f"Number of Trades: {num_trades}")
print(f"Maximum Drawdown: {max_drawdown:.2f}%")
print(f"Average Drawdown: {avg_drawdown:.2f}%")
print(f"Win Rate: {win_rate:.2f}%")
print(f"Best Trade: {best_trade:.2f}%")
print(f"Worst Trade: {worst_trade:.2f}%")
print(f"Average Trade: {avg_trade:.2f}%")

# ===================== Equity Curve Plot =====================
equity_curves = [stats['_equity_curve']['Equity'] for stats in results]
max_length = max(len(equity) for equity in equity_curves)

padded_curves = []
for equity in equity_curves:
    last_val = equity.iloc[-1]
    padded = equity.tolist() + [last_val] * (max_length - len(equity))
    padded_curves.append(padded)

equity_df = pd.DataFrame(padded_curves).T
equity_df.plot(kind='line', figsize=(10, 6), legend=False)
plt.title("Equity Curves")
plt.xlabel("Time")
plt.ylabel("Equity")
plt.grid(True)
plt.show()
