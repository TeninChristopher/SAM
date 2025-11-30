from services.fetch_weather import fetch_and_save_weather
from ml_model.join_datasets import load_and_join
from ml_model.weather_predictor import predict_next_7_days


def run_full_pipeline():
    print("\n=== STEP 1: FETCH & SAVE WEATHER ===")
    fetch_and_save_weather()

    print("\n=== STEP 2: JOIN DATASETS ===")
    df = load_and_join()
    print("Joined rows:", len(df))

    print("\n=== STEP 3: MAKE PREDICTIONS ===")
    predictions = predict_next_7_days()
    print("Predictions saved:", predictions)

    print("\n✔ Pipeline completed.\n")
