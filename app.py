from flask import Flask, render_template, request, jsonify
import joblib, os
import base64
from monitoring.owm_ingest import get_features
from monitoring.preprocess import features_to_vector, load_scaler, scale


app = Flask(__name__, template_folder="templates", static_folder="static")

MODEL_PATH = "artifacts/model.pkl"
SCALER_PATH = "artifacts/scaler.pkl"

# --- Load model + scaler at startup ---
if not os.path.exists(MODEL_PATH):
    raise RuntimeError("Model not found. Run: python train_model.py to create artifacts/model.pkl")

model = joblib.load(MODEL_PATH)
scaler = load_scaler()


@app.route("/home")
def home():
    """Landing / Home page"""
    return render_template("index.html")


@app.route("/")
def index():
    """Main dashboard page"""
    return render_template("home.html")

@app.route('/plots.html')
def plots():
    return render_template('plots.html')

@app.route('/heatmaps.html')
def heatmaps():
    return render_template('heatmaps.html')

@app.route('/damage_analysis.html')
def damage_analysis():
    return render_template('damage_analysis.html')

@app.route('/satellite.html')
def satellite():
    direc = "processed_satellite_images/Delhi_July.png"
    with open(direc, "rb") as image_file:
        image = base64.b64encode(image_file.read())
    image = image.decode('utf-8')
    return render_template('satellite.html', data=data, image_file=image, months=months, text="Delhi in January 2020")

@app.route('/satellite.html', methods=['GET', 'POST'])
def satelliteimages():
    place = request.form.get('place')
    date = request.form.get('date')
    data = [{'name':'Delhi', "sel": ""}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}]
    months = [{"name":"May", "sel": ""}, {"name":"June", "sel": ""}, {"name":"July", "sel": ""}]
    for item in data:
        if item["name"] == place:
            item["sel"] = "selected"
    
    for item in months:
        if item["name"] == date:
            item["sel"] = "selected"

    text = place + " in " + date + " 2020"

    direc = "processed_satellite_images/{}_{}.png".format(place, date)
    with open(direc, "rb") as image_file:
        image = base64.b64encode(image_file.read())
    image = image.decode('utf-8')
    return render_template('satellite.html', data=data, image_file=image, months=months, text=text)


@app.route("/predict")
def predict():
    """
    API endpoint for monitoring.
    Query params:
      - ?city=CityName   OR
      - ?lat=..&lon=..
    Returns:
      { risk: LOW|MEDIUM|HIGH, score: float, features: {...} }
    """
    city = request.args.get("city")
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    try:
        if city:
            feats = get_features(city=city, station_sim=True)
        elif lat is not None and lon is not None:
            feats = get_features(lat=lat, lon=lon, station_sim=True)
        else:
            return jsonify({"error": "Provide either ?city=CityName OR ?lat=..&lon=.."}), 400
    except Exception as e:
        return jsonify({"error": f"Data fetch failed: {e}"}), 500

    # Convert features to vector + scale
    X = features_to_vector(feats)
    Xs = scale(X, scaler)

    # Predict flood probability
    proba = model.predict_proba(Xs)[0]
    prob_flood = float(proba[1])  # probability of flood

    # Risk classification
    if prob_flood > 0.7:
        risk = "HIGH"
    elif prob_flood > 0.4:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return jsonify({
        "risk": risk,
        "score": prob_flood,
        "features": feats
    })


if __name__ == "__main__":
    # Run in debug mode for development
    app.run(debug=True, host="0.0.0.0", port=5000)
