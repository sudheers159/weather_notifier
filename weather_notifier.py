import requests
from plyer import notification
import time

# OpenWeatherMap ki free API key yahan dalein (Apni khud ki free key bhi bana sakte hain)
API_KEY = "8b430c495c96ee17d41514a3d88a2dd1"  # Free account banakar yahan apni key dalein
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(city_name):
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric' # Temperature Celsius mein lene ke liye
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            desc = data['weather'][0]['description']
            
            # Har cheez console (screen) par show karna
            print("\n" + "="*30)
            print(f"🌍 City: {city_name.capitalize()}")
            print(f"🌡️ Temperature: {temp}°C")
            print(f"💧 Humidity: {humidity}%")
            print(f"☁️ Condition: {desc.capitalize()}")
            print("="*30 + "\n")
            
            # Desktop Notification trigger karna
            notification.notify(
                title=f"Weather Update: {city_name.capitalize()}",
                message=f"Temp: {temp}°C, {desc.capitalize()}",
                timeout=10
            )
            
            # Log file mein save karna (History show karne ke liye)
            with open("weather_log.txt", "a") as f:
                f.write(f"City: {city_name} | Temp: {temp}C | Condition: {desc} | Time: {time.ctime()}\n")
                
        else:
            print("❌ City nahi mili! Sahi spelling check karein.")
    except Exception as e:
        print(f"⚠️ Error aa gaya: {e}")

if __name__ == "__main__":
    print("--- 🌤️ Python Weather & Notification System ---")
    city = input("Apni city ka naam enter karein: ")
    get_weather(city)