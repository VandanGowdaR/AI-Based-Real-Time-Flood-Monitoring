# train_model.py
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import joblib

os.makedirs("artifacts", exist_ok=True)

def generate_synthetic(n=3000, seed=42):
    np.random.seed(seed)
    avg_temp = np.random.normal(25, 5, n)
    max_temp = avg_temp + np.abs(np.random.normal(3, 1.5, n))
    avg_wind = np.random.normal(5, 2, n)
    avg_cloud = np.clip(np.random.normal(50, 25, n), 0, 100)
    total_precip = np.abs(np.random.normal(10, 20, n))
    avg_humidity = np.clip(np.random.normal(70, 15, n), 0, 100)
    water_level = np.abs(np.random.normal(1.0, 0.7, n))
    flow_rate = np.abs(np.random.normal(40, 30, n))

    # label: flood if precip + water_level + flow_rate high
    score = (total_precip / 20.0) + (water_level / 1.5) + (flow_rate / 200.0) + (avg_humidity / 200.0)
    label = (score + np.random.normal(0, 0.3, n) > 1.0).astype(int)

    df = pd.DataFrame({
        "avg_temp": avg_temp,
        "max_temp": max_temp,
        "avg_wind": avg_wind,
        "avg_cloud": avg_cloud,
        "total_precip": total_precip,
        "avg_humidity": avg_humidity,
        "water_level": water_level,
        "flow_rate": flow_rate,
        "label": label
    })
    return df

def train(df):
    X = df.drop(columns=["label"])
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    clf = RandomForestClassifier(n_estimators=120, random_state=42)
    clf.fit(X_train_s, y_train)
    acc = clf.score(scaler.transform(X_test), y_test)
    print("Test accuracy:", acc)
    joblib.dump(clf, "artifacts/model.pkl")
    joblib.dump(scaler, "artifacts/scaler.pkl")
    print("Saved artifacts/model.pkl and artifacts/scaler.pkl")

if __name__ == "__main__":
    print("Generating synthetic data and training model...")
    df = generate_synthetic()
    train(df)
