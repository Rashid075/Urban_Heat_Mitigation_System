import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


def create_mitigation(df_live, model):

    zone = st.selectbox("Select Zone", df_live["zone"], key="zone_mitigation")
    zone_data = df_live[df_live["zone"] == zone].iloc[0]

    now = datetime.now()

    #  FULL FEATURE SET
    base_input = pd.DataFrame([{
        "humidity_pct": zone_data["humidity"],
        "wind_speed_kmph": zone_data["wind_speed"],
        "month": now.month,
        "hour": now.hour,
        "latitude": zone_data["latitude"],
        "longitude": zone_data["longitude"],
        "temp_lag1": zone_data["temperature"],
        "temp_lag2": zone_data["temperature"],
        "temp_rolling_mean_3": zone_data["temperature"],
        "day_of_week": now.weekday()
    }])

    base_temp = model.predict(base_input)[0]

    st.metric("🌡 Current Predicted Temp", round(base_temp, 2))

    # ======================
    # SIMULATION FUNCTION
    # ======================
    def simulate(h=0, w=0):
        temp_input = base_input.copy()
        temp_input["humidity_pct"] += h
        temp_input["wind_speed_kmph"] += w
        return model.predict(temp_input)[0]

    # ======================
    # STRATEGIES
    # ======================
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
        orientation="h",
        title="Mitigation Strategy Comparison"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.success(f"🏆 Best Strategy: {comparison_df.iloc[0]['Strategy']}")