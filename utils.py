import requests
import pandas as pd
import os
from datetime import datetime

# Centralized Token - Set BANXICO_TOKEN environment variable
# Get your free token from: https://www.banxico.org.mx/SieAPIRest/service/v1/
BANXICO_TOKEN = os.environ.get('BANXICO_TOKEN')
if not BANXICO_TOKEN:
    print("⚠️  WARNING: BANXICO_TOKEN environment variable not set!")
    print("   Get your token from: https://www.banxico.org.mx/SieAPIRest/service/v1/")

def get_banxico_series(series_id, start_date=None, end_date=None, description="Data"):
    """
    Fetches historical data for a given series ID.
    If dates are not provided, it fetches 'oportuno' (latest).
    Returns a Pandas DataFrame with 'Date' and 'Value'.
    """
    headers = {
        "Bmx-Token": BANXICO_TOKEN,
        "Accept": "application/json"
    }

    if start_date and end_date:
        url = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{series_id}/datos/{start_date}/{end_date}"
    else:
        url = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{series_id}/datos/oportuno"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        series_data = data['bmx']['series'][0]
        if 'datos' in series_data:
            records = []
            for d in series_data['datos']:
                try:
                    val = float(d['dato'])
                    date = d['fecha']
                    records.append({'Date': date, description: val})
                except ValueError:
                    # Handle cases where value might be 'N/E'
                    continue
            
            df = pd.DataFrame(records)
            if not df.empty:
                df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
                df.set_index('Date', inplace=True)
                df.sort_index(inplace=True)
            return df
        else:
            print(f"No data found for {series_id}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error fetching {series_id}: {e}")
        return pd.DataFrame()
