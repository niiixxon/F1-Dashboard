import os
import json
import requests
import shutil

CACHE_DIR = "data_cache"
BASE_API_URL = "https://api.openf1.org/v1/"

def fetch_data_with_cache(endpoint, params, cache_filename):
    filepath = os.path.join(CACHE_DIR, cache_filename)

    # Create cache dir if not exists
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Load from cache if file exists
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        return data

    # Else fetch from API
    url = BASE_API_URL + endpoint
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Save to cache
    with open(filepath, "w") as f:
        json.dump(data, f)

    return data

def fetch_meetings(year):
    return fetch_data_with_cache("meetings", {"year": year}, f"meetings_{year}.json")

def fetch_sessions(meeting_key):
    return fetch_data_with_cache("sessions", {"meeting_key": meeting_key}, f"sessions_{meeting_key}.json")

def fetch_drivers(session_key):
    return fetch_data_with_cache("drivers", {"session_key": session_key}, f"drivers_{session_key}.json")

def fetch_laps(session_key, driver_number=None):
    params = {"session_key": session_key}
    if driver_number:
        params["driver_number"] = driver_number
    cache_name = f"laps_{session_key}"
    if driver_number:
        cache_name += f"_{driver_number}"
    cache_name += ".json"
    return fetch_data_with_cache("laps", params, cache_name)

def fetch_pit_stops(session_key):
    return fetch_data_with_cache("pit", {"session_key": session_key}, f"pit_{session_key}.json")

def fetch_stints(session_key):
    return fetch_data_with_cache("stints", {"session_key": session_key}, f"stints_{session_key}.json")

def fetch_pit(session_key):
    return fetch_data_with_cache("pit", {"session_key": session_key}, f"pit_{session_key}.json")

def fetch_weather(session_key):
    return fetch_data_with_cache("weather", {"session_key": session_key}, f"weather_{session_key}.json")



CACHE_DIR = "data_cache"

def clear_cache_files():
    """Delete all cached JSON files in the cache directory."""
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)  # Delete entire cache directory and contents
        print("Cache cleared.")
    else:
        print("No cache directory to clear.")

