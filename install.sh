#!/bin/bash
# DeckTune post-install script
# Sets executable permissions on binaries

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Setting executable permissions for DeckTune binaries..."

chmod +x "$PLUGIN_DIR/bin/ryzenadj" 2>/dev/null || true
chmod +x "$PLUGIN_DIR/bin/gymdeck3" 2>/dev/null || true
chmod +x "$PLUGIN_DIR/bin/stress-ng" 2>/dev/null || true
chmod +x "$PLUGIN_DIR/bin/memtester" 2>/dev/null || true

echo "DeckTune binaries are now executable"
