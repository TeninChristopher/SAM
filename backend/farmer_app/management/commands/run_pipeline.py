# farmer_app/management/commands/run_pipeline.py

from django.core.management.base import BaseCommand
from services.fetch_weather import fetch_and_save_weather
from ml_model.join_datasets import load_and_join
from ml_model.weather_predictor import predict_next_7_days


class Command(BaseCommand):
    help = "Run full weather pipeline: fetch → join → predict"

    def handle(self, *args, **kwargs):
        self.stdout.write("\n=== STEP 1: FETCHING & SAVING WEATHER ===")
        fetch_and_save_weather()

        self.stdout.write("\n=== STEP 2: JOINING SOLID DATASETS ===")
        df = load_and_join()
        self.stdout.write(f"Joined dataset rows: {len(df)}")

        self.stdout.write("\n=== STEP 3: PREDICTING NEXT 7 DAYS ===")
        predictions = predict_next_7_days()
        self.stdout.write(f"Predictions saved: {predictions}")

        self.stdout.write("\nPipeline completed successfully.\n")
