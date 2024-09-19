import requests

def get_weather_data(latitude, longitude, forecast_days=14):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": "true",
        "hourly": ["relative_humidity_2m", "precipitation", "showers", "cloudcover"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "sunshine_duration", "precipitation_sum", "rain_sum", "precipitation_probability_max", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant", "sunrise", "sunset"],
        "timezone": "Asia/Bangkok",
        "past_days": 60,
        "forecast_days": forecast_days  # Thêm tham số để lấy dự đoán 14 ngày tới
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Kiểm tra xem có lỗi HTTP không
        data = response.json()
        
        if 'current_weather' not in data or not isinstance(data['current_weather'], dict):
            raise KeyError(f"API response does not contain valid 'current_weather' data. Response: {data}")
        if 'daily' not in data:
            raise KeyError(f"API response does not contain 'daily' data. Response: {data}")
        if 'hourly' not in data:
            raise KeyError(f"API response does not contain 'hourly' data. Response: {data}")
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None
