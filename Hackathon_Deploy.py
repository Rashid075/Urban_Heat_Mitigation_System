import streamlit as st
import pandas as pd
import numpy as np
import concurrent.futures
import joblib
from datetime import datetime

# ======================
# IMPORT MODULES
# ======================
from db import init_db, get_locations, insert_location, insert_weather
from utils.api import fetch_weather
from utils.livemap import create_live_map
from utils.zone_analysis import create_zone_analysis
from utils.mitigation import create_mitigation
from utils.ranking import create_ranking
from utils.history import create_history
from utils.planning import create_planning

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(page_title="Urban Heat Intelligence", layout="wide")

# ======================
# PREMIUM UI CSS
# ======================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a);
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
}
.block-container {
    padding-top: 3rem !important;
}

/* Ensure title container spacing */
.title-container {
    margin-top: 20px;
    padding-top: 10px;
}


.metric-card {
    background: rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    transition: 0.3s;
}
.metric-card:hover { transform: scale(1.05); }

.glass-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(14px);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.08);
}

.title {
    font-size: 42px;
    text-align: center;
    font-weight: 700;
}
.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 20px;
}

section[data-testid="stSidebar"] {
    background: #020617;
}
.main-title {
    animation: glow 3s infinite alternate;
}

@keyframes glow {
    from { text-shadow: 0 0 10px #22c55e; }
    to { text-shadow: 0 0 25px #38bdf8; }
}
</style>
""", unsafe_allow_html=True)

# ======================
# HEADER
# ======================
st.markdown("""
<style>
.title-container {
    text-align: center;
    margin-bottom: 10px;
}

.main-title {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(90deg, #38bdf8, #22c55e, #facc15);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.3;   /* 🔥 THIS FIXES CUTTING */
    padding-top: 10px;
}

.subtitle {
    font-size: 16px;
    color: #94a3b8;
    margin-top: 8px;
}

/* Glow effect */
.main-title::after {
    content: '';
    display: block;
    height: 2px;
    width: 120px;
    margin: 12px auto;
    background: linear-gradient(90deg, #38bdf8, #22c55e);
    border-radius: 10px;
}
</style>

<div class="title-container">
    <div class="main-title">🌍 Urban Heat Intelligence</div>
    <div class="subtitle">AI-powered Heat Monitoring & Smart Mitigation</div>
</div>
""", unsafe_allow_html=True)
# ======================
# INIT DB
# ======================
init_db()

# ======================
# DEFAULT LOCATIONS
# ======================
locations = get_locations()
if not locations:
    default_locations = {
        "Hyderabad": (17.3850, 78.4867),
        "Mumbai": (19.0760, 72.8777),
        "Delhi": (28.6139, 77.2090),
        "Bangalore": (12.9716, 77.5946),
        "Chennai": (13.0827, 80.2707),
        "Kolkata": (22.5726, 88.3639),
        "Pune": (18.5204, 73.8567),
        "Ahmedabad": (23.0225, 72.5714),
        "Jaipur": (26.9124, 75.7873),
        "Lucknow": (26.8467, 80.9462),
        "Chandigarh": (30.7333, 76.7794),
        "Bhopal": (23.2599, 77.4126),
        "Patna": (25.5941, 85.1376),
        "Vizag": (17.6868, 83.2185),
        "Coimbatore": (11.0168, 76.9558)
    }
    for n,(lat,lon) in default_locations.items():
        insert_location(n, lat, lon)

locations = get_locations()

# ======================
# LOAD MODELS
# ======================
xgb_model = joblib.load("xgb_model.pkl")
heatwave_model = joblib.load("heatwave_model.pkl")
kmeans_model = joblib.load("kmeans_model.pkl")
strategy_model = joblib.load("strategy_model.pkl")
le = joblib.load("label_encoder.pkl")

# ======================
# FETCH DATA
# ======================
@st.cache_data(ttl=300)
def get_live_data(locations):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_weather, name, lat, lon)
            for name,(lat,lon) in locations.items()
        ]
        for future in concurrent.futures.as_completed(futures):
            r = future.result()
            if r:
                insert_weather(r)
                results.append(r)
    return pd.DataFrame(results)

df_live = get_live_data(locations)

if df_live.empty:
    st.stop()

# ======================
# FEATURE ENGINEERING
# ======================
now = datetime.now()

df_live["month"] = now.month
df_live["hour"] = now.hour
df_live["day_of_week"] = now.weekday()

df_live["humidity_pct"] = df_live["humidity"]
df_live["wind_speed_kmph"] = df_live["wind_speed"]

df_live["temp_lag1"] = df_live["temperature"]
df_live["temp_lag2"] = df_live["temperature"]
df_live["temp_rolling_mean_3"] = df_live["temperature"]

features = [
    "humidity_pct","wind_speed_kmph","month","hour",
    "latitude","longitude","temp_lag1","temp_lag2",
    "temp_rolling_mean_3","day_of_week"
]

# ======================
# MODEL PREDICTIONS
# ======================
df_live["predicted_temp"] = xgb_model.predict(df_live[features])
df_live["heatwave"] = heatwave_model.predict(df_live[features])

df_live["cluster"] = kmeans_model.predict(
    df_live[["temperature","humidity_pct","wind_speed_kmph"]]
)

df_live["wind"] = df_live["wind_speed"]
df_live["strategy"] = le.inverse_transform(
    strategy_model.predict(df_live[["temperature","humidity","wind"]])
)

df_live["heat_risk"] = (
    0.5*df_live["temperature"] +
    0.3*df_live["humidity"] -
    0.2*df_live["wind_speed"]
)

# ======================
# NAVIGATION TABS
# ======================
tabs = st.tabs([
    "📊 Dashboard","🗺 Live Map","📈 Analysis",
    "🌿 Mitigation","🏆 Ranking","📜 History","🏗 Planning", "🔮 Forecast" 
])

# ======================
# DASHBOARD
# ======================

with tabs[0]:
   
    col1,col2,col3,col4 = st.columns(4)

    def card(title,val):
        return f"<div class='metric-card'><h4>{title}</h4><h2>{val}</h2></div>"

    col1.markdown(card("🌡 Avg Temp",f"{round(df_live.temperature.mean(),2)}°C"),True)
    col2.markdown(card("🔥 Max Temp",f"{round(df_live.temperature.max(),2)}°C"),True)
    col3.markdown(card("💧 Humidity",f"{round(df_live.humidity.mean(),2)}%"),True)
    col4.markdown(card("🌬 Wind",f"{round(df_live.wind_speed.mean(),2)}"),True)

    import plotly.express as px

    fig = px.scatter(
        df_live,x="longitude",y="latitude",
        color="heat_risk",size="temperature",
        hover_name="zone",color_continuous_scale="Turbo"
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      font_color="white")

    st.plotly_chart(fig,use_container_width=True)

# ======================
# OTHER PAGES
# ======================

with tabs[1]:
    create_live_map(df_live,xgb_model)

with tabs[2]:
    create_zone_analysis(df_live,xgb_model)

with tabs[3]:
    create_mitigation(df_live,xgb_model)

with tabs[4]:
    create_ranking(df_live)

with tabs[5]:
    create_history()

with tabs[6]:
    create_planning(df_live, xgb_model)
    
# ======================
# TAB 7 → FORECAST
# ======================
with tabs[7]:

    st.subheader("🔮 Future Temperature Prediction (Next 3 Hours)")

    zone = st.selectbox("Select Zone", df_live["zone"], key="forecast_zone")

    row = df_live[df_live["zone"] == zone].iloc[0]

    def predict_future(row):
        preds = []
        temp = row["temperature"]

        for i in range(3):
            input_df = pd.DataFrame([{
                "humidity_pct": row["humidity"],
                "wind_speed_kmph": row["wind_speed"],
                "month": datetime.now().month,
                "hour": datetime.now().hour,
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "temp_lag1": temp,
                "temp_lag2": temp,
                "temp_rolling_mean_3": temp,
                "day_of_week": datetime.now().weekday()
            }])

            temp = xgb_model.predict(input_df)[0]
            preds.append(temp)

        return preds

    future = predict_future(row)

    st.line_chart(future)
# ======================
# ADD LOCATION 
# ======================
st.sidebar.markdown("## 📍 Zone Insights")

zone = st.sidebar.selectbox("Select Zone", df_live["zone"])
row = df_live[df_live["zone"]==zone].iloc[0]

st.sidebar.markdown(f"""
<div class="glass-card">
🌡 Temp: {row['temperature']}°C<br><br>
🤖 Predicted: {round(row['predicted_temp'],2)}°C<br><br>
🔥 Heatwave: {"YES" if row['heatwave'] else "NO"}<br><br>
📍 Cluster: {int(row['cluster'])}<br><br>
🌿 Strategy: {row['strategy']}
</div>
""",unsafe_allow_html=True)

st.sidebar.markdown("### ➕ Add New Location")

new_name = st.sidebar.text_input("City Name", key="add_name")
new_lat = st.sidebar.number_input("Latitude", format="%.6f", key="add_lat")
new_lon = st.sidebar.number_input("Longitude", format="%.6f", key="add_lon")

if st.sidebar.button("Add Location", key="add_btn"):
    if not new_name:
        st.sidebar.error("Enter city name")
    elif not (-90 <= new_lat <= 90 and -180 <= new_lon <= 180):
        st.sidebar.error("Invalid coordinates")
    else:
        insert_location(new_name, new_lat, new_lon)
        st.sidebar.success("✅ Location added successfully")
        st.rerun()


# ======================
# DOWNLOAD
# ======================
st.sidebar.download_button(
    "📥 Download Data",
    df_live.to_csv(index=False),
    "urban_heat.csv"
)