import streamlit as st
import plotly.graph_objects as go

def create_planning(df_live):

    zone = st.selectbox("Select Zone", df_live["zone"])
    row = df_live[df_live["zone"] == zone].iloc[0]

    trees = st.slider("Add Trees (%)", 0, 50, 10)
    wind_boost = st.slider("Wind Improvement", 0, 5, 1)

    new_temp = (
        row["temperature"]
        - (trees * 0.05)
        - (wind_boost * 0.5)
    )

    st.metric("Current Temp", row["temperature"])
    st.metric("After Planning", round(new_temp, 2))

    fig = go.Figure()
    fig.add_bar(x=["Current", "Planned"], y=[row["temperature"], new_temp])

    st.plotly_chart(fig, width='content')