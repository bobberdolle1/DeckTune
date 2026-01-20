#!/bin/sh
# Build DeckTune release for Decky Loader
# Files must be in ZIP ROOT, not in subdirectory

set -e

echo "=== DeckTune Decky Release Builder ==="

PROJECT_DIR="/mnt/host/f/Projects/DeckTune"
cd "$PROJECT_DIR"

VERSION=$(grep '"version"' plugin.json | cut -d'"' -f4)
echo "Building DeckTune v$VERSION"

# Clean
rm -rf release/temp
mkdir -p release/temp

# Build frontend
echo "Building frontend..."
npm run build

# Copy files to temp (flat structure)
echo "Copying files..."
cp plugin.json release/temp/
cp main.py release/temp/
cp LICENSE release/temp/
cp package.json release/temp/
cp README.md release/temp/
cp CHANGELOG.md release/temp/
cp install.sh release/temp/
cp setup-sudo.sh release/temp/

# Copy directories
cp -r dist release/temp/
cp -r backend release/temp/
cp -r bin release/temp/

# Remove pycache
find release/temp -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find release/temp -name "*.pyc" -delete 2>/dev/null || true

# Fix line endings
find release/temp -name "*.sh" -exec sed -i 's/\r$//' {} \;

# Set permissions
chmod +x release/temp/bin/*
chmod +x release/temp/*.sh

# Create zip from temp directory (files in root)
echo "Creating zip..."
cd release/temp
zip -r "../DeckTune-v${VERSION}.zip" . -x "*.pyc" "*/__pycache__/*"
cd ../..

# Cleanup
rm -rf release/temp

SIZE=$(du -h "release/DeckTune-v${VERSION}.zip" | cut -f1)
echo ""
echo "=== Build Complete ==="
echo "Version: v$VERSION"
echo "Output: release/DeckTune-v${VERSION}.zip"
echo "Size: $SIZE"
echo ""
echo "Install in Decky Loader:"
echo "1. Settings > Developer Mode > Install from ZIP"
echo "2. Select DeckTune-v${VERSION}.zip"
