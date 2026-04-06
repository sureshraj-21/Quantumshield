import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from config import LOOKBACK_PERIOD


def predict_stock_return(symbol):

    data = yf.download(
        symbol,
        period=LOOKBACK_PERIOD,
        progress=False
    )

    if data.empty:
        return 0.0

    df = pd.DataFrame()
    df["Close"] = data["Close"]

    # Feature Engineering
    df["Return"] = df["Close"].pct_change()
    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA10"] = df["Close"].rolling(10).mean()
    df["Volatility"] = df["Return"].rolling(5).std()

    df = df.dropna()

    if len(df) < 20:
        return 0.0

    # Target = Next day return
    df["Target"] = df["Return"].shift(-1)
    df = df.dropna()

    features = ["Return", "MA5", "MA10", "Volatility"]

    X = df[features].values
    y = df["Target"].values

    model = LinearRegression()
    model.fit(X, y)

    # Use latest row to predict next return
    last_row = df[features].iloc[-1].values.reshape(1, -1)

    predicted_return = model.predict(last_row)[0]

    return float(predicted_return)
def predict_stock_price(symbol, selected_date):

    data = yf.download(symbol, period="6mo", progress=False)

    if data.empty:
        return None

    data = data.reset_index()
    data["DayIndex"] = np.arange(len(data))

    features = ["DayIndex"]
    targets = ["Open", "High", "Low", "Close", "Volume"]

    predictions = {}

    future_index = len(data) + (
        pd.to_datetime(selected_date) - data["Date"].max()
    ).days

    for target in targets:
        y = data[target].values
        X = data[features].values

        model = LinearRegression()
        model.fit(X, y)

        pred = model.predict([[future_index]])[0]
        predictions[target] = float(pred)

    return predictions