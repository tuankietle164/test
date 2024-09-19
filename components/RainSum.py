import pandas as pd

def get_daily_rain_sum(daily_data):
    if not daily_data.get('precipitation_sum'):
        raise ValueError("Missing 'precipitation_sum' in daily data")

    dates = pd.to_datetime(daily_data['time'])
    rain_sum = daily_data['precipitation_sum']
    
    rain_df = pd.DataFrame({
        'date': dates,
        'rain_sum': rain_sum
    })
    
    return rain_df
