# update_data.py
import os
from app.data_loader import (
    fetch_meetings, fetch_sessions, fetch_drivers, fetch_laps,
    fetch_stints, fetch_weather
)

def update_latest_race(years=[2025, 2024, 2023]):
    """Fetch only the latest race for each year"""
    for year in years:
        meetings = fetch_meetings(year)
        if not meetings:
            continue
        # Assume meetings are sorted by date; get the last one
        latest_meeting = meetings[-1]
        meeting_key = latest_meeting["meeting_key"]

        sessions = fetch_sessions(meeting_key)
        if not sessions:
            continue

        for session in sessions:
            session_key = session["session_key"]
            fetch_drivers(session_key)
            fetch_laps(session_key)
            fetch_stints(session_key)
            fetch_weather(session_key)

        print(f"Updated latest race for {year}: {latest_meeting['meeting_name']}")


def update_all_races(years=[2025, 2024, 2023]):
    """Fetch all races for each year (can take a long time)"""
    for year in years:
        meetings = fetch_meetings(year)
        if not meetings:
            continue
        for meeting in meetings:
            meeting_key = meeting["meeting_key"]
            sessions = fetch_sessions(meeting_key)
            if not sessions:
                continue
            for session in sessions:
                session_key = session["session_key"]
                fetch_drivers(session_key)
                fetch_laps(session_key)
                fetch_stints(session_key)
                fetch_weather(session_key)
            print(f"Updated race: {meeting['meeting_name']}")
