import numpy as np
import yfinance as yf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

def predict_with_lstm(symbol):

    data = yf.download(symbol, period="6mo", progress=False)

    if data.empty:
        return None

    close_prices = data["Close"].values.reshape(-1, 1)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(close_prices)

    X, y = [], []
    for i in range(60, len(scaled)):
        X.append(scaled[i-60:i])
        y.append(scaled[i])

    X, y = np.array(X), np.array(y)

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(60,1)),
        LSTM(50),
        Dense(1)
    ])

    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=3, batch_size=16, verbose=0)

    last_60 = scaled[-60:]
    last_60 = np.reshape(last_60, (1,60,1))

    predicted = model.predict(last_60)
    predicted_price = scaler.inverse_transform(predicted)[0][0]

    return float(predicted_price)