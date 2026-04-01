import folium
from streamlit_folium import st_folium
from tomlkit import datetime
import pandas as pd
from datetime import datetime

def create_live_map(df_live, model):
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