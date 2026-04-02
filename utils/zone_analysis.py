import datetime
import streamlit as st
import pandas as pd


def create_zone_analysis(df_live, model):
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

    st.metric("Live Temp", zone_data["temperature"].values[0])
    st.metric("Predicted Heat", round(predicted_temp, 2))
    st.metric("Heat Risk", round(zone_data["heat_risk"].values[0], 2))