#!/bin/bash
# Alpha Dashboard - Update Market Data (Stocks & Global Indicators)
# Runs hourly during market hours (9 AM - 3 PM, Mon-Fri)

# Get script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================="
echo "Updating Market Data - $(date)"
echo "=========================================="

# Run market scripts
python3 5_US_Stocks/us_stocks.py
python3 6_Global_Indicators/global_indicators.py
python3 3_Risk_Thermometer/risk_thermometer.py

# Export to JSON
python3 export_to_json.py

echo "✅ Market data updated at $(date)"
echo ""
