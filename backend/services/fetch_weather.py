import requests
import csv
import os
from datetime import datetime
from django.conf import settings
from farmer_app.models import WeatherData

CSV_PATH = os.path.join(settings.BASE_DIR, "ml_model", "data", "weather_data.csv")


def fetch_and_save_weather():
    print("=== FETCH FUNCTION RUNNING ===")

    # API URL
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        "latitude=12.97&longitude=77.59&"
        "hourly=temperature_2m,cloudcover,precipitation&timezone=auto"
    )

    data = requests.get(url).json()
    hourly = data["hourly"]

    # Pick closest hourly value to real time
    now = datetime.now()
    hourly_times = [datetime.fromisoformat(t) for t in hourly["time"]]
    closest_index = min(range(len(hourly_times)), key=lambda i: abs(hourly_times[i] - now))

    today_date = hourly_times[closest_index].date()
    temp = hourly["temperature_2m"][closest_index]
    cloud = hourly["cloudcover"][closest_index]
    rain = hourly["precipitation"][closest_index]

    # Create CSV if not exists
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "temperature", "cloudcover", "precipitation"])

    # Remove duplicate for same day
    remove_csv_duplicate(today_date)

    # Save to CSV (append)
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([today_date, temp, cloud, rain])

    # Save into DB
    WeatherData.objects.update_or_create(
        date=today_date,
        defaults={
            "temperature": temp,
            "cloudcover": cloud,
            "precipitation": rain,
        },
    )

    print(f"Weather Saved: {today_date}  {temp}°C  {cloud}%  {rain}mm")


def remove_csv_duplicate(today_date):
    """Keep full history but remove duplicates of same date."""
    rows = []
    if not os.path.exists(CSV_PATH):
        return

    with open(CSV_PATH, "r") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            row_date = datetime.fromisoformat(row[0]).date()
            if row_date != today_date:
                rows.append(row)

    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "temperature", "cloudcover", "precipitation"])
        writer.writerows(rows)