#!/bin/bash
# Quick Start Script for Laboratory QC System
# This script helps new users get started quickly

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BOLD}${BLUE}"
echo "========================================================================"
echo "Laboratory Quality Control & Sigma Abnormality Detection System"
echo "Quick Start Setup"
echo "========================================================================"
echo -e "${NC}"

# Check Python version
echo -e "${BOLD}Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "\n${BOLD}Creating virtual environment...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "\n${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo -e "\n${BOLD}Activating virtual environment...${NC}"
source .venv/bin/activate

# Upgrade pip
echo -e "\n${BOLD}Upgrading pip...${NC}"
pip install --upgrade pip --quiet

# Install dependencies
echo -e "\n${BOLD}Installing dependencies...${NC}"
echo "This may take a few minutes..."
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓${NC} All dependencies installed"

# Run quick test
echo -e "\n${BOLD}Running quick test...${NC}"
python3 -c "
from lab_qc_analysis import LabQCAnalysis
qc = LabQCAnalysis(seed=42)
data = qc.generate_qc_data('creatinine', n_days=1)
print('✓ System test passed!')
"

echo -e "\n${BOLD}${GREEN}Setup complete!${NC}\n"

echo -e "${BOLD}What would you like to do?${NC}"
echo "1) Run complete QC analysis"
echo "2) Try interactive demo"
echo "3) Start real-time web dashboard"
echo "4) Start real-time desktop monitor"
echo "5) View quick reference"
echo "6) Exit"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo -e "\n${BOLD}Running complete QC analysis...${NC}"
        python3 lab_qc_analysis.py
        ;;
    2)
        echo -e "\n${BOLD}Starting interactive demo...${NC}"
        echo "Available modes: levey, westgard, sigma, comparison, correlation, statistical, advanced, realtime"
        read -p "Enter mode (or press Enter for menu): " mode
        if [ -z "$mode" ]; then
            python3 lab_qc_demo.py
        else
            python3 lab_qc_demo.py "$mode"
        fi
        ;;
    3)
        echo -e "\n${BOLD}Starting web dashboard...${NC}"
        echo -e "${YELLOW}Opening browser to http://localhost:8050${NC}"
        python3 realtime_qc_monitor.py
        ;;
    4)
        echo -e "\n${BOLD}Starting desktop monitor...${NC}"
        python3 realtime_qc_desktop.py
        ;;
    5)
        echo -e "\n${BOLD}Quick Reference:${NC}"
        python3 quick_reference.py
        ;;
    6)
        echo -e "\n${GREEN}Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo -e "\n${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "\n${BOLD}${GREEN}Done!${NC}"
echo -e "Check the ${BOLD}results/${NC} directory for output files."
echo ""
