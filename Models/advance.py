import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt

# Function to calculate the RSI (Relative Strength Index)

# Function to calculate the RSI (Relative Strength Index)
def calculate_rsi(series, window=14):
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    rs.replace([np.inf, -np.inf], np.nan, inplace=True)  # Handle division by zero
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# Step 1: Download Vedanta stock data
stock_data = yf.download('VEDL.NS', start='2020-01-01', end='2024-09-12')

# Step 2: Add Technical Indicators (SMA, RSI)
stock_data['SMA50'] = stock_data['Close'].rolling(window=50).mean()
stock_data['SMA200'] = stock_data['Close'].rolling(window=200).mean()
stock_data['RSI'] = calculate_rsi(stock_data['Close'], window=14)

# Drop rows with NaN values (created by rolling calculations)
stock_data.dropna(inplace=True)

# Verify data integrity
# print(stock_data.head())
# print(stock_data.shape)
# print(stock_data)
stock_data.to_csv('D:/! Kalash/AI/Models/Stocks/Data/vedanta_test.csv')

# Drop NaN values created by rolling calculations
stock_data = stock_data.dropna()

# Step 3: Preprocess the data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(stock_data[['Close', 'SMA50', 'SMA200', 'RSI']].values)

train_size = int(len(scaled_data) * 0.8)
train_data, test_data = scaled_data[:train_size], scaled_data[train_size:]

# Create dataset with time steps
def create_dataset(data, time_step=60):
    X, Y = [], []
    for i in range(time_step, len(data)):
        X.append(data[i-time_step:i, :])  # Use all features (Close, SMA, RSI)
        Y.append(data[i, 0])  # Predicting the next close price
    return np.array(X), np.array(Y)

time_step = 60  # The number of previous days used to predict the next
X_train, Y_train = create_dataset(train_data, time_step)
X_test, Y_test = create_dataset(test_data, time_step)

# Reshape the input for LSTM: [samples, time steps, features]
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2])
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[2])

# Step 4: Build a deeper LSTM model
model = Sequential()
model.add(LSTM(units=100, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dropout(0.3))
model.add(LSTM(units=100, return_sequences=False))
model.add(Dropout(0.3))
model.add(Dense(units=1))  # Predict the next closing price
model.compile(optimizer='adam', loss='mean_squared_error')

# Step 5: Train the model
model.fit(X_train, Y_train, epochs=50, batch_size=4)

# Step 6: Make predictions
predicted_stock_price = model.predict(X_test)
predicted_stock_price = scaler.inverse_transform(np.concatenate((predicted_stock_price, X_test[:, -1, 1:]), axis=1))[:, 0]
real_stock_price = scaler.inverse_transform(np.concatenate((Y_test.reshape(-1, 1), X_test[:, -1, 1:]), axis=1))[:, 0]

# Step 7: Calculate accuracy score for stock movement prediction

# Convert real and predicted stock prices to binary movement (1 = price increased, 0 = price decreased)
real_movement = np.where(np.diff(real_stock_price.flatten()) > 0, 1, 0)
predicted_movement = np.where(np.diff(predicted_stock_price.flatten()) > 0, 1, 0)

# Calculate accuracy score
accuracy = accuracy_score(real_movement, predicted_movement)

# Step 8: Calculate and print RMSE and accuracy
rmse = np.sqrt(mean_squared_error(real_stock_price, predicted_stock_price))

print(f"RMSE: {rmse}")
print(f"Accuracy Score: {accuracy}")

# Step 9: Plot the results
plt.figure(figsize=(14,7))
plt.plot(real_stock_price, color='blue', label='Real Stock Price')
plt.plot(predicted_stock_price, color='red', label='Predicted Stock Price')
plt.title('Vedanta Stock Price Prediction with LSTM')
plt.xlabel('Time')
plt.ylabel('Stock Price')
plt.legend()
plt.show()