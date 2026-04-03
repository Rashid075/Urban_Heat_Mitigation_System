import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_complete_history, get_history

def create_history():

    zone = st.selectbox("Select Zone", list(st.session_state.zones.keys()))
    data = get_history(zone)
    # data2 = get_complete_history()
    # print(data2)

    if data:
        df_hist = pd.DataFrame(
            data, columns=["temp", "humidity", "wind", "time"]
        )
        df_hist["time"] = pd.to_datetime(df_hist["time"])

        fig = px.line(df_hist, x="time", y="temp", title="Temperature Trend")
        st.plotly_chart(fig, width='content')