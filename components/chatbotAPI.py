import requests

def get_chatbot_weather_data(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": "true",
        "hourly": ["relative_humidity_2m", "precipitation", "showers", "cloudcover", "temperature_2m"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "sunshine_duration", "precipitation_sum", "rain_sum", 
                  "precipitation_probability_max", "wind_speed_10m_max", "wind_gusts_10m_max", 
                  "wind_direction_10m_dominant", "sunrise", "sunset"],
        "timezone": "Asia/Bangkok",
        "forecast_days": 16,  # Lấy dự báo cho 16 ngày tới
        "past_days": 90  # Lấy dữ liệu của 3 tháng trước (90 ngày)
    }
    
    response = requests.get(url, params=params)
    data = response.json()

    if 'current_weather' not in data or not isinstance(data['current_weather'], dict):
        raise KeyError("API response does not contain valid 'current_weather' data")
    if 'daily' not in data:
        raise KeyError("API response does not contain 'daily' data")
    if 'hourly' not in data:
        raise KeyError("API response does not contain 'hourly' data")
    
    return data
