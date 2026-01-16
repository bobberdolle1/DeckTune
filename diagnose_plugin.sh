#!/bin/bash
# DeckTune Plugin Diagnostic Script

echo "=== DeckTune Plugin Diagnostics ==="
echo ""

PLUGIN_DIR="$HOME/homebrew/plugins/DeckTune"

echo "1. Plugin directory structure:"
ls -la "$PLUGIN_DIR/" 2>/dev/null || echo "Plugin directory not found!"
echo ""

echo "2. dist/index.js info:"
ls -la "$PLUGIN_DIR/dist/" 2>/dev/null
file "$PLUGIN_DIR/dist/index.js" 2>/dev/null
echo ""

echo "3. First 100 bytes (hex):"
head -c 100 "$PLUGIN_DIR/dist/index.js" 2>/dev/null | xxd | head -10
echo ""

echo "4. First line of index.js:"
head -1 "$PLUGIN_DIR/dist/index.js" 2>/dev/null
echo ""

echo "5. Last line of index.js:"
tail -1 "$PLUGIN_DIR/dist/index.js" 2>/dev/null
echo ""

echo "6. plugin.json content:"
cat "$PLUGIN_DIR/plugin.json" 2>/dev/null
echo ""

echo "7. Decky Loader version:"
cat "$HOME/homebrew/services/.loader.version" 2>/dev/null || echo "Version file not found"
echo ""

echo "8. Looking for logs:"
find "$HOME/homebrew" -name "*.log" -type f 2>/dev/null | head -10
echo ""

echo "9. Decky services:"
ls -la "$HOME/homebrew/services/" 2>/dev/null
echo ""

echo "10. Compare with working plugin (if SimpleDeckyTDP installed):"
if [ -d "$HOME/homebrew/plugins/SimpleDeckyTDP" ]; then
    echo "SimpleDeckyTDP found, comparing first line:"
    echo "DeckTune: $(head -c 50 $PLUGIN_DIR/dist/index.js)"
    echo "SimpleTDP: $(head -c 50 $HOME/homebrew/plugins/SimpleDeckyTDP/dist/index.js)"
else
    echo "SimpleDeckyTDP not installed"
fi
echo ""

echo "=== End of diagnostics ==="
