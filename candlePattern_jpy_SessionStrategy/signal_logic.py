import numpy as np
import pandas as pd

def strict_total_signal(df, current_candle):
    """
    Returns:
        2: Strict bullish signal
        1: Strict bearish signal
        0: No signal
    """
    try:
        current_pos = df.index.get_loc(current_candle)
        if current_pos < 2:
            return 0

        # Strict bullish signal: only if all conditions are met and not ambiguous
        bullish = (
            df['Low'].iloc[current_pos] > df['Low'].iloc[current_pos - 1]
            and df['Low'].iloc[current_pos - 1] < df['Low'].iloc[current_pos - 2]
            and ((df['Close'].iloc[current_pos] - df['Close'].iloc[current_pos - 1]) / max(abs(df['Close'].iloc[current_pos - 1]), 1e-8)) > 0.005
        )
        # Strict bearish signal: only if all conditions are met and not ambiguous
        bearish = (
            df['High'].iloc[current_pos] < df['High'].iloc[current_pos - 1]
            and df['High'].iloc[current_pos - 1] > df['High'].iloc[current_pos - 2]
            and ((df['Close'].iloc[current_pos - 1] - df['Close'].iloc[current_pos]) / max(abs(df['Close'].iloc[current_pos]), 1e-8)) > 0.005
        )

        # Only one signal per candle, bullish takes precedence if both (should not happen)
        if bullish and not bearish:
            return 2
        elif bearish and not bullish:
            return 1
        else:
            return 0
    except Exception:
        return 0

def add_strict_total_signal(df):
    if df is None or df.empty:
        print("⚠️ Cannot compute total signal: DataFrame is empty or None")
        return df
    df['TotalSignal'] = df.progress_apply(lambda row: strict_total_signal(df, row.name), axis=1)
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
