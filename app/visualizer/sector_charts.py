# app/visualizer/sector_charts.py
import plotly.graph_objects as go
import pandas as pd

def plot_sector_times(laps, driver_colors):
    """
    Standard sector times per driver over laps.
    """
    fig = go.Figure()
    sectors = ['duration_sector_1', 'duration_sector_2', 'duration_sector_3']
    sector_names = ['Sector 1', 'Sector 2', 'Sector 3']

    for d in laps['driver_number'].unique():
        df_driver = laps[laps['driver_number'] == d]
        for sector, name in zip(sectors, sector_names):
            fig.add_trace(go.Scatter(
                x=df_driver['lap_number'],
                y=df_driver[sector],
                mode='lines',
                name=f'Driver {d} - {name}',
                line=dict(color=driver_colors.get(d, '#999999')),
                hovertemplate=f'Lap %{{x}}<br>{name} Time: %{{y:.2f}}s<extra></extra>'
            ))

    fig.update_layout(
        title="Sector Times Over Laps",
        xaxis_title="Lap Number",
        yaxis_title="Sector Time (s)"
    )
    return fig

def plot_sector_leaderboard(laps, drivers, driver_colors):
    """
    Horizontal bar charts for average sector times (S1, S2, S3)
    """
    figures = []
    sectors = ['duration_sector_1', 'duration_sector_2', 'duration_sector_3']
    sector_names = ['Sector 1', 'Sector 2', 'Sector 3']

    for sector, name in zip(sectors, sector_names):
        df_sector = laps.groupby('driver_number').agg(avg_time=(sector, 'mean')).reset_index()
        df_sector = df_sector.merge(drivers[['driver_number','broadcast_name','team_name']], on='driver_number', how='left')
        df_sector = df_sector.sort_values('avg_time')
        leader_time = df_sector['avg_time'].min()
        df_sector['Delta'] = df_sector['avg_time'] - leader_time

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_sector['avg_time'],
            y=df_sector['broadcast_name'],
            orientation='h',
            marker=dict(color=[driver_colors.get(d,'#999999') for d in df_sector['driver_number']]),
            text=[f"+{d:.3f}s" if d>0 else "Leader" for d in df_sector['Delta']],
            hovertemplate="<b>%{y}</b><br>Avg Time: %{x:.3f}s<br>Delta: %{text}<extra></extra>"
        ))

        fig.update_layout(
            title=f"{name} Leaderboard (Avg Times)",
            xaxis_title="Average Sector Time (s)",
            yaxis=dict(autorange='reversed'),
            margin=dict(l=120,r=40,t=60,b=40)
        )
        figures.append(fig)

    return figures

def plot_speed_trap(laps, driver_colors):
    """
    Plot speed trap data per driver if available.
    """
    fig = go.Figure()
    speed_traps = [c for c in laps.columns if 'speed_trap' in c]
    if not speed_traps:
        return fig

    for d in laps['driver_number'].unique():
        df_driver = laps[laps['driver_number']==d]
        for st in speed_traps:
            fig.add_trace(go.Scatter(
                x=df_driver['lap_number'],
                y=df_driver[st],
                mode='lines+markers',
                name=f'Driver {d} - {st}',
                line=dict(color=driver_colors.get(d,'#999999')),
                hovertemplate=f'Lap %{{x}}<br>{st}: %{{y:.2f}} km/h<extra></extra>'
            ))

    fig.update_layout(
        title="Speed Trap Data Over Laps",
        xaxis_title="Lap Number",
        yaxis_title="Speed (km/h)"
    )
    return fig
