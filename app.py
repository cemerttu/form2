from flask import Flask, jsonify, request
import pandas as pd
import pandas_ta as ta
import yfinance as yf

app = Flask(__name__)

# === Root route ===
@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Signal API! Visit /signal to get signals."})

# === Fetch 5-minute candles ===
def fetch_5min_candles(n=500, symbol="EURUSD=X"):
    df = yf.download(symbol, interval="5m", period="7d", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df = df.tail(n).reset_index(drop=True)
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    return df

# === Add signal column ===
def add_signal(df):
    df['EMA_9'] = ta.ema(df['Close'], length=9)
    df['SMA_21'] = ta.sma(df['Close'], length=21)
    df['recent_high'] = df['High'].rolling(window=10, min_periods=1).max()
    df['recent_low'] = df['Low'].rolling(window=10, min_periods=1).min()
    df['signal'] = 0

    buy = (df['EMA_9'] > df['SMA_21']) & (df['EMA_9'].shift(1) <= df['SMA_21'].shift(1))
    sell = (df['EMA_9'] < df['SMA_21']) & (df['EMA_9'].shift(1) >= df['SMA_21'].shift(1))
    df.loc[buy, 'signal'] = 1
    df.loc[sell, 'signal'] = -1

    breakout_buy = (df['Close'] > df['recent_high'].shift(1)) & (df['signal'] == 1)
    breakout_sell = (df['Close'] < df['recent_low'].shift(1)) & (df['signal'] == -1)
    df.loc[breakout_buy, 'signal'] = 2
    df.loc[breakout_sell, 'signal'] = -2
    return df

# === Signal endpoint ===
@app.route("/signal")
def get_latest_signal():
    symbol = request.args.get("symbol", "EURUSD=X")
    try:
        df = fetch_5min_candles(500, symbol)
        df = add_signal(df)
        latest = df[df['signal'] != 0].iloc[-1:]

        if latest.empty:
            return jsonify({"message": "No signal generated"}), 200

        row = latest.iloc[0]
        signal_type = {
            1: "BUY", -1: "SELL", 2: "STRONG BUY", -2: "STRONG SELL"
        }.get(row['signal'], "HOLD")

        return jsonify({
            "symbol": symbol,
            "close": round(row['Close'], 5),
            "EMA_9": round(row['EMA_9'], 5),
            "SMA_21": round(row['SMA_21'], 5),
            "signal": row['signal'],
            "signal_type": signal_type
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === Run the app ===
if __name__ == "__main__":
    app.run(debug=True)
