"""
Presentation Layer (UI Components).

This module defines functions responsible for rendering specific parts of the
Streamlit user interface, such as headers, tabs, charts, and metrics.
It receives prepared data and handles the visual layout, keeping the main
application script clean and declarative.
"""


import streamlit as st
from utils import plot_data, display_metrics
import constants as c
import pandas as pd



def render_sidebar_header():
    """Renders the header and instructions in the sidebar."""
    
    st.sidebar.title("Sidebar Menu")
    st.sidebar.info("**Instructions:** Select a location from the dropdown above to load the latest telemetry data.")

def render_header_metrics(location_name: str, lat: float, lon: float) -> None:
    """Renders the main location header and key geographic metrics."""

    st.header(f"Location: {location_name}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Latitude", f"{lat}°S")
    col2.metric("Longitude", f"{lon}°W")
    col3.metric("Data Source", "Meteoblue API")
    st.divider()


def render_about_tab():
    """Renders the content for the 'About' tab."""

    st.header("About Peru Regional Telemetry")
    st.markdown("""
    This application serves as a **weather data visualization dashboard** for strategic locations in Peru. 
    It is designed to demonstrate a complete end-to-end data pipeline: from raw API ingestion to interactive visualization.

    ### 🎯 Functionality & Workflow
    1.  **Select Location:** Use the Sidebar menu to choose a target city.
    2.  **7-Day Overview:** Analyze weekly trends for temperature and precipitation.
    3.  **1-Day Detail:** Drill down into a specific 24-hour period.

    ### 🛠️ Tech Stack & Architecture
    * **Data Acquisition:** Meteoblue API (REST).
    * **Data Processing:** Pandas (Time-series manipulation).
    * **Visualization:** Matplotlib (Static, high-quality charts).
    * **Interface:** Streamlit (Reactive UI).

    ### 📡 Data Source
    Weather forecast data provided by [Meteoblue](https://www.meteoblue.com).
    """)

def render_overview_content(df: pd.DataFrame) -> None:
    """Renders charts and metrics for the 7-Day Overview."""

    # Safety check using the constant
    if df.empty:
        st.warning(c.MSG_NO_DATA)
        return
    
    # 1. Temperature Section
    st.subheader("Temperature")
    display_metrics(df, 'temperature', 'temperature', '°C')
    st.caption("""💡 **Insight:** Blue line = measured air temperature. Yellow line = **'Felt Temperature'** (accounts for wind chill, humidity, radiation).""")
    
    fig = plot_data(df, 
            x_col='time', y_cols=['temperature', 'felttemperature'], 
            x_label=c.LABEL_DATE, y_label=c.LABEL_TEMP, 
            graph_type="line", date_format=c.DATE_FMT_OVERVIEW)
    st.pyplot(fig)

    # 2. Precipitation Section
    st.subheader("All Precipitations")
    display_metrics(df, 'precipitation', 'precipitation', 'mm')
    
    fig = plot_data(df, 
            x_col='time', y_cols=['precipitation'], 
            x_label=c.LABEL_DATE, y_label=c.LABEL_TOTAL_PREP, 
            graph_type="bar", date_format=c.DATE_FMT_OVERVIEW)
    st.pyplot(fig)

    # 3. Convective Precipitation Section
    st.subheader("Convective precipitations")
    st.caption("💡 **Note:** Showers and thunderstorms (short, intense events).")
    display_metrics(df, 'convective_precipitation', 'conv. precipitation', 'mm')
    
    fig = plot_data(df, 
            x_col='time', y_cols=['convective_precipitation'], 
            x_label=c.LABEL_DATE, y_label=c.LABEL_CONV_PREP, 
            graph_type="bar", date_format=c.DATE_FMT_OVERVIEW)
    st.pyplot(fig)

def render_detail_content(df_day: pd.DataFrame) -> None:
    """Renders charts and metrics for the 1-Day Detail view."""

    # Safety check using the constant
    if df_day.empty:
        st.warning(c.MSG_NO_DATA)
        return
    
    # 1. Temperature
    st.subheader("Temperature (24h)")
    display_metrics(df_day, 'temperature', 'temperature', '°C')
    
    fig = plot_data(df_day, 
            x_col='time', y_cols=['temperature', 'felttemperature'], 
            x_label=c.LABEL_HOURS, y_label=c.LABEL_TEMP, 
            graph_type="line", date_format=c.DATE_FMT_DETAIL)
    st.pyplot(fig)

    # 2. Precipitation
    st.subheader("All Precipitations (24h)")
    display_metrics(df_day, 'precipitation', 'precipitation', 'mm')
    
    fig = plot_data(df_day, 
            x_col='time', y_cols=['precipitation'], 
            x_label=c.LABEL_HOURS, y_label=c.LABEL_TOTAL_PREP, 
            graph_type="bar", date_format=c.DATE_FMT_DETAIL)
    st.pyplot(fig)

    # 3. Convective Precipitation
    st.subheader("Convective precipitations (24h)")
    display_metrics(df_day, 'convective_precipitation', 'conv. precipitation', 'mm')
    
    fig = plot_data(df_day, 
            x_col='time', y_cols=['convective_precipitation'], 
            x_label=c.LABEL_HOURS, y_label=c.LABEL_CONV_PREP, 
            graph_type="bar", date_format=c.DATE_FMT_DETAIL)
    st.pyplot(fig)

def render_footer():
    """Renders the application footer."""
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: grey; font-size: small;'>
            Telemetry Dashboard v1.0 | Built with Streamlit & Python <br>
            Data provider: <a href='https://www.meteoblue.com'>Meteoblue Weather API</a>
        </div>
        """,
        unsafe_allow_html=True
    )


# views.py

def setup_page_styling():
    """
    Injects CSS to hide default Streamlit elements (footer, menu, header)
    to give the application a custom, professional look.
    """
    hide_streamlit_style = """
        <style>      
        /* Hide streamlit footer "Made with Streamlit" */
        footer {visibility: hidden;}
        
        /* Hide streamlit header */
        header {visibility: hidden;}
        </style>
        """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)