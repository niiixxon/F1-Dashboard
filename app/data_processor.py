import pandas as pd

def clean_laps(laps):
    """
    Clean raw laps data by filtering invalid laps and converting lap duration to numeric.
    
    Parameters:
        laps (list/dict): Raw laps data from API
    
    Returns:
        pd.DataFrame: Cleaned laps dataframe
    """
    df = pd.DataFrame(laps)
    # Remove rows with missing lap_duration
    df = df[df['lap_duration'].notna()]
    # Convert lap_duration to numeric, coerce errors to NaN then drop them
    df['lap_duration'] = pd.to_numeric(df['lap_duration'], errors='coerce')
    df = df.dropna(subset=['lap_duration'])
    return df


def clean_drivers(drivers):
    """
    Clean raw driver data, ensure team colors are formatted as hex strings.
    
    Parameters:
        drivers (list/dict): Raw drivers data from API
    
    Returns:
        pd.DataFrame: Cleaned drivers dataframe with team_colour formatted for plotting
    """
    df = pd.DataFrame(drivers)
    # Defensive: handle missing 'team_colour' column or values
    df['team_colour'] = df.get('team_colour', '').astype(str).apply(
        lambda x: f"#{x}" if x and not x.startswith("#") else x)
    return df


def build_driver_color_map(drivers):
    """
    Create a mapping of driver_number to hex color string for visualization.
    
    Parameters:
        drivers (list/dict): Raw drivers data from API
    
    Returns:
        dict: {driver_number: hex_color_string}
    """
    color_map = {}
    for d in drivers:
        color = d.get('team_colour', '#000000')  # fallback black if missing
        if not color.startswith("#"):
            color = "#" + color
        color_map[d.get('driver_number')] = color
    return color_map


def calculate_stint_lap_ranges(stints):
    """
    For each stint, create a list of lap numbers covered (lap_range).

    Skips stints where lap_start or lap_end is missing.
    """
    df = pd.DataFrame(stints)

    # Drop rows with missing lap_start or lap_end
    df = df.dropna(subset=['lap_start', 'lap_end'])

    # Ensure lap_start and lap_end are integers
    df['lap_start'] = df['lap_start'].astype(int)
    df['lap_end'] = df['lap_end'].astype(int)

    # Create lap_range list
    df['lap_range'] = df.apply(lambda row: list(range(row['lap_start'], row['lap_end'] + 1)), axis=1)

    return df



def clean_weather(raw_weather):
    """
    Convert raw weather data to DataFrame.
    
    Parameters:
        raw_weather (list/dict): Raw weather data
    
    Returns:
        pd.DataFrame: Weather data as DataFrame
    """
    return pd.DataFrame(raw_weather)


def prepare_tyre_degradation_data(laps_raw, stints_raw):
    """
    Combine laps and stints data to compute tyre age for each lap in a stint.
    
    Parameters:
        laps_raw (list/dict): Raw laps data
        stints_raw (list/dict): Raw stints data
    
    Returns:
        pd.DataFrame: Combined DataFrame with 'tyre_age' per lap per driver
    """
    laps = pd.DataFrame(laps_raw)
    stints = pd.DataFrame(stints_raw)

    merged = []
    for _, stint in stints.iterrows():
        driver = stint['driver_number']
        lap_start = int(stint['lap_start'])
        lap_end = int(stint['lap_end'])
        tyre_age_start = int(stint.get('tyre_age_at_start', 0))

        stint_laps = laps[
            (laps['driver_number'] == driver) &
            (laps['lap_number'] >= lap_start) &
            (laps['lap_number'] <= lap_end)
        ].copy()

        stint_laps['tyre_age'] = tyre_age_start + (stint_laps['lap_number'] - lap_start)
        merged.append(stint_laps)

    if merged:
        return pd.concat(merged, ignore_index=True)
    else:
        return pd.DataFrame()
