#!/bin/bash
# Build DeckTune release for Decky Loader
# This script should be run in WSL or Linux environment

set -e

echo "=== DeckTune Release Builder ==="
echo ""

# Get project root directory
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# Get version from plugin.json
VERSION=$(grep '"version"' plugin.json | cut -d'"' -f4)
echo "Building DeckTune v$VERSION"
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf release/DeckTune
rm -f release/DeckTune.zip
rm -f release/DeckTune-v*.zip
mkdir -p release/DeckTune

# Build frontend
echo ""
echo "Building frontend..."

npm install
npm run build

# Check if dist/index.js was created
if [ ! -f "dist/index.js" ]; then
    echo "Error: dist/index.js not found after build"
    exit 1
fi

echo "Frontend build complete: dist/index.js"

# Copy files to release directory
echo ""
echo "Copying files to release directory..."

# Required files per Decky Loader documentation
cp plugin.json release/DeckTune/
cp main.py release/DeckTune/
cp LICENSE release/DeckTune/
cp package.json release/DeckTune/
cp README.md release/DeckTune/
cp CHANGELOG.md release/DeckTune/

# Copy dist directory
mkdir -p release/DeckTune/dist
cp dist/index.js release/DeckTune/dist/

# Copy backend directory
cp -r backend release/DeckTune/

# Copy bin directory (binaries)
cp -r bin release/DeckTune/

# Copy defaults directory if exists
if [ -d "defaults" ]; then
    cp -r defaults release/DeckTune/
fi

# Copy shell scripts
cp install.sh release/DeckTune/
cp setup-sudo.sh release/DeckTune/

# Set executable permissions
echo ""
echo "Setting executable permissions..."
chmod +x release/DeckTune/bin/*
chmod +x release/DeckTune/*.sh

# Fix line endings for shell scripts (CRLF -> LF)
echo ""
echo "Fixing line endings for shell scripts..."
for script in release/DeckTune/*.sh; do
    if [ -f "$script" ]; then
        sed -i 's/\r$//' "$script" 2>/dev/null || true
        echo "  Fixed: $(basename $script)"
    fi
done

# Create zip archive with proper Unix paths
echo ""
echo "Creating zip archive..."
cd release
zip -r "DeckTune-v${VERSION}.zip" DeckTune/ -x "*.pyc" "*/__pycache__/*"
cp "DeckTune-v${VERSION}.zip" DeckTune.zip

# Calculate size
SIZE=$(du -h "DeckTune-v${VERSION}.zip" | cut -f1)
echo ""
echo "=== Build Complete ==="
echo "Version: v$VERSION"
echo "Output: release/DeckTune-v${VERSION}.zip"
echo "Size: $SIZE"
echo ""
echo "To install on Steam Deck:"
echo "1. Copy DeckTune-v${VERSION}.zip to Steam Deck"
echo "2. Enable Developer Mode in Decky Loader settings"
echo "3. Install from zip file"
echo ""
