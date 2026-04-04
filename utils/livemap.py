import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
from folium.plugins import HeatMap

def create_live_map(df_live, model):

    map_obj = folium.Map(
        location=[20.5937, 78.9629],
        zoom_start=5,
        tiles="OpenStreetMap"
    )

    now = datetime.now()

    for _, row in df_live.iterrows():

        input_df = pd.DataFrame([{
            "humidity_pct": row["humidity"],
            "wind_speed_kmph": row["wind_speed"],
            "month": now.month,
            "hour": now.hour,
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "temp_lag1": row["temperature"],
            "temp_lag2": row["temperature"],
            "temp_rolling_mean_3": row["temperature"],
            "day_of_week": now.weekday()
        }])

        predicted_temp = model.predict(input_df)[0]

        color = (
            "red" if predicted_temp > 40 else
            "orange" if predicted_temp > 35 else
            "yellow" if predicted_temp > 30 else "green"
        )

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=12,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            tooltip=f"""
            <b>{row['zone']}</b><br>
            🌡 Live: {row['temperature']} °C<br>
            🤖 Predicted: {round(predicted_temp, 2)} °C
            """
        ).add_to(map_obj)

    st_folium(map_obj, width=1200, height=600)
    heat_data = [
    [row["latitude"], row["longitude"], row["heat_risk"]]
    for _, row in df_live.iterrows()
    ]

    HeatMap(heat_data).add_to(map_obj)