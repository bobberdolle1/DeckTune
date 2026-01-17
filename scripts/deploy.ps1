# Quick deploy script for DeckTune
# Builds, packages, and deploys to Steam Deck in one command

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_DIR = Split-Path -Parent $SCRIPT_DIR

Write-Host "=== DeckTune Quick Deploy ===" -ForegroundColor Cyan

# Build and package
Write-Host ""
Write-Host "Building and packaging..." -ForegroundColor Yellow
& "$SCRIPT_DIR\build-release.ps1"

# Deploy to Steam Deck
$ZIP_FILE = Join-Path $PROJECT_DIR "release\DeckTune.zip"
Write-Host ""
Write-Host "Deploying to Steam Deck..." -ForegroundColor Yellow

# Copy zip
scp $ZIP_FILE deck@192.168.0.163:~/Downloads/

# Install and restart
ssh -t deck@192.168.0.163 "echo 7373 | sudo -S rm -rf ~/homebrew/plugins/DeckTune && echo 7373 | sudo -S unzip -q -o ~/Downloads/DeckTune.zip -d ~/homebrew/plugins/ && echo 7373 | sudo -S ~/homebrew/plugins/DeckTune/install.sh && echo 7373 | sudo -S systemctl restart plugin_loader && sleep 2 && echo 'Deployment complete!'"

Write-Host ""
Write-Host "=== Deployed successfully ===" -ForegroundColor Green
Write-Host "Plugin should be reloaded on Steam Deck now"
