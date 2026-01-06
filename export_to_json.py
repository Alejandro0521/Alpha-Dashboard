import pandas as pd
import json
import os
import glob
import ast
from datetime import datetime
import yfinance as yf

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATHS = {
    "carry_trade": os.path.join(BASE_DIR, "1_Carry_Trade/carry_trade_data.csv"),
    "inflation": os.path.join(BASE_DIR, "2_Inflation_Shield/inflation_data.csv"),
    "risk": os.path.join(BASE_DIR, "3_Risk_Thermometer/risk_data.csv"),
    "economy": os.path.join(BASE_DIR, "4_Real_Economy/economy_data.csv"),
    "us_stocks": os.path.join(BASE_DIR, "5_US_Stocks/us_stocks_data.csv"),
    "global_indicators": os.path.join(BASE_DIR, "6_Global_Indicators/global_indicators_data.csv")
}

OUTPUT_PATH = os.path.join(BASE_DIR, "Web/data/dashboard_data.json")

def load_and_clean(path):
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            if 'price_history' in df.columns:
                # Parse string representations of lists to actual Python lists
                df['price_history'] = df['price_history'].apply(
                    lambda x: ast.literal_eval(x) if pd.notna(x) and isinstance(x, str) else x
                )
            # Convert to records (list of dicts) to avoid JSON serialization issues
            records = df.to_dict(orient='records')
            return records
        except Exception as e:
            print(f"Error reading {path}: {e}")
            return []
    return []


def fetch_live_fx():
    TWELVE_DATA_API_KEY = os.environ.get('TWELVE_DATA_API_KEY', '')
    try:
        import requests
        url = f"https://api.twelvedata.com/price?symbol=USD/MXN&apikey={TWELVE_DATA_API_KEY}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'price' in data:
                live_price = float(data['price'])
                print(f"Live USD/MXN (Twelve Data): {live_price}")
                return live_price
    except Exception as e:
        print(f"Twelve Data failed: {e}")

    try:
        ticker = yf.Ticker("MXN=X")
        data = ticker.history(period='1d', interval='1m')
        if not data.empty:
            live_price = float(data['Close'].iloc[-1])
            print(f"Live USD/MXN (Yahoo): {live_price}")
            return live_price
    except Exception as e:
        print(f"Yahoo Finance failed: {e}")

    return None


def generate_alpha_signal(data_carry, data_risk):
    signal = {
        "status": "NEUTRAL",
        "action": "ESPERAR",
        "probability": "50%",
        "stop_loss": "N/A",
        "reason": "Datos insuficientes"
    }

    if not data_carry or not data_risk:
        return signal

    last_carry = data_carry[-1]
    last_risk = data_risk[-1]

    try:
        spread = float(last_carry.get('Carry Spread (bp)', 0))
        vol_z = float(last_risk.get('Vol_Z_Score', 0))
        upper_band = float(last_risk.get('Upper_Band', 0))
        close_fx = float(last_risk.get('Close', 0))
    except:
        return signal

    if spread > 500 and vol_z < 1.5:
        signal["status"] = "🟢 RIESGO ACEPTABLE"
        signal["action"] = "LONG MXN (CARRY)"
        signal["probability"] = "68%"
        sl = upper_band * 1.01 if upper_band > 0 else close_fx * 1.02
        signal["stop_loss"] = f"${sl:.2f}"
        signal["reason"] = f"Spread {spread:.0f}pbs + Volatilidad Baja (Z={vol_z:.1f})"

    elif spread < 400 or vol_z > 2.0:
        signal["status"] = "🔴 RIESGO ALTO"
        signal["action"] = "SHORT MXN (COMPRA USD)"
        signal["probability"] = "75%"
        sl = close_fx * 0.99
        signal["stop_loss"] = f"${sl:.2f}"
        signal["reason"] = f"Compresión de Spread ({spread:.0f}pbs) o Pánico (Z={vol_z:.1f})"

    else:
        signal["status"] = "🟡 PRECAUCIÓN"
        signal["action"] = "MANTENER / HEDGE"
        signal["probability"] = "55%"
        signal["stop_loss"] = f"${upper_band:.2f}"
        signal["reason"] = "Condiciones Mixtas"

    return signal

def replace_nan_with_none(obj):
    """Recursively replace NaN values with None in nested structures"""
    if isinstance(obj, dict):
        return {k: replace_nan_with_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan_with_none(item) for item in obj]
    elif isinstance(obj, float) and pd.isna(obj):
        return None
    else:
        return obj

def main():
    # Load existing data first (to preserve data from other workflows)
    existing_data = {}
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            print(f"Loaded existing data from {OUTPUT_PATH}")
        except Exception as e:
            print(f"Could not load existing data: {e}")

    # Load new data from CSVs
    carry_data = load_and_clean(CSV_PATHS["carry_trade"])
    inflation_data = load_and_clean(CSV_PATHS["inflation"])
    risk_data = load_and_clean(CSV_PATHS["risk"])
    economy_data = load_and_clean(CSV_PATHS["economy"])
    us_stocks_data = load_and_clean(CSV_PATHS["us_stocks"])
    global_indicators_data = load_and_clean(CSV_PATHS["global_indicators"])

    # Merge: use new data if available, else preserve existing
    final_carry = carry_data if carry_data else existing_data.get("carry_trade", [])
    final_inflation = inflation_data if inflation_data else existing_data.get("inflation", [])
    final_risk = risk_data if risk_data else existing_data.get("risk", [])
    final_economy = economy_data if economy_data else existing_data.get("economy", [])
    final_us_stocks = us_stocks_data if us_stocks_data else existing_data.get("us_stocks", [])
    final_global = global_indicators_data if global_indicators_data else existing_data.get("global_indicators", [])

    # Generate Alpha Decision (use merged data)
    alpha_signal = generate_alpha_signal(final_carry, final_risk)

    # Fetch live FX rate
    live_fx = fetch_live_fx()

    data = {
        "metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "live_fx_rate": live_fx
        },
        "system_status": alpha_signal,
        "carry_trade": final_carry,
        "inflation": final_inflation,
        "risk": final_risk,
        "economy": final_economy,
        "us_stocks": final_us_stocks,
        "global_indicators": final_global
    }


    # Clean NaN values from the data structure
    data = replace_nan_with_none(data)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Data exported to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()

