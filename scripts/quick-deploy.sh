#!/bin/bash
# Quick Deploy v3.1.21 - Gamepad Activation Fix

echo "=== DeckTune v3.1.21 Quick Deploy ==="
echo ""

# Remove old
sudo rm -rf ~/homebrew/plugins/DeckTune && echo "✓ Old plugin removed"

# Extract new
sudo unzip -q -o ~/Downloads/DeckTune.zip -d ~/homebrew/plugins/ && echo "✓ New version extracted"

# Set permissions
cd ~/homebrew/plugins/DeckTune
sudo chmod +x bin/* install.sh && echo "✓ Permissions set"

# Restart service
sudo systemctl restart plugin_loader && echo "✓ Plugin loader restarted"

# Verify
echo ""
echo "=== Verification ==="
VERSION=$(cat plugin.json | grep '"version"' | cut -d'"' -f4)
echo "Installed version: $VERSION"

if [ "$VERSION" = "3.1.21" ]; then
    echo "✓ Version correct!"
else
    echo "✗ Version mismatch! Expected 3.1.21, got $VERSION"
fi

echo ""
echo "=== Changes in v3.1.21 ==="
echo "✓ FocusableButton: Removed onClick from Focusable (gamepad fix)"
echo "✓ PanicDisableButton: Border now on inner red div (rounded)"
echo "✓ PresetsTabNew: ButtonItem replaced with FocusableButton"
echo "✓ All focus borders are ROUNDED (pill-shaped)"
echo ""
echo "=== Test Checklist ==="
echo "1. Panic Disable - WHITE ROUNDED outline on RED button"
echo "2. Tab buttons - Press A button to switch tabs (MUST WORK!)"
echo "3. All buttons - Gamepad A button should activate"
echo "4. All outlines should be PILL-SHAPED, not square!"
echo ""
echo "=== Done! ==="
echo "Switch to Gaming Mode and test!"
