# realtime_simulator.py
import time, requests

SERVER = "http://127.0.0.1:5000"

def loop(lat, lon, interval=30):
    while True:
        try:
            r = requests.get(f"{SERVER}/predict", params={"lat": lat, "lon": lon}, timeout=10)
            if r.ok:
                j = r.json()
                print(time.strftime("%Y-%m-%d %H:%M:%S"), "Risk:", j["risk"], "Score:", round(j["score"],3))
            else:
                print("Error:", r.status_code, r.text)
        except Exception as e:
            print("Exception:", e)
        time.sleep(interval)

if __name__ == "__main__":
    # Example Bangalore location
    loop(12.9716, 77.5946, interval=30)
