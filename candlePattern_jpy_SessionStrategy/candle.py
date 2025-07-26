import numpy as np
import pandas as pd
from tqdm import tqdm
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from backtesting import Backtest, Strategy
 # TA-Lib removed; using pure-Pandas ATR below

tqdm.pandas()    

# ========== Generate Dummy Data ==========
# (for quick testing—you can replace this with real CSV data later)
def generate_dummy_data(num_rows=5000):
    date_rng = pd.date_range(start='2024-01-01', periods=num_rows, freq='5min')
    prices = np.cumsum(np.random.normal(0, 0.0006, size=num_rows)) + 1.1000
    high = prices + np.random.uniform(0.0004, 0.0009, size=num_rows)
    low = prices - np.random.uniform(0.0004, 0.0009, size=num_rows)
    open_ = prices + np.random.uniform(-0.00025, 0.00025, size=num_rows)
    close = prices + np.random.uniform(-0.00025, 0.00025, size=num_rows)

    df = pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close}, index=date_rng)
    df.index.name = "Gmt time"
    return df

# ========== Signal Logic ==========
def total_signal(df, current_candle):
    try:
        idx = df.index.get_loc(current_candle)
        if idx < 2:
            return 0
        c1 = df.Low.iloc[idx] > df.Low.iloc[idx - 1]
        c2 = df.Low.iloc[idx - 1] < df.Low.iloc[idx - 2]
        c3 = (df.Close.iloc[idx] - df.Close.iloc[idx - 1]) / df.Close.iloc[idx - 1] > 0.0001
        if c1 and c2 and c3:
            return 2
        c1 = df.High.iloc[idx] < df.High.iloc[idx - 1]
        c2 = df.High.iloc[idx - 1] > df.High.iloc[idx - 2]
        c3 = (df.Close.iloc[idx - 1] - df.Close.iloc[idx]) / df.Close.iloc[idx] > 0.0001
        if c1 and c2 and c3:
            return 1
        return 0
    except:
        return 0

def add_total_signal(df):
    df['TotalSignal'] = df.progress_apply(lambda r: total_signal(df, r.name), axis=1)
    return df

def add_pointpos_column(df, sigcol):
    df['pointpos'] = df.apply(lambda r: (r.Low - 0.0005) if r[sigcol] == 2
                               else (r.High + 0.0005) if r[sigcol] == 1 else np.nan, axis=1)
    return df

# ========== Strategy Class with Fixes ==========
def SIGNAL():
    return df.TotalSignal

class MyStrategy(Strategy):
    mysize = 0.2

    def init(self):
        self.signal1 = self.I(SIGNAL)
        self.ordertime = []
        # Pure-Pandas ATR implementation
        def atr_func():
            hl = self.data.High - self.data.Low
            hc = abs(self.data.High - self.data.Close.shift())
            lc = abs(self.data.Low - self.data.Close.shift())
            tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
            return tr.rolling(14).mean()
        self.atr = self.I(atr_func)
        self.ma = self.I(lambda: self.data.Close.rolling(20).mean())

    def next(self):
        self.cancel_old_orders()
        self.manage_trades()
        self.handle_signals()

    def cancel_old_orders(self):
        i = 0
        while i < len(self.orders):
            if (self.data.index[-1] - self.ordertime[i]) > pd.Timedelta(days=2):
                self.orders[i].cancel()
                self.ordertime.pop(i)
            else:
                i += 1

    def manage_trades(self):
        for trade in self.trades:
            if (self.data.index[-1] - trade.entry_time) >= pd.Timedelta(days=2):
                trade.close()
            # also closing on profit/loss is automatically handled by SL/TP

    def handle_signals(self):
        atr = self.atr[-1]
        ma = self.ma[-1]
        price = self.data.Close[-1]

        if np.isnan(atr) or atr < 0.0004:
            return

        if self.signal1[-1] == 2 and not self.position and price > ma:
            self.cancel_all_orders()
            sl = price - 1.5 * atr
            tp = price + 3 * atr
            self.buy(size=self.mysize, sl=sl, tp=tp)
            self.ordertime.append(self.data.index[-1])

        elif self.signal1[-1] == 1 and not self.position and price < ma:
            self.cancel_all_orders()
            sl = price + 1.5 * atr
            tp = price - 3 * atr
            self.sell(size=self.mysize, sl=sl, tp=tp)
            self.ordertime.append(self.data.index[-1])

    def cancel_all_orders(self):
        while self.orders:
            self.orders[0].cancel()
            self.ordertime.pop(0)

# ========== Run Backtest ==========
df = generate_dummy_data()
df = add_total_signal(df)
df = add_pointpos_column(df, "TotalSignal")

bt = Backtest(df, MyStrategy, cash=5000, margin=1/5, commission=0.0002)
results = bt.run()

# ========== Charting ==========
def plot_candlestick_with_equity_and_trades(df, equity_curve, trades, start=0, rows=200):
    df_sub = df.iloc[start:start + rows]
    eq_sub = equity_curve.iloc[start:start + rows]

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])

    fig.add_trace(go.Candlestick(x=df_sub.index, open=df_sub.Open, high=df_sub.High,
                                 low=df_sub.Low, close=df_sub.Close, name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_sub.index, y=df_sub.pointpos, mode='markers',
                             marker=dict(size=8, color='MediumPurple'), name='Signal'), row=1, col=1)

    if trades is not None and not trades.empty:
        buys = trades[trades.Size > 0]
        sells = trades[trades.Size < 0]
        fig.add_trace(go.Scatter(x=buys.EntryTime, y=df.loc[buys.EntryTime, 'Open'],
                                 mode='markers', marker=dict(size=10, color='white', symbol='triangle-up'),
                                 name='Buy'), row=1, col=1)
        fig.add_trace(go.Scatter(x=sells.EntryTime, y=df.loc[sells.EntryTime, 'Open'],
                                 mode='markers', marker=dict(size=10, color='yellow', symbol='triangle-down'),
                                 name='Sell'), row=1, col=1)
        fig.add_trace(go.Scatter(x=trades.ExitTime, y=df.loc[trades.ExitTime, 'Open'],
                                 mode='markers', marker=dict(size=10, color='red', symbol='x'),
                                 name='Exit'), row=1, col=1)

    fig.add_trace(go.Scatter(x=eq_sub.index, y=eq_sub.Equity, mode='lines',
                             line=dict(color='deepskyblue', width=2), name='Equity'), row=2, col=1)

    fig.update_layout(width=1200, height=800, plot_bgcolor='black', paper_bgcolor='black',
                      font=dict(color='white'), showlegend=True)
    fig.show()

plot_candlestick_with_equity_and_trades(df, results['_equity_curve'], results['_trades'])

# ========== Print Metrics ==========
print("\n📈 Backtest Summary:")
for k, v in results.items():
    if isinstance(v, (float, int, str)):
        print(f"{k}: {v}")

# Calculate Win Rate
if '_trades' in results:
    trades = results['_trades']
    wr = (trades.PnL > 0).sum() / len(trades) * 100
    print(f"Win Rate: {wr:.2f}%")
