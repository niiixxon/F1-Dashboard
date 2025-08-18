import plotly.graph_objects as go
import math
import pandas as pd

def format_lap_time(seconds):
    mins = math.floor(seconds / 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{mins}:{secs:02d}.{ms:03d}"

def plot_lap_times(laps_df: pd.DataFrame, driver_colors: dict, drivers: pd.DataFrame):
    fig = go.Figure()
    for driver_number in laps_df['driver_number'].unique():
        driver_laps = laps_df[laps_df['driver_number'] == driver_number].copy()
        driver_laps['lap_duration_str'] = driver_laps['lap_duration'].apply(format_lap_time)
        driver_info = drivers[drivers['driver_number'] == driver_number].iloc[0]
        driver_label = f"{driver_info['broadcast_name']} {driver_info['driver_number']}"

        # Add both driver name and lap time to customdata
        driver_laps['hover_text'] = driver_laps['lap_duration_str'].apply(lambda x: f"{driver_info['broadcast_name']}: {x}")

        fig.add_trace(go.Scatter(
            x=driver_laps['lap_number'],
            y=driver_laps['lap_duration'],
            mode='lines+markers',
            name=driver_label,
            line=dict(color=driver_colors.get(driver_number)),
            customdata=driver_laps['hover_text'],
            hovertemplate="<b>%{customdata}</b><extra></extra>"
        ))
    fig.update_yaxes(title="Lap Duration")
    fig.update_xaxes(title="Lap Number")
    fig.update_layout(title="Lap Times per Driver", hovermode="x unified", legend_title="Drivers", height=1000)
    return fig
