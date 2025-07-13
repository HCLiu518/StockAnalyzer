#!/bin/bash

echo "🐍 Activating virtual environment..."
source venv/bin/activate

echo "🚀 Running main.py..."
python ./src/main.py

echo "🧹 Deactivating virtual environment..."
deactivate
