#!/bin/bash
# Alpha Dashboard - Cron Job Installer
# Configures automatic updates for the dashboard

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║        ALPHA DASHBOARD - CRON INSTALLER                   ║"
echo "║        Automatic Data Update Configuration                ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get absolute path to this directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "📂 Dashboard location: $SCRIPT_DIR"
echo ""

# Make scripts executable
echo "🔧 Making update scripts executable..."
chmod +x "$SCRIPT_DIR/update_banxico.sh"
chmod +x "$SCRIPT_DIR/update_markets.sh"
chmod +x "$SCRIPT_DIR/run_pipeline.py"
echo "✅ Scripts are now executable"
echo ""

# Create cron jobs file
CRON_FILE="/tmp/alpha_dashboard_cron.txt"

echo "📝 Creating cron configuration..."
cat > "$CRON_FILE" << EOF
# Alpha Dashboard - Automatic Data Updates
# Configuration: Balanced (recommended for most users)

# ========================================
# BANXICO DATA - Once daily at 11:30 AM
# ========================================
30 11 * * * $SCRIPT_DIR/update_banxico.sh >> $SCRIPT_DIR/logs/banxico.log 2>&1

# ========================================
# MARKET DATA - Hourly during market hours (9 AM - 3 PM, Monday-Friday)
# ========================================
0 9-15 * * 1-5 $SCRIPT_DIR/update_markets.sh >> $SCRIPT_DIR/logs/markets.log 2>&1

# ========================================
# END OF ALPHA DASHBOARD CRON JOBS
# ========================================
EOF

echo "✅ Cron configuration created"
echo ""

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"
echo "📁 Created logs directory"
echo ""

# Show cron jobs to user
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Cron jobs to be installed:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "$CRON_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ask for confirmation
echo "⚠️  IMPORTANT: This will add cron jobs to your system."
echo ""
echo "Schedule:"
echo "  • Banxico data:  Daily at 11:30 AM"
echo "  • Market data:   Every hour from 9 AM to 3 PM (Mon-Fri)"
echo ""
read -p "Do you want to install these cron jobs? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Backup existing crontab
    echo "💾 Backing up existing crontab..."
    crontab -l > "$SCRIPT_DIR/crontab_backup_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || true
    
    # Install new cron jobs
    echo "⚙️  Installing cron jobs..."
    (crontab -l 2>/dev/null; cat "$CRON_FILE") | crontab -
    
    echo ""
    echo "✅ Cron jobs installed successfully!"
    echo ""
    echo "📊 Dashboard will now update automatically:"
    echo "   • Banxico: 11:30 AM daily"
    echo "   • Markets: Every hour 9 AM-3 PM (Mon-Fri)"
    echo ""
    echo "📝 Logs will be saved to: $SCRIPT_DIR/logs/"
    echo ""
    echo "To view installed cron jobs, run: crontab -l"
    echo "To remove cron jobs, run: crontab -e (and delete the Alpha Dashboard section)"
    echo ""
    
    # Run initial update
    read -p "Run initial data update now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        echo "🚀 Running initial update..."
        python3 "$SCRIPT_DIR/run_pipeline.py"
    fi
else
    echo ""
    echo "❌ Installation cancelled."
    echo ""
    echo "To install manually, run:"
    echo "  crontab -e"
    echo ""
    echo "Then add these lines:"
    cat "$CRON_FILE"
fi

# Cleanup
rm -f "$CRON_FILE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
