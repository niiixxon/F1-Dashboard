import pandas as pd
import plotly.graph_objects as go

def plot_tyre_degradation(laps_df, stints_df, driver_colors, weather_df=None, selected_drivers=None, rolling_window=3):
    """
    Tyre Degradation Chart with:
    - Multi-driver support
    - Rolling mean with ribbons for variation
    - Fuel-corrected lap times
    - Track temperature in hover
    """

    # Merge stints info for compound & stint number
    laps = laps_df.copy()
    stints = stints_df.copy()
    compound_map = []
    for _, stint in stints.iterrows():
        compound_map.extend([
            {"lap_number": lap,
             "driver_number": stint['driver_number'],
             "compound": stint['compound'],
             "stint_number": stint['stint_number']}
            for lap in range(stint['lap_start'], stint['lap_end'] + 1)
        ])
    compound_df = pd.DataFrame(compound_map)
    laps = laps.merge(compound_df, on=['lap_number', 'driver_number'], how='left')

    # Fuel correction
    laps['fuel_effect'] = laps.groupby('driver_number')['lap_number'].transform(lambda x: max(x) - x)
    laps['lap_duration_corrected'] = laps['lap_duration'] - 0.1 * laps['fuel_effect']

    # Filter drivers
    if selected_drivers:
        laps = laps[laps['driver_number'].isin(selected_drivers)]

    # Merge weather
    if weather_df is not None and not weather_df.empty:
        weather_df['date'] = pd.to_datetime(weather_df['date'])
        laps['date_start'] = pd.to_datetime(laps['date_start'])
        laps = pd.merge_asof(
            laps.sort_values('date_start'),
            weather_df.sort_values('date'),
            left_on='date_start',
            right_on='date',
            direction='backward'
        )
    else:
        laps['track_temperature'] = None

    # Compute rolling mean & std
    laps['lap_number_int'] = laps['lap_number'].astype(int)
    rolling_df = (
        laps.groupby(['driver_number', 'compound'])
        .apply(lambda x: x.sort_values('lap_number_int')
               .assign(
                   lap_roll_mean=x['lap_duration_corrected'].rolling(rolling_window, min_periods=1).mean(),
                   lap_roll_std=x['lap_duration_corrected'].rolling(rolling_window, min_periods=1).std()
               ))
        .reset_index(drop=True)
    )

    # Plot
    fig = go.Figure()
    for driver in rolling_df['driver_number'].unique():
        driver_data = rolling_df[rolling_df['driver_number'] == driver]
        driver_name = driver_data['driver_number'].iloc[0]

        for compound in driver_data['compound'].unique():
            comp_data = driver_data[driver_data['compound'] == compound]

            # Ribbon for std
            fig.add_traces(go.Scatter(
                x=comp_data['lap_number'],
                y=comp_data['lap_roll_mean'] + comp_data['lap_roll_std'],
                line=dict(width=0),
                hoverinfo='skip',
                showlegend=False
            ))
            fig.add_traces(go.Scatter(
                x=comp_data['lap_number'],
                y=comp_data['lap_roll_mean'] - comp_data['lap_roll_std'],
                fill='tonexty',
                fillcolor='rgba(0,0,0,0.1)',
                line=dict(width=0),
                hoverinfo='skip',
                showlegend=False
            ))

            # Rolling mean line
            fig.add_trace(go.Scatter(
                x=comp_data['lap_number'],
                y=comp_data['lap_roll_mean'],
                mode='lines+markers',
                name=f"{driver_name} ({compound})",
                marker=dict(color=driver_colors.get(driver_name, '#000000')),
                hovertemplate=(
                    "Driver: %{text}<br>"
                    "Lap: %{x}<br>"
                    "Lap Time Corrected: %{y:.2f}s<br>"
                    "Compound: " + compound + "<br>"
                    "Sector1: %{customdata[0]:.2f}s, "
                    "S2: %{customdata[1]:.2f}s, "
                    "S3: %{customdata[2]:.2f}s<br>"
                    "Track Temp: %{customdata[3]}°C"
                ),
                text=[driver_name]*len(comp_data),
                customdata=comp_data[['duration_sector_1','duration_sector_2','duration_sector_3','track_temperature']].values
            ))

    fig.update_layout(
        title="Tyre Degradation Trends by Compound",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (Corrected for Fuel)",
        height=700,
        template='plotly_white'
    )

    return fig
