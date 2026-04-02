import streamlit as st
import plotly.express as px

def create_ranking(df_live):

    df_rank = df_live[["zone", "heat_risk"]].sort_values(
        "heat_risk", ascending=False
    )

    fig = px.bar(df_rank, x="heat_risk", y="zone", orientation="h")
    st.plotly_chart(fig, width='content')