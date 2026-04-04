import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px


def create_planning(df_live, xgb_model):

    st.markdown("## 🏗 Urban Planning Simulation")

    # ======================
    # SELECT ZONE
    # ======================
    zone = st.selectbox("Select Zone", df_live["zone"], key="zone_planning")
    zone_data = df_live[df_live["zone"] == zone].iloc[0]

    now = datetime.now()

    st.markdown("### ⚙️ Adjust Planning Parameters")

    # ======================
    # INPUT SLIDERS
    # ======================
    col1, col2 = st.columns(2)

    with col1:
        tree_pct = st.slider("🌳 Tree Coverage (%)", 0, 100, 20)
        cool_roof = st.slider("🏠 Cool Roof Coverage (%)", 0, 100, 10)
        pavement = st.slider("🧱 Cool Pavement (%)", 0, 100, 10)
        water = st.slider("🌊 Water Bodies (%)", 0, 100, 5)

    with col2:
        wind_boost = st.slider("🌬 Wind Improvement", 0, 10, 2)
        density = st.slider("🏢 Reduce Building Density (%)", 0, 100, 5)
        traffic = st.slider("🚗 Traffic Reduction (%)", 0, 100, 10)

    # ======================
    # BASE VALUES
    # ======================
    base_temp = zone_data["temperature"]
    base_humidity = zone_data["humidity"]
    base_wind = zone_data["wind_speed"]

    # ======================
    # APPLY SIMULATION EFFECTS
    # ======================
    new_temp = base_temp
    new_humidity = base_humidity
    new_wind = base_wind

    # 🌳 Trees
    new_humidity += tree_pct * 0.05
    new_temp -= tree_pct * 0.03

    # 🌬 Wind
    new_wind += wind_boost

    # 🏠 Cool Roof
    new_temp -= cool_roof * 0.04

    # 🧱 Pavement
    new_temp -= pavement * 0.02
    new_humidity += pavement * 0.01

    # 🌊 Water
    new_temp -= water * 0.05
    new_humidity += water * 0.03

    # 🏢 Density
    new_wind += density * 0.05
    new_temp -= density * 0.02

    # 🚗 Traffic
    new_temp -= traffic * 0.03

    # ======================
    # CREATE MODEL INPUT
    # ======================
    input_df = pd.DataFrame([{
        "humidity_pct": new_humidity,
        "wind_speed_kmph": new_wind,
        "month": now.month,
        "hour": now.hour,
        "latitude": zone_data["latitude"],
        "longitude": zone_data["longitude"],
        "temp_lag1": new_temp,
        "temp_lag2": new_temp,
        "temp_rolling_mean_3": new_temp,
        "day_of_week": now.weekday()
    }])

    # ======================
    # PREDICTION
    # ======================
    predicted_temp = xgb_model.predict(input_df)[0]

    # ======================
    # DISPLAY RESULTS
    # ======================
    st.markdown("### 📊 Results")

    col1, col2 = st.columns(2)

    col1.metric("🌡 Current Temp", round(base_temp, 2))
    col2.metric("🤖 Predicted Temp After Planning", round(predicted_temp, 2))

    reduction = base_temp - predicted_temp

    if reduction > 0:
        st.success(f"✅ Temperature reduced by {round(reduction, 2)}°C")
    else:
        st.warning("⚠️ No improvement detected")

    # ======================
    # VISUAL COMPARISON
    # ======================
    comparison_df = pd.DataFrame({
        "Type": ["Current", "After Planning"],
        "Temperature": [base_temp, predicted_temp]
    })

    fig = px.bar(
        comparison_df,
        x="Type",
        y="Temperature",
        color="Type",
        title="Temperature Comparison"
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ======================
    # INSIGHTS
    # ======================
    st.markdown("### 🧠 Planning Insights")

    insights = []

    if tree_pct > 50:
        insights.append("🌳 High tree coverage significantly reduces heat.")

    if cool_roof > 40:
        insights.append("🏠 Cool roofs are effectively reflecting heat.")

    if water > 20:
        insights.append("🌊 Water bodies provide strong cooling via evaporation.")

    if wind_boost > 5:
        insights.append("🌬 Improved airflow is reducing trapped heat.")

    if traffic > 40:
        insights.append("🚗 Traffic reduction is lowering heat emissions.")

    if density > 30:
        insights.append("🏢 Reduced building density improves ventilation.")

    if insights:
        for i in insights:
            st.info(i)
    else:
        st.info("Try increasing parameters to see stronger cooling effects.")