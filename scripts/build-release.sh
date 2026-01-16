#!/bin/bash
# DeckTune Release Build Script
# Creates a clean release zip without macOS metadata files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
RELEASE_DIR="$PROJECT_DIR/release"

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
rm -rf "$RELEASE_DIR/DeckTune"
rm -f "$RELEASE_DIR/DeckTune.zip"
mkdir -p "$RELEASE_DIR/DeckTune/dist"
mkdir -p "$RELEASE_DIR/DeckTune/backend"
mkdir -p "$RELEASE_DIR/DeckTune/bin"

# Copy files
echo ""
echo "3. Copying files..."
cp "$PROJECT_DIR/dist/index.js" "$RELEASE_DIR/DeckTune/dist/"
cp "$PROJECT_DIR/dist/index.js.map" "$RELEASE_DIR/DeckTune/dist/" 2>/dev/null || true
cp "$PROJECT_DIR/main.py" "$RELEASE_DIR/DeckTune/"
cp "$PROJECT_DIR/plugin.json" "$RELEASE_DIR/DeckTune/"
cp "$PROJECT_DIR/LICENSE" "$RELEASE_DIR/DeckTune/"

# Copy backend (excluding __pycache__)
rsync -a --exclude='__pycache__' --exclude='*.pyc' "$PROJECT_DIR/backend/" "$RELEASE_DIR/DeckTune/backend/"

# Copy bin
cp -r "$PROJECT_DIR/bin/"* "$RELEASE_DIR/DeckTune/bin/"

# Remove macOS metadata files
echo ""
echo "4. Cleaning macOS metadata..."
find "$RELEASE_DIR/DeckTune" -name "._*" -delete 2>/dev/null || true
find "$RELEASE_DIR/DeckTune" -name ".DS_Store" -delete 2>/dev/null || true
find "$RELEASE_DIR/DeckTune" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Create zip without macOS metadata
echo ""
echo "5. Creating zip archive..."
cd "$RELEASE_DIR"
COPYFILE_DISABLE=1 zip -r DeckTune.zip DeckTune -x "*.DS_Store" -x "*._*" -x "*__pycache__*"

# Show result
echo ""
echo "=== Release created ==="
ls -la "$RELEASE_DIR/DeckTune.zip"
echo ""
echo "Contents:"
unzip -l "$RELEASE_DIR/DeckTune.zip" | head -20
echo "..."
echo ""
echo "To deploy to Steam Deck:"
echo "  scp $RELEASE_DIR/DeckTune.zip deck@<IP>:~/Downloads/"
echo "  # On Steam Deck:"
echo "  sudo rm -rf ~/homebrew/plugins/DeckTune"
echo "  sudo unzip -o ~/Downloads/DeckTune.zip -d ~/homebrew/plugins/"
echo "  sudo systemctl restart plugin_loader"
