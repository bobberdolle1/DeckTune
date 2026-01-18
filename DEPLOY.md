# DeckTune Deployment Guide

## Quick Deploy (Automatic)

```powershell
.\scripts\deploy.ps1
```

Builds, packages, and deploys to Steam Deck automatically.

## Manual Deploy (When automatic fails)

### 1. Build Release
```powershell
.\scripts\build-release.ps1
```

### 2. Deploy to Steam Deck
```powershell
.\scripts\manual-deploy.ps1
```

Or manually:
```powershell
# Copy to Steam Deck
scp release\DeckTune.zip deck@192.168.0.163:~/Downloads/

# Install on Steam Deck
ssh deck@192.168.0.163
cd ~/Downloads
echo 7373 | sudo -S rm -rf ~/homebrew/plugins/DeckTune
echo 7373 | sudo -S unzip -q -o DeckTune.zip -d ~/homebrew/plugins/
echo 7373 | sudo -S chmod +x ~/homebrew/plugins/DeckTune/bin/*
echo 7373 | sudo -S ~/homebrew/plugins/DeckTune/install.sh
echo 7373 | sudo -S systemctl restart plugin_loader
```

## Verify Installation

### Check binaries are executable
```bash
ssh deck@192.168.0.163
ls -la ~/homebrew/plugins/DeckTune/bin/
```

Should show:
- `ryzenadj` (executable)
- `gymdeck3` (executable)
- `stress-ng` (executable)
- `memtester` (executable)

### Check plugin loaded
```bash
ssh deck@192.168.0.163
systemctl status plugin_loader
journalctl -u plugin_loader -f
```

## Troubleshooting

### "Missing Components" warning in Tests tab
- Binaries are bundled in `bin/` folder
- Check permissions: `ls -la ~/homebrew/plugins/DeckTune/bin/`
- Re-run: `sudo chmod +x ~/homebrew/plugins/DeckTune/bin/*`

### Connection timeout
- Check Steam Deck IP: `192.168.0.163`
- Enable SSH in Steam Deck developer mode
- Test connection: `Test-Connection 192.168.0.163`

### Plugin not loading
- Check logs: `journalctl -u plugin_loader -f`
- Restart: `sudo systemctl restart plugin_loader`
- Check Python errors in logs

## Development Workflow

1. Make changes to code
2. Test locally: `npm run build`
3. Deploy: `.\scripts\deploy.ps1`
4. Check on Steam Deck
5. Commit: `git add -A && git commit -m "message"`
