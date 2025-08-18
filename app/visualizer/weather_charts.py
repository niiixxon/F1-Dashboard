import plotly.graph_objects as go
import pandas as pd

def plot_weather(weather_df: pd.DataFrame):
    fig = go.Figure()
    if weather_df.empty:
        return fig

    weather_df['date'] = pd.to_datetime(weather_df['date'])
    fig.add_trace(go.Scatter(x=weather_df['date'], y=weather_df['air_temperature'], mode='lines', name='Air Temp (°C)'))
    fig.add_trace(go.Scatter(x=weather_df['date'], y=weather_df['track_temperature'], mode='lines', name='Track Temp (°C)'))
    fig.add_trace(go.Scatter(x=weather_df['date'], y=weather_df['humidity'], mode='lines', name='Humidity (%)'))
    fig.add_trace(go.Scatter(x=weather_df['date'], y=weather_df['rainfall'], mode='lines', name='Rainfall (boolean)'))
    fig.update_layout(title="Weather Conditions During Session", xaxis_title="Time")
    return fig
