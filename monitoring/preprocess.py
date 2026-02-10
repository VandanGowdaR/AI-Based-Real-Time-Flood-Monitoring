# monitoring/preprocess.py
import numpy as np
import joblib
import os

SCALER_PATH = "artifacts/scaler.pkl"

def features_to_vector(d: dict):
    """
    Convert dictionary returned by get_features into model input vector.
    Order must match training.
    """
    vec = [
        d.get("avg_temp", 0.0),
        d.get("max_temp", 0.0),
        d.get("avg_wind", 0.0),
        d.get("avg_cloud", 0.0),
        d.get("total_precip", 0.0),
        d.get("avg_humidity", 0.0),
        d.get("water_level", -1.0) if d.get("water_level") is not None else -1.0,
        d.get("flow_rate", -1.0) if d.get("flow_rate") is not None else -1.0
    ]
    return np.array(vec).reshape(1, -1)

def load_scaler():
    if os.path.exists(SCALER_PATH):
        return joblib.load(SCALER_PATH)
    return None

def scale(X, scaler):
    if scaler is None:
        return X
    return scaler.transform(X)
