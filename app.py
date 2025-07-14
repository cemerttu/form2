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
    df['signal'] = 0

    crossover = (df['EMA_9'] > df['SMA_21']) & (df['EMA_9'].shift(1) <= df['SMA_21'].shift(1))
    crossunder = (df['EMA_9'] < df['SMA_21']) & (df['EMA_9'].shift(1) >= df['SMA_21'].shift(1))

    df.loc[crossover, 'signal'] = 1
    df.loc[crossunder, 'signal'] = -1
    return df


# === Signal endpoint ===
@app.route("/signal")
def get_latest_signal():
    symbol = request.args.get("symbol", "EURUSD=X")
    try:
        df = fetch_5min_candles(500, symbol)
        df = add_signal(df)

        # Show the latest non-zero signal
        latest = df[df['signal'] != 0].iloc[-1:] if not df[df['signal'] != 0].empty else None

        if latest is None or latest.empty:
            return jsonify({"message": "No signal generated in the last 500 candles."}), 200

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



