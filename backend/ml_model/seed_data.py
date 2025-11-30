import csv
import os
import random
from datetime import datetime, timedelta

# UPDATE THIS PATH TO MATCH YOUR PROJECT
CSV_PATH = "data/weather_data.csv"
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)  # create 'data/' if missing


def seed_past_weather():
    # Create dummy data for the last 14 days
    data = []
    base_date = datetime.now().date() - timedelta(days=14)
    
    print("Seeding data...")
    
    for i in range(14):
        curr_date = base_date + timedelta(days=i)
        # Randomize slightly around 18-25 degrees
        temp = round(random.uniform(18.0, 25.0), 1)
        cloud = round(random.uniform(20.0, 80.0), 1)
        rain = round(random.uniform(0.0, 5.0), 1)
        
        data.append([curr_date, temp, cloud, rain])

    # Overwrite CSV with header and seed data
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "temperature", "cloudcover", "precipitation"])
        writer.writerows(data)
    
    print(f"Successfully added {len(data)} rows of historical weather data.")

if __name__ == "__main__":
    seed_past_weather()