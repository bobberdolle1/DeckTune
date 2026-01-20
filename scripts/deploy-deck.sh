#!/bin/sh
# Deploy DeckTune to Steam Deck - handles Windows zip backslash paths

EXTRACT_DIR="/tmp/decktune_extract"
TARGET_DIR="$HOME/homebrew/plugins/DeckTune"

echo "Deploying DeckTune v3.1.29..."

# Remove old installation
echo 7373 | sudo -S rm -rf "$TARGET_DIR"
echo 7373 | sudo -S mkdir -p "$TARGET_DIR"

cd "$EXTRACT_DIR"

# Copy all files recursively, converting backslash paths
for file in $(find . -type f); do
    # Skip hidden files
    case "$file" in
        */.*) continue ;;
    esac
    
    # Convert backslash to forward slash
    target=$(echo "$file" | sed 's|\\|/|g' | sed 's|^\./||')
    targetdir=$(dirname "$TARGET_DIR/$target")
    
    # Create directory if needed
    echo 7373 | sudo -S mkdir -p "$targetdir"
    
    # Copy file
    echo 7373 | sudo -S cp "$file" "$TARGET_DIR/$target"
done

# Set executable permissions
echo 7373 | sudo -S chmod +x "$TARGET_DIR/bin/"* 2>/dev/null || true
echo 7373 | sudo -S chmod +x "$TARGET_DIR/"*.sh 2>/dev/null || true

# Run install script
echo 7373 | sudo -S "$TARGET_DIR/install.sh"

# Restart plugin loader
echo 7373 | sudo -S systemctl restart plugin_loader

echo "Deploy complete! DeckTune v3.1.29 installed."
