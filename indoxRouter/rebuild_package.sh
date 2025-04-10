#!/bin/bash
# Script to rebuild the indoxRouter package for local development and testing

echo "Rebuilding indoxRouter package..."

# Clean up old build artifacts
rm -rf build/ dist/ indoxrouter.egg-info/

# Build the package
python setup.py sdist bdist_wheel

# Check if the build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful"
    echo "Package files:"
    ls -la dist/
    
    echo ""
    echo "To install the package locally, run:"
    echo "pip install -e ."
    echo ""
    echo "To install the development package from dist, run:"
    echo "pip install dist/*.whl"
    echo ""
else
    echo "❌ Build failed"
    exit 1
fi 