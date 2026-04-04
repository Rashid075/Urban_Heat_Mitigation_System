import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_history, get_complete_history, get_locations


def create_history():

    st.subheader("📜 Historical Weather Analysis")

    # ==============================
    # ZONE SELECTION
    # ==============================
    locations = get_locations()

    if not locations:
        st.warning("No zones available")
        return

    zones = list(locations.keys())

    zone = st.selectbox("Select Zone", zones, key="zone_history")

    # ==============================
    # FETCH DATA
    # ==============================
    df_hist = get_history(zone)

    if df_hist.empty:
        st.warning("No historical data available for this zone")
        return

   
    df_hist["datetime"] = pd.to_datetime(df_hist["datetime"])

    # ==============================
    # METRICS 
    # ==============================
    col1, col2, col3 = st.columns(3)

    col1.metric("🌡 Avg Temp", round(df_hist["temperature"].mean(), 2))
    col2.metric("💧 Avg Humidity", round(df_hist["humidity"].mean(), 2))
    col3.metric("🌬 Avg Wind", round(df_hist["wind_speed"].mean(), 2))

    st.divider()

    # ==============================
    # TEMPERATURE TREND
    # ==============================
    st.subheader("🌡 Temperature Trend")

    fig_temp = px.line(
        df_hist,
        x="datetime",
        y="temperature",
        title="Temperature Over Time"
    )
    st.plotly_chart(fig_temp, use_container_width=True)

    # ==============================
    # HUMIDITY TREND
    # ==============================
    st.subheader("💧 Humidity Trend")

    fig_hum = px.line(
        df_hist,
        x="datetime",
        y="humidity",
        title="Humidity Over Time"
    )
    st.plotly_chart(fig_hum, use_container_width=True)

    # ==============================
    # WIND SPEED TREND
    # ==============================
    st.subheader("🌬 Wind Speed Trend")

    fig_wind = px.line(
        df_hist,
        x="datetime",
        y="wind_speed",
        title="Wind Speed Over Time"
    )
    st.plotly_chart(fig_wind, use_container_width=True)

    st.divider()

    # ==============================
    # COMBINED ANALYSIS
    # ==============================
    st.subheader("📊 Combined Weather Trends")

    fig_all = px.line(
        df_hist,
        x="datetime",
        y=["temperature", "humidity", "wind_speed"],
        title="All Parameters Trend"
    )
    st.plotly_chart(fig_all, use_container_width=True)

    # ==============================
    # RAW DATA TABLE
    # ==============================
    with st.expander("📄 View Raw Data"):
        st.dataframe(df_hist, use_container_width=True)


# ==============================
# GLOBAL HISTORY VIEW
# ==============================
def create_global_history():

    st.subheader("🌍 Global Historical Data")

    df_all = get_complete_history()

    if df_all.empty:
        st.warning("No data available")
        return

    df_all["datetime"] = pd.to_datetime(df_all["datetime"])

    fig = px.line(
        df_all,
        x="datetime",
        y="temperature",
        color="zone",
        title="Temperature Comparison Across Zones"
    )

    st.plotly_chart(fig, use_container_width=True)