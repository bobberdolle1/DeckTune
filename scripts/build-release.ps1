# DeckTune Release Build Script (PowerShell)
# Creates a clean release zip without macOS metadata files

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_DIR = Split-Path -Parent $SCRIPT_DIR
$RELEASE_DIR = Join-Path $PROJECT_DIR "release"

Write-Host "=== DeckTune Release Builder ===" -ForegroundColor Cyan
Write-Host "Project: $PROJECT_DIR"

# Build frontend
Write-Host ""
Write-Host "1. Building frontend..." -ForegroundColor Yellow
Set-Location $PROJECT_DIR
npm run build

# Clean release directory
Write-Host ""
Write-Host "2. Preparing release directory..." -ForegroundColor Yellow
$DECKTUNE_DIR = Join-Path $RELEASE_DIR "DeckTune"
if (Test-Path $DECKTUNE_DIR) {
    Remove-Item -Recurse -Force $DECKTUNE_DIR
}
$ZIP_FILE = Join-Path $RELEASE_DIR "DeckTune.zip"
if (Test-Path $ZIP_FILE) {
    Remove-Item -Force $ZIP_FILE
}

New-Item -ItemType Directory -Force -Path (Join-Path $DECKTUNE_DIR "dist") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $DECKTUNE_DIR "backend") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $DECKTUNE_DIR "bin") | Out-Null

# Copy files
Write-Host ""
Write-Host "3. Copying files..." -ForegroundColor Yellow
Copy-Item (Join-Path $PROJECT_DIR "dist\index.js") (Join-Path $DECKTUNE_DIR "dist\")
if (Test-Path (Join-Path $PROJECT_DIR "dist\index.js.map")) {
    Copy-Item (Join-Path $PROJECT_DIR "dist\index.js.map") (Join-Path $DECKTUNE_DIR "dist\")
}
Copy-Item (Join-Path $PROJECT_DIR "main.py") $DECKTUNE_DIR
Copy-Item (Join-Path $PROJECT_DIR "plugin.json") $DECKTUNE_DIR
Copy-Item (Join-Path $PROJECT_DIR "LICENSE") $DECKTUNE_DIR
Copy-Item (Join-Path $PROJECT_DIR "install.sh") $DECKTUNE_DIR

# Copy backend (excluding __pycache__)
Write-Host "Copying backend..."
Get-ChildItem (Join-Path $PROJECT_DIR "backend") -Recurse | Where-Object {
    $_.FullName -notmatch '__pycache__' -and $_.Extension -ne '.pyc'
} | ForEach-Object {
    $targetPath = $_.FullName.Replace((Join-Path $PROJECT_DIR "backend"), (Join-Path $DECKTUNE_DIR "backend"))
    if ($_.PSIsContainer) {
        New-Item -ItemType Directory -Force -Path $targetPath | Out-Null
    } else {
        $targetDir = Split-Path -Parent $targetPath
        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
        }
        Copy-Item $_.FullName $targetPath
    }
}

# Copy bin
Write-Host "Copying binaries..."
Copy-Item (Join-Path $PROJECT_DIR "bin\*") (Join-Path $DECKTUNE_DIR "bin\") -Recurse

# Set executable permissions for binaries (will be applied on Linux)
Write-Host "Note: Binary permissions will need to be set on Steam Deck after installation"

# Clean macOS metadata files
Write-Host ""
Write-Host "4. Cleaning metadata..." -ForegroundColor Yellow
Get-ChildItem $DECKTUNE_DIR -Recurse -Force | Where-Object {
    $_.Name -like "._*" -or $_.Name -eq ".DS_Store" -or $_.Name -eq "__pycache__"
} | Remove-Item -Recurse -Force

# Create zip
Write-Host ""
Write-Host "5. Creating zip archive..." -ForegroundColor Yellow
Set-Location $RELEASE_DIR
Compress-Archive -Path "DeckTune" -DestinationPath "DeckTune.zip" -Force

# Show result
Write-Host ""
Write-Host "=== Release created ===" -ForegroundColor Green
Get-Item $ZIP_FILE | Format-List Name, Length, LastWriteTime

Write-Host ""
Write-Host "To deploy to Steam Deck:" -ForegroundColor Cyan
Write-Host "  scp $ZIP_FILE deck@192.168.0.163:~/Downloads/"
Write-Host "  # On Steam Deck:"
Write-Host "  sudo rm -rf ~/homebrew/plugins/DeckTune"
Write-Host "  sudo unzip -o ~/Downloads/DeckTune.zip -d ~/homebrew/plugins/"
Write-Host "  sudo ~/homebrew/plugins/DeckTune/install.sh"
Write-Host "  sudo systemctl restart plugin_loader"
