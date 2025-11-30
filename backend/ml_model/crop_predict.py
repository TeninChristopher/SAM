'''import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "crop_data.csv")

def get_highest_stock_crop():
    print("🌾 Loading dataset...")
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Dataset not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    df = df.fillna(0)

    # Ensure necessary columns exist
    required_cols = {"Crop", "Production", "Yield"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Dataset must contain these columns: {required_cols}")

    # 🔍 Group by crop and sum up production and yield
    crop_summary = (
        df.groupby("Crop")[["Production", "Yield"]]
        .sum()
        .sort_values(by="Production", ascending=False)
    )

    # 🌟 Find highest production crop
    top_crop = crop_summary.head(1)
    crop_name = top_crop.index[0]
    production = top_crop["Production"].values[0]
    yield_value = top_crop["Yield"].values[0]
    #print(top_crop["Production"])

    print("📊 Top Crop by Production:")
    print(top_crop)

    result = {
        "Top_Crop": crop_name,
        "Total_Production": round(production, 2),
        "Total_Yield": round(yield_value, 2),
    }

    print(f"🌟 Highest Stock Crop: {crop_name}")
    print(f"🏭 Total Production: {production}")
    print(f"🌱 Total Yield: {yield_value}")

    return result

if __name__ == "__main__":
    highest_crop = get_highest_stock_crop()
    print("\n✅ Final Output:")
    print(highest_crop)
'''


'''
import pandas as pd
import numpy as np
import os
import pickle

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "data", "crop_model.pkl")

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"❌ Model not found at {MODEL_PATH}. Train it first.")
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    return model

def predict_best_crop(input_data: dict):
    """
    input_data example:
    {
        "Crop_Year": 2025,
        "Season": "Kharif",
        "State": "Maharashtra",
        "Area": 1200,
        "Production": 3500,
        "Annual_Rainfall": 820,
        "Fertilizer": 120,
        "Pesticide": 15,
        "Yield": 2.5
    }
    """

    print("🌱 Loading trained model...")
    model = load_model()

    # Create DataFrame for input
    input_df = pd.DataFrame([input_data])

    # Load dummy dataset to rebuild feature columns (to match training model)
    data_path = os.path.join(BASE_DIR, "data", "crop_data.csv")
    df_train = pd.read_csv(data_path)
    df_train = df_train.dropna(subset=["Crop", "Yield"])
    df_train = pd.get_dummies(df_train, columns=["Season", "State"], drop_first=True)

    # Prepare same dummy columns for input
    df_input = pd.get_dummies(input_df, columns=["Season", "State"], drop_first=True)

    # Align columns with training data (missing columns filled with 0)
    df_input = df_input.reindex(columns=df_train.drop("Crop", axis=1).columns, fill_value=0)

    # 🔮 Predict crop
    prediction = model.predict(df_input)[0]
    print(f"🌾 Predicted best-selling crop: {prediction}")

    return prediction

if __name__ == "__main__":
    # Example input for prediction
    sample_input = {
        "Crop_Year": 2025,
        "Season": "Kharif",
        "State": "Maharashtra",
        "Area": 1500,
        "Production": 4200,
        "Annual_Rainfall": 870,
        "Fertilizer": 110,
        "Pesticide": 20,
        "Yield": 2.8
    }

    best_crop = predict_best_crop(sample_input)
    print(f"🌟 Recommended Crop to Grow: {best_crop}")
'''
'''
import pandas as pd
import joblib
import os
import numpy as np

# Define file paths
DATA_PATH = os.path.join("data", "crop_data.csv")
MODEL_PATH = os.path.join("data", "crop_yield_model_V3.pkl")

print("Script started...")

# 1. Load the trained model pipeline
# 1. Load the trained model pipeline
try:
    pipeline = joblib.load(MODEL_PATH)
    print("Model loaded successfully.")
    
    # <<< ADD THIS LINE >>>
    # This proves the pipeline object has been successfully loaded
    print(f"DEBUG: Pipeline object loaded from: {MODEL_PATH}") 
    # <<< END ADDITION >>>
except FileNotFoundError:
    print(f"Error: Model file not found at {MODEL_PATH}")
    print("Please run crop_train.py first to create the model.")
    exit()

# 2. Load the original data to get unique crops and feature averages
try:
    df = pd.read_csv(DATA_PATH)
    df.dropna(inplace=True)
    print("Data loaded for analysis.")
except FileNotFoundError:
    print(f"Error: Data file not found at {DATA_PATH}")
    exit()

# 3. Get all unique crops
unique_crops = df['Crop'].unique()
crop_yield_predictions = []

print("Generating predictions for typical crop profiles...")

# 4. Loop through each crop to create a typical profile and predict its yield
for crop in unique_crops:
    # Filter data for the specific crop
    crop_data = df[df['Crop'] == crop]
    
    if crop_data.empty:
        continue

    # Create a "typical" profile for this crop
    # For numerical features: use the mean
    # For categorical features: use the mode (most common value)
    typical_profile = {
        'Crop': crop,
        'Season': crop_data['Season'].mode()[0],
        'State': crop_data['State'].mode()[0],
        'Area': crop_data['Area'].mean(),
        'Annual_Rainfall': crop_data['Annual_Rainfall'].mean(),
        'Fertilizer': crop_data['Fertilizer'].mean(),
        'Pesticide': crop_data['Pesticide'].mean()
    }
    
    # Convert this profile into a DataFrame for the pipeline
    input_data = pd.DataFrame([typical_profile])
    
    # Use the pipeline to predict yield
    # The pipeline handles all preprocessing (scaling, one-hot encoding)
    predicted_yield = pipeline.predict(input_data)[0]
    
    crop_yield_predictions.append((crop, predicted_yield))

# 5. Sort the results
# The user prompt "from ascending to descending" is ambiguous.
# This code sorts in DESCENDING order (highest yield first), as this is typically more useful.
# To sort in ASCENDING order (lowest first), change `reverse=True` to `reverse=False`.
sorted_crops = sorted(crop_yield_predictions, key=lambda x: x[1], reverse=True)

# 6. Display the results
print("\n--- Predicted Crop Yields (Ranked High to Low) ---")
for crop, yield_val in sorted_crops:
    print(f"{crop}: {yield_val:.2f}")

print("\nScript finished.")'''

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os
import django
import sys

# --- GLOBAL CONFIGURATION ---
TARGET_PREDICTION_YEAR = 2025
DEFAULT_PRICE = 1000.0

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ml_model -> outer backend
sys.path.append(BASE_DIR)
DATA_PATH = os.path.join(BASE_DIR, "ml_model", "data")
print("Looking for files in:", DATA_PATH)
print(os.listdir(DATA_PATH))
# --- 1. Data Loading and Cleaning ---

print("--- 1. Loading Datasets from 'data/' directory ---")

try:
    # 1.1 Load FAOSTAT-style crop dataset (Global/Large Scale)
    df_fao = pd.read_csv(os.path.join(DATA_PATH, "FAOSTAT_data_en_11-6-2025.csv"))
    
    print(f"FAOSTAT File Columns Loaded: {list(df_fao.columns)}")

    # --- Standard FAOSTAT Data Reformatting ---
    df_fao = df_fao.rename(columns={
        'Item': 'Crop',
        'Year': 'Year', 
        'Element': 'Metric',
        'Value': 'Value'
    })
    
    METRICS_TO_KEEP = ['Area harvested', 'Production', 'Yield'] 
    df_fao_filtered = df_fao[df_fao['Metric'].isin(METRICS_TO_KEEP)].copy()
    
    # Debug check to confirm metrics were found
    print(f"FAOSTAT Unique Metrics Found (Post-Filter Check): {list(df_fao_filtered['Metric'].unique())}")


    df_fao_pivoted = df_fao_filtered.pivot_table(
        index=['Crop', 'Year'], 
        columns='Metric', 
        values='Value', 
        aggfunc='sum' 
    ).reset_index()

    df_fao = df_fao_pivoted.rename(columns={
        'Area harvested': 'Area', 
        'Production': 'Production', 
        'Yield': 'Yield'
    })
    
    df_fao = df_fao[['Crop', 'Year', 'Area', 'Production', 'Yield']].copy()
    
    # 1.2 Load Indian state crop dataset (Detailed/Input Features)
    df_india = pd.read_csv(os.path.join(DATA_PATH, "crop_data.csv"))

    # Rename Indian state columns to standard names for processing
    df_india = df_india.rename(columns={
        'Crop_Year': 'Year', 
        'Crop': 'Crop',
        'Area': 'State_Area', 
        'Production': 'State_Production', 
        'Annual_Rainfall': 'Annual_Rainfall', 
        'Fertilizer': 'Fertilizer', 
        'Pesticide': 'Pesticide', 
        'Yield': 'State_Yield'
    })
    
    required_india_cols = ['Crop', 'Year', 'State_Area', 'State_Production', 'Annual_Rainfall', 'Fertilizer', 'Pesticide', 'State_Yield']
    df_india = df_india[required_india_cols].copy()

    # --- CRITICAL FIX: Robust Data Cleaning for ML Training ---
    df_india['Crop'] = df_india['Crop'].astype(str).str.strip()
    
    numeric_cols = ['State_Area', 'State_Production', 'Annual_Rainfall', 'Fertilizer', 'Pesticide', 'State_Yield']
    for col in numeric_cols:
        # Use errors='coerce' to turn non-numeric values into NaN
        df_india[col] = pd.to_numeric(df_india[col], errors='coerce')
    # --- END CRITICAL FIX ---
    # counts before/after cleaning
    print("Original df_india shape:", pd.read_csv(os.path.join(DATA_PATH, "crop_data.csv")).shape)
    print("After initial rename/coerce shape:", df_india.shape)

    # How many rice rows exist
    print("Rice rows (raw):", df_india[df_india['Crop'].str.contains('rice', case=False, na=False)].shape)

    # Null counts per column
    print("Nulls per column in df_india:\n", df_india.isnull().sum())

    # How many rows survive the dropna
    base_features = ['State_Area','State_Production','Annual_Rainfall','Fertilizer','Pesticide']
    print("Rows before dropna:", df_india.shape[0])
    print("Rows after dropna:", df_india.dropna(subset=base_features + ['State_Yield']).shape[0])

    # Value counts by year and crop uniqueness
    print("Unique years:", df_india['Year'].nunique())
    print("Unique crops:", df_india['Crop'].nunique())
    print("Top 10 crops:\n", df_india['Crop'].value_counts().head(10))

    print("\n--- DEBUGGING CROP/YEAR ALIGNMENT ---")
    print(f"State Data Crops (crop_data.csv): {list(df_india['Crop'].unique())[:5]}...")
    print(f"Global Data Crops (FAOSTAT): {list(df_fao['Crop'].unique())[:5]}...")
    print("-------------------------------------")

except Exception as e:
    print(f"ERROR during file loading or initial cleaning: {e}. Using simulated data fallback.")
    # Fallback to simulated data if files fail to load
    
    # --- START: Enhanced Simulated Data Generation ---
    BASE_SIMULATED_DATA = {
        'Rice': {'State_Area': 10000, 'State_Production': 550, 'State_Yield': 5.5, 'Global_Area': 40000, 'Global_Production': 2200, 'Global_Yield': 55.0},
        'Wheat': {'State_Area': 8000, 'State_Production': 360, 'State_Yield': 4.5, 'Global_Area': 30000, 'Global_Production': 1350, 'Global_Yield': 45.0},
        'Maize': {'State_Area': 12000, 'State_Production': 720, 'State_Yield': 6.0, 'Global_Area': 50000, 'Global_Production': 3000, 'Global_Yield': 60.0},
        'Barley': {'State_Area': 6000, 'State_Production': 200, 'State_Yield': 3.33, 'Global_Area': 25000, 'Global_Production': 830, 'Global_Yield': 33.2},
        'Cotton': {'State_Area': 15000, 'State_Production': 900, 'State_Yield': 6.0, 'Global_Area': 60000, 'Global_Production': 3600, 'Global_Yield': 60.0},
        'Soybeans': {'State_Area': 18000, 'State_Production': 1100, 'State_Yield': 6.11, 'Global_Area': 70000, 'Global_Production': 4300, 'Global_Yield': 61.4},
        'Groundnuts': {'State_Area': 9000, 'State_Production': 400, 'State_Yield': 4.44, 'Global_Area': 35000, 'Global_Production': 1600, 'Global_Yield': 45.7},
    }

    def apply_random_variation(value, year_offset, max_variation=0.05):
        random_factor = np.random.uniform(1 - max_variation, 1 + max_variation)
        trend_factor = 1 + (year_offset * 0.005) 
        return value * random_factor * trend_factor

    data_fao_list = []
    data_india_list = []
    training_years = [2021, 2022, 2023, 2024] 
    
    for year_index, year in enumerate(training_years):
        for crop, bases in BASE_SIMULATED_DATA.items():
            
            state_area = apply_random_variation(bases['State_Area'], year_index, 0.03)
            state_prod = apply_random_variation(bases['State_Production'], year_index, 0.04)
            state_yield = state_prod / state_area * 100 
            
            data_india_list.append({
                'Crop': crop + '-India',
                'Year': year,
                'State_Area': state_area,
                'State_Production': state_prod,
                'Annual_Rainfall': np.random.uniform(800, 1500),
                'Fertilizer': np.random.uniform(150, 250),
                'Pesticide': np.random.uniform(40, 60),
                'State_Yield': state_yield
            })

            global_area = apply_random_variation(bases['Global_Area'], year_index, 0.02)
            global_prod = apply_random_variation(bases['Global_Production'], year_index, 0.03)
            global_yield = global_prod / global_area * 100 
            
            data_fao_list.append({
                'Crop': crop,
                'Year': year,
                'Area': global_area,
                'Production': global_prod,
                'Yield': global_yield
            })

    # Generate the 2025 Global features (Input data for prediction)
    year_index = len(training_years)
    for crop, bases in BASE_SIMULATED_DATA.items():
        global_area = apply_random_variation(bases['Global_Area'], year_index, 0.02)
        global_prod = apply_random_variation(bases['Global_Production'], year_index, 0.03)
        global_yield = global_prod / global_area * 100 
        
        data_fao_list.append({
            'Crop': crop,
            'Year': TARGET_PREDICTION_YEAR, 
            'Area': global_area,
            'Production': global_prod,
            'Yield': global_yield
        })

    df_fao = pd.DataFrame(data_fao_list)
    df_fao = df_fao[['Crop', 'Year', 'Area', 'Production', 'Yield']] 

    df_india = pd.DataFrame(data_india_list)
    
    # --- END: Enhanced Simulated Data Generation ---


# --- 2. Combine Datasets (Mapping only) ---

# 2.1. Define Crop Mapping (Local Name -> Global Name)
CROP_MAPPING = {
    'Arecanut': 'Areca nuts',
    'Cotton(lint)': 'Cotton', 
    'Arhar/Tur': 'Pigeon peas', 
    'Castor seed': 'Castor oil seeds',
    'Coconut ': 'Coconuts', 
    'Coconut': 'Coconuts', 
    # Mappings for simulated data:
    'Soybeans-India': 'Soybeans', 
    'Groundnuts-India': 'Groundnuts', 
    'Rice-India': 'Rice', 
    'Wheat-India': 'Wheat',
    'Maize-India': 'Maize',
    'Barley-India': 'Barley',
    'Cotton-India': 'Cotton',
}

def clean_and_merge_data(df_fao, df_india):
    """
    Refactored merge function to prevent 'Crop' column duplication.
    """
    
    # 1. Prepare Local Data (df_india) for merge
    df_local_for_merge = df_india.copy()
    # Create the merge key using the Global Crop name
    df_local_for_merge['Crop_Merge_Key'] = df_local_for_merge['Crop'].map(CROP_MAPPING)
    df_local_for_merge.dropna(subset=['Crop_Merge_Key'], inplace=True)
    
    # Select feature columns, renaming the merge key to 'Crop'
    feature_cols = ['Year', 'State_Area', 'State_Production', 'Annual_Rainfall', 'Fertilizer', 'Pesticide', 'State_Yield']
    df_local_features = df_local_for_merge[['Crop_Merge_Key'] + feature_cols]
    df_local_features = df_local_features.rename(columns={'Crop_Merge_Key': 'Crop'})

    # 2. Prepare Global Data (df_fao)
    df_fao_clean = df_fao.rename(columns={'Area': 'Global_Area', 'Production': 'Global_Production', 'Yield': 'Global_Yield'})

    # 3. Merge on the singular 'Crop' column and 'Year'
    df_merged = pd.merge(
        df_local_features,
        df_fao_clean,
        on=['Crop', 'Year'],
        how='left' 
    )
    
    # --- DEBUGGING MERGE CHECK ---
    print("\n--- DEBUGGING MERGE CHECK ---")
    print(f"Master Dataframe columns: {list(df_merged.columns)}")
    print("-----------------------------")

    return df_merged

df_master = clean_and_merge_data(df_fao, df_india)


# --- 3. Predict Yield using Machine Learning ---
# (Training logic is robust and unchanged)
# ... (rest of section 3 remains the same)

# 3.1. Prepare Data for ML
df_ml = df_india.copy()

# CRITICAL: Drop rows where any feature or the target is missing (NaN)
base_features = ['State_Area', 'State_Production', 'Annual_Rainfall', 'Fertilizer', 'Pesticide']
target = 'State_Yield' 
df_ml.dropna(subset=base_features + [target], inplace=True) 

if df_ml.empty:
    print("\nERROR: No clean data available for ML training after dropping NaNs.")
    exit()

# 3.2. One-Hot Encode Crop 
df_ml_encoded = pd.get_dummies(df_ml, columns=['Crop'], prefix='Crop')

# Define final features set
crop_features = [col for col in df_ml_encoded.columns if col.startswith('Crop_')]
features = base_features + crop_features

X = df_ml_encoded[features]
y = df_ml_encoded[target]

# Store the list of all feature column names for future alignment
training_features = X.columns

# 3.3. Split Data & Train the Model
if len(X) < 2:
    print("\nWARNING: Too little data for proper train/test split. Skipping evaluation.")
    X_train, y_train = X, y
else:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 3.4. Evaluate 
if len(X) >= 2:
    y_pred = model.predict(X_test)

    # Compute Metrics
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\n--- 3. Machine Learning Model Results ---")
    print(f"Random Forest Regressor trained on {len(X_train)} samples.")
    print(f"RMSE (Root Mean Squared Error): {rmse:.4f}")
    print(f"MAE  (Mean Absolute Error): {mae:.4f}")
    print(f"R² Score: {r2:.4f}")

else:
    print("\n--- 3. Machine Learning Model Results ---")
    print("Model trained on available data without formal evaluation.")



# --- 4. Prepare for 2025 Prediction ---

# Determine the features to use for 2025 prediction
prediction_source_year = TARGET_PREDICTION_YEAR
if TARGET_PREDICTION_YEAR not in df_fao['Year'].unique():
    prediction_source_year = df_fao['Year'].max()
    print(f"\nINFO: Using latest available global features from {prediction_source_year} to predict for {TARGET_PREDICTION_YEAR}.")

df_future_inputs = df_fao[df_fao['Year'] == prediction_source_year].copy()
df_future_inputs = df_future_inputs.rename(columns={
    'Area': 'Global_Area',
    'Production': 'Global_Production'
})
df_future_inputs['Year'] = TARGET_PREDICTION_YEAR

# Create a reverse mapping for prediction: Global Name (Key) -> Local Name (Value)
reverse_crop_mapping = {v: k for k, v in CROP_MAPPING.items()}

# --- 4.1. DEBUGGING PREDICTION MAPPING (New Section) ---
print("\n--- 4.1. DEBUGGING PREDICTION MAPPING ---")
print(f"Required Global Crop Names (Map Keys): {list(reverse_crop_mapping.keys())}")
print(f"Actual Global Crops in {TARGET_PREDICTION_YEAR} Data: {list(df_future_inputs['Crop'].unique())}")


initial_pred_count = len(df_future_inputs)
# Map the FAO crop name back to the local training crop name
df_future_inputs['Crop_Mapped_Local'] = df_future_inputs['Crop'].map(reverse_crop_mapping)
df_future_inputs.dropna(subset=['Crop_Mapped_Local'], inplace=True)
final_pred_count = len(df_future_inputs)

if final_pred_count == 0:
    print("\nFATAL ERROR: After mapping, 0 crops remain for prediction.")
    print("This means none of the global crops in the FAO data could be matched")
    print("to the local crops defined in CROP_MAPPING (Section 2.1).")
    print("ACTION: Check the list of 'Actual Global Crops' above and ensure all are present as values in CROP_MAPPING.")
    exit()
    
print(f"Prediction Setup: Initial global crops: {initial_pred_count} rows.")
print(f"Prediction Setup: Final matched crops: {final_pred_count} rows.")
print("-------------------------------------")
# --- END DEBUGGING PREDICTION MAPPING ---


# Calculate the mean of the environmental/local features from the training set (df_ml)
state_avg_features = df_ml[base_features].mean()

# Fill the prediction inputs with the average local features
for feature in base_features:
    df_future_inputs[feature] = state_avg_features[feature]

# Encode future inputs and align columns
df_future_inputs_encoded = pd.get_dummies(df_future_inputs, columns=['Crop_Mapped_Local'], prefix='Crop')

# Align the prediction features (X_future) with the training features (training_features)
X_future = df_future_inputs_encoded.reindex(columns=training_features, fill_value=0)

print(f"Prediction Setup: Final feature matrix shape for model.predict(): {X_future.shape}")
predicted_yields = model.predict(X_future)
df_future_inputs['Predicted_Yield'] = predicted_yields


# --- 5. Estimate Synthetic Price (Annual Baseline) ---

# 5.1. Define Crop-Specific Demand Factors 
DEMAND_FACTORS = {
    'Rice': 1500,  
    'Wheat': 1200, 
    'Maize': 800,  
    'Barley': 750,  
    'Cotton': 1800, 
    'Areca nuts': 2500,
    'Pigeon peas': 1300, 
    'Castor oil seeds': 1100, 
    'Coconuts': 1900, 
    'Soybeans': 1600, 
    'Groundnuts': 1400,
}

# 5.2. Apply the Synthetic Price Formula
def calculate_synthetic_price(row):
    demand_factor = DEMAND_FACTORS.get(row['Crop'], 1000) 
    # Use a small constant to prevent division by zero
    price = demand_factor / (row['Predicted_Yield'] + 1e-6)
    return round(price, 2)

df_future_inputs['Synthetic_Price_Annual'] = df_future_inputs.apply(calculate_synthetic_price, axis=1)


# --- 6. Short-Term Daily Forecast Simulation ---

def simulate_daily_forecast(base_price_annual, num_days=7):
    """
    Simulates a 7-day price forecast based on the predicted annual price.
    """
    forecast = []
    current_price = base_price_annual
    start_date = datetime.now().date()
    
    # Introduce a slight weekly drift (e.g., 0% to +/- 2% change over 7 days)
    weekly_drift_rate = np.random.uniform(-0.02, 0.02)
    
    for i in range(num_days):
        # 1. Base Fluctuation (daily noise)
        daily_noise = np.random.uniform(-0.005, 0.005) # +/- 0.5% daily noise
        
        # 2. Apply weekly trend
        trend_adjustment = 1 + (weekly_drift_rate * (i / num_days))
        
        # Calculate new price
        price = current_price * (1 + daily_noise) * trend_adjustment
        
        forecast.append({
            'Day': (start_date + timedelta(days=i)).strftime('%Y-%m-%d'),
            'Price_Estimate': round(price, 2)
        })
        
        # Update current price slightly to carry forward the movement
        current_price = price 
        
    return forecast

# Generate 7-day forecasts for all predicted crops
daily_forecasts = {}
for _, row in df_future_inputs.iterrows():
    crop_name = row['Crop']
    base_price = row['Synthetic_Price_Annual']
    daily_forecasts[crop_name] = simulate_daily_forecast(base_price)

# --- 7. Final Results Output ---

print("\n\n#################################################################")
print(f"--- 7. PREDICTED MARKET ESTIMATE & SHORT-TERM FORECAST ({TARGET_PREDICTION_YEAR}) ---")
print("#################################################################")

if df_future_inputs.empty:
    print("\n--- FALLBACK MESSAGE ---")
    print("Could not generate price estimates. Ensure data files are correctly formatted and CROP_MAPPING is complete.")
else:
    # Print Annual Prediction Summary
    final_output_annual = df_future_inputs[['Crop', 'Year', 'Predicted_Yield', 'Synthetic_Price_Annual']]
    print("\n--- A. ANNUAL BASELINE PREDICTION (2025 Average) ---")
    print(final_output_annual.to_string(index=False))

    # Print Daily Forecast Summary
    print("\n\n--- B. 7-DAY SHORT-TERM FORECAST (Simulated Daily Prices) ---")
    
    for crop, forecast_list in daily_forecasts.items():
        print(f"\nCrop: {crop} (Baseline Annual Price: {df_future_inputs[df_future_inputs['Crop'] == crop]['Synthetic_Price_Annual'].iloc[0]:.2f})")
        
        daily_df = pd.DataFrame(forecast_list)
        print(daily_df.to_string(index=False))

'''feature_importances = model.feature_importances_

# Create a DataFrame for easier viewing
feat_imp_df = pd.DataFrame({
    'Feature': training_features,
    'Importance': feature_importances
}).sort_values(by='Importance', ascending=False)

print("\n--- Feature Importances ---")
print(feat_imp_df)

# Optional: Plot the top 10 most important features
top_n = 10
plt.figure(figsize=(10,6))
plt.barh(feat_imp_df['Feature'][:top_n][::-1], feat_imp_df['Importance'][:top_n][::-1], color='skyblue')
plt.xlabel("Importance")
plt.title(f"Top {top_n} Features Impacting Yield Prediction")
plt.show()'''


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from farmer_app.models import CropPrices

print("\n--- 8. Saving predictions to CropPrices model ---")
CropPrices.objects.filter(year=TARGET_PREDICTION_YEAR).delete()
for _, row in df_future_inputs.iterrows():

    crop_name = row['Crop']
    year_val = row['Year']
    predicted_yield = float(row['Predicted_Yield'])
    synthetic_price = float(row['Synthetic_Price_Annual'])

    obj, created = CropPrices.objects.update_or_create(
        crop=crop_name,
        year=year_val,
        defaults={
            'predicted_yield': predicted_yield,
            'synthetic_price': synthetic_price
        }
    )

    print(f"[{'CREATED' if created else 'UPDATED'}] {crop_name} {year_val} → Yield={predicted_yield:.2f}, Price={synthetic_price:.2f}")

print("\n✔ DONE: All predictions saved to database.")

from farmer_app.models import DailyCropForecast

print("\n--- 9. Saving 7-day daily forecasts ---")

# Clear existing records for the same crops/dates (optional but recommended)
DailyCropForecast.objects.all().delete()

for crop, forecast_list in daily_forecasts.items():
    for entry in forecast_list:
        date_str = entry['Day']
        price = entry['Price_Estimate']

        DailyCropForecast.objects.update_or_create(
            crop=crop,
            date=date_str,
            defaults={'price_estimate': price}
        )

        print(f"Saved: {crop} {date_str} → ₹{price}")