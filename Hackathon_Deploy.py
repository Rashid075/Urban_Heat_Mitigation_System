import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import concurrent.futures
import joblib
from datetime import datetime
from streamlit_option_menu import option_menu
from utils.livemap import create_live_map

# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(
    page_title="Urban Heat Intelligence",
    page_icon="🌍",
    layout="wide"
)

st.title("🌡 Urban Heat Intelligence System")

API_KEY = st.secrets["API_KEY"]

# ==============================
# LOAD MODEL
# ==============================

model = joblib.load("weather_model_updated.pkl")

# ==============================
# SESSION STATE ZONES
# ==============================

if "zones" not in st.session_state:
    st.session_state.zones = {
        "Charminar": (17.3616, 78.4747),
        "Falaknuma": (17.3326, 78.4751),
        "Saidabad": (17.3615, 78.5118),
        "Malakpet": (17.3736, 78.4996),
        "Dilsukhnagar": (17.3684, 78.5228),
        "LB Nagar": (17.3501, 78.5510),
        "Uppal": (17.4025, 78.5612),
        "Habsiguda": (17.4154, 78.5426),
        "Secunderabad": (17.5042, 78.5426),
        "Malkajgiri": (17.4511, 78.5369),
        "Kukatpally": (17.4930, 78.4054),
        "Moosapet": (17.4685, 78.4206),
        "Miyapur": (17.4981, 78.3567),
        "BHEL": (17.4951, 78.2958),
        "Gachibowli": (17.4436, 78.3519),
        "Kondapur": (17.4587, 78.3730),
        "Madhapur": (17.4408, 78.3916),
        "HITEC City": (17.4490, 78.3831),
        "Jubilee Hills": (17.4308, 78.4102),
        "Banjara Hills": (17.4177, 78.4399),
    }

# ==============================
# ADD LOCATION UI (SIDEBAR)
# ==============================

st.sidebar.subheader("➕ Add New Location")

zone_name = st.sidebar.text_input("Location Name")
lat = st.sidebar.number_input("Latitude", format="%.6f")
lon = st.sidebar.number_input("Longitude", format="%.6f")

if st.sidebar.button("Add Location"):
    if not zone_name:
        st.sidebar.error("Enter location name")
    elif not (-90 <= lat <= 90 and -180 <= lon <= 180):
        st.sidebar.error("Invalid latitude/longitude")
    elif zone_name in st.session_state.zones:
        st.sidebar.warning("Location already exists")
    else:
        st.session_state.zones[zone_name] = (lat, lon)
        st.cache_data.clear()  # IMPORTANT
        st.sidebar.success(f"{zone_name} added!")

# ==============================
# FETCH WEATHER
# ==============================

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

# ==============================
# PARALLEL FETCH
# ==============================

@st.cache_data(ttl=300)
def get_live_data(zones):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_weather, zone, lat, lon)
            for zone, (lat, lon) in zones.items()
        ]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    return pd.DataFrame(results)

df_live = get_live_data(st.session_state.zones)

# ==============================
# NAVBAR
# ==============================

options = option_menu(
    menu_title=None,
    options=["Live Map", "Zone Analysis", "Mitigation", "Ranking"],
    icons=["globe", "bar-chart", "tree", "trophy"],
    orientation="horizontal"
)

# ==============================
# LIVE MAP
# ==============================

if options == "Live Map":
    create_live_map(df_live, model)

# ==============================
# ZONE ANALYSIS
# ==============================

elif options == "Zone Analysis":

    zone = st.selectbox("Select Zone", df_live["zone"])
    zone_data = df_live[df_live["zone"] == zone]

    hour_now = datetime.now().hour

    input_df = pd.DataFrame([{
        "humidity_pct": zone_data["humidity"].values[0],
        "wind_speed_kmph": zone_data["wind_speed"].values[0],
        "month": datetime.now().month,
        "hour": hour_now
    }])

    predicted_temp = model.predict(input_df)[0]

    col1, col2 = st.columns(2)
    col1.metric("Live Temperature", zone_data["temperature"].values[0])
    col2.metric("Predicted Heat", round(predicted_temp, 2))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Live", "Predicted"],
        y=[zone_data["temperature"].values[0], predicted_temp]
    ))

    st.plotly_chart(fig, width='stretch')

# ==============================
# MITIGATION
# ==============================

elif options == "Mitigation":

    zone = st.selectbox("Select Zone", df_live["zone"])
    zone_data = df_live[df_live["zone"] == zone]

    humidity = zone_data["humidity"].values[0]
    wind = zone_data["wind_speed"].values[0]
    month_now = datetime.now().month
    hour_now = datetime.now().hour

    base_input = pd.DataFrame([{
        "humidity_pct": humidity,
        "wind_speed_kmph": wind,
        "month": month_now,
        "hour": hour_now
    }])

    base_temp = model.predict(base_input)[0]
    st.metric("Current Predicted Heat (°C)", round(base_temp, 2))

    strategies = {}

    def simulate(h=0, w=0):
        temp_input = base_input.copy()
        temp_input["humidity_pct"] += h
        temp_input["wind_speed_kmph"] += w
        return model.predict(temp_input)[0]

    strategies["Urban Forest Program"] = simulate(2, 1)
    strategies["Cool Roof Policy"] = simulate(-1, 0)
    strategies["Permeable Pavement"] = simulate(0, 2)
    strategies["Wind Corridor"] = simulate(0, 4)
    strategies["Tree Canopy Mission"] = simulate(3, 1)

    comparison_df = pd.DataFrame({
        "Strategy": strategies.keys(),
        "Predicted Temp": strategies.values()
    }).sort_values("Predicted Temp")

    fig = px.bar(
        comparison_df,
        x="Predicted Temp",
        y="Strategy",
        orientation="h"
    )

    st.plotly_chart(fig, width='stretch')

    st.success(f"🏆 Best Strategy: {comparison_df.iloc[0]['Strategy']}")

# ==============================
# RANKING
# ==============================

elif options == "Ranking":

    ranking = []
    hour_now = datetime.now().hour

    for _, row in df_live.iterrows():
        input_df = pd.DataFrame([{
            "humidity_pct": row["humidity"],
            "wind_speed_kmph": row["wind_speed"],
            "month": datetime.now().month,
            "hour": hour_now
        }])

        pred = model.predict(input_df)[0]

        ranking.append({
            "zone": row["zone"],
            "predicted_temperature": pred
        })

    ranking_df = pd.DataFrame(ranking).sort_values(
        "predicted_temperature",
        ascending=False
    )

    fig = px.bar(
        ranking_df,
        x="predicted_temperature",
        y="zone",
        orientation="h"
    )

    st.plotly_chart(fig,width='stretch')