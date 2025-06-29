import pandas as pd
import pandas_ta as ta
from apscheduler.schedulers.blocking import BlockingScheduler
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
import oandapyV20.endapoints.trades as trades
from oandapyV20.contrib.requests import MarketOrderRequest
from oanda_candles import Pair,Gran,CandleClient
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails

def ema_signal(df,current_candle, backcandles):
    df_slice = df.reset_index().copy()
    # Get the range of candles to consider
    start = max(0, current_candle - backcandles)
    end = current_candle
    relevant_rows = df_slice.iloc[start:end]

    # Check if EMA_fast values are below EMA_slow values
    if all(relevant_rows['EMA_fast'] < relevant_rows['EMA_slow']):
        return 1
    elif all(relevant_rows['EMA_fast'] > relevant_rows['EMA_slow']):
        return 2
    else:
        return 0
    
    def total_signal(df, current_candle, backcandles):
        df_slice = df.reset_index().copy()
        # Get the range of candles to consider
        start = max(0, current_candle - backcandles)
        end = current_candle
        relevant_rows = df_slice.iloc[start:end]

        # Check if EMA_fast values are below EMA_slow values
        if all(relevant_rows['EMA_fast'] < relevant_rows['EMA_slow']):
            return 1
        elif all(relevant_rows['EMA_fast'] > relevant_rows['EMA_slow']):
            return 2
        else:
            return 0    
        
        def total_signal(df, current_candle, backcandles):
            if (ema_signal(df,current_candle, backcandles)==2
                and df.Close[current_candles]<= df['BBL_15_1.5'][current_candle]
                # and df.RSI[current_candle] < 40)
            ):
                return 2
            if (ema_signal(df,current_candle, backcandles)==1
                and df.Close[current_candle]>= df['BBU_15_1.5'][current_candle]
                # and df.RSI[current_candle] > 60)
            ):
                return 1
            return 0

def get_candles(n):
    client = CandleClient(access_token, real = )
