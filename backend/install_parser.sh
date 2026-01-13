#!/bin/bash
# Script to install parse_hh_data parser

echo "Installing parse_hh_data library..."
pip install git+https://github.com/arinaaageeva/parse_hh_data.git

if [ $? -eq 0 ]; then
    echo "✓ parse_hh_data installed successfully"
    echo "The system will now use the parser instead of mock data"
else
    echo "✗ Failed to install parse_hh_data"
    echo "The system will continue using mock data"
    exit 1
fi
