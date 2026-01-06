import pandas as pd
import json
import os
import glob
import ast
from datetime import datetime
import yfinance as yf

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Root is one level up from 'Alpha_Dashboard/Web/..' if we run this script from somewhere else.
# Let's assume this script sits in Alpha_Dashboard root for easy access to subfolders.
# We will save it in Alpha_Dashboard/export_to_json.py

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
        df = pd.read_csv(path)
        # Parse price_history column from string to list if it exists
        if 'price_history' in df.columns:
            df['price_history'] = df['price_history'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) and isinstance(x, str) else x)
        # Pandas to_json handles NaNs as nulls correctly by default
        json_str = df.to_json(orient='records')
        return json.loads(json_str)
    return []


def fetch_live_fx():
    """Fetch real-time USD/MXN rate from Twelve Data (primary) and Yahoo (backup)"""
    
    # Source 1: Twelve Data (800 req/day free tier, updates every minute)
    # Get your free API key from: https://twelvedata.com/
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
    
    # Source 2: Yahoo Finance (fallback)
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
    # Default Signal
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
    
    # 1. Extraction
    try:
        spread = float(last_carry.get('Carry Spread (bp)', 0))
        vol_z = float(last_risk.get('Vol_Z_Score', 0))
        upper_band = float(last_risk.get('Upper_Band', 0))
        close_fx = float(last_risk.get('Close', 0)) # Using 'Close' from YF, was 'Tipo de Cambio FIX'
    except:
        return signal

    # 2. Logic
    # Scenario A: Strong Carry (Long MXN)
    # Spread > 500bps AND Volatility is Normal (Z < 1)
    if spread > 500 and vol_z < 1.5:
        signal["status"] = "🟢 RIESGO ACEPTABLE"
        signal["action"] = "LONG MXN (CARRY)"
        signal["probability"] = "68%"
        # Stop Loss: slightly above Upper Bollinger Band (Explosion risk) or recent high
        sl = upper_band * 1.01 if upper_band > 0 else close_fx * 1.02
        signal["stop_loss"] = f"${sl:.2f}"
        signal["reason"] = f"Spread {spread:.0f}pbs + Volatilidad Baja (Z={vol_z:.1f})"
        
    # Scenario B: Risk OFF (Short MXN / Buy USD)
    # Spread compressing (<400) OR Volatility Exploding (Z > 2)
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

def main():
    # Load Data
    carry_data = load_and_clean(CSV_PATHS["carry_trade"])
    inflation_data = load_and_clean(CSV_PATHS["inflation"])
    risk_data = load_and_clean(CSV_PATHS["risk"])
    economy_data = load_and_clean(CSV_PATHS["economy"])
    us_stocks_data = load_and_clean(CSV_PATHS["us_stocks"])
    global_indicators_data = load_and_clean(CSV_PATHS["global_indicators"])
    
    # Generate Alpha Decision
    alpha_signal = generate_alpha_signal(carry_data, risk_data)

    # Fetch live FX rate
    live_fx = fetch_live_fx()
    
    data = {
        "metadata": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "live_fx_rate": live_fx
        },
        "system_status": alpha_signal,
        "carry_trade": carry_data,
        "inflation": inflation_data,
        "risk": risk_data,
        "economy": economy_data,
        "us_stocks": us_stocks_data,
        "global_indicators": global_indicators_data
    }
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Data exported to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()

