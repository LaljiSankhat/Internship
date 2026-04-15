#!/bin/bash
# Fix dependency conflicts script

set -e

echo "🔧 Fixing dependency conflicts..."
echo "=================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Upgrade pip
pip install --upgrade pip

# Uninstall conflicting packages
echo "Removing conflicting packages..."
pip uninstall -y torchaudio torchvision transformers huggingface-hub || true

# Reinstall compatible versions
echo "Installing compatible versions..."

# Install huggingface-hub compatible with transformers
pip install "huggingface-hub>=1.3.0,<2.0.0"

# Install transformers compatible with huggingface-hub
pip install "transformers>=4.40.0,<5.0.0"

# Install torchaudio and torchvision compatible with installed torch version
TORCH_VERSION=$(python -c "import torch; print(torch.__version__)" 2>/dev/null || echo "2.4.1")
echo "Detected torch version: $TORCH_VERSION"

# Try to install matching versions
if [[ "$TORCH_VERSION" == "2.4.1"* ]]; then
    echo "Installing torchaudio and torchvision compatible with torch 2.4.1..."
    pip install torchaudio torchvision --no-deps
    # Install dependencies manually
    pip install typing-extensions sympy networkx jinja2 fsspec
elif [[ "$TORCH_VERSION" == "2.10.0"* ]]; then
    echo "Installing torchaudio and torchvision compatible with torch 2.10.0..."
    pip install "torchaudio==2.10.0" "torchvision==0.25.0"
else
    echo "Installing latest compatible torchaudio and torchvision..."
    pip install torchaudio torchvision
fi

# Verify installations
echo ""
echo "Verifying installations..."
python -c "import torch; import torchaudio; import torchvision; import transformers; import huggingface_hub; print(f'✅ torch: {torch.__version__}'); print(f'✅ torchaudio: {torchaudio.__version__}'); print(f'✅ torchvision: {torchvision.__version__}'); print(f'✅ transformers: {transformers.__version__}'); print(f'✅ huggingface-hub: {huggingface_hub.__version__}')"

echo ""
echo "✅ Dependency conflicts resolved!"
