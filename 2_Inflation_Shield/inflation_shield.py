import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_banxico_series

# IDs
ID_UDI = 'SP68257'
ID_BONO_M_10 = 'SF43912'
ID_UDIBONO_10 = 'SF3338' 
ID_INPC_MENSUAL = 'SP30578' # Inflation Index Monthly
ID_CETES_28 = 'SF43936' # For Real Rate calculation

def fetch_data():
    print("Fetching Inflation & Real Rate Data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*2) # 2 years for broad view
    
    s_start = start_date.strftime('%Y-%m-%d')
    s_end = end_date.strftime('%Y-%m-%d')
    
    # Fetch
    df_udi = get_banxico_series(ID_UDI, s_start, s_end, "UDI")
    df_bono10 = get_banxico_series(ID_BONO_M_10, s_start, s_end, "Bono M 10y")
    df_udibono10 = get_banxico_series(ID_UDIBONO_10, s_start, s_end, "Udibono 10y")
    
    # Real Rate Data
    df_cetes = get_banxico_series(ID_CETES_28, s_start, s_end, "Cetes 28d")
    # INPC is monthly. 
    df_inpc = get_banxico_series(ID_INPC_MENSUAL, s_start, s_end, "INPC")
    
    # Fallback for Udibono
    if df_udibono10.empty:
         print(f"Warning: Udibono ID {ID_UDIBONO_10} failed. Using nulls.")
         df_udibono10 = pd.DataFrame()
    
    dfs = [df_udi, df_bono10, df_udibono10, df_cetes, df_inpc]
    df = pd.concat(dfs, axis=1)
    
    # Forward fill to daily logic for most rates, but INPC is monthly.
    df = df.ffill()
    df.dropna(inplace=True)
    
    
    return df

def analyze_inflation(df):
    results = df.copy()
    
    # 1. Breakeven
    if 'Bono M 10y' in results.columns and 'Udibono 10y' in results.columns:
        results['Breakeven Inflation'] = results['Bono M 10y'] - results['Udibono 10y']
        
    # 2. UDI Velocity
    if 'UDI' in results.columns:
        results['UDI Velocity (%)'] = results['UDI'].pct_change() * 100

    # 3. Real Rate Ex-Post (Cetes - Annual Inflation)
    # Calculate Annual Inflation first
    if 'INPC' in results.columns:
        # We need YoY change. Shifts approx 365 days? 
        # Refine: INPC is strictly monthly but ffilled. 365 days would be 365 rows if daily.
        # Let's assume daily rows (ffilled).
        results['Inflation YoY'] = results['INPC'].pct_change(periods=360) * 100 # Approx
        
        if 'Cetes 28d' in results.columns:
            results['Real Rate Ex-Post'] = results['Cetes 28d'] - results['Inflation YoY']
    
    return results

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    df = fetch_data()
    if df.empty:
        print("No data fetched.")
        return
        
    df_analyzed = analyze_inflation(df)
    df_analyzed.to_csv('inflation_data.csv')
    print("Data saved to inflation_data.csv")
    
    last = df_analyzed.iloc[-1]
    print("\n--- LATEST SIGNALS ---")
    print(f"Date: {last.name.date()}")
    if 'Breakeven Inflation' in df_analyzed.columns:
        print(f"Breakeven 10y: {last['Breakeven Inflation']:.2f}%")
    if 'Real Rate Ex-Post' in df_analyzed.columns:
        print(f"Real Rate (Cetes - Inflation): {last['Real Rate Ex-Post']:.2f}%")

if __name__ == "__main__":
    main()
