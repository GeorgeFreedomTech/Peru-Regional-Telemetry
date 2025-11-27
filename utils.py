"""
Core Business Logic and Data Pipeline.

This module contains pure Python functions responsible for:
1. Fetching raw data from the Meteoblue API (with caching).
2. Transforming and cleaning data using Pandas.
3. Generating visualization objects (Matplotlib figures).

This layer is decoupled from the Streamlit UI to ensure separation of concerns.
"""


import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import constants


# Loads API key from .toml file
API_KEY = st.secrets["METEOBLUE_API_KEY"]

# The base URL for meteodata - the API package
METEODATA_URL = "https://my.meteoblue.com/packages/basic-1h"

# ttl = maximum time to keep an entry in the cache (e.g. ttl="1d" - keep for 1 day) - for production
# persist = save data locally (e.g. persist="disk" save to .streamlit/cache) - for development
@st.cache_data(ttl="1d")
def fetch_data(lat: float, lon: float) -> dict | None:
    """
    Fetches hourly weather forecast data from the Meteoblue API.

    This function makes an authenticated GET request to the Meteoblue API
    to retrieve 'basic-1h' forecast data. It enforces metric units
    (Celsius, mm, m/s) to ensure consistency. The result is cached 
    by Streamlit for 24 hours to minimize API calls.

    Parameters:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.

    Returns:
        dict: The raw JSON response from the API containing weather data,
              or None if the request fails.
    """

    # 1. Check if the API key is available
    if not API_KEY:
        st.error("System Error: API Key is missing.")
        return

    # 2. Set up the request parameters:
    # get data for a location, force units
    meteo_params = {
        'apikey': API_KEY,
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'forecast_days': 7,
        'temperature': 'C',       
        'windspeed': 'ms-1',      
        'precipitationamount': 'mm'
    }

    # 3. Make the API call to fetch meteo data
    try:
        response = requests.get(METEODATA_URL, params=meteo_params)
        response.raise_for_status() 

    except requests.exceptions.HTTPError as http_err:
        status_code = response.status_code

        if status_code == 403:
            st.error("⛔ **Authorization Error:** The API key is invalid or unauthorized.")
        elif status_code == 429:
            st.error("⏳ **Quota Exceeded:** The daily API limit has been reached. Please try again later.")
        elif status_code >= 500:
            st.error(f"🔥 **Server Error:** Meteoblue services are currently unavailable (Status: {status_code}).")
        else:
            st.error(f"❌ **API Error:** An unexpected error occurred: {http_err}")
        
        # Log details to console for developer debugging
        print(f"Detailed error: {response.text}")
        return None

    except requests.exceptions.ConnectionError:
        st.error("📡 **Connection Error:** Unable to reach the API. Check your internet connection.")
        return None

    except requests.exceptions.RequestException as err:
        st.error(f"⚠️ **Request Error:** Something went wrong: {err}")
        return None

    # 4. Process and return the successful response
    try:
        data = response.json()
        
        # Check if API returned a business logic error inside JSON
        if "error_message" in data: 
             st.error(f"API Message: {data['error_message']}")
             return None

        return data

    except requests.exceptions.JSONDecodeError:
        st.error("🧩 **Data Error:** Received invalid data format from API.")
        return None


# create DataFrame from json
def transform_data(data: dict) -> pd.DataFrame:
    """
    Transforms raw API JSON data into a clean Pandas DataFrame.

    This function extracts the 'data_1h' timeseries section from the API
    response, converts it into a DataFrame, filters for relevant columns,
    parses the 'time' column into datetime objects, and adds calculated
    columns for smoothed data trends.

    Parameters:
        data (dict): The raw JSON dictionary returned by fetch_data().

    Returns:
        pd.DataFrame: A cleaned DataFrame ready for visualization.
    """

    data_1h = data["data_1h"] # extract the relevant part from the JSON dict
    target_columns = [
        "time", 
        "temperature", 
        "felttemperature", 
        "precipitation", 
        "convective_precipitation"
        ]
    df = pd.DataFrame(data_1h, columns=target_columns) # get DataFrame

    # clean and prepare data
    df['time'] = pd.to_datetime(df['time']) 
    # converts column with timestamp to DateTime object
    df['smooth_temperature'] = df['temperature'].rolling(3, min_periods=1).mean() 
    # smoothing the curve (of 3 values, if not possible of 1 value)
    df['smooth_felttemperature'] = df['felttemperature'].rolling(3, min_periods=1).mean() 
    # smoothing the curve (of 3 values, if not possible of 1 value)
    return df


def plot_data(df: pd.DataFrame, x_col: str, y_cols: list[str] | str, x_label: str, y_label: str, graph_type: str, date_format: str) -> Figure:    
    """
    Plots data (line chart) from the provided DataFrame.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing the data to plot.
    x_col (str): Name of the column to use for the X-axis (e.g., 'time').
    y_cols (list): List of column names to plot on the Y-axis (e.g., ['temperature', 'precipitation']).
    x_label (str): Label for the X-axis.
    y_label (str): Label for the Y-axis.
    graph_type (str): Type of graph to plot ("line" or "bar").
    date_format (str): Y-axis time/date formatting 

    Example:
    plot_data(
        df_to_plot, 
        x_col="time", 
        y_cols=["temperature", "felttemperature"], 
        x_label="Date", 
        y_label="Temperature (°C)", 
        graph_type="line",
        date_format="%d-%m-%Y"
    )    
    """
    if isinstance(y_cols, str): # in case y_cols parameter is "str" and not "list"
        y_cols = [y_cols]

    # --- Configuration ---
    fig, ax = plt.subplots(figsize=constants.CHART_FIGSIZE) # create the Figure (fig) and Axes (ax) objects

    # --- Plotting the Data ---
    if graph_type == "line": # plot line chart
        for y_col in y_cols: # loop through each Y column to plot
            ax.plot(df[x_col], df[y_col], linewidth=1, label=df[y_col].name)
    elif graph_type == "bar": # plot bar chart
        ax.bar(df[x_col], df[y_cols[0]], label=df[y_cols[0]].name)

    # --- Ax Formatting (labels, ticks, fonts) ---
    ax.set_xlabel(x_label, fontsize=20) # X-axis label
    ax.set_ylabel(y_label, fontsize=16) # Y-axis label
    ax.tick_params(axis='x', labelsize=12) 
    ax.tick_params(axis='y', labelsize=12)

    # ax.set_ylim(-10, 10) # Optional: Set Y-axis limits if needed

    # Date formatter for the X-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))

    # Legend
    ax.legend(fontsize=16) # display label for each line
    ax.grid(True) # grid for readability

    # The plot
    return fig


def get_city_mapping(raw_data: list[dict]) -> tuple[list[str], dict]:
    """
    Parses the hierarchical data to create a flat list of 'City (Province)'
    and a lookup dictionary for their coordinates.
    """

    city_display_names = []
    city_lookup = {}

    for province in raw_data:
        province_name = province["name"]
        
        for city in province["cities"]:
            display_name = f"{city['name']} ({province_name})" # combine city & province
            city_display_names.append(display_name)
            city_lookup[display_name] = city["location"]
            
    return city_display_names, city_lookup


def display_metrics(df: pd.DataFrame, column_name: str, label: str, unit: str = "") -> None:
    """
    Calculates and displays max/min metrics for a specific column in two columns.
    
    Parameters:
    df (pd.DataFrame): The dataframe containing the data.
    column_name (str): The name of the column to analyze.
    label (str): The label description (e.g., 'Temperature').
    unit (str): Optional unit string to append to the value (e.g., '°C').
    """

    max_val = df[column_name].max()
    min_val = df[column_name].min()

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=f"Maximum {label}", value=f"{max_val:.1f} {unit}")
    with col2:
        st.metric(label=f"Minimum {label}", value=f"{min_val:.1f} {unit}")
    st.divider()