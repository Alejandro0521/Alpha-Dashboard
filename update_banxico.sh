#!/bin/bash
# Alpha Dashboard - Update Banxico Data
# Runs once daily at 11:30 AM

# Get script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================="
echo "Updating Banxico Data - $(date)"
echo "=========================================="

# Run Banxico scripts
python3 1_Carry_Trade/carry_trade.py
python3 2_Inflation_Shield/inflation_shield.py
python3 4_Real_Economy/real_economy.py

# Export to JSON
python3 export_to_json.py

echo "✅ Banxico data updated at $(date)"
echo ""
