# customer_recommendation_demo.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# SIMULATED CUSTOMER ACTION DATA
# -------------------------------

np.random.seed(42)

CUSTOMERS = ["Alice", "Bob", "Charlie", "Diana"]
CROPS = ["Wheat", "Rice", "Maize", "Cotton"]
ACTIONS = ["ADD", "REMOVE", "PURCHASE"]
ACTION_SCORES = {"ADD": 1, "REMOVE": -1, "PURCHASE": 3}

# Simulate multiple actions per customer per crop
def simulate_customer_actions():
    data = []
    for customer in CUSTOMERS:
        for crop in CROPS:
            num_actions = np.random.randint(3, 10)
            for _ in range(num_actions):
                action = np.random.choice(ACTIONS, p=[0.4, 0.3, 0.3])
                data.append({
                    "customer": customer,
                    "crop": crop,
                    "action": action,
                    "price_at_action": np.random.uniform(20, 100),
                    "discount_at_action": np.random.uniform(0, 20),
                    "stock_at_action": np.random.randint(1, 50)
                })
    return pd.DataFrame(data)

df_actions = simulate_customer_actions()

# -------------------------------
# FEATURE ENGINEERING FUNCTION
# -------------------------------

FEATURE_COLUMNS = [
    "total_weighted_score", "add_count", "remove_count", "purchase_count",
    "avg_price", "avg_discount", "avg_stock",
    "discount_sensitivity", "price_elasticity", "stock_urgency"
]

# Fake customer profile features
CUSTOMER_PROFILES = {
    "Alice": {"discount_sensitivity": 0.5, "price_elasticity": 0.2, "stock_urgency": 0.1},
    "Bob": {"discount_sensitivity": 0.3, "price_elasticity": 0.4, "stock_urgency": 0.2},
    "Charlie": {"discount_sensitivity": 0.2, "price_elasticity": 0.1, "stock_urgency": 0.3},
    "Diana": {"discount_sensitivity": 0.4, "price_elasticity": 0.3, "stock_urgency": 0.2}
}

def prepare_features(df, customer_name):
    df_cust = df[df["customer"] == customer_name].copy()
    df_cust["score"] = df_cust["action"].map(ACTION_SCORES)

    # Aggregate features per crop
    features = df_cust.groupby("crop").agg(
        total_weighted_score=("score", "sum"),
        add_count=("score", lambda x: (x==1).sum()),
        remove_count=("score", lambda x: (x==-1).sum()),
        purchase_count=("score", lambda x: (x==3).sum()),
        avg_price=("price_at_action", "mean"),
        avg_discount=("discount_at_action", "mean"),
        avg_stock=("stock_at_action", "mean")
    ).reset_index()

    # Broadcast customer profile
    profile = CUSTOMER_PROFILES[customer_name]
    for key, value in profile.items():
        features[key] = value

    # Label: whether crop was purchased at least once
    features["label"] = (features["purchase_count"] > 0).astype(int)
    return features

# -------------------------------
# MODEL TRAINING AND METRICS
# -------------------------------

def train_and_evaluate(features, customer_name):
    X_raw = features[FEATURE_COLUMNS]
    y = features["label"]

    # Scaling
    scaler = MinMaxScaler()
    X = scaler.fit_transform(X_raw)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)

    # Predictions
    y_pred = clf.predict(X)
    y_prob = clf.predict_proba(X)[:,1]

    # Metrics
    rmse = mean_squared_error(y, y_prob, squared=False)
    precision = precision_score(y, y_pred, zero_division=0)
    recall = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    cm = confusion_matrix(y, y_pred)

    print(f"\n--- Customer: {customer_name} ---")
    print(f"RMSE: {rmse:.4f}")
    print(f"Precision: {precision:.4f}, Recall: {recall:.4f}, F1 Score: {f1:.4f}")
    print("Confusion Matrix:\n", cm)

    # Visualize Confusion Matrix
    plt.figure(figsize=(4,3))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=[0,1], yticklabels=[0,1])
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(f"Confusion Matrix for {customer_name}")
    plt.show()

# -------------------------------
# RUN FOR ALL CUSTOMERS
# -------------------------------

for customer in CUSTOMERS:
    features = prepare_features(df_actions, customer)
    train_and_evaluate(features, customer)
