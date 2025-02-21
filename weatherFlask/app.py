from flask import Flask, render_template, request, redirect, url_for
import requests
import sqlite3

app = Flask(__name__)
WEATHER_API_KEY = '0ed6368787480dc7ce6c89fa3c81d455'

def init_db():
    conn = sqlite3.connect('weather.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_name TEXT UNIQUE,
                    temperature REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def get_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            'city': city.capitalize(),
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'].capitalize(),
            'wind_speed': data['wind']['speed'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure']
        }
    return None

def save_to_history(city, temperature):
    conn = sqlite3.connect('weather.db')
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO search_history (city_name, temperature, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP)", (city, temperature))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect('weather.db')
    cur = conn.cursor()
    cur.execute("SELECT city_name, temperature FROM search_history ORDER BY timestamp DESC LIMIT 5")
    rows = cur.fetchall()
    conn.close()
    return [{'city': row[0], 'temperature': row[1]} for row in rows]

def delete_history():
    conn = sqlite3.connect('weather.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM search_history")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather():
    city = request.form.get('city')
    if city:
        weather_data = get_weather(city)
        if weather_data:
            save_to_history(city, weather_data['temperature'])
            history = get_history()
            return render_template('weather.html', **weather_data, history=history)
    return redirect(url_for('index'))

@app.route('/clear_history', methods=['GET', 'POST'])
def clear():
    delete_history()
    return render_template('clear_history.html', message="История пуста.")

if __name__ == '__main__':
    app.run(debug=True)
