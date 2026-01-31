#!/bin/bash
# Installation script for Bitcoin Trading Framework

echo "======================================================"
echo "Installing Bitcoin Trading Framework Dependencies"
echo "======================================================"
echo ""

# Check if pip is available
if ! command -v pip &> /dev/null
then
    echo "ERROR: pip is not installed. Please install Python and pip first."
    exit 1
fi

echo "Installing required packages..."
pip install -r requirements.txt

echo ""
echo "======================================================"
echo "Installation Complete!"
echo "======================================================"
echo ""
echo "To verify the installation, run:"
echo "  PYTHONPATH=. python examples/backtest_sma_example.py"
echo ""
echo "For more information, see:"
echo "  - README.md for detailed documentation"
echo "  - QUICKSTART.md for a 5-minute tutorial"
echo ""
