#!/bin/bash
# Setup NOPASSWD for DeckTune ryzenadj
# This script configures sudo to allow ryzenadj to run without password

set -e

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RYZENADJ_PATH="${PLUGIN_DIR}/bin/ryzenadj"
SUDOERS_FILE="/etc/sudoers.d/decktune"

echo "==================================="
echo "DeckTune - Setup sudo NOPASSWD"
echo "==================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Do not run this script as root!"
    echo "Run as deck user: ./setup-sudo.sh"
    exit 1
fi

# Check if ryzenadj exists
if [ ! -f "$RYZENADJ_PATH" ]; then
    echo "ERROR: ryzenadj not found at $RYZENADJ_PATH"
    exit 1
fi

echo "Plugin directory: $PLUGIN_DIR"
echo "ryzenadj path: $RYZENADJ_PATH"
echo ""

# Create sudoers configuration
echo "Creating sudoers configuration..."
echo "This will require your sudo password."
echo ""

# Create the sudoers file with both deck and root users
sudo tee "$SUDOERS_FILE" > /dev/null << EOF
# DeckTune - Allow ryzenadj to run without password
# This is required for undervolt functionality
deck ALL=(ALL) NOPASSWD: $RYZENADJ_PATH
root ALL=(ALL) NOPASSWD: $RYZENADJ_PATH
EOF

# Set correct permissions
sudo chmod 0440 "$SUDOERS_FILE"

# Verify the configuration
if sudo visudo -c -f "$SUDOERS_FILE" > /dev/null 2>&1; then
    echo ""
    echo "✓ NOPASSWD configured successfully!"
    echo ""
    echo "Configuration file: $SUDOERS_FILE"
    echo "Contents:"
    sudo cat "$SUDOERS_FILE"
    echo ""
    
    # Test the configuration
    echo "Testing configuration..."
    if sudo -n "$RYZENADJ_PATH" --info > /dev/null 2>&1; then
        echo "✓ Test passed! ryzenadj can run without password."
    else
        echo "⚠ Test failed. You may need to restart the plugin loader:"
        echo "  sudo systemctl restart plugin_loader"
    fi
    
    echo ""
    echo "Setup complete! DeckTune should now work fully."
    echo ""
    echo "If binning still doesn't work, restart the plugin loader:"
    echo "  sudo systemctl restart plugin_loader"
    echo ""
else
    echo ""
    echo "✗ ERROR: Invalid sudoers configuration!"
    echo "Removing the file..."
    sudo rm -f "$SUDOERS_FILE"
    exit 1
fi
