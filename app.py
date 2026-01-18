import os
import sqlite3
import random
from datetime import datetime
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

OPENWEATHER_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_KEY)

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
            plant_type TEXT,
            last_watered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'happy'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_weather(city_name):
    if not OPENWEATHER_KEY:
        return None
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_KEY}&units=metric&lang=en"
        response = requests.get(url, timeout=3)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print("OpenWeather exception:", e)
        return None

# Fallback local de consejos
def local_advice(species, temp, humidity, city):
    tips = []
    if temp is None: temp = 25
    if humidity is None: humidity = 50
    if temp >= 32:
        tips.append("Hace mucho calor: sombra parcial y riego temprano o al atardecer.")
    elif temp <= 10:
        tips.append("Frío: resguarda del viento, reduce riegos y busca microclima más cálido.")
    else:
        tips.append("Temperatura moderada: mantén riego regular y buena luz indirecta.")
    if humidity < 30:
        tips.append("El sustrato está muy seco: riega hoy y revisa drenaje.")
    elif humidity < 60:
        tips.append("Riega pronto; el sustrato se está secando.")
    else:
        tips.append("Humedad correcta: evita encharcar.")
    s = (species or "").lower()
    if "cactus" in s or "succulent" in s or "suculenta" in s:
        tips.append("Para suculentas/cactus: riego profundo pero espaciado; mucha luz.")
    elif "orchid" in s or "orquídea" in s:
        tips.append("Orquídea: riego ligero, buena aireación y luz filtrada.")
    elif "fern" in s or "helecho" in s:
        tips.append("Helecho: mantén sustrato húmedo y alta humedad ambiental.")
    else:
        tips.append("Revisa hojas: amarillas suele ser exceso de agua; secas, falta de agua/luz.")
    return " ".join(tips)

def ai_advice(prompt_text):
    if not OPENAI_KEY:
        return None
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a concise plant care coach."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=120,
            temperature=0.6,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI exception:", e)
        return None

def get_advice(species, temp, humidity, city):
    prompt = (
        f"Plant: {species}. City: {city}. Temp: {temp}°C. Humidity: {humidity}%. "
        "Give ONE actionable, specific tip (max 35 words). "
        "If heat risk, mention shade/evaporation. If cold risk, mention insulation. "
        "Tone: friendly, direct. No disclaimers."
    )
    ai_resp = ai_advice(prompt)
    if ai_resp:
        return ai_resp
    return local_advice(species, temp, humidity, city)

def calculate_status_physics(last_watered_str, current_temp):
    try:
        last_watered = datetime.fromisoformat(last_watered_str)
    except Exception:
        last_watered = datetime.now()
    hours_passed = (datetime.now() - last_watered).total_seconds() / 3600
    base_decay_rate = 5
    multiplier = 2.5 if current_temp > 30 else 1.0
    moisture_loss = hours_passed * base_decay_rate * multiplier
    current_humidity = max(0, 100 - moisture_loss)
    if current_humidity < 30:
        status = 'critical'
    elif current_humidity < 60:
        status = 'thirsty'
    else:
        status = 'happy'
    return int(current_humidity), status

@app.route('/')
def index():
    city = request.args.get('city', 'Managua')
    weather_data = get_weather(city)
    current_temp = weather_data['main']['temp'] if weather_data else 35
    conn = get_db_connection()
    db_plants = conn.execute('SELECT * FROM plants').fetchall()
    conn.close()
    processed_plants = []
    for plant in db_plants:
        humidity, status = calculate_status_physics(plant['last_watered'], current_temp)
        advice = get_advice(plant['species'], current_temp, humidity, city)
        plant_type_val = plant['plant_type'] if 'plant_type' in plant.keys() else 'Unknown'
        processed_plants.append({
            'id': plant['id'],
            'name': plant['name'],
            'species': plant['species'],
            'plant_type': plant_type_val,
            'humidity': humidity,
            'status': status,
            'advice': advice
        })
    return render_template('index.html', plants=processed_plants, weather=weather_data, temp=current_temp, current_city=city)

@app.route('/add', methods=('POST',))
def add_plant():
    name = request.form['name']
    species = request.form['species']
    plant_type = request.form['type']
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO plants (name, species, plant_type, last_watered) VALUES (?, ?, ?, ?)',
        (name, species, plant_type, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/water/<int:id>')
def water_plant(id):
    conn = get_db_connection()
    conn.execute('UPDATE plants SET last_watered = ? WHERE id = ?', (datetime.now().isoformat(), id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_plant(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM plants WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json() or {}
    message = (data.get('message') or '').strip()
    city = (data.get('city') or 'Managua').strip()
    if not message:
        return jsonify({"reply": "Pregunta algo específico sobre riego, luz o estrés por calor/frío."})
    prompt = (
        f"City: {city}. Question: {message}. "
        "Respond with ONE actionable, specific tip (max 35 words). "
        "If heat risk, mention shade/evaporation. If cold risk, mention insulation. "
        "Tone: friendly, direct. No disclaimers."
    )
    ai_resp = ai_advice(prompt)
    if not ai_resp:
        ai_resp = local_advice("generic", 25, 60, city)
    return jsonify({"reply": ai_resp})

if __name__ == '__main__':
    app.run(debug=True)