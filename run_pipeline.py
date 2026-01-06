#!/usr/bin/env python3
"""
Alpha Dashboard - Master Data Collection Pipeline
Runs all data collectors in sequence and exports to JSON
"""

import subprocess
import sys
import os
from datetime import datetime

def run_script(script_path, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Script: {script_path}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout per script
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            print(f"❌ ERROR in {description}")
            if result.stderr:
                print(f"Error details:\n{result.stderr}")
            return False
        else:
            print(f"✅ {description} completed successfully")
            return True
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ TIMEOUT: {description} took too long")
        return False
    except Exception as e:
        print(f"❌ EXCEPTION in {description}: {e}")
        return False

def main():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║           ALPHA DASHBOARD - DATA PIPELINE                 ║
    ║         Economic Intelligence Collection System           ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    start_time = datetime.now()
    print(f"Pipeline started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define all data collection scripts
    scripts = [
        ("1_Carry_Trade/carry_trade.py", "Carry Trade Analysis"),
        ("2_Inflation_Shield/inflation_shield.py", "Inflation Shield"),
        ("3_Risk_Thermometer/risk_thermometer.py", "Risk Thermometer"),
        ("4_Real_Economy/real_economy.py", "Real Economy Pulse"),
        ("5_US_Stocks/us_stocks.py", "US Stocks Radar"),
        ("6_Global_Indicators/global_indicators.py", "Global Indicators"),
    ]
    
    results = {}
    
    # Run each data collector
    for script_path, description in scripts:
        full_path = os.path.join(base_dir, script_path)
        if os.path.exists(full_path):
            results[description] = run_script(full_path, description)
        else:
            print(f"⚠️  WARNING: {script_path} not found, skipping...")
            results[description] = False
    
    # Run export to JSON
    print(f"\n{'='*60}")
    print("FINAL STEP: Exporting data to JSON")
    print(f"{'='*60}")
    
    export_path = os.path.join(base_dir, "export_to_json.py")
    if os.path.exists(export_path):
        results["Export to JSON"] = run_script(export_path, "Export to JSON")
    else:
        print("❌ export_to_json.py not found!")
        results["Export to JSON"] = False
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n{'='*60}")
    print("PIPELINE SUMMARY")
    print(f"{'='*60}")
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for task, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{task:.<50} {status}")
    
    print(f"\n{'='*60}")
    print(f"Completed: {success_count}/{total_count} tasks successful")
    print(f"Duration: {duration:.1f} seconds")
    print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    if success_count == total_count:
        print("🎉 All systems operational! Dashboard data is fresh.\n")
        print("📊 Open Web/index.html in your browser to view the dashboard.")
        return 0
    else:
        print(f"⚠️  {total_count - success_count} task(s) failed. Check logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
