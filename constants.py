"""
Global Constants and Configuration.

This module stores application-wide constants such as chart labels,
date formats, and styling parameters to ensure consistency and easy maintenance.
"""


# date formats
DATE_FMT_OVERVIEW = '%d-%m-%Y' # set an X-axis format to show days
DATE_FMT_DETAIL = '%H:%M' # set a new X-axis format to show hours and minute

# graph labels
LABEL_TEMP = "Temperature (°C)"
LABEL_TOTAL_PREP = "Total Precipitation (mm)"
LABEL_CONV_PREP = "Convective Precipitation - rains (mm)"
LABEL_DATE = "Date"
LABEL_HOURS = "Time (hours)"

# graph config
CHART_FIGSIZE = (13, 7) # graph size 

# UI messages
MSG_SELECT_LOCATION = "👈 Please select a location to view the forecast."
MSG_SELECT_DATE = "👈 Please select a date to get a detailed view."
MSG_NO_DATA = "No data available."