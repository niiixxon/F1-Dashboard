import plotly.graph_objects as go
import pandas as pd

def plot_race_positions(laps, drivers, driver_colors):
    """
    Step chart of race positions per lap for each driver
    """
    fig = go.Figure()
    for driver_number in laps['driver_number'].unique():
        driver_laps = laps[laps['driver_number'] == driver_number].sort_values('lap_number')
        driver_name = drivers.loc[drivers['driver_number'] == driver_number, 'broadcast_name'].iloc[0]
        fig.add_trace(go.Scatter(
            x=driver_laps['lap_number'],
            y=driver_laps['position'],
            mode='lines+markers',
            name=f"{driver_name} ({driver_number})",
            line=dict(color=driver_colors.get(driver_number, '#000000'), shape='hv'),
            hoverinfo='text',
            text=[f"{driver_name} Lap {lap}" for lap in driver_laps['lap_number']]
        ))
    fig.update_yaxes(title="Position", autorange='reversed')  # lower numbers = better positions
    fig.update_xaxes(title="Lap Number")
    fig.update_layout(title="Race Positions per Lap", height=600, hovermode="x unified")
    return fig


def plot_position_changes(laps, drivers, driver_colors):
    """
    Heatmap of positions gained/lost per lap
    """
    # Compute positions gained/lost lap by lap
    laps_sorted = laps.sort_values(['driver_number', 'lap_number']).copy()
    laps_sorted['position_change'] = laps_sorted.groupby('driver_number')['position'].diff().fillna(0)
    
    # Create pivot table for heatmap
    heatmap_df = laps_sorted.pivot(index='driver_number', columns='lap_number', values='position_change')
    
    # Map driver colors
    row_colors = [driver_colors.get(d, '#FFFFFF') for d in heatmap_df.index]
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns,
        y=[drivers.loc[drivers['driver_number'] == d, 'broadcast_name'].iloc[0] for d in heatmap_df.index],
        colorscale='RdYlGn',  # red = lost positions, green = gained
        colorbar=dict(title='Positions Gained/Lost')
    ))
    fig.update_layout(title="Position Changes per Lap", xaxis_title="Lap", yaxis_title="Driver")
    return fig
