#!/bin/bash

echo "📦 Checking for Homebrew..."
if ! command -v brew &>/dev/null; then
    echo "🍺 Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew is already installed."
fi

echo "🐍 Checking for Python 3..."
if ! command -v python3 &>/dev/null; then
    echo "📥 Installing Python 3 via Homebrew..."
    brew install python
else
    echo "✅ Python 3 is already installed."
fi

echo "🧪 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "⬆️ Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing required packages..."
pip install python-dotenv requests pandas gspread oauth2client google-api-python-client google-auth-httplib2 google-auth-oauthlib

echo "✅ Setup complete!"
echo "To activate the virtual environment later, run:"
echo "source venv/bin/activate"
