import os
import json
import time
import shutil
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# -----------------------------
# CONFIGURATION
# -----------------------------
CACHE_DIR = "data_cache"
BASE_API_URL = "https://api.openf1.org/v1/"

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

# Create a retry-enabled session
session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
session.mount("https://", HTTPAdapter(max_retries=retries))


# -----------------------------
# CORE FETCH FUNCTION WITH CACHE
# -----------------------------
def fetch_data_with_cache(endpoint: str, params: dict, cache_filename: str):
    """
    Fetch data from OpenF1 API with caching to reduce redundant API calls.
    """
    filepath = os.path.join(CACHE_DIR, cache_filename)

    # Load from cache if available
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)

    # Otherwise, fetch from API
    url = BASE_API_URL + endpoint
    response = session.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Save response to cache
    with open(filepath, "w") as f:
        json.dump(data, f)

    # Small delay to avoid rate limits
    time.sleep(0.2)

    return data


# -----------------------------
# INDIVIDUAL FETCH FUNCTIONS
# -----------------------------
def fetch_meetings(year: int):
    return fetch_data_with_cache("meetings", {"year": year}, f"meetings_{year}.json")


def fetch_sessions(meeting_key: int):
    return fetch_data_with_cache("sessions", {"meeting_key": meeting_key}, f"sessions_{meeting_key}.json")


def fetch_drivers(session_key: int):
    return fetch_data_with_cache("drivers", {"session_key": session_key}, f"drivers_{session_key}.json")


def fetch_laps(session_key: int, driver_number: int | None = None):
    params = {"session_key": session_key}
    if driver_number:
        params["driver_number"] = driver_number
    cache_name = f"laps_{session_key}" + (f"_{driver_number}" if driver_number else "") + ".json"
    return fetch_data_with_cache("laps", params, cache_name)


def fetch_pit(session_key: int):
    return fetch_data_with_cache("pit", {"session_key": session_key}, f"pit_{session_key}.json")


def fetch_stints(session_key: int):
    return fetch_data_with_cache("stints", {"session_key": session_key}, f"stints_{session_key}.json")


def fetch_weather(session_key: int):
    return fetch_data_with_cache("weather", {"session_key": session_key}, f"weather_{session_key}.json")


# -----------------------------
# CACHE MANAGEMENT
# -----------------------------
def clear_cache_files():
    """
    Delete all cached JSON files in the cache directory.
    """
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
        print("✅ Cache cleared successfully.")
    else:
        print("ℹ️ No cache directory found.")


# -----------------------------
# BULK UPDATE FUNCTION
# -----------------------------
def update_all_data(year: int = 2025):
    """
    Fetch and cache all meeting/session data for a given year.
    """
    print(f"\n🔄 Updating OpenF1 data for {year}...\n")

    meetings = fetch_meetings(year)
    print(f"📅 Found {len(meetings)} meetings for {year}.\n")

    for meeting in meetings:
        meeting_key = meeting["meeting_key"]
        meeting_name = meeting.get("meeting_name", "Unknown Meeting")
        print(f"🏁 Meeting: {meeting_name} ({meeting_key})")

        sessions = fetch_sessions(meeting_key)
        for session in sessions:
            session_key = session["session_key"]
            session_name = session.get("session_name", "Unnamed Session")

            print(f"  ⏱  Fetching session: {session_name}")

            # Fetch all relevant session data
            fetch_drivers(session_key)
            fetch_laps(session_key)
            fetch_pit(session_key)
            fetch_stints(session_key)
            fetch_weather(session_key)

            print(f"  ✅ Completed: {session_name}")

        print(f"✅ Finished meeting: {meeting_name}\n")

    print("🎉 All data updated and cached successfully.")


# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    update_all_data(2025)
