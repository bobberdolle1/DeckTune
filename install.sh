#!/bin/bash

# DeckTune Installer Script
# Installs DeckTune plugin for Decky Loader

set -e

PLUGIN_NAME="DeckTune"
PLUGIN_DIR="$HOME/homebrew/plugins/$PLUGIN_NAME"
RELEASE_URL="https://github.com/bobberdolle1/DeckTune/releases/latest/download/DeckTune.zip"

echo "==================================="
echo "  DeckTune Installer"
echo "==================================="
echo ""

# Check if running on Steam Deck
if [[ ! -f /etc/os-release ]] || ! grep -q "SteamOS" /etc/os-release 2>/dev/null; then
    echo "Warning: This script is designed for SteamOS on Steam Deck."
    echo "Continuing anyway..."
fi

# Check if Decky Loader is installed
if [[ ! -d "$HOME/homebrew" ]]; then
    echo "Error: Decky Loader not found!"
    echo "Please install Decky Loader first: https://decky.xyz/"
    exit 1
fi

echo "Downloading $PLUGIN_NAME..."
TEMP_DIR=$(mktemp -d)
curl -L "$RELEASE_URL" -o "$TEMP_DIR/$PLUGIN_NAME.zip"

echo "Installing $PLUGIN_NAME..."
# Remove old version if exists
if [[ -d "$PLUGIN_DIR" ]]; then
    echo "Removing old version..."
    rm -rf "$PLUGIN_DIR"
fi

# Extract new version
unzip -q "$TEMP_DIR/$PLUGIN_NAME.zip" -d "$HOME/homebrew/plugins/"

# Cleanup
rm -rf "$TEMP_DIR"

# Set permissions for ryzenadj
if [[ -f "$PLUGIN_DIR/bin/ryzenadj" ]]; then
    chmod +x "$PLUGIN_DIR/bin/ryzenadj"
fi

if [[ -f "$PLUGIN_DIR/bin/gymdeck2" ]]; then
    chmod +x "$PLUGIN_DIR/bin/gymdeck2"
fi

echo ""
echo "==================================="
echo "  Installation Complete!"
echo "==================================="
echo ""
echo "Please restart Decky Loader to load the plugin."
echo "You can do this by restarting Steam or your Steam Deck."
echo ""
