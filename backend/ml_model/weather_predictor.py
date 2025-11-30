import pandas as pd
from datetime import timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from django.db import connection, transaction
import random
import os
from farmer_app.models import WeatherPrediction, WeatherData
from .join_datasets import load_and_join

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def predict_next_7_days(user_state=None, user_district=None):

    monthly_rain_avg, monthly_temp_avg = load_and_join(user_state, user_district)

    # ---------- Get today's live data ----------
    try:
        today_row = WeatherData.objects.latest("date")
        today_date = today_row.date
        today_temp = today_row.temperature
        today_cloud = today_row.cloudcover
        today_rain = today_row.precipitation
    except WeatherData.DoesNotExist:
        today_date = pd.Timestamp.today()
        today_temp = monthly_temp_avg.get(today_date.month, 25.0)
        today_cloud = 50.0
        today_rain = monthly_rain_avg.get(today_date.month, 10.0)

    # ---------- Load FULL CSV (NOT last 7 days) ----------
    try:
        df_weather = pd.read_csv(os.path.join(BASE_DIR, "ml_model", "data", "weather_data.csv"))
        df_weather["date"] = pd.to_datetime(df_weather["date"])
        df_weather = df_weather.sort_values("date")  # ALL rows
    except FileNotFoundError:
        df_weather = pd.DataFrame()

    # ---------- Train using ALL CSV rows ----------
    if not df_weather.empty and len(df_weather) >= 3:
        df_weather["day_index"] = (df_weather["date"] - df_weather["date"].min()).dt.days

        X = df_weather[["day_index"]]
        Y_temp = df_weather["temperature"]
        Y_rain = df_weather["precipitation"]

        model_temp = LinearRegression().fit(X, Y_temp)
        model_rain = LinearRegression().fit(X, Y_rain)

        last_day_index = df_weather["day_index"].max()

    else:
        # fallback if CSV empty
        model_temp = None
        model_rain = None
        last_day_index = 0

    # ---------- Clear old predictions ----------
    WeatherPrediction.objects.all().delete()

    forecasts = []

    # ---------- Predict next 7 days ----------
    for i in range(1, 8):

        future_date = today_date + timedelta(days=i)
        future_day_index = last_day_index + i

        # Temperature
        if model_temp:
            t_pred = float(model_temp.predict(
                pd.DataFrame({"day_index": [future_day_index]})
            )[0])
        else:
            t_pred = monthly_temp_avg.get(future_date.month, today_temp)

        # Rainfall
        if model_rain:
            r_pred = float(model_rain.predict(
                pd.DataFrame({"day_index": [future_day_index]})
            )[0])
        else:
            r_pred = monthly_rain_avg.get(future_date.month, today_rain)

        # Cloudcover (random variation)
        c_pred = min(max(today_cloud * random.uniform(0.8, 1.2), 0), 100)

        WeatherPrediction.objects.update_or_create(
            date=future_date,
            defaults={
                "temperature": round(t_pred, 1),
                "cloudcover": round(c_pred, 1),
                "precipitation": round(r_pred, 1)
            }
        )

        forecasts.append({
            "date": future_date.strftime("%Y-%m-%d"),
            "temperature": round(t_pred, 1),
            "cloudcover": round(c_pred, 1),
            "precipitation": round(r_pred, 1),
        })

    # ---------- Optional training metrics ----------
    metrics = {}
    if not df_weather.empty and len(df_weather) >= 10:
        X_train, X_test, y_train, y_test = train_test_split(X, Y_temp, test_size=0.2)
        temp_model_eval = LinearRegression().fit(X_train, y_train)
        metrics["Temperature R2"] = r2_score(y_test, temp_model_eval.predict(X_test))
        metrics["Temperature MSE"] = mean_squared_error(y_test, temp_model_eval.predict(X_test))

        X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X, Y_rain, test_size=0.2)
        rain_model_eval = LinearRegression().fit(X_train_r, y_train_r)
        metrics["Rainfall R2"] = r2_score(y_test_r, rain_model_eval.predict(X_test_r))
        metrics["Rainfall MSE"] = mean_squared_error(y_test_r, rain_model_eval.predict(X_test_r))

    return forecasts, metrics

