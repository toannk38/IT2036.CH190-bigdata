#!/bin/bash

# Price Data Initialization Setup Script
# This script helps set up and run the price data initialization

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "scripts/init_price_data.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Price Data Initialization Setup"
echo "=================================="

# Check Python environment
print_status "Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check required packages
print_status "Checking required packages..."
python3 -c "import vnstock, pymongo, pandas" 2>/dev/null || {
    print_warning "Some required packages may be missing"
    print_status "Installing requirements..."
    pip install -r requirements.txt
}

# Check if MongoDB is running
print_status "Checking MongoDB connection..."
python3 -c "
import sys
sys.path.append('src')
from config import config
from pymongo import MongoClient
try:
    client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print('MongoDB connection successful')
except Exception as e:
    print(f'MongoDB connection failed: {e}')
    sys.exit(1)
" || {
    print_error "Cannot connect to MongoDB. Please ensure it's running."
    print_status "You can start MongoDB using: docker-compose up -d mongodb"
    exit 1
}

print_success "Environment checks passed!"

# Show menu
echo ""
print_status "Choose an initialization option:"
echo "1. Initialize all VN30 symbols (1 year, 1-minute data) - RECOMMENDED"
echo "2. Initialize specific symbols"
echo "3. Initialize with custom parameters"
echo "4. Quick test (5 symbols, 7 days, 1-hour data)"
echo "5. Verify existing data"
echo "6. Exit"

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        print_status "Initializing all VN30 symbols with 1 year of 1-minute data..."
        print_warning "This will take a significant amount of time and storage space!"
        read -p "Continue? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            python3 scripts/init_price_data.py --load-symbols --days 365 --interval 1m --output results_full_init.json
        else
            print_status "Operation cancelled"
        fi
        ;;
    2)
        read -p "Enter symbols (comma-separated, e.g., VNM,VIC,HPG): " symbols
        read -p "Enter number of days (default 30): " days
        days=${days:-30}
        read -p "Enter interval (1m/5m/15m/30m/1h/1d, default 1m): " interval
        interval=${interval:-1m}
        
        python3 scripts/init_price_data.py --symbols "$symbols" --days "$days" --interval "$interval"
        ;;
    3)
        read -p "Enter symbols (leave empty for all): " symbols
        read -p "Enter number of days: " days
        read -p "Enter interval (1m/5m/15m/30m/1h/1d): " interval
        
        cmd="python3 scripts/init_price_data.py --days $days --interval $interval"
        if [ ! -z "$symbols" ]; then
            cmd="$cmd --symbols $symbols"
        fi
        
        eval $cmd
        ;;
    4)
        print_status "Running quick test initialization..."
        python3 scripts/init_price_data.py --symbols "VNM,VIC,HPG,FPT,GAS" --days 7 --interval 1h --load-symbols
        ;;
    5)
        print_status "Verifying existing data..."
        python3 scripts/verify_price_data.py
        ;;
    6)
        print_status "Exiting..."
        exit 0
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Offer to verify data after initialization
if [[ $choice =~ ^[1-4]$ ]]; then
    echo ""
    read -p "Would you like to verify the initialized data? (y/N): " verify
    if [[ $verify =~ ^[Yy]$ ]]; then
        print_status "Running data verification..."
        python3 scripts/verify_price_data.py
    fi
fi

print_success "Setup completed!"