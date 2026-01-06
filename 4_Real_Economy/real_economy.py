import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_banxico_series

# IDs
ID_M1 = 'SF61745' # Billetes y Monedas (Daily Liquidity Proxy)
TICKER_IPC = '^MXX'


def fetch_data():
    print("Fetching Real Economy Data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*2) 
    
    s_start = start_date.strftime('%Y-%m-%d')
    s_end = end_date.strftime('%Y-%m-%d')
    
    # Banxico M1 is Monthly/Daily. Fetching history.
    df_m1 = get_banxico_series(ID_M1, s_start, s_end, "M1")
    print(f"Debug M1: {df_m1.head()}")
    if df_m1.empty:
         print("Debug: M1 Fetch returned empty.")
    
    # IPC
    print("Fetching IPC Data...")
    try:
        ipc_data = yf.download(TICKER_IPC, start=s_start, end=s_end, progress=False)
    except Exception as e:
        print(f"Error fetching IPC download: {e}")
        ipc_data = pd.DataFrame()

    try:
        if not ipc_data.empty:
            ipc_series = ipc_data['Close']
            if isinstance(ipc_series, pd.DataFrame):
                 ipc_series = ipc_series.iloc[:, 0]
            df_ipc = pd.DataFrame(ipc_series)
            df_ipc.columns = ['IPC Index']
            df_ipc.index = pd.to_datetime(df_ipc.index).tz_localize(None)
        else:
            df_ipc = pd.DataFrame()
    except Exception as e:
        print(f"Error processing IPC: {e}")
        df_ipc = pd.DataFrame()
        
    dfs = [df_m1, df_ipc]
    df = pd.concat(dfs, axis=1)
    
    # Ensure M1 column exists to prevent crash
    if 'M1' not in df.columns:
        print("Warning: M1 data missing. Creating empty column.")
        df['M1'] = float('nan')
    
    # Forward fill (M1 has different freq, IPC daily)
    df = df.ffill()
    # df.dropna(inplace=True) # Keep data even if partial
    return df

def analyze_economy(df):
    results = df.copy()
    
    # Normalize to compare divergence
    # Rebase to 100 at start
    if 'M1' in results.columns and 'IPC Index' in results.columns:
        # Use first valid index to avoid NaN if start date has no data
        first_valid_m1 = results['M1'].first_valid_index()
        first_valid_ipc = results['IPC Index'].first_valid_index()
        
        m1_start = results['M1'].loc[first_valid_m1] if first_valid_m1 else 1
        ipc_start = results['IPC Index'].loc[first_valid_ipc] if first_valid_ipc else 1

        results['M1 Normalized'] = (results['M1'] / m1_start) * 100
        results['IPC Normalized'] = (results['IPC Index'] / ipc_start) * 100
        
        results['Divergence'] = results['M1 Normalized'] - results['IPC Normalized']
    
    return results

def plot_analysis(df):
    if 'M1 Normalized' in df.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df['M1 Normalized'], label='M1 Supply (Money)', color='blue')
        plt.plot(df.index, df['IPC Normalized'], label='IPC Index (Stocks)', color='green')
        plt.title('Liquidez vs Bolsa (Dinero Real vs Activos)')
        plt.legend()
        plt.grid(True)
        plt.savefig('m1_vs_ipc.png')
        plt.close()

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    df = fetch_data()
    if df.empty:
        print("No data fetched.")
        return
        
    df_analyzed = analyze_economy(df)
    df_analyzed.to_csv('economy_data.csv')
    print("Data saved to economy_data.csv")
    
    plot_analysis(df_analyzed)
    print("Plots generated: m1_vs_ipc.png")
    
    last = df_analyzed.iloc[-1]
    print("\n--- LATEST SIGNALS ---")
    print(f"Date: {last.name.date()}")
    if 'Divergence' in df_analyzed.columns:
        div = last['Divergence']
        print(f"M1 vs IPC Divergence: {div:.2f} " + ("(HIGH M1 - BUY STOCKS?)" if div > 10 else "(NORMAL)"))


if __name__ == "__main__":
    main()
