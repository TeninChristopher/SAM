'''import pandas as pd
import numpy as np
import os
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "crop_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "data", "crop_model.pkl")

def train_crop_model():
    print("🌾 Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    # ✅ Clean and preprocess
    df = df.dropna(subset=["Crop", "Yield"])  # remove rows missing crop or yield
    df = df.fillna(0)

    # 🎯 We want to PREDICT the "Crop" based on numeric + environmental features
    feature_cols = ["Crop_Year", "Season", "State", "Area", "Production",
                    "Annual_Rainfall", "Fertilizer", "Pesticide", "Yield"]

    # Convert categorical columns to numeric (Season, State)
    df = pd.get_dummies(df, columns=["Season", "State"], drop_first=True)

    X = df.drop(["Crop"], axis=1)
    y = df["Crop"]

    print("📊 Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("🧠 Training model...")
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    print("✅ Evaluating model...")
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"Accuracy: {acc:.2f}")
    print("\n📈 Classification Report:\n")
    print(classification_report(y_test, y_pred))

    # 💾 Save trained model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"🎉 Training complete! Model saved to: {MODEL_PATH}")

if __name__ == "__main__":
    train_crop_model()
'''
'''
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import os

# Define file paths based on the project structure
# Assumes this script is in FARMER/backend/ml_model
DATA_PATH = os.path.join("data", "crop_data.csv")
MODEL_PATH = os.path.join("data", "crop_yield_model.pkl")

print("Script started...")

# 1. Load Data
try:
    df = pd.read_csv(DATA_PATH)
    print("Data loaded successfully.")
except FileNotFoundError:
    print(f"Error: Data file not found at {DATA_PATH}")
    exit()

# 2. Pre-processing
# Drop rows with missing values for simplicity
df.dropna(inplace=True)

# Define features (X) and target (y)
# We drop 'Production' because Yield is derived from it (Yield = Production / Area),
# which would cause data leakage.
# We drop 'Crop_Year' for simplicity, but you could include it as a feature.
features = ['Crop', 'Season', 'State', 'Area', 'Annual_Rainfall', 'Fertilizer', 'Pesticide']
target = 'Yield'

X = df[features]
y = df[target]

# 3. Define Preprocessing Pipeline
# Identify categorical and numerical features
categorical_features = ['Crop', 'Season', 'State']
numerical_features = ['Area', 'Annual_Rainfall', 'Fertilizer', 'Pesticide']

# Create a preprocessor using ColumnTransformer
# OneHotEncoder for categorical features (handles unknown categories)
# StandardScaler for numerical features
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough'
)

# 4. Define the Model
# We use RandomForestRegressor, a powerful and common model
model = RandomForestRegressor(n_estimators=100, random_state=42)

# 5. Create the Full Pipeline
# This pipeline chains the preprocessor and the model
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', model)
])

# 6. Split and Train the Model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Starting model training...")
pipeline.fit(X_train, y_train)
print("Model training complete.")

# 7. Evaluate the Model (Optional but recommended)
score = pipeline.score(X_test, y_test)
print(f"Model R^2 score on test set: {score:.4f}")

# 8. Save the Pipeline
joblib.dump(pipeline, MODEL_PATH)
print(f"Model pipeline saved to {MODEL_PATH}")

print("Script finished.")
'''

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import os
import numpy as np

# Define file paths (assuming the script is in ml_model folder)
DATA_PATH = os.path.join("data", "crop_data.csv")
MODEL_PATH = os.path.join("data", "crop_yield_model_V3.pkl")

print("Script started...")

# --- NEW: Define Conversion Constants ---
# Assuming 'Production' for these crops is in 'Count' (units or bunches)
# and we want to convert everything to KILOGRAMS (kg).
# The final Yield will be in kg/Hectare.

# 1.5 kg per Coconut unit
COCONUT_KG_PER_UNIT = 1.5 / 1000000.0

# 15 kg per Banana bunch (adjust this if 'Production' is individual bananas)
BANANA_KG_PER_UNIT = 15.0
print(f"DEBUG: Coconut factor is set to {COCONUT_KG_PER_UNIT}") # <-- ADD THIS LINE
# 1. Load Data
try:
    df = pd.read_csv(DATA_PATH)
    print("Data loaded successfully.")
except FileNotFoundError:
    print(f"Error: Data file not found at {DATA_PATH}")
    exit()

# 2. Data Cleaning and Standardization
df.dropna(inplace=True)

# Ensure Production and Area are non-zero to calculate Yield
df = df[(df['Area'] > 0) & (df['Production'] >= 0)]

print("Starting unit standardization...")

def standardize_production_to_kg(row):
    """Converts Production from 'Count' to 'Weight (kg)' for specific crops."""
    crop = row['Crop']
    #print(crop)
    production = row['Production']
    if crop == 'Coconut ':
        #print("yes")
        # Production in Count * 1.5 kg/unit
        return production * COCONUT_KG_PER_UNIT
    
    elif crop == 'Banana':
        # Production in Count * 15 kg/unit
        return production * BANANA_KG_PER_UNIT
    
    else:
        # Assuming all other crops' Production is already in Tonnes (T).
        # Convert Tonnes (T) to Kilograms (kg): T * 1000
        return production * 1000

# Apply the standardization
#print(df['Production'])
df['Production_kg'] = df.apply(standardize_production_to_kg, axis=1)

# Calculate the new YIELD in Kilograms per Area (kg/Hectare)
df['Yield_kg_per_Hectare'] = df['Production_kg'] / df['Area']

print("Unit standardization and new Yield calculation complete.")
# --- END NEW ---


# 3. Define Features and Target
# Now we target the new standardized yield column
features = ['Crop', 'Season', 'State', 'Area', 'Annual_Rainfall', 'Fertilizer', 'Pesticide']
target = 'Yield_kg_per_Hectare' # Use the new target column

X = df[features]
y = df[target]

# 4. Define Preprocessing Pipeline
categorical_features = ['Crop', 'Season', 'State']
numerical_features = ['Area', 'Annual_Rainfall', 'Fertilizer', 'Pesticide']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough'
)

# 5. Define the Model (using optimized parameters)
model = RandomForestRegressor(
    n_estimators=50,       # Reduced trees for faster training
    n_jobs=-1,             # Use all available CPU cores (MAJOR speedup)
    max_depth=10,          # Limit depth to prevent overfitting/slow training (optional, but recommended)
    random_state=42
)

# 6. Create the Full Pipeline
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', model)
])

# 7. Split and Train the Model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Starting model training...")
pipeline.fit(X_train, y_train)
print("Model training complete.")

# 8. Evaluate and Save the Pipeline
score = pipeline.score(X_test, y_test)
print(f"Model R^2 score on test set: {score:.4f}")

joblib.dump(pipeline, MODEL_PATH)
print(f"Model pipeline saved to {MODEL_PATH}")

print("Script finished.")