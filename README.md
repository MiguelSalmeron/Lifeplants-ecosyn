# LifePlants Eco-Sync

A digital twin garden that connects virtual plants to real world weather conditions. Built during United Hacks V6.

## The Problem

In Managua, Nicaragua, temperatures regularly exceed 35°C.  During heat waves, plants lose water at alarming rates through evaporation, and most people don't realize their garden is dying until it's too late.  Meanwhile, someone in Oslo faces the opposite challenge: cold stress and overwatering. Climate affects plant care differently depending on location, but most plant apps ignore this entirely.

## The Solution

LifePlants creates a digital twin of your garden that reacts to actual weather conditions in your city. When it's 38°C in Managua, virtual plants wilt faster. When it's raining in London, the interface reflects that atmosphere. The system calculates moisture loss using a physics based model that accounts for temperature, making plant care advice actually relevant to local conditions.

## How It Works

The application connects three systems together: 

1. **Real Weather Data**:  Pulls current conditions from OpenWeather API for any city worldwide
2. **Physics Engine**: Calculates plant hydration using time since last watering multiplied by temperature based evaporation rates
3. **AI Advisor**:  GPT provides contextual care tips based on species, current weather, and plant status

When temperature exceeds 30°C, the evaporation multiplier increases to 2.5x, causing plants to dehydrate faster. This reflects how real plants behave under heat stress.

```python
def calculate_status_physics(last_watered_str, current_temp):
    hours_passed = (datetime.now() - last_watered).total_seconds() / 3600
    base_decay_rate = 5
    multiplier = 2.5 if current_temp > 30 else 1.0
    moisture_loss = hours_passed * base_decay_rate * multiplier
    current_humidity = max(0, 100 - moisture_loss)
```

## Features

**Weather Sync**: Search any city or pick a location on the interactive map. The entire interface adapts to current conditions with rain overlays, cloud animations, and automatic night mode.

**Plant Status Visualization**: SVG plants visually respond to their health. Healthy plants float gently, thirsty plants droop at 15 degrees, and critical plants wilt dramatically at 65 degrees.

**AI Plant Coach**: Chat with an AI that understands your local climate. Ask about watering schedules, heat protection, or cold stress and get specific advice for your situation.

**Heat Alerts**:  When temperatures exceed 30°C, the system warns you and shows the accelerated evaporation rate affecting your plants.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask, Python 3.12 |
| Database | SQLite |
| Weather | OpenWeather API |
| AI | OpenAI GPT-4o-mini |
| Frontend | Jinja2 templates, Pico CSS |
| Maps | Leaflet with OpenStreetMap |

## Running Locally

```bash
git clone https://github.com/MiguelSalmeron/Lifeplants-ecosyn.git
cd Lifeplants-ecosyn
python -m venv . venv
source .venv/bin/activate
pip install flask requests python-dotenv openai
```

Create a `.env` file:

```
OPENWEATHER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

Start the server: 

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

## Project Structure

```
lifeplants-ecosyn/
├── app.py              # Flask routes and physics engine
├── templates/
│   └── index.html      # Main dashboard
├── static/
│   ├── css/style.css   # Glassmorphism and weather themes
│   └── js/
│       ├── chatbot.js
│       ├── map_picker.js
│       └── zen_audio.js
└── lifeplants. db       # SQLite database (created on first run)
```

## Why This Matters

Climate inequality is real. A plant owner in a tropical country deals with heat stress that someone in a temperate climate never experiences. By connecting virtual plants to real weather, LifePlants makes this invisible problem visible and helps people understand how climate shapes daily life differently around the world.

## Built For
Demo: https://lifeplants-ecosyn.onrender.com/
United Hacks V6 | Human Interaction Track | Solo Hack
