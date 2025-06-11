import json
import os
import requests

def get_new_data():
    api_url = "https://api.myshiptracking.com/api/v2/fleets/vessels"
    api_key = "mSHSW44EqOd@5RTSCZJKMyCRsAkEc6*!vo"
    params = {
        "fleet_id": "297096",
        "response": "simple"
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    response = requests.get(api_url, params=params, headers=headers)
    response.raise_for_status()  # Hata varsa exception fırlatır
    return response.json()

def update_json_file():
    data = get_new_data()
    json_path = os.path.join(".venv", "datas.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data

if __name__ == "__main__":
    data = update_json_file()
    print(json.dumps(data, ensure_ascii=False, indent=4))