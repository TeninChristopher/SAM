import pandas as pd
import os
from django.conf import settings
import difflib

DATA_PATH = os.path.join(settings.BASE_DIR, "ml_model", "data")


def find_best_match(target, options):
    if not target:
        return None
    target_upper = target.upper()
    options_upper = [o.upper() for o in options]
    if target_upper in options_upper:
        return options[options_upper.index(target_upper)]
    matches = difflib.get_close_matches(target_upper, options_upper, n=1, cutoff=0.6)
    if matches:
        return options[options_upper.index(matches[0])]
    return None


def load_and_join(user_state=None, user_district=None):
    """
    Load rainfall and seasonal temperature data individually.
    Returns dicts:
        - monthly_rain_avg: {month: state/district average rainfall}
        - monthly_temp_avg: {month: seasonal average temperature}
    Defaults to Karnataka / Bengaluru Urban if no user value provided.
    """
    # ---------------- Default location ----------------
    state = user_state or "Karnataka"
    district = user_district or "Bengaluru Urban"

    # ---------------- Load rainfall data ----------------
    try:
        df_rain = pd.read_csv(os.path.join(DATA_PATH, "rainfall_in_india.csv"))
    except FileNotFoundError:
        print("Rainfall CSV not found")
        df_rain = pd.DataFrame()

    df_rain["Date"] = pd.to_datetime(df_rain["Date"], errors="coerce")
    df_rain["month"] = df_rain["Date"].dt.month.astype(int)
    df_rain["Avg_rainfall"] = pd.to_numeric(df_rain["Avg_rainfall"], errors="coerce")

    # Match district/state
    csv_states = df_rain["State"].dropna().unique().tolist()
    csv_districts = df_rain["District"].dropna().unique().tolist()
    matched_state = find_best_match(state, csv_states)
    matched_district = find_best_match(district, csv_districts)

    # Filter rainfall data
    df_filtered_rain = pd.DataFrame()
    if matched_district:
        df_filtered_rain = df_rain[df_rain["District"].str.upper().str.strip() == matched_district.upper().strip()]
    if df_filtered_rain.empty and matched_state:
        df_filtered_rain = df_rain[df_rain["State"].str.upper().str.strip() == matched_state.upper().strip()]
    if df_filtered_rain.empty:
        df_filtered_rain = df_rain

    monthly_rain_avg = df_filtered_rain.groupby("month")["Avg_rainfall"].mean().to_dict()

    # ---------------- Load seasonal temperature data ----------------
    try:
        df_temp = pd.read_csv(os.path.join(DATA_PATH, "TEMP_ANNUAL_SEASONAL_MEAN.csv"))
    except FileNotFoundError:
        print("Temperature CSV not found")
        df_temp = pd.DataFrame()

    df_temp_melt = df_temp.melt(
        id_vars=["YEAR"],
        value_vars=["JAN-FEB", "MAR-MAY", "JUN-SEP", "OCT-DEC"],
        var_name="season",
        value_name="season_temp"
    )
    df_temp_melt["season_temp"] = pd.to_numeric(df_temp_melt["season_temp"], errors="coerce")
    df_temp_melt = df_temp_melt.dropna(subset=["season_temp"])

    season_map = {"JAN-FEB": [1, 2],
                  "MAR-MAY": [3, 4, 5],
                  "JUN-SEP": [6, 7, 8, 9],
                  "OCT-DEC": [10, 11, 12]}

    temp_rows = []
    for _, r in df_temp_melt.iterrows():
        for m in season_map[r["season"]]:
            temp_rows.append({"month": m, "monthly_temp": r["season_temp"]})

    df_historical_temp = pd.DataFrame(temp_rows)
    monthly_temp_avg = df_historical_temp.groupby("month")["monthly_temp"].mean().to_dict()

    return monthly_rain_avg, monthly_temp_avg