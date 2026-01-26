#!/bin/bash
# DeckTune Release Build Script
# Creates a clean release zip with proper Unix paths

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
RELEASE_DIR="$PROJECT_DIR/release"
TEMP_DIR="$RELEASE_DIR/temp"
DECKTUNE_DIR="$TEMP_DIR/DeckTune"

echo "=== DeckTune Release Builder ==="
echo "Project: $PROJECT_DIR"

# Build frontend
echo ""
echo "1. Building frontend..."
cd "$PROJECT_DIR"
npm run build

# Clean release directory
echo ""
echo "2. Preparing release directory..."
rm -rf "$TEMP_DIR"
rm -f "$RELEASE_DIR/DeckTune.zip"

mkdir -p "$DECKTUNE_DIR/dist"
mkdir -p "$DECKTUNE_DIR/backend"
mkdir -p "$DECKTUNE_DIR/bin"

# Copy files
echo ""
echo "3. Copying files..."
cp "$PROJECT_DIR/dist/index.js" "$DECKTUNE_DIR/dist/"
[ -f "$PROJECT_DIR/dist/index.js.map" ] && cp "$PROJECT_DIR/dist/index.js.map" "$DECKTUNE_DIR/dist/"
cp "$PROJECT_DIR/main.py" "$DECKTUNE_DIR/"
cp "$PROJECT_DIR/plugin.json" "$DECKTUNE_DIR/"
cp "$PROJECT_DIR/LICENSE" "$DECKTUNE_DIR/"
cp "$PROJECT_DIR/install.sh" "$DECKTUNE_DIR/"

# Copy backend (excluding __pycache__)
echo "Copying backend..."
rsync -av --exclude='__pycache__' --exclude='*.pyc' "$PROJECT_DIR/backend/" "$DECKTUNE_DIR/backend/"

# Copy bin
echo "Copying binaries..."
cp -r "$PROJECT_DIR/bin/"* "$DECKTUNE_DIR/bin/"

# Create zip with Unix paths
echo ""
echo "4. Creating zip archive..."
cd "$TEMP_DIR"
zip -r "$RELEASE_DIR/DeckTune.zip" DeckTune/

# Clean up
cd "$RELEASE_DIR"
rm -rf "$TEMP_DIR"

# Show result
echo ""
echo "=== Release created ==="
ls -lh "$RELEASE_DIR/DeckTune.zip"

echo ""
echo "To deploy to Steam Deck:"
echo "  scp $RELEASE_DIR/DeckTune.zip deck@steamdeck:~/Downloads/"
echo "  # On Steam Deck:"
echo "  cd ~/homebrew/plugins"
echo "  rm -rf DeckTune"
echo "  unzip ~/Downloads/DeckTune.zip"
echo "  sudo systemctl restart plugin_loader"
