# Weather + Flood Intelligence — Full Stack

This zip includes:
- **backend/** Flask API for weather, risk prediction, alerts, radar proxy
- **frontend/** React + Vite app with animated UI, radar map, risk card

## Setup

### 1) Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Put your OpenWeatherMap API key in .env as OWM_API_KEY=...
python app.py
```
The API should start at **http://localhost:8000**.

### 2) Frontend
```bash
cd frontend
cp .env.example .env
# If needed, change VITE_API_BASE to your backend URL
npm install
npx tailwindcss init -p  # if config missing, else skip
npm run dev
```
Open **http://localhost:5173** in your browser.

## Notes
- Radar tiles & weather require a valid **OWM_API_KEY** in backend `.env`.
- The risk model uses the included `backend/artifacts/model.pkl` and `scaler.pkl` copied from your project.
- `GET /api/risk` derives features from current weather; replace placeholders with your river/soil inputs as available.
