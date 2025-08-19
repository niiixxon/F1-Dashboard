import sys
import os
import pandas as pd
import streamlit as st
import colorsys
import time

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# --- Data Loading & Processing ---
from app.data_loader import (
    fetch_meetings, fetch_sessions, fetch_drivers, fetch_laps,
    fetch_pit, fetch_stints, fetch_weather, clear_cache_files
)
from app.data_processor import (
    clean_laps, clean_drivers, build_driver_color_map, calculate_stint_lap_ranges,
    prepare_tyre_degradation_data, clean_weather
)

# --- Visualizers ---
from app.visualizer.lap_charts import plot_lap_times
from app.visualizer.stint_charts import plot_tire_strategy
from app.visualizer.position_charts import plot_race_positions, plot_position_changes
from app.visualizer.weather_charts import plot_weather
from app.visualizer.sector_charts import plot_sector_times
from app.visualizer.degradation_charts import plot_tyre_degradation

# --- Streamlit Page Setup ---
st.set_page_config(page_title="OpenF1 Strategy Dashboard", layout="wide")
# Developer key for hidden functionality
DEV_MODE = st.sidebar.text_input("Developer Key", type="password") == "gilfoylehyde"

st.title("F1 Dashboard — Interactive Version")

# --- Step 1: Select Year ---
possible_years = [2025, 2024, 2023, 2022]
available_years = []

for y in possible_years:
    try:
        meetings_for_year = fetch_meetings(y)
        if meetings_for_year:  # Only include years with meetings
            available_years.append(y)
    except:
        pass  # Ignore errors for that year

if not available_years:
    st.error("No meetings available for any year.")
    st.stop()

year = st.selectbox("Select Year", available_years, index=0)

try:
    with st.spinner("Fetching meetings..."):
        meetings = fetch_meetings(year)
except Exception as e:
    st.error(f"Error fetching meetings: {e}")
    st.stop()

if not meetings:
    st.warning("No meetings found for this year.")
    st.stop()

# --- Developer Tools (Hidden) ---
DEV_MODE = False
show_dev = st.sidebar.checkbox("Show Developer Tools")  # minimal sidebar toggle

if show_dev:
    dev_key = st.sidebar.text_input("Enter Developer Key", type="password")
    if dev_key == "my_secret_key":  # replace with your own secret
        DEV_MODE = True

if DEV_MODE:
    st.markdown("---")
    st.subheader("Developer Tools")

    if st.button("Refresh Data Cache"):
        clear_cache_files()
        st.experimental_rerun()

    if st.button("Refresh Laps Data"):
        laps_raw = fetch_laps(session_key)
        laps = clean_laps(laps_raw)
        st.success("Laps data refreshed!")



meeting_names = [m["meeting_name"] for m in meetings]
selected_meeting = st.selectbox("Select Race/Meeting", meeting_names)
meeting_key = next(m["meeting_key"] for m in meetings if m["meeting_name"] == selected_meeting)

# --- Step 2: Select Session ---
try:
    with st.spinner("Fetching sessions..."):
        sessions = fetch_sessions(meeting_key)
except Exception as e:
    st.error(f"Error fetching sessions: {e}")
    st.stop()

if not sessions:
    st.warning("No sessions found for this meeting.")
    st.stop()

session_names = [s["session_name"] for s in sessions]
selected_session = st.selectbox("Select Session", session_names)
session_key = next(s["session_key"] for s in sessions if s["session_name"] == selected_session)

# --- Step 3: Fetch and Clean Laps ---
try:
    laps_raw = fetch_laps(session_key)
except Exception as e:
    st.error(f"Error fetching laps: {e}")
    st.stop()

if not laps_raw:
    st.warning("No laps data found for this session.")
    st.stop()

laps = clean_laps(laps_raw)

# --- Step 4: Fetch Drivers and Build Color Map ---
try:
    with st.spinner("Fetching drivers..."):
        drivers_raw = fetch_drivers(session_key)
except Exception as e:
    st.error(f"Error fetching drivers: {e}")
    st.stop()

if not drivers_raw:
    st.warning("No drivers data found for this session.")
    st.stop()

drivers = clean_drivers(drivers_raw)
driver_colors = build_driver_color_map(drivers_raw)



# --- Display Driver Info ---
display_df = drivers[['driver_number', 'broadcast_name', 'full_name', 'name_acronym', 'team_name', 'team_colour', 'headshot_url']].copy()

def color_box(hex_color):
    return f'<div style="width:80px; height:50px; background-color:{hex_color}; border:1px solid #000;"></div>'

display_df['team_color_box'] = display_df['team_colour'].apply(color_box)

def img_tag(url):
    return f'<img src="{url}" width="100" style="border-radius:10%;">'

display_df['headshot_img'] = display_df['headshot_url'].apply(img_tag)

display_df = display_df.drop(columns=['team_colour', 'headshot_url'])
display_df = display_df.rename(columns={
    'driver_number': 'Driver Number',
    'broadcast_name': 'Broadcast Name',
    'full_name': 'Full Name',
    'name_acronym': 'Acronym',
    'team_name': 'Team',
    'team_color_box': 'Team Color',
    'headshot_img': 'Headshot'
}).sort_values(by=['Team', 'Driver Number']).reset_index(drop=True)

st.write("### Drivers Info with Colors and Headshots")
st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# --- Step 5: Lap Times Chart ---
st.subheader("Lap Times")
st.plotly_chart(plot_lap_times(laps, driver_colors, drivers), use_container_width=True)

if st.checkbox("Show lap data table"):
    st.dataframe(laps[['lap_number', 'driver_number', 'lap_duration']].sort_values(['driver_number', 'lap_number']))

# --- Step 6: Tire Strategy / Stints ---
try:
    with st.spinner("Fetching stints..."):
        stints_raw = fetch_stints(session_key)
except Exception as e:
    st.error(f"Error fetching stints: {e}")
    st.stop()

if not stints_raw:
    st.warning("No stints data found for this session.")
    stints = pd.DataFrame()
else:
    stints = calculate_stint_lap_ranges(stints_raw)

st.subheader("Tire Strategy")
driver_options = ["All"] + drivers["broadcast_name"].tolist()
selected_driver = st.selectbox("Select Driver", driver_options)

if selected_driver != "All":
    driver_num = drivers.loc[drivers["broadcast_name"] == selected_driver, "driver_number"].iloc[0]
    stints_filtered = stints[stints["driver_number"] == driver_num]
else:
    stints_filtered = stints

if not stints_filtered.empty:
    st.plotly_chart(plot_tire_strategy(stints_filtered, driver_colors, drivers), use_container_width=True)
else:
    st.info("No tire stint data available.")

# --- Step 7: Race Position Charts ---


# --- Fetch Weather Early ---
try:
    with st.spinner("Fetching weather data..."):
        weather_raw = fetch_weather(session_key)
except Exception as e:
    st.error(f"Error fetching weather data: {e}")
    weather_raw = []

weather = clean_weather(weather_raw)

# --- Step 8: Tyre Degradation ---
# --- Step 8: Tyre Degradation ---
from app.visualizer.degradation_charts import plot_tyre_degradation

# Multi-driver selection & rolling window
driver_options = drivers["broadcast_name"].tolist()
selected_drivers_deg = st.multiselect(
    "Select Drivers for Degradation Chart (multi-select allowed)",
    driver_options,
    default=driver_options[:2]  # show first 2 by default
)


if laps_raw and stints_raw:
    laps_df = clean_laps(laps_raw)
    stints_df = calculate_stint_lap_ranges(stints_raw)

    if selected_drivers_deg:
        selected_driver_nums = drivers[drivers["broadcast_name"].isin(selected_drivers_deg)]["driver_number"].tolist()
    else:
        selected_driver_nums = None

    st.subheader("Tyre Degradation Trends")
    st.plotly_chart(
        plot_tyre_degradation(laps_df, stints_df, driver_colors, weather, selected_drivers=selected_driver_nums),
        use_container_width=True
    )
else:
    st.info("No data available to show tyre degradation trends.")



# --- Step 9: Weather Conditions ---
try:
    with st.spinner("Fetching weather data..."):
        weather_raw = fetch_weather(session_key)
except Exception as e:
    st.error(f"Error fetching weather data: {e}")
    weather_raw = []

weather = clean_weather(weather_raw)
if not weather.empty:
    st.subheader("Weather Conditions")
    st.plotly_chart(plot_weather(weather), use_container_width=True)
else:
    st.info("No weather data available for this session.")

# --- Step 10: Sector Times ---
# --- Step 10: Sector Times ---
from app.visualizer.sector_charts import (
    plot_sector_times,
    plot_sector_leaderboard  # ensure this exists in sector_charts.py
)

st.subheader("Sector Times Overview")

# --- 1. Standard Sector Times Chart (all drivers) ---
#st.write("### Sector Times per Driver")
#st.plotly_chart(plot_sector_times(laps, driver_colors), use_container_width=True)

# --- 2. Sector Leaders Bar Charts ---
st.write("### Sector Leaders (Average Sector Times)")
leader_charts = plot_sector_leaderboard(laps, drivers, driver_colors)

cols = st.columns(3)
for i, fig in enumerate(leader_charts):
    with cols[i]:
        st.plotly_chart(fig, use_container_width=True)

# --- 3. Sector Leaders Tables ---
st.write("### Sector Leaders Tables")
sectors = ['duration_sector_1', 'duration_sector_2', 'duration_sector_3']
sector_names = ['Sector 1', 'Sector 2', 'Sector 3']

cols = st.columns(3)
for i, (sector, name) in enumerate(zip(sectors, sector_names)):
    df_sector = laps.groupby('driver_number').agg(
        avg_time=(sector, 'mean')
    ).reset_index()

    # Merge driver info
    df_sector = df_sector.merge(drivers[['driver_number', 'broadcast_name', 'team_name']],
                                on='driver_number', how='left')

    # Sort by fastest and compute Position and Delta
    df_sector = df_sector.sort_values('avg_time').reset_index(drop=True)
    df_sector['Position'] = df_sector.index + 1
    leader_time = df_sector['avg_time'].iloc[0]
    df_sector['Avg Time (s)'] = df_sector['avg_time'].apply(lambda x: f"{x:.3f}")
    df_sector['Delta'] = df_sector['avg_time'] - leader_time
    df_sector['Avg Time (s)'] = df_sector.apply(
        lambda row: f"{row['Avg Time (s)']} (+{row['Delta']:.3f})" if row['Delta'] > 0 else row['Avg Time (s)'],
        axis=1
    )

    # Select columns to show
    df_sector = df_sector[['Position', 'broadcast_name', 'driver_number', 'Avg Time (s)']]
    df_sector = df_sector.rename(columns={
        'broadcast_name': 'Driver',
        'driver_number': 'Number'
    })

    # Build HTML table with row colors
    table_html = "<table>"
    table_html += "<tr>" + "".join([f"<th>{col}</th>" for col in df_sector.columns]) + "</tr>"

    for _, row in df_sector.iterrows():
        driver_num = drivers.loc[drivers['broadcast_name'] == row['Driver'], 'driver_number'].iloc[0]
        color = driver_colors.get(driver_num, '#FFFFFF')
        table_html += f"<tr style='background-color:{color};'>"
        table_html += "".join([f"<td>{row[col]}</td>" for col in df_sector.columns])
        table_html += "</tr>"

    table_html += "</table>"

    with cols[i]:
        st.markdown(f"**{name}**")
        st.markdown(table_html, unsafe_allow_html=True)




CACHE_DIR = "data_cache"

def get_last_update_time():
    if not os.path.exists(CACHE_DIR):
        return "Never"
    files = [os.path.join(CACHE_DIR, f) for f in os.listdir(CACHE_DIR)]
    if not files:
        return "Never"
    last_time = max(os.path.getmtime(f) for f in files)
    return st.write(f"Last cache update: {time.ctime(last_time)}")

get_last_update_time()