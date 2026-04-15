#!/bin/bash
# Setup script for PersonaPlex Voice Agent

set -e

echo "🎙️ PersonaPlex Voice Agent Setup"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip

# Check if PersonaPlex is cloned
if [ ! -d "personaplex" ]; then
    echo "Cloning PersonaPlex repository..."
    git clone https://github.com/NVIDIA/personaplex.git
fi

# Install PersonaPlex FIRST (it will install torch and other core dependencies)
echo "Installing PersonaPlex (this will install torch and core dependencies)..."
cd personaplex
pip install moshi/.
cd ..

# Now install compatible versions of torchaudio and torchvision to match PersonaPlex's torch
echo "Installing compatible torchaudio and torchvision..."
pip install torchaudio torchvision --upgrade

# Install other Python dependencies
echo "Installing other Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your HF_TOKEN"
    echo "   Get your token from: https://huggingface.co/settings/tokens"
    echo "   Accept the model license at: https://huggingface.co/nvidia/personaplex-7b-v1"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your HF_TOKEN"
echo "2. Run: python run_server.py"
echo "3. Open: http://localhost:8998/client"
