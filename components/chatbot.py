import spacy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from components.chatbotAPI import get_chatbot_weather_data
import json
import os
from datetime import datetime, timedelta
from dateutil import parser

nlp = spacy.load("en_core_web_sm")

user_location_memory = None
user_weather_type_memory = None
suggested_locations = None
previous_weather_types = None

location_file_path = os.path.join(os.path.dirname(__file__), '../data/location_coordinates.json')
qa_file_path = os.path.join(os.path.dirname(__file__), '../data/conversation.json')

def load_location_data():
    try:
        with open(location_file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def find_closest_match(input_location, possible_locations):
    input_location = input_location.strip().lower()
    possible_locations = [loc.strip().lower() for loc in possible_locations]
    matches = process.extract(input_location, possible_locations, scorer=fuzz.ratio, limit=5)
    
    if not matches or matches[0][1] < 70:
        return None, matches
    return matches[0][0], None

def analyze_time(user_input):
    today = datetime.now().date()
    
    # Thử phân tích ngày cụ thể từ input của người dùng
    try:
        date_requested = parser.parse(user_input, fuzzy=True).date()
        # Kiểm tra nếu ngày nằm trong phạm vi API cung cấp (tối đa 90 ngày trước và 16 ngày sau)
        if today - timedelta(days=90) <= date_requested <= today + timedelta(days=16):
            return date_requested
        else:
            return None  # Ngày yêu cầu nằm ngoài phạm vi dữ liệu của API
    except (ValueError, OverflowError):
        pass  # Nếu không có ngày cụ thể, tiếp tục với các từ khóa thời gian
    
    # Từ khóa thời gian
    time_keywords = {
        "today": ["today", "now"],
        "yesterday": ["yesterday"],
        "tomorrow": ["tomorrow"],
        "last_week": ["last week"],
        "next_week": ["next week"],
        "last_month": ["last month"],
        "next_month": ["next month"],
    }

    # Kiểm tra từ khóa thời gian
    for time_key, keywords in time_keywords.items():
        for keyword in keywords:
            if keyword in user_input:
                if time_key == "yesterday":
                    return today - timedelta(days=1)
                elif time_key == "tomorrow":
                    return today + timedelta(days=1)
                elif time_key == "last_week":
                    return today - timedelta(weeks=1)
                elif time_key == "next_week":
                    return today + timedelta(weeks=1)
                elif time_key == "last_month":
                    return (today.replace(day=1) - timedelta(days=1)).replace(day=1)
                elif time_key == "next_month":
                    return (today.replace(day=28) + timedelta(days=4)).replace(day=1)
                elif time_key == "today":
                    return today

    return today  # Mặc định trả về hôm nay nếu không tìm thấy từ khóa thời gian hoặc ngày cụ thể

def get_chatbot_response(user_input):
    locations, weather_types, suggestions = analyze_question(user_input)
    date_requested = analyze_time(user_input)

    if date_requested is None:
        return "Sorry, I can only provide weather data for dates within the past 90 days and the next 16 days."

    if suggestions and not user_location_memory:
        suggestion_list = ", ".join([f"{loc} (Similarity: {score})" for loc, score in suggestions])
        return f"Did you mean one of these locations? {suggestion_list}"

    if not locations:
        return "Could you please specify the location you're asking about?"

    if not weather_types:
        return "Could you please specify what weather information you're interested in?"

    responses = []
    for location in locations:
        coords = load_location_data().get(location)
        if coords:
            try:
                weather_data = get_chatbot_weather_data(coords['latitude'], coords['longitude'])
                # Đảm bảo rằng bạn đang lấy dữ liệu cho đúng ngày được yêu cầu
                specific_weather_data = get_weather_for_specific_day(weather_data, date_requested)
                if specific_weather_data:
                    responses.append(generate_weather_response_for_date(weather_data, location, weather_types, date_requested))
                else:
                    responses.append(f"Sorry, I couldn't find weather data for {date_requested}.")
            except KeyError as e:
                responses.append(f"Error fetching weather data for {location.title()}: {e}")
        else:
            responses.append(f"Sorry, I could not find the coordinates for {location.title()}.")

    return " ".join(responses)


def get_weather_for_specific_day(weather_data, date_requested):
    daily_data = weather_data['daily']
    for i, date_str in enumerate(daily_data['time']):
        if date_str == date_requested.strftime('%Y-%m-%d'):
            return {key: value[i] for key, value in daily_data.items()}
    return None

def generate_weather_response_for_date(weather_data, location, weather_types, date_requested):
    specific_weather_data = get_weather_for_specific_day(weather_data, date_requested)
    if not specific_weather_data:
        return f"Sorry, I couldn't find the weather data for {date_requested}."

    responses = []
    responses.append(f"Weather in {location.title()} on {date_requested}:")
    
    for weather_type in weather_types:
        if weather_type == "temperature":
            temp_min = specific_weather_data['temperature_2m_min']
            temp_max = specific_weather_data['temperature_2m_max']
            responses.append(f"Temperature: {temp_min}°C - {temp_max}°C")
        elif weather_type == "rain":
            rain_probability = specific_weather_data['precipitation_probability_max']
            responses.append(f"Rain Probability: {rain_probability}%")
        elif weather_type == "humidity":
            humidity = weather_data['hourly']['relative_humidity_2m'][0]
            responses.append(f"Humidity: {humidity}%")
        elif weather_type == "cloudcover":
            cloud_cover = weather_data['hourly']['cloudcover'][0]
            responses.append(f"Cloud Cover: {cloud_cover}%")
        elif weather_type == "wind":
            wind_speed = specific_weather_data['wind_speed_10m_max']
            responses.append(f"Wind Speed: {wind_speed} km/h")
        elif weather_type == "sunrise":
            sunrise_time = specific_weather_data['sunrise']
            responses.append(f"Sunrise: {sunrise_time}")
        elif weather_type == "sunset":
            sunset_time = specific_weather_data['sunset']
            responses.append(f"Sunset: {sunset_time}")
    
    return " ".join(responses)

def analyze_question(user_input):
    global user_location_memory, user_weather_type_memory, suggested_locations, previous_weather_types
    doc = nlp(user_input.lower())
    locations = []
    weather_types = []
    suggestions = None

    location_coordinates = load_location_data()
    possible_locations = list(location_coordinates.keys())

    weather_keywords = {
        "temperature": ["temperature", "hot"],
        "rain": ["rain", "precipitation"],
        "humidity": ["humidity"],
        "cloudcover": ["cloud", "cloud cover"],
        "wind": ["wind"],
        "sunrise": ["sunrise"],
        "sunset": ["sunset"],
        "all": ["weather"]
    }

    for weather_type, keywords in weather_keywords.items():
        for keyword in keywords:
            if keyword in user_input:
                weather_types.append(weather_type)

    if weather_types:
        user_weather_type_memory = weather_types
    else:
        if user_weather_type_memory:
            weather_types = user_weather_type_memory

    for keyword in sum(weather_keywords.values(), []):
        user_input = user_input.replace(keyword, "").strip()

    fuzzy_location, suggestions = find_closest_match(user_input, possible_locations)
    if fuzzy_location:
        locations.append(fuzzy_location)
        user_location_memory = fuzzy_location

    if not locations and user_location_memory:
        locations.append(user_location_memory)

    suggested_locations = suggestions

    return locations, weather_types, suggestions

def get_chatbot_response(user_input):
    locations, weather_types, suggestions = analyze_question(user_input)
    date_requested = analyze_time(user_input)

    if suggestions and not user_location_memory:
        suggestion_list = ", ".join([f"{loc} (Similarity: {score})" for loc, score in suggestions])
        return f"Did you mean one of these locations? {suggestion_list}"

    if not locations:
        return "Could you please specify the location you're asking about?"

    if not weather_types:
        return "Could you please specify what weather information you're interested in?"

    responses = []
    for location in locations:
        coords = load_location_data().get(location)
        if coords:
            try:
                weather_data = get_chatbot_weather_data(coords['latitude'], coords['longitude'])
                responses.append(generate_weather_response_for_date(weather_data, location, weather_types, date_requested))
            except KeyError as e:
                responses.append(f"Error fetching weather data for {location.title()}: {e}")
        else:
            responses.append(f"Sorry, I could not find the coordinates for {location.title()}.")

    return " ".join(responses)

def process_user_message(user_input):
    return get_chatbot_response(user_input)
