#!/bin/sh
# Create DeckTune release zip with proper Unix permissions
# Run after building frontend with npm run build

set -e

echo "=== DeckTune Release Packager ==="
echo ""

# Get version from plugin.json
VERSION=$(grep '"version"' plugin.json | cut -d'"' -f4)
echo "Packaging DeckTune v$VERSION"
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf release/DeckTune
rm -f release/DeckTune.zip
rm -f release/DeckTune-v*.zip
mkdir -p release/DeckTune

# Check if dist/index.js exists
if [ ! -f "dist/index.js" ]; then
    echo "Error: dist/index.js not found. Run 'npm run build' first."
    exit 1
fi

# Copy files to release directory
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

# Copy defaults directory if it exists
if [ -d "defaults" ]; then
    cp -r defaults release/DeckTune/
fi

# Copy shell scripts
cp install.sh release/DeckTune/
cp setup-sudo.sh release/DeckTune/

# Set executable permissions
echo "Setting executable permissions..."
chmod +x release/DeckTune/bin/*
chmod +x release/DeckTune/*.sh

# Fix line endings for shell scripts (CRLF -> LF)
echo "Fixing line endings for shell scripts..."
for script in release/DeckTune/*.sh; do
    if [ -f "$script" ]; then
        sed -i 's/\r$//' "$script" 2>/dev/null || true
        echo "  Fixed: $(basename "$script")"
    fi
done

# Create zip archive with proper Unix paths
echo "Creating zip archive..."
cd release
zip -r "DeckTune-v${VERSION}.zip" DeckTune/ -x "*.pyc" "*/__pycache__/*"
cp "DeckTune-v${VERSION}.zip" DeckTune.zip

# Calculate size
SIZE=$(du -h "DeckTune-v${VERSION}.zip" | cut -f1)
echo ""
echo "=== Package Complete ==="
echo "Version: v$VERSION"
echo "Output: release/DeckTune-v${VERSION}.zip"
echo "Size: $SIZE"
echo ""
echo "To install on Steam Deck:"
echo "1. Copy DeckTune-v${VERSION}.zip to Steam Deck"
echo "2. Enable Developer Mode in Decky Loader settings"
echo "3. Install from zip file"
echo ""
