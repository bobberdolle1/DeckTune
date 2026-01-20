#!/bin/sh
# Fix Windows backslash paths in extracted zip and deploy

set -e

EXTRACT_DIR="/tmp/decktune_extract"
TARGET_DIR="$HOME/homebrew/plugins/DeckTune"

echo "Fixing Windows paths and deploying..."

# Remove old installation
echo 7373 | sudo -S rm -rf "$TARGET_DIR"
echo 7373 | sudo -S mkdir -p "$TARGET_DIR"

# Copy files with proper Unix paths
cd "$EXTRACT_DIR"

# Copy root files
for file in main.py plugin.json package.json LICENSE README.md CHANGELOG.md install.sh setup-sudo.sh; do
    if [ -f "$file" ]; then
        echo 7373 | sudo -S cp "$file" "$TARGET_DIR/"
    fi
done

# Recreate directory structure
echo 7373 | sudo -S mkdir -p "$TARGET_DIR/backend/api" "$TARGET_DIR/backend/core" "$TARGET_DIR/backend/dynamic" "$TARGET_DIR/backend/platform" "$TARGET_DIR/backend/tuning"
echo 7373 | sudo -S mkdir -p "$TARGET_DIR/bin" "$TARGET_DIR/dist"

# Copy all files with backslash in name
find . -name '*\\*' -type f | while read file; do
    # Convert Windows path to Unix path
    target=$(echo "$file" | sed 's|\\|/|g' | sed 's|^\./||')
    targetdir=$(dirname "$TARGET_DIR/$target")
    echo 7373 | sudo -S mkdir -p "$targetdir"
    echo 7373 | sudo -S cp "$file" "$TARGET_DIR/$target"
done

# Set permissions
echo 7373 | sudo -S chmod +x "$TARGET_DIR/bin/"* 2>/dev/null || true
echo 7373 | sudo -S chmod +x "$TARGET_DIR/"*.sh 2>/dev/null || true

# Run install script
echo 7373 | sudo -S "$TARGET_DIR/install.sh"

# Restart plugin loader
echo 7373 | sudo -S systemctl restart plugin_loader

echo "Deploy complete!"
