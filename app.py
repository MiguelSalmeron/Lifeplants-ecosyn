import os
import sqlite3
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Configuración
OPENWEATHER_KEY = os.getenv('OPENWEATHER_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

def get_db_connection():
    conn = sqlite3.connect('lifeplants.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            last_watered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'happy'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- MODIFICADO: Ahora acepta una ciudad dinámica ---
def get_weather(city_name):
    if not OPENWEATHER_KEY: return None
    try:
        # Usamos la ciudad que pide el usuario
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_KEY}&units=metric&lang=en"
        response = requests.get(url, timeout=3)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_gemini_advice(species, temp, humidity, city):
    if not GEMINI_KEY or humidity > 60: return None
    try:
        prompt = (f"Act as a survival botanist. Plant: {species}. "
                  f"Location: {city} (Temp: {temp}°C). Soil Humidity: {humidity}%. "
                  f"Give a 1-sentence urgent survival tip in English.")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Check water levels immediately."
    return None

def calculate_status_physics(last_watered_str, current_temp):
    try:
        last_watered = datetime.fromisoformat(last_watered_str)
    except:
        last_watered = datetime.now()

    hours_passed = (datetime.now() - last_watered).total_seconds() / 3600
    base_decay_rate = 5 
    multiplier = 2.5 if current_temp > 30 else 1.0 # Multiplicador de calor
    
    moisture_loss = hours_passed * base_decay_rate * multiplier
    current_humidity = max(0, 100 - moisture_loss)
    
    if current_humidity < 30: status = 'critical'
    elif current_humidity < 60: status = 'thirsty'
    else: status = 'happy'
        
    return int(current_humidity), status

@app.route('/')
def index():
    # 1. Buscamos si hay una ciudad en la URL (?city=London), si no, Managua
    city = request.args.get('city', 'Managua')
    
    weather_data = get_weather(city)
    current_temp = weather_data['main']['temp'] if weather_data else 35 
    
    conn = get_db_connection()
    db_plants = conn.execute('SELECT * FROM plants').fetchall()
    conn.close()
    
    processed_plants = []
    for plant in db_plants:
        humidity, status = calculate_status_physics(plant['last_watered'], current_temp)
        # Pasamos la ciudad a la IA también
        advice = get_gemini_advice(plant['species'], current_temp, humidity, city)
        
        processed_plants.append({
            'id': plant['id'],
            'name': plant['name'],
            'species': plant['species'],
            'humidity': humidity,
            'status': status,
            'advice': advice
        })
    
    # Pasamos 'city' al template para que el buscador recuerde qué escribiste
    return render_template('index.html', plants=processed_plants, weather=weather_data, temp=current_temp, current_city=city)

@app.route('/add', methods=('POST',))
def add_plant():
    name = request.form['name']
    species = request.form['species']
    conn = get_db_connection()
    conn.execute('INSERT INTO plants (name, species, last_watered) VALUES (?, ?, ?)', 
                 (name, species, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/water/<int:id>')
def water_plant(id):
    conn = get_db_connection()
    conn.execute('UPDATE plants SET last_watered = ? WHERE id = ?', 
                 (datetime.now().isoformat(), id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)