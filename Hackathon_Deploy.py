import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import concurrent.futures
import joblib
from datetime import datetime
from streamlit_option_menu import option_menu

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
# LOAD TRAINED MODEL
# ==============================

model = joblib.load("weather_model_updated.pkl")

# ==============================
# ZONE COORDINATES
# ==============================

zones = {
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
# FETCH LIVE WEATHER
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

@st.cache_data(ttl=300)
def get_live_data():
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

df_live = get_live_data()

# ==============================
# HORIZONTAL NAVBAR
# ==============================

selected = option_menu(
    menu_title=None,
    options=["Live Map", "Zone Analysis", "Mitigation", "Ranking"],
    icons=["globe", "bar-chart", "tree", "trophy"],
    orientation="horizontal"
)

# ==============================
# LIVE MAP
# ==============================

if selected == "Live Map":

    map_obj = folium.Map(
        location=[17.3850, 78.4867],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    for _, row in df_live.iterrows():

        hour_now = datetime.now().hour

        input_df = pd.DataFrame([{
            "humidity_pct": row["humidity"],
            "wind_speed_kmph": row["wind_speed"],
            "month": datetime.now().month,
            "hour": hour_now
        }])

        predicted_temp = model.predict(input_df)[0]

        color = "red" if predicted_temp > 40 else \
                "orange" if predicted_temp > 35 else \
                "yellow" if predicted_temp > 30 else "green"

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=14,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            tooltip=f"""
            <b>{row['zone']}</b><br>
            🌡 Live: {row['temperature']} °C<br>
            🤖 Predicted: {round(predicted_temp,2)} °C
            """
        ).add_to(map_obj)

    st_folium(map_obj, width=1200, height=600)

# ==============================
# ZONE ANALYSIS
# ==============================

elif selected == "Zone Analysis":

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
        y=[zone_data["temperature"].values[0], predicted_temp],
        marker_color=["cyan", "orange"]
    ))

    st.plotly_chart(fig, use_container_width=True)

# ==============================
# MITIGATION SIMULATOR
# ==============================

elif selected == "Mitigation":

    zone = st.selectbox("Select Zone", df_live["zone"])

    zone_data = df_live[df_live["zone"] == zone]

    humidity = zone_data["humidity"].values[0]
    wind = zone_data["wind_speed"].values[0]
    month_now = datetime.now().month
    hour_now = datetime.now().hour

    # Base Prediction (using correct model features)
    base_input = pd.DataFrame([{
        "humidity_pct": humidity,
        "wind_speed_kmph": wind,
        "month": month_now,
        "hour": hour_now
    }])

    base_temp = model.predict(base_input)[0]

    st.metric("Current Predicted Heat (°C)", round(base_temp, 2))

    strategies = {}
    solutions = []

    # -----------------------------
    # Strategy 1: Urban Forest
    # Effect: Slight humidity increase + slight wind improvement
    # -----------------------------
    forest_input = base_input.copy()
    forest_input["humidity_pct"] += 2
    forest_input["wind_speed_kmph"] += 1
    strategies["Urban Forest Program"] = model.predict(forest_input)[0]
    solutions.append("Urban Forest Program")

    # -----------------------------
    # Strategy 2: Cool Roof
    # Effect: Slight temperature moderation (reduce heat effect via month impact proxy)
    # -----------------------------
    roof_input = base_input.copy()
    roof_input["humidity_pct"] -= 1
    strategies["Mandatory Cool Roof Policy"] = model.predict(roof_input)[0]
    solutions.append("Mandatory Cool Roof Policy")

    # -----------------------------
    # Strategy 3: Permeable Pavement
    # Effect: Slight wind increase
    # -----------------------------
    road_input = base_input.copy()
    road_input["wind_speed_kmph"] += 2
    strategies["Permeable Pavement Conversion"] = model.predict(road_input)[0]
    solutions.append("Permeable Pavement Conversion")

    # -----------------------------
    # Strategy 4: Wind Corridor
    # Effect: Strong wind improvement
    # -----------------------------
    wind_input = base_input.copy()
    wind_input["wind_speed_kmph"] += 4
    strategies["Wind Corridor Planning"] = model.predict(wind_input)[0]
    solutions.append("Wind Corridor Planning")

    # -----------------------------
    # Strategy 5: Tree Canopy Mission
    # Effect: Moderate humidity rise + wind rise
    # -----------------------------
    tree_input = base_input.copy()
    tree_input["humidity_pct"] += 3
    tree_input["wind_speed_kmph"] += 1
    strategies["5-Year Tree Canopy Mission"] = model.predict(tree_input)[0]
    solutions.append("5-Year Tree Canopy Mission")

    # -----------------------------
    # Display Strategy List
    # -----------------------------
    st.subheader("Recommended Sustainable Strategies")

    for s in solutions:
        st.write("•", s)

    # -----------------------------
    # Graph Comparison
    # -----------------------------
    comparison_df = pd.DataFrame({
        "Strategy": list(strategies.keys()),
        "Predicted Temp": list(strategies.values())
    })

    comparison_df = comparison_df.sort_values("Predicted Temp")

    fig = px.bar(
        comparison_df,
        x="Predicted Temp",
        y="Strategy",
        orientation="h",
        color="Predicted Temp",
        color_continuous_scale="Viridis",
        title="Mitigation Strategy Impact (Lower is Better)"
    )

    fig.update_layout(transition_duration=500)

    st.plotly_chart(fig, use_container_width=True)

    best_strategy = comparison_df.iloc[0]["Strategy"]

    st.success(f"🏆 Best Strategy for {zone}: {best_strategy}")

# ==============================
# RANKING
# ==============================

elif selected == "Ranking":

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
        orientation="h",
        color="predicted_temperature",
        color_continuous_scale="Reds"
    )

    st.plotly_chart(fig, use_container_width=True)
