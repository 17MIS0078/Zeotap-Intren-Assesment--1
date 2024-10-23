from flask import Flask, render_template, request
import requests
import time
from datetime import datetime
from collections import defaultdict
import threading

# Your OpenWeatherMap API key
API_KEY = '9be57cf882b9ff4748f1f397c386c868'  
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

app = Flask(__name__)

# Store daily weather data
daily_weather = defaultdict(list)

# Function to fetch weather data for a city
def get_weather_data(city):
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'  # Get temperature in Celsius
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# Function to process and store daily weather data
def process_weather_data(data):
    if data:
        city = data['name']
        main = data['main']
        weather_condition = data['weather'][0]['main']
        temp = main['temp']
        feels_like = main['feels_like']
        timestamp = datetime.fromtimestamp(data['dt']).date()

        # Store the weather data
        daily_weather[timestamp].append({
            'city': city,
            'temperature': temp,
            'feels_like': feels_like,
            'condition': weather_condition
        })

# Function to calculate daily summaries
def calculate_daily_summary():
    summaries = {}
    for date, records in daily_weather.items():
        temperatures = [record['temperature'] for record in records]
        conditions = [record['condition'] for record in records]

        avg_temp = sum(temperatures) / len(temperatures)
        max_temp = max(temperatures)
        min_temp = min(temperatures)
        dominant_condition = max(set(conditions), key=conditions.count)

        summaries[date] = {
            'avg_temp': avg_temp,
            'max_temp': max_temp,
            'min_temp': min_temp,
            'dominant_condition': dominant_condition
        }
    return summaries

# Function to continuously fetch and process weather data
def fetch_weather_data():
    cities = ["Delhi", "Mumbai", "Chennai", "Bangalore", "Kolkata", "Hyderabad"]
    while True:
        for city in cities:
            weather_data = get_weather_data(city)
            if weather_data:  # Check if data is valid
                process_weather_data(weather_data)
        time.sleep(300)  # Sleep for 5 minutes

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form.get('city')
        weather_data = get_weather_data(city)
        if weather_data:
            process_weather_data(weather_data)
            daily_summaries = calculate_daily_summary()
            return render_template('index.html', summaries=daily_summaries)
    return render_template('index.html', summaries={})

if __name__ == "__main__":
    # Start the background thread for fetching weather data
    threading.Thread(target=fetch_weather_data, daemon=True).start()
    app.run(debug=True)
