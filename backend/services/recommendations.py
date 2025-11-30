from farmer_app.models import CustomerAction, CustomerRecommendation
from farmer_app.models import Customer # <-- Ensure Customer is imported!
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from django.utils import timezone
from sklearn.ensemble import RandomForestClassifier

# Define the full list of features for scaling and training
# NOTE: The order matters and must be consistent.
FEATURE_COLUMNS = [
    "total_weighted_score", "add_count", "remove_count", "purchase_count",
    "avg_price", "avg_discount", "avg_stock", 
    "discount_sensitivity", "price_elasticity", "stock_urgency" # <-- NEW PROFILE FEATURES
]

ACTION_SCORES = {"ADD": 1, "REMOVE": -1, "PURCHASE": 3}

def get_customer_recommendations(customer):
    """
    Analyzes customer actions, integrates customer profile scores, 
    scales data, and generates effective recommendations.
    """
    # FIX: We filter the actions using the primary key (pk) of the customer 
    # instead of passing the object directly, which resolves the FieldError.
    actions = CustomerAction.objects.filter(customer_id=customer.pk)
    print(f"[DEBUG] Customer {customer.pk}: Found {actions.count()} actions")

    # 1. HANDLE NO DATA (Cold Start)
    if not actions.exists():
        # ... (Cold start logic remains the same)
        recommendations = [{"crop": "Wheat", "purchase_prob": 0.1}, {"crop": "Rice", "purchase_prob": 0.05}]
    else:
        # 1.5. RETRIEVE CUSTOMER PROFILE SCORES (NEW)
        # Use getattr() for safety if profile features haven't been calculated yet
        customer_profile = {
            "discount_sensitivity": getattr(customer, 'discount_sensitivity', 0.0),
            "price_elasticity": getattr(customer, 'price_elasticity', 0.0),
            "stock_urgency": getattr(customer, 'stock_urgency', 0.0)
        }

        # 2. PREPARE DATA & FEATURE ENGINEERING (Crop-Specific)
        df = pd.DataFrame(list(actions.values(
            "crop", "action", "timestamp", "price_at_action", "discount_at_action", "stock_at_action"
        )))

        # (Calculate weighted score and ensure numerical types - same as existing code)
        df["score"] = df["action"].map(ACTION_SCORES)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        now = timezone.now()
        df["recency"] = (now - df["timestamp"]).dt.total_seconds() / (60*60*24)
        df["recency_weight"] = np.exp(-0.1 * df["recency"])
        df["weighted_score"] = df["score"] * df["recency_weight"]
        df['price_at_action'] = pd.to_numeric(df['price_at_action'], errors='coerce')
        df['discount_at_action'] = pd.to_numeric(df['discount_at_action'], errors='coerce')
        df['stock_at_action'] = pd.to_numeric(df['stock_at_action'], errors='coerce')

        # Aggregation of Crop-Specific Features
        features = df.groupby("crop").agg(
            total_weighted_score=("weighted_score", "sum"), add_count=("score", lambda x: (x==1).sum()),
            remove_count=("score", lambda x: (x==-1).sum()), purchase_count=("score", lambda x: (x==3).sum()),
            avg_price=("price_at_action", "mean"), avg_discount=("discount_at_action", "mean"),
            avg_stock=("stock_at_action", "mean"),
        ).reset_index()

        # 2.5. BROADCAST CUSTOMER PROFILE TO ALL CROPS (NEW)
        for key, value in customer_profile.items():
            features[key] = value

        # 3. ML MODEL TRAINING & PREDICTION
        features["label"] = (features["purchase_count"] > 0).astype(int)
        y = features["label"]
        X_raw = features[FEATURE_COLUMNS] # <-- Use the full feature list
        
        # 3a. SCALING (CRITICAL FOR PERFORMANCE)
        scaler = MinMaxScaler()
        X = scaler.fit_transform(X_raw)

        # Safety Check (remains the same)
        if len(features) < 2 or y.nunique() < 2:
            print("[DEBUG] Not enough data/variance for ML. Using Weighted Score Fallback.")
            # ... (Fallback logic)
            max_score = features["total_weighted_score"].max()
            if max_score <= 0: max_score = 1
            features["purchase_prob"] = features["total_weighted_score"] / max_score
            features["purchase_prob"] = features["purchase_prob"].clip(lower=0.01, upper=0.99)
        else:
            print("[DEBUG] Running Random Forest Classifier with full Feature set and scaling.")
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X, y)
            features["purchase_prob"] = clf.predict_proba(X)[:,1]

        recommendations = features[["crop", "purchase_prob"]].sort_values(
            "purchase_prob", ascending=False
        ).to_dict(orient="records")

    # 4. SAVE TO DB (Where Recommendations are Stored)
    # Recommendations are stored in the CustomerRecommendation table.
    print(f"[DEBUG] Saving {len(recommendations)} recommendations...")
    CustomerRecommendation.objects.filter(customer=customer).delete()
    
    new_entries = []
    for rec in recommendations:
        new_entries.append(CustomerRecommendation(
            customer=customer,
            crop=rec["crop"],
            purchase_prob=rec["purchase_prob"]
        ))
    
    CustomerRecommendation.objects.bulk_create(new_entries)
    print("[DEBUG] Database updated successfully.")

    return recommendations