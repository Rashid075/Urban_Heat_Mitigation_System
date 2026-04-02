import streamlit as st
import joblib
from streamlit_option_menu import option_menu

from utils.util import *
from utils.zone_analysis import create_zone_analysis
from utils.livemap import create_live_map
from utils.mitigation import create_mitigation
from utils.ranking import create_ranking
from utils.planning import create_planning
from utils.history import create_history


# ==============================
# INIT DB
# ==============================
from db import *
init_db()

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Urban Heat Intelligence",
    page_icon="🌍",
    layout="wide"
)

st.title("🌡 Urban Heat Intelligence System")



# ==============================
# LOAD MODEL
# ==============================
model = joblib.load("weather_model_updated.pkl")

# ==============================
# LOAD ZONES FROM DB
# ==============================
if "zones" not in st.session_state:
    st.session_state.zones = get_zones()
    if not st.session_state.zones:
        st.session_state.zones = {
            "Charminar": (17.3616, 78.4747),
            "Falaknuma": (17.3326, 78.4751),
            "Saidabad": (17.3615, 78.5118),
            "Malakpet": (17.3736, 78.4996),
            "Dilsukhnagar": (17.3684, 78.5228),
            "LB Nagar": (17.3501, 78.5510),
            "Uppal": (17.4025, 78.5612),
            "Habsiguda": (17.4154, 78.5426),
            "Secunderabad": (17.5042, 78.5426),
            "Malkajgiri": (17.4511, 78.5369),
            "Kukatpally": (17.4930, 78.4054),
            "Moosapet": (17.4685, 78.4206),
            "Miyapur": (17.4981, 78.3567),
            "BHEL": (17.4951, 78.2958),
            "Gachibowli": (17.4436, 78.3519),
            "Kondapur": (17.4587, 78.3730),
            "Madhapur": (17.4408, 78.3916),
            "HITEC City": (17.4490, 78.3831),
            "Jubilee Hills": (17.4308, 78.4102),
            "Banjara Hills": (17.4177, 78.4399),
    }

# ==============================
# ADD LOCATION UI
# ==============================
st.sidebar.subheader("➕ Add New Location")

zone_name = st.sidebar.text_input("Location Name")
lat = st.sidebar.number_input("Latitude", format="%.6f")
lon = st.sidebar.number_input("Longitude", format="%.6f")

if st.sidebar.button("Add Location"):
    if not zone_name:
        st.sidebar.error("Enter name")
    elif not (-90 <= lat <= 90 and -180 <= lon <= 180):
        st.sidebar.error("Invalid coordinates")
    else:
        insert_zone(zone_name, lat, lon)
        st.session_state.zones[zone_name] = (lat, lon)
        st.cache_data.clear()
        st.sidebar.success("Saved to DB ✅")

# ==============================
# FETCH DATA PARALLEL + SAVE
# ==============================
df_live = get_live_data(st.session_state.zones)

# ==============================
# HEAT RISK SCORE
# ==============================
df_live = compute_heat_risk(df_live)

# ==============================
# NAVBAR options
# ==============================
options = option_menu(
    menu_title=None,
    options=[
        "Live Map",
        "Zone Analysis",
        "Mitigation",
        "Ranking",
        "History",
        "Planning"
    ],
    icons=["globe", "bar-chart", "tree", "trophy", "clock", "building"],
    orientation="horizontal"
)

# ==============================
# Rendering navbar content
# ==============================
if options == "Live Map":
    create_live_map(df_live, model)
elif options == "Zone Analysis":
    create_zone_analysis(df_live, model)
elif options == "Mitigation":
    create_mitigation(df_live, model)
elif options == "Ranking":
    create_ranking(df_live)
elif options == "History":
    create_history()
elif options == "Planning":
    create_planning(df_live)

# ==============================
# EXPORT
# ==============================
st.sidebar.download_button(
    "📥 Download Data",
    df_live.to_csv(index=False),
    file_name="urban_heat_data.csv"
)