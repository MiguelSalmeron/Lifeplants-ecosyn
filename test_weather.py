import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Securely get the API Key
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = "Managua"

def get_weather():
    if not API_KEY:
        print(" Error: No API Key found. Please set OPENWEATHER_API_KEY in your .env file.")
        return

    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=en"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        print(f"✅ SUCCESS! In {CITY} it is {temp}°C with {desc}.")
        
        # logic for Lifeplantsd
        if temp > 30:
            print(" HEAT ALERT! It's very hot. The plant will need water soon.")
        else:
            print(" The weather is nice. The plant is chilling.")
    else:
        print(" Error: Check your API Key or the city name.")

if __name__ == "__main__":
    get_weather()