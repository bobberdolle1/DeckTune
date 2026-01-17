# Manual deployment script for DeckTune
# Use this when automatic deploy fails

param(
    [string]$DeckIP = "192.168.0.163",
    [string]$Password = "7373"
)

Write-Host "=== DeckTune Manual Deploy ===" -ForegroundColor Cyan
Write-Host ""

# Check if release exists
if (-not (Test-Path "release\DeckTune.zip")) {
    Write-Host "ERROR: release\DeckTune.zip not found!" -ForegroundColor Red
    Write-Host "Run build-release.ps1 first" -ForegroundColor Yellow
    exit 1
}

Write-Host "1. Testing connection to Steam Deck..." -ForegroundColor Yellow
$testResult = Test-Connection -ComputerName $DeckIP -Count 1 -Quiet
if (-not $testResult) {
    Write-Host "ERROR: Cannot reach Steam Deck at $DeckIP" -ForegroundColor Red
    Write-Host "Make sure Steam Deck is on and SSH is enabled" -ForegroundColor Yellow
    exit 1
}
Write-Host "   Connection OK!" -ForegroundColor Green

Write-Host ""
Write-Host "2. Copying DeckTune.zip to Steam Deck..." -ForegroundColor Yellow
scp release\DeckTune.zip deck@${DeckIP}:~/Downloads/
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to copy file" -ForegroundColor Red
    exit 1
}
Write-Host "   Copy complete!" -ForegroundColor Green

Write-Host ""
Write-Host "3. Installing on Steam Deck..." -ForegroundColor Yellow
$commands = @"
echo $Password | sudo -S rm -rf ~/homebrew/plugins/DeckTune
echo $Password | sudo -S unzip -q -o ~/Downloads/DeckTune.zip -d ~/homebrew/plugins/
echo $Password | sudo -S chmod +x ~/homebrew/plugins/DeckTune/bin/*
echo $Password | sudo -S ~/homebrew/plugins/DeckTune/install.sh
echo $Password | sudo -S systemctl restart plugin_loader
"@

ssh -t deck@${DeckIP} $commands
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Installation may have issues" -ForegroundColor Yellow
} else {
    Write-Host "   Installation complete!" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Deploy Complete ===" -ForegroundColor Cyan
Write-Host "Plugin should be reloaded on Steam Deck now" -ForegroundColor Green
Write-Host ""
Write-Host "If you see 'Missing Components' warning:" -ForegroundColor Yellow
Write-Host "  ssh deck@$DeckIP" -ForegroundColor White
Write-Host "  ls -la ~/homebrew/plugins/DeckTune/bin/" -ForegroundColor White
Write-Host "  # Check that stress-ng and memtester are there and executable" -ForegroundColor Gray
