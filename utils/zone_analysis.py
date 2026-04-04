from datetime import datetime
import streamlit as st
import pandas as pd
import shap
import matplotlib.pyplot as plt


def create_zone_analysis(df_live, model):

    # ======================
    # SELECT ZONE
    # ======================
    zone = st.selectbox("Select Zone", df_live["zone"], key="zone_analysis")

    zone_data = df_live[df_live["zone"] == zone].iloc[0]

    now = datetime.now()

    # ======================
    # CREATE INPUT FEATURES
    # ======================
    input_df = pd.DataFrame([{
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

    # ======================
    # PREDICTION
    # ======================
    predicted_temp = model.predict(input_df)[0]

    # ======================
    # METRICS
    # ======================
    col1, col2, col3 = st.columns(3)

    col1.metric("🌡 Live Temp", zone_data["temperature"])
    col2.metric("🤖 Predicted Temp", round(predicted_temp, 2))
    col3.metric("🔥 Heat Risk", round(zone_data["heat_risk"], 2))

    # ======================
    # SHAP EXPLANATION
    # ======================


    st.subheader("📊 AI Explanation")

    features = [
        "humidity_pct",
        "wind_speed_kmph",
        "month",
        "hour",
        "latitude",
        "longitude",
        "temp_lag1",
        "temp_lag2",
        "temp_rolling_mean_3",
        "day_of_week"
    ]

    # Create input
    input_df = pd.DataFrame([{
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

    #  Use model.predict
    explainer = shap.Explainer(model.predict, input_df)

    shap_values = explainer(input_df)

    fig, ax = plt.subplots(figsize=(8, 4))
    shap.plots.waterfall(shap_values[0], show=False)

    st.pyplot(fig)

    st.info("📌 This shows which features increased or decreased temperature.")