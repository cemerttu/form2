import pandas as pd
import pandas_ta as ta
from oanda_candles import Pair, Gran, CandleClient

# Set your OANDA access token
access_token = "YOUR_OANDA_ACCESS_TOKEN"

def fetch_5min_candles(n=100):
    # Fetch last n 5-minute candles from OANDA
    client = CandleClient(access_token, real=False)
    collector = client.get_collector(Pair.EUR_USD, Gran.M5)
    candles = collector.grab(n)
    df = pd.DataFrame({
        'Open': [float(str(candle.bid.o)) for candle in candles],
        'High': [float(str(candle.bid.h)) for candle in candles],
        'Low': [float(str(candle.bid.l)) for candle in candles],
        'Close': [float(str(candle.bid.c)) for candle in candles]
    })
    return df

def add_ma_signals(df):
    # Calculate 12 EMA and 15 SMA
    df['EMA_12'] = ta.ema(df['Close'], length=12)
    df['SMA_15'] = ta.sma(df['Close'], length=15)
    # Generate signals: 1 for buy, -1 for sell, 0 for hold
    df['signal'] = 0
    df.loc[(df['EMA_12'] > df['SMA_15']) & (df['EMA_12'].shift(1) <= df['SMA_15'].shift(1)), 'signal'] = 1
    df.loc[(df['EMA_12'] < df['SMA_15']) & (df['EMA_12'].shift(1) >= df['SMA_15'].shift(1)), 'signal'] = -1
    return df

# Example usage:
df = fetch_5min_candles(100)
df = add_ma_signals(df)
print(df[['Close', 'EMA_12', 'SMA_15', 'signal']].tail(10))\




