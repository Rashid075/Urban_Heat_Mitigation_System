import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def create_mitigation(df_live, model):

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

    def simulate(h=0, w=0):
        temp_input = base_input.copy()
        temp_input["humidity_pct"] += h
        temp_input["wind_speed_kmph"] += w
        return model.predict(temp_input)[0]

    strategies = {
        "Urban Forest Program": simulate(2, 1),
        "Cool Roof Policy": simulate(-1, 0),
        "Permeable Pavement": simulate(0, 2),
        "Wind Corridor": simulate(0, 4),
        "Tree Canopy Mission": simulate(3, 1),
    }

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

    st.plotly_chart(fig, width='content')
    st.success(f"🏆 Best Strategy: {comparison_df.iloc[0]['Strategy']}")