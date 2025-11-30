"""
Main Application Entry Point.

This script serves as the orchestrator for the Streamlit application.
It handles the application lifecycle, initializes the UI layout, manages
user inputs (sidebar), and coordinates data flow between the backend logic
(utils.py) and the presentation layer (views.py).
"""


import streamlit as st
import pandas as pd
from utils import fetch_data, transform_data, get_city_mapping
from views import (
    render_sidebar_header, 
    render_header_metrics, 
    render_about_tab, 
    render_overview_content,
    render_detail_content, 
    render_footer
)
from data import data
import constants as c

# 1. App Configuration
st.set_page_config(page_title="Peru Regional Telemetry", layout="wide")
st.title("Peru Regional Telemetry")

# 2. Sidebar & Inputs
render_sidebar_header()
city_options, city_lookup = get_city_mapping(data)

selected_location = st.sidebar.selectbox(
    "Select Location:", 
    city_options, 
    index=None, 
    placeholder="Choose a location to start..."
)

# 3. Main Layout Structure
tab_about, tab_overview, tab_detail = st.tabs(["About", "7-Day Overview", "1-Day Detail"])

# 4. Content Rendering
# Always render About tab
with tab_about:
    render_about_tab()

# Render Data tabs only if location is selected
if selected_location:
    # Prepare Data
    coords = city_lookup[selected_location]
    raw_data = fetch_data(lat=coords['lat'], lon=coords['lon'])
    
    if raw_data is None:
        st.stop()
        
    df = transform_data(data=raw_data)

    # Presentation: Overview Tab
    with tab_overview:
    # Presentation: Header Metrics (Shared)
        render_header_metrics(selected_location, coords['lat'], coords['lon'])
        render_overview_content(df)

    # Presentation: Detail Tab
    with tab_detail:
        # Logic for Detail View
        min_date = df['time'].dt.date.min()
        max_date = df['time'].dt.date.max()
        
        selected_date = st.sidebar.date_input(
            "Select a day for hourly detail:",
            value=None,
            min_value=min_date,
            max_value=max_date,
            help="Choose a date within the forecast range to see hourly details."
        )
        
        if selected_date:
            # Filter data
            df_day = df[df['time'].dt.date == selected_date]
            # Presentation: Header Metrics (Shared)
            render_header_metrics(selected_location, coords['lat'], coords['lon'])
            # Render content
            render_detail_content(df_day)
        else:
            st.info(c.MSG_SELECT_DATE)

else:
    st.info(c.MSG_SELECT_LOCATION)

# 5. Footer
render_footer()