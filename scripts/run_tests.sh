#!/usr/bin/env bash
set -e

# Ensure virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment using uv..."
    uv venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install test dependencies (optional)
if [ -f "pyproject.toml" ]; then
    echo "Installing dependencies from pyproject.toml..."
    uv sync --lock --dev --
fi

# Run tests
echo "Running tests with pytest..."
pytest .
