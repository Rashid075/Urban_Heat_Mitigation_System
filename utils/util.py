import concurrent
import requests
import streamlit as st
import pandas as pd
from db import insert_weather
import requests

API_KEY = st.secrets["API_KEY"]
def fetch_weather(zone, lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code != 200:
            return None

        return {
            "zone": zone,
            "latitude": lat,
            "longitude": lon,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"]
        }
    except:
        return None

@st.cache_data(ttl=300)
def get_live_data(zones):
    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_weather, z, lat, lon)
            for z, (lat, lon) in zones.items()
        ]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
                insert_weather(result)   # SAVE HISTORY

    return pd.DataFrame(results)

def compute_heat_risk(df):
    df["heat_risk"] = (
        0.5 * df["temperature"] +
        0.3 * df["humidity"] -
        0.2 * df["wind_speed"]
    )
    return df