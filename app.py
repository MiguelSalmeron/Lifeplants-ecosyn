import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from dotenv import load_dotenv

#Configuración Inicial
load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv('OPENWEATHER_API_KEY')
CITY = "Managua"

#Conexión a la database
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

#logica
def get_weather(city_name):
    if not API_KEY: return None
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric&lang=es"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

#  Rutas de la Web
@app.route('/')
def index():
    # Obtener clima real
    weather_data = get_weather(CITY)
    current_temp = weather_data['main']['temp'] if weather_data else 25
    
    # Calcular estado de las plantas 
    conn = get_db_connection()
    plants = conn.execute('SELECT * FROM plants').fetchall()
    conn.close()
    
    return render_template('index.html', plants=plants, weather=weather_data, temp=current_temp)

@app.route('/add', methods=('POST',))
def add_plant():
    name = request.form['name']
    species = request.form['species']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO plants (name, species) VALUES (?, ?)', (name, species))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/water/<int:id>')
def water_plant(id):
    conn = get_db_connection()
    conn.execute('UPDATE plants SET last_watered = CURRENT_TIMESTAMP, status = "happy" WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)