import schedule
import time
from update_data import update_latest_race, update_all_races

# Update latest race every 30 minutes
schedule.every(30).minutes.do(update_latest_race)

# Update all races once daily (or weekly)
schedule.every().day.at("03:00").do(update_all_races)

print("Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(5)
