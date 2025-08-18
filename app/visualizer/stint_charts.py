import plotly.graph_objects as go
import pandas as pd

def plot_tire_strategy(stints: pd.DataFrame, driver_colors: dict, drivers: pd.DataFrame):
    stints = stints.copy()
    drivers_map = drivers.set_index("driver_number")["broadcast_name"].to_dict()
    stints["driver_name"] = stints["driver_number"].map(drivers_map)
    stints["stint_length"] = stints["lap_end"] - stints["lap_start"] + 1

    compound_colors = {
        "SOFT": "#FF4C4C",
        "MEDIUM": "#FFC34C",
        "HARD": "#D9D9D9",
        "INTERMEDIATE": "#4CFF4C",
        "WET": "#4C4CFF",
    }

    fig = go.Figure()
    for _, stint in stints.iterrows():
        fig.add_trace(go.Bar(
            x=[stint['stint_length']],
            y=[stint['driver_name']],
            base=stint['lap_start'],
            width=0.4,
            orientation='h',
            marker_color=compound_colors.get(stint['compound'], 'grey'),
            marker_line_color=driver_colors.get(stint['driver_number'], 'black'),
            marker_line_width=0.2,
            text=stint['stint_number'],
            textposition='inside',
            hovertemplate=(
                f"Driver: {stint['driver_name']}<br>"
                f"Tire: {stint['compound']}<br>"
                f"Stint: {stint['stint_number']}<br>"
                f"Laps: {stint['lap_start']} - {stint['lap_end']}<extra></extra>"
            )
        ))
    fig.update_layout(title="Tire Strategy", xaxis_title="Lap Number", yaxis_title="Driver", yaxis=dict(autorange='reversed'), barmode='stack', height=800, showlegend=False)
    return fig
