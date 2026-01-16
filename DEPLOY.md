# DeckTune Deployment Guide

## Quick Deploy to Steam Deck

### Prerequisites
- Steam Deck with Decky Loader v3.2.1+
- SSH access to Steam Deck (enable in Developer Settings)
- Steam Deck IP address (find in Settings > Network)

### Build & Deploy

```bash
# 1. Build frontend
npm run build

# 2. Create release package
rm -rf release/DeckTune release/DeckTune.zip
mkdir -p release/DeckTune/dist release/DeckTune/backend release/DeckTune/bin

cp dist/index.js dist/index.js.map release/DeckTune/dist/
cp main.py plugin.json LICENSE release/DeckTune/
cp -r backend/* release/DeckTune/backend/
cp -r bin/* release/DeckTune/bin/

# Remove macOS metadata
find release/DeckTune -name "._*" -delete
find release/DeckTune -name ".DS_Store" -delete
find release/DeckTune -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Create zip (COPYFILE_DISABLE prevents macOS extended attributes)
cd release
COPYFILE_DISABLE=1 zip -r DeckTune.zip DeckTune -x "*.DS_Store" -x "*._*"
cd ..

# 3. Copy to Steam Deck
scp release/DeckTune.zip deck@<STEAM_DECK_IP>:~/Downloads/

# 4. SSH to Steam Deck and install
ssh deck@<STEAM_DECK_IP>
sudo rm -rf ~/homebrew/plugins/DeckTune
sudo unzip -o ~/Downloads/DeckTune.zip -d ~/homebrew/plugins/
sudo systemctl restart plugin_loader
```

### One-liner Deploy (after build)

```bash
# Replace <IP> with your Steam Deck IP
scp release/DeckTune.zip deck@<IP>:~/Downloads/ && \
ssh deck@<IP> "sudo rm -rf ~/homebrew/plugins/DeckTune && sudo unzip -o ~/Downloads/DeckTune.zip -d ~/homebrew/plugins/ && sudo systemctl restart plugin_loader"
```

## Development Workflow

### Quick Frontend Update (no full rebuild)

```bash
# Build and deploy just index.js
npm run build
scp dist/index.js deck@<IP>:~/Downloads/
ssh deck@<IP> "sudo cp ~/Downloads/index.js ~/homebrew/plugins/DeckTune/dist/ && sudo systemctl restart plugin_loader"
```

### Quick Backend Update

```bash
# Deploy just Python files
rsync -avz --exclude='._*' --exclude='.DS_Store' --exclude='__pycache__' \
  backend/ deck@<IP>:~/Downloads/backend/
ssh deck@<IP> "sudo rm -rf ~/homebrew/plugins/DeckTune/backend && sudo cp -r ~/Downloads/backend ~/homebrew/plugins/DeckTune/ && sudo systemctl restart plugin_loader"
```

## Troubleshooting

### Check Decky Loader logs
```bash
ssh deck@<IP> "journalctl -u plugin_loader -n 50 --no-pager"
```

### Verify plugin structure
```bash
ssh deck@<IP> "ls -la ~/homebrew/plugins/DeckTune/"
```

### Check if plugin loaded
```bash
ssh deck@<IP> "journalctl -u plugin_loader | grep DeckTune"
```

### Common Issues

1. **"Unexpected token 'export'" error**
   - Usually means macOS metadata files (._*) were included
   - Solution: Use `COPYFILE_DISABLE=1` when creating zip

2. **Plugin not appearing in Decky menu**
   - Check plugin.json is valid JSON
   - Verify dist/index.js exists and is not empty

3. **"Failed to initialize" error**
   - Check browser console for specific error
   - Usually means API incompatibility - wrap SteamClient calls in try-catch

## Release Checklist

1. Update version in `plugin.json` and `package.json`
2. Update `CHANGELOG.md`
3. Run `npm run build`
4. Create release package (see above)
5. Test on Steam Deck
6. Create GitHub release with DeckTune.zip
