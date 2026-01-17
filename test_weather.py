import os
import requests
from dotenvimpot load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = "Managua"

def get_weather():
    if not API_KEY:
        print(" Error: No API Key found. Please set OPENWEATHER_API_KEY in your .env file.")
        return

    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=es"
    response = requests.get(url)

    
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        print(f" ¡ÉXITO! En {CITY} hace {temp}°C con {desc}.")
        
        # Lógica simple para Lifeplants
        if temp > 30:
            print(" ¡ALERTA! Hace mucho calor. La planta necesitará agua pronto.")
        else:
            print(" El clima es agradable. La planta está tranquila.")
    else:
        print(" Error: Revisa tu API Key o el nombre de la ciudad.")

if __name__ == "__main__":
    get_weather()