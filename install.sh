#!/bin/bash
# DeckTune post-install script
# Sets executable permissions on binaries and configures sudo

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==================================="
echo "DeckTune - Post-Install Setup"
echo "==================================="
echo ""

# Set executable permissions
echo "Setting executable permissions for DeckTune binaries..."
chmod +x "$PLUGIN_DIR/bin/ryzenadj" 2>/dev/null || true
chmod +x "$PLUGIN_DIR/bin/gymdeck3" 2>/dev/null || true
chmod +x "$PLUGIN_DIR/bin/stress-ng" 2>/dev/null || true
chmod +x "$PLUGIN_DIR/bin/memtester" 2>/dev/null || true
chmod +x "$PLUGIN_DIR/setup-sudo.sh" 2>/dev/null || true
echo "✓ Binaries are now executable"
echo ""

# Configure sudo NOPASSWD
echo "Configuring sudo for ryzenadj..."
echo "This allows DeckTune to apply undervolt without password prompts."
echo ""

RYZENADJ_PATH="$PLUGIN_DIR/bin/ryzenadj"
SUDOERS_FILE="/etc/sudoers.d/decktune"

# Check if already configured
if [ -f "$SUDOERS_FILE" ]; then
    echo "✓ sudo already configured"
else
    echo "Creating sudo configuration..."
    echo "You may be prompted for your password."
    echo ""
    
    # Create sudoers file
    if sudo tee "$SUDOERS_FILE" > /dev/null 2>&1 << EOF
# DeckTune - Allow ryzenadj to run without password
deck ALL=(ALL) NOPASSWD: $RYZENADJ_PATH
root ALL=(ALL) NOPASSWD: $RYZENADJ_PATH
EOF
    then
        sudo chmod 0440 "$SUDOERS_FILE" 2>/dev/null || true
        
        # Verify configuration
        if sudo visudo -c -f "$SUDOERS_FILE" > /dev/null 2>&1; then
            echo "✓ sudo configured successfully"
        else
            echo "⚠ Warning: sudo configuration may be invalid"
            sudo rm -f "$SUDOERS_FILE" 2>/dev/null || true
        fi
    else
        echo "⚠ Warning: Could not configure sudo automatically"
        echo "   You can run ./setup-sudo.sh manually later"
    fi
fi

echo ""
echo "==================================="
echo "DeckTune installation complete!"
echo "==================================="
echo ""
echo "The plugin will be available in Decky menu after reload."
echo ""
echo "If binning doesn't work, restart the plugin loader:"
echo "  sudo systemctl restart plugin_loader"
echo ""
