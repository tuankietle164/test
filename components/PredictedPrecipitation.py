import numpy as np
import pandas as pd
import datetime
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import MeanSquaredError
import os

# Hàm xử lý dữ liệu
def process_data(daily_data, hourly_data):
    hourly_df = pd.DataFrame(hourly_data)
    hourly_df['time'] = pd.to_datetime(hourly_df['time'])
    hourly_df.set_index('time', inplace=True)

    daily_cloudcover = hourly_df['cloudcover'].resample('D').median().reset_index()
    daily_relative_humidity = hourly_df['relative_humidity_2m'].resample('D').median().reset_index()
    daily_showers = hourly_df['showers'].resample('D').median().reset_index()

    daily_df = pd.DataFrame(daily_data)
    daily_df['time'] = pd.to_datetime(daily_df['time'])
    daily_df = pd.merge(daily_df, daily_cloudcover, on='time')
    daily_df = pd.merge(daily_df, daily_relative_humidity, on='time')
    daily_df = pd.merge(daily_df, daily_showers, on='time')

    features = ['temperature_2m_max', 'temperature_2m_min', 'sunshine_duration',
                'precipitation_probability_max', 'wind_speed_10m_max',
                'cloudcover', 'relative_humidity_2m', 'showers']

    daily_df['precipitation_sum_7d_mean'] = daily_df['precipitation_sum'].rolling(window=7).mean()
    daily_df['precipitation_sum_14d_mean'] = daily_df['precipitation_sum'].rolling(window=14).mean()
    daily_df['precipitation_sum_7d_std'] = daily_df['precipitation_sum'].rolling(window=7).std()
    daily_df['precipitation_sum_14d_std'] = daily_df['precipitation_sum'].rolling(window=14).std()
    daily_df['precipitation_sum_cumsum'] = daily_df['precipitation_sum'].cumsum()

    features += ['precipitation_sum_7d_mean', 'precipitation_sum_14d_mean', 
                 'precipitation_sum_7d_std', 'precipitation_sum_14d_std', 
                 'precipitation_sum_cumsum']

    daily_df.dropna(inplace=True)
    return daily_df, features

# Hàm tạo mô hình LSTM
def create_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer=Adam(learning_rate=0.001), loss=MeanSquaredError())  # Sử dụng đối tượng MeanSquaredError
    return model

# Huấn luyện mô hình và lưu
def train_and_save_models(daily_df, features):
    target = 'precipitation_sum'
    y = daily_df[target].values
    print(f"Shape of target variable y: {y.shape}")

    trend_features = ['precipitation_sum_7d_mean', 'precipitation_sum_14d_mean', 
                      'precipitation_sum_7d_std', 'precipitation_sum_14d_std', 
                      'precipitation_sum_cumsum']
    X_trend = daily_df[trend_features].values
    X_trend = X_trend.reshape((X_trend.shape[0], 1, X_trend.shape[1]))
    print(f"Shape of trend features X_trend: {X_trend.shape}")

    lstm_model = create_lstm_model((X_trend.shape[1], X_trend.shape[2]))
    lstm_model.fit(X_trend, y, epochs=50, batch_size=32, verbose=2, shuffle=False)

    trend_features_lstm = lstm_model.predict(X_trend)
    print(f"Shape of trend features from LSTM: {trend_features_lstm.shape}")

    X_combined = np.hstack((daily_df[features].values, trend_features_lstm))
    print(f"Shape of combined features X_combined: {X_combined.shape}")

    X_train_full, X_test, y_train_full, y_test = train_test_split(X_combined, y, test_size=0.2, shuffle=False)
    print(f"Shape of X_train_full: {X_train_full.shape}, Shape of y_train_full: {y_train_full.shape}")

    gb_model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        min_samples_split=5,
        min_samples_leaf=3,
        subsample=0.8,
        random_state=42
    )
    gb_model.fit(X_train_full, y_train_full)

    # Tạo thư mục lưu mô hình nếu chưa có
    if not os.path.exists('models'):
        os.makedirs('models')

    # Lưu mô hình
    lstm_model.save('models/lstm_model.h5')
    joblib.dump(gb_model, 'models/gb_model.pkl')

    return gb_model, lstm_model

# Tải mô hình đã lưu
def load_models():
    lstm_model_path = 'models/lstm_model.h5'
    gb_model_path = 'models/gb_model.pkl'

    if os.path.exists(lstm_model_path) and os.path.exists(gb_model_path):
        lstm_model = load_model(lstm_model_path, compile=False)  # Sử dụng compile=False để tránh lỗi khi tải mô hình
        lstm_model.compile(optimizer='adam', loss=MeanSquaredError())  # Biên dịch lại mô hình sau khi tải

        gb_model = joblib.load(gb_model_path)
        return gb_model, lstm_model
    else:
        raise FileNotFoundError("Mô hình không tồn tại. Hãy kiểm tra lại đường dẫn hoặc huấn luyện mô hình.")


# Hàm dự đoán
def predict_precipitation(daily_df, gb_model, lstm_model, features):
    future_dates = pd.date_range(datetime.datetime.now() + pd.Timedelta(days=1), periods=14)
    print(f"Future dates: {future_dates}")

    trend_features = ['precipitation_sum_7d_mean', 'precipitation_sum_14d_mean', 
                      'precipitation_sum_7d_std', 'precipitation_sum_14d_std', 
                      'precipitation_sum_cumsum']

    future_trend_features_lstm = lstm_model.predict(daily_df[trend_features].tail(14).values.reshape((14, 1, len(trend_features))))
    print(f"Shape of future trend features from LSTM: {future_trend_features_lstm.shape}")

    future_features_combined = np.hstack((daily_df[features].tail(14).values, future_trend_features_lstm))
    print(f"Shape of future combined features: {future_features_combined.shape}")

    predictions = gb_model.predict(future_features_combined)
    predictions = np.maximum(predictions, 0)

    pred_df = pd.DataFrame({'date': future_dates, 'predicted_precipitation_sum': predictions.flatten()})
    print(f"Prediction DataFrame: {pred_df}")
    
    return pred_df
