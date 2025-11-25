#!/bin/bash
# Development installation script for PyDevToolkit MagicCLI

set -e

echo "🚀 Setting up PyDevToolkit MagicCLI development environment..."

# Check if Python 3.7+ is available
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+' || echo "0.0")
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.7+ is required. Found version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install the package in development mode
echo "📥 Installing PyDevToolkit MagicCLI in development mode..."
pip install -e ".[dev,test]"

# Install pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

# Create logs directory if it doesn't exist
mkdir -p logs

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "To activate the environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the application:"
echo "  magic"
echo "  # or"
echo "  python src/main.py"
echo ""
echo "To run tests:"
echo "  make test"
echo "  # or"
echo "  python -m pytest tests/"
echo ""