import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_banxico_series

# IDs
ID_TIIE_FONDEO = 'SF60648'
ID_TIIE_28 = 'SF61745'
ID_CETES_28 = 'SF43936'
ID_CETES_91 = 'SF43939'
ID_CETES_364 = 'SF43945' # Verified typical ID, if fails we handle nulls

def fetch_data():
    print("Fetching Banxico Data...")
    # Fetch last 360 days to have enough context
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    s_start = start_date.strftime('%Y-%m-%d')
    s_end = end_date.strftime('%Y-%m-%d')
    
    df_fondeo = get_banxico_series(ID_TIIE_FONDEO, s_start, s_end, "TIIE Fondeo")
    df_tiie28 = get_banxico_series(ID_TIIE_28, s_start, s_end, "TIIE 28d")
    df_cetes28 = get_banxico_series(ID_CETES_28, s_start, s_end, "Cetes 28d")
    df_cetes364 = get_banxico_series(ID_CETES_364, s_start, s_end, "Cetes 364d")
    
    # Merge Banxico Data
    dfs = [df_fondeo, df_tiie28, df_cetes28, df_cetes364]
    df_mx = pd.concat(dfs, axis=1)
    
    print("Fetching External Data (FED Rates)...")
    # Using 13 Week Treasury Bill (^IRX) as proxy for short term risk-free rate
    fed_data = yf.download("^IRX", start=s_start, end=s_end, progress=False)
    if not fed_data.empty:
        # yfinance returns multi-index columns sometimes, handle 'Close'
        try:
            fed_series = fed_data['Close']
            if isinstance(fed_series, pd.DataFrame):
                 fed_series = fed_series.iloc[:, 0]
            
            # Reindex to match MX data logic (fill weekends or just join)
            # We will join on index (Date)
            fed_df = pd.DataFrame(fed_series)
            fed_df.columns = ['FED Rate (Proxy 13W)']
            fed_df.index = pd.to_datetime(fed_df.index).tz_localize(None)
            
            df_mx = df_mx.join(fed_df, how='outer')
        except Exception as e:
            print(f"Error processing FED data: {e}")
            
    # Fill Forward for missing weekends where applicable (rates usually hold)
    df_mx = df_mx.ffill()
    df_mx.dropna(inplace=True) # Drop beginning NaNs
    
    
    return df_mx

def analyze_carry_trade(df):
    results = df.copy()
    
    # 1. Liquidity Spread: TIIE 28d - TIIE Fondeo
    results['Liquidity Spread'] = results['TIIE 28d'] - results['TIIE Fondeo']
    
    # 2. Yield Curve: Cetes 364 - Cetes 28 (Inversion check)
    if 'Cetes 364d' in results.columns and 'Cetes 28d' in results.columns:
        results['Yield Curve Slope'] = results['Cetes 364d'] - results['Cetes 28d']
        
    # 3. Carry Spread: TIIE 28d - FED Rate
    if 'FED Rate (Proxy 13W)' in results.columns:
        results['Carry Spread (bp)'] = (results['TIIE 28d'] - results['FED Rate (Proxy 13W)']) * 100
        
    return results

def plot_analysis(df):
    # Plot Liquidity Spread
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['Liquidity Spread'], label='Spread TIIE 28d - Fondeo')
    plt.title('Liquidity Spread (Market Stress Proxy)')
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.3)
    plt.legend()
    plt.grid(True)
    plt.savefig('liquidity_spread.png')
    plt.close()
    
    # Plot Yield Curve
    if 'Yield Curve Slope' in df.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df['Yield Curve Slope'], label='Slope (Cetes 364 - 28)', color='orange')
        plt.title('Yield Curve Slope (Recession Signal if < 0)')
        plt.axhline(y=0, color='r', linestyle='--', linewidth=2)
        plt.fill_between(df.index, df['Yield Curve Slope'], 0, where=(df['Yield Curve Slope'] < 0), color='red', alpha=0.3)
        plt.legend()
        plt.grid(True)
        plt.savefig('yield_curve.png')
        plt.close()
        
    # Plot Carry Spread
    if 'Carry Spread (bp)' in df.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df['Carry Spread (bp)'], label='MXN-USD Spread (bp)', color='green')
        plt.title('Carry Trade Attractiveness (Spread vs FED)')
        plt.axhline(y=400, color='r', linestyle='--', label='Critical Level (400bp)')
        plt.legend()
        plt.grid(True)
        plt.savefig('carry_spread.png')
        plt.close()

def save_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

def main():
    df = fetch_data()
    if df.empty:
        print("No data fetched.")
        return
        
    df_analyzed = analyze_carry_trade(df)
    
    # Save Data
    df_analyzed.to_csv(save_path('carry_trade_data.csv'))
    print(f"Data saved to {save_path('carry_trade_data.csv')}")
    
    # Plot
    # Update plot_analysis to take a directory or handle paths inside
    # Ideally refactor plot_analysis to return figures or save using save_path
    # For quick fix, let's just change CWD or pass paths.
    # Passing paths is cleaner but requires modifying plot_analysis signature.
    # Let's simple change plot_analysis to save using save_path provided globally or passed.
    
    plot_analysis(df_analyzed) # This still saves to CWD. Let's patch imports/functions.
    
    # Actually, easiest is to just chdir to script dir at start of main
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    df_analyzed.to_csv('carry_trade_data.csv')
    print("Data saved to carry_trade_data.csv")
    
    plot_analysis(df_analyzed)
    print("Plots generated: liquidity_spread.png, yield_curve.png, carry_spread.png")

    # Latest Signals
    last = df_analyzed.iloc[-1]
    print("\n--- LATEST SIGNALS ---")
    print(f"Date: {last.name.date()}")
    print(f"Liquidity Spread: {last['Liquidity Spread']:.4f} " + ("(STRESS)" if last['Liquidity Spread'] > 0.5 else "(OK)"))
    
    if 'Yield Curve Slope' in df_analyzed.columns:
        print(f"Yield Curve Slope: {last['Yield Curve Slope']:.4f} " + ("(INVERTED - RECESSION WARNING)" if last['Yield Curve Slope'] < 0 else "(NORMAL)"))
        
    if 'Carry Spread (bp)' in df_analyzed.columns:
        print(f"Carry Spread: {last['Carry Spread (bp)']:.0f} bp " + ("(LOW ATTRACTIVENESS)" if last['Carry Spread (bp)'] < 400 else "(HEALTHY)"))


if __name__ == "__main__":
    main()
