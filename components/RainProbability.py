import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM, Bidirectional, Conv1D, MaxPooling1D, Dropout
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.regularizers import l2
from tensorflow.keras.losses import MeanSquaredError
import os
import pickle

# Hàm để lưu model và scaler
def save_model_and_scaler(model, feature_scaler, target_scaler, model_path='models/rain_probability_model.h5', scaler_path='models/'):
    if not os.path.exists('models'):
        os.makedirs('models')
    model.save(model_path)

    with open(os.path.join(scaler_path, 'feature_scaler.pkl'), 'wb') as f:
        pickle.dump(feature_scaler, f)
    with open(os.path.join(scaler_path, 'target_scaler.pkl'), 'wb') as f:
        pickle.dump(target_scaler, f)

# Hàm để tải model và scaler
def load_model_and_scaler(model_path='models/rain_probability_model.h5', scaler_path='models/'):
    if not os.path.exists(model_path):
        raise FileNotFoundError("Model file not found. Please train the model first.")

    model = load_model(model_path)

    feature_scaler_path = os.path.join(scaler_path, 'feature_scaler.pkl')
    target_scaler_path = os.path.join(scaler_path, 'target_scaler.pkl')

    if not os.path.exists(feature_scaler_path) or not os.path.exists(target_scaler_path):
        raise FileNotFoundError("Scaler files not found. Please train the model first.")

    with open(feature_scaler_path, 'rb') as f:
        feature_scaler = pickle.load(f)
    with open(target_scaler_path, 'rb') as f:
        target_scaler = pickle.load(f)

    return model, feature_scaler, target_scaler

# Hàm huấn luyện và lưu model
def train_and_save_rain_probability_model(df):
    features = df.columns.difference(['precipitation_sum'])
    target = 'precipitation_sum'

    feature_scaler = MinMaxScaler()
    scaled_features = feature_scaler.fit_transform(df[features])
    target_scaler = MinMaxScaler()
    scaled_target = target_scaler.fit_transform(df[[target]])

    look_back = 14
    X, y = [], []
    for i in range(look_back, len(scaled_features)):
        X.append(scaled_features[i-look_back:i])
        y.append(scaled_target[i])

    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], len(features)))

    model = Sequential()
    model.add(Conv1D(filters=64, kernel_size=2, activation='relu', input_shape=(look_back, len(features))))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Dropout(0.4))
    model.add(Bidirectional(LSTM(64, return_sequences=True, kernel_regularizer=l2(0.01))))
    model.add(Dropout(0.4))
    model.add(Bidirectional(LSTM(64, kernel_regularizer=l2(0.01))))
    model.add(Dropout(0.4))
    model.add(Dense(50, activation='relu', kernel_regularizer=l2(0.01)))
    model.add(Dropout(0.4))
    model.add(Dense(1))

    # Sử dụng MeanSquaredError thay vì 'mse'
    model.compile(optimizer='adam', loss=MeanSquaredError())

    model.fit(X, y, epochs=200, batch_size=16, validation_split=0.2, verbose=0, shuffle=False)

    save_model_and_scaler(model, feature_scaler, target_scaler)

    return model, feature_scaler, target_scaler

# Hàm dự đoán xác suất mưa
def predict_precipitation_probability(data, predict_next_14_days=False):
    if not data.get('time') or not data.get('temperature_2m_max'):
        raise ValueError("Missing necessary fields in daily data")

    dates = pd.to_datetime(data['time'])
    df = pd.DataFrame({
        'date': dates,
        'temperature_2m_max': data['temperature_2m_max'],
        'temperature_2m_min': data['temperature_2m_min'],
        'sunshine_duration': data['sunshine_duration'],
        'precipitation_sum': data['precipitation_sum'],
        'precipitation_probability_max': data['precipitation_probability_max'],
        'wind_speed_10m_max': data['wind_speed_10m_max'],
        'wind_gusts_10m_max': data['wind_gusts_10m_max'],
        'wind_direction_10m_dominant': data['wind_direction_10m_dominant']
    })
    df.set_index('date', inplace=True)
    df.fillna(0, inplace=True)

    try:
        model, feature_scaler, target_scaler = load_model_and_scaler()
    except FileNotFoundError:
        model, feature_scaler, target_scaler = train_and_save_rain_probability_model(df)

    features = df.columns.difference(['precipitation_sum'])
    scaled_features = feature_scaler.transform(df[features])

    look_back = 14
    predictions = []
    last_14_days = scaled_features[-look_back:]

    for _ in range(14):
        X_pred = last_14_days.reshape((1, look_back, len(features)))
        y_pred = model.predict(X_pred)
        predicted_precipitation = target_scaler.inverse_transform(y_pred)
        precipitation_probability = np.minimum(predicted_precipitation[0][0] * 10, 100)
        predictions.append(precipitation_probability)

        # Cập nhật dữ liệu mới từ dự đoán vào bộ dữ liệu cho lần dự đoán tiếp theo
        new_row = np.hstack((X_pred[0, -1, :-1], y_pred[0]))  # Thêm giá trị y_pred vào hàng mới
        last_14_days = np.vstack((last_14_days[1:], new_row))  # Cập nhật dữ liệu 14 ngày tiếp theo

    return predictions
