# Alpha Dashboard - Economic Intelligence Platform

![Status](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 📊 Overview

Alpha Dashboard is a comprehensive economic intelligence platform that provides real-time market analysis and trading signals for Mexican financial markets. The system combines data from Banxico (Bank of Mexico), Yahoo Finance, and other market APIs to generate actionable insights across four key analytical pillars.

## 🎯 Key Features

### Four Analytical Pillars

1. **💵 Carry Trade Engine**
   - TIIE 28d vs FED Rate spread analysis
   - Liquidity spread monitoring (stress indicators)
   - Yield curve inversion detection
   - Target: >400bp spread for healthy carry trades

2. **🔥 Inflation Shield**
   - Breakeven inflation expectations (10-year)
   - Real rate calculations (Cetes - Inflation)
   - UDI velocity tracking
   - Banxico inflation target monitoring

3. **🌡️ Risk Thermometer**
   - USD/MXN volatility analysis
   - Bollinger Bands for overbought/oversold detection
   - Historical period switching (30/90/365 days)
   - Z-score volatility metrics

4. **🏭 Real Economy Pulse**
   - M1 Money Supply vs IPC Stock Index divergence
   - Liquidity vs asset price correlation
   - Normalized trend analysis

### Global Market Indicators

- **VIX** - S&P 500 Volatility Index
- **S&P 500** - US Stock Market Benchmark
- **Nasdaq** - Technology Index
- **WTI Oil** - Crude Oil Prices
- **Gold** - Safe Haven Asset

### US Stock Radar

Technical analysis for the "Magnificent 7":
- Apple (AAPL)
- Microsoft (MSFT)
- Alphabet (GOOGL)
- Amazon (AMZN)
- Nvidia (NVDA)
- Meta (META)
- Tesla (TSLA)

Includes RSI, SMA crossovers, and 30-day price sparklines.

## 🏗️ Architecture

```
Alpha_Dashboard/
├── 1_Carry_Trade/          # Carry trade analysis scripts
├── 2_Inflation_Shield/     # Inflation & real rates
├── 3_Risk_Thermometer/     # FX volatility analysis
├── 4_Real_Economy/         # M1 vs IPC analysis
├── 5_US_Stocks/            # Magnificent 7 stock analysis
├── 6_Global_Indicators/    # VIX, S&P, Oil, Gold data
├── Dashboard/              # Streamlit web interface
├── Web/                    # Static HTML/JS dashboard
│   ├── index.html
│   ├── css/style.css
│   ├── js/dashboard.js
│   └── data/dashboard_data.json
├── export_to_json.py       # Data consolidation pipeline
└── utils.py                # Banxico API utilities
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Modern web browser (for static dashboard)
- Banxico API token (stored in `BANXICO_TOKEN` environment variable or `utils.py`)

### Installation

1. **Clone or download the repository**

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up Banxico API token**:
   - Get your free token from [Banxico SIE API](https://www.banxico.org.mx/SieAPIRest/service/v1/)
   - Set environment variable: `export BANXICO_TOKEN=your_token_here`
   - Or update the token in `utils.py`

### Running the System

#### Option 1: Static Web Dashboard (Recommended)

1. **Collect data from all sources**:
```bash
# Run individual modules
python 1_Carry_Trade/carry_trade.py
python 2_Inflation_Shield/inflation_shield.py
python 3_Risk_Thermometer/risk_thermometer.py
python 4_Real_Economy/real_economy.py
python 5_US_Stocks/us_stocks.py
python 6_Global_Indicators/global_indicators.py
```

2. **Export data to JSON**:
```bash
python export_to_json.py
```

3. **Open the dashboard**:
```bash
# Simply open in your browser
open Web/index.html
```

The dashboard auto-refreshes every 60 seconds.

#### Option 2: Streamlit Dashboard

```bash
cd Dashboard
streamlit run app.py
```

Navigate to `http://localhost:8501` in your browser.

## 📡 Data Sources

- **Banxico SIE API**: Mexican economic indicators (TIIE, Cetes, INPC, M1, UDI, etc.)
- **Yahoo Finance**: Stock prices, indices, FX rates
- **Twelve Data API**: Real-time USD/MXN quotes (800 requests/day free tier)

## 🎨 Web Dashboard Features

### Interactive Elements

- **Smart Tooltips**: Hover over `?` icons for detailed explanations
- **Period Selectors**: Switch between 30/90/365 day views for historical charts
- **Alpha Signal Boxes**: Click for deep-dive analysis modals
- **Global Indicator Modals**: Click any global indicator for professional charts
- **Mini Sparklines**: 30-day trend visualizations on stock and indicator cards

### Mobile Responsive

- Optimized layout for tablets and smartphones
- Touch-friendly tooltips and modals
- Centered, professional design

## 🔧 Configuration

### Updating Refresh Rate

Edit `Web/index.html` line 7:
```html
<meta http-equiv="refresh" content="60">  <!-- Change 60 to desired seconds -->
```

### Adding New Stocks

Edit `5_US_Stocks/us_stocks.py`:
```python
TICKERS = ["AAPL", "MSFT", "YOUR_TICKER"]
COMPANY_NAMES = {
    "YOUR_TICKER": "Company Name"
}
```

### Custom API Keys

- **Banxico**: Set `BANXICO_TOKEN` in environment or `utils.py`
- **Twelve Data**: Update `TWELVE_DATA_API_KEY` in `export_to_json.py`

## 📈 Signal Interpretation

### Carry Trade Signals

- **🟢 RIESGO ACEPTABLE**: Spread >500bp AND low volatility → Long MXN
- **🟡 PRECAUCIÓN**: Mixed conditions → Maintain/Hedge
- **🔴 RIESGO ALTO**: Spread <400bp OR vol spike → Short MXN (Buy USD)

### Stock Signals

- **COMPRAR**: Golden Cross (SMA50 > SMA200)
- **VENDER**: Death Cross (SMA50 < SMA200)
- **SOBRECOMPRA**: RSI > 75
- **SOBREVENTA**: RSI < 25

## 🛠️ Troubleshooting

### Common Issues

**"No module named 'pandas'"**
```bash
pip install -r requirements.txt
```

**"Banxico API returns 401"**
- Verify your API token is correct
- Check token hasn't expired

**"Data not updating in dashboard"**
- Ensure `export_to_json.py` ran successfully
- Check `Web/data/dashboard_data.json` exists and has recent timestamp

**Deprecated pandas warnings**
- This has been fixed in the latest version
- All `fillna(method='ffill')` replaced with `ffill()`

## 📝 License

MIT License - Feel free to use and modify for your own trading/analysis needs.

## ⚠️ Disclaimer

**This software is for educational and informational purposes only.** 

- Not financial advice
- Markets are inherently risky
- Past performance does not guarantee future results
- Always do your own research (DYOR)
- Consider consulting a licensed financial advisor

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional technical indicators
- More global markets
- Machine learning signals
- Automated trading integrations (use with caution!)
- Better mobile UI

## 📧 Support

For issues or questions, please review the code comments and ensure all dependencies are properly installed.

---

**Built with ❤️ for Mexican market traders and analysts**

*Last updated: January 2026*
