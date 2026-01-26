#!/usr/bin/env python3
"""DeckTune Decky Zip Builder - Creates proper Unix-path zip for Decky Loader"""

import os
import shutil
import zipfile
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
RELEASE_DIR = PROJECT_DIR / "release"
TEMP_DIR = RELEASE_DIR / "temp"
DECKTUNE_DIR = TEMP_DIR / "DeckTune"

# Read version from plugin.json
import json
with open(PROJECT_DIR / "plugin.json") as f:
    version = json.load(f)["version"]

ZIP_FILE = RELEASE_DIR / f"DeckTune-v{version}.zip"

print("=== DeckTune Decky Zip Builder ===")

# Clean
if TEMP_DIR.exists():
    shutil.rmtree(TEMP_DIR)
if ZIP_FILE.exists():
    ZIP_FILE.unlink()

# Create structure
print("Copying files...")
DECKTUNE_DIR.mkdir(parents=True)
(DECKTUNE_DIR / "dist").mkdir()
(DECKTUNE_DIR / "backend").mkdir()
(DECKTUNE_DIR / "bin").mkdir()

# Copy files
shutil.copy(PROJECT_DIR / "dist" / "index.js", DECKTUNE_DIR / "dist")
if (PROJECT_DIR / "dist" / "index.js.map").exists():
    shutil.copy(PROJECT_DIR / "dist" / "index.js.map", DECKTUNE_DIR / "dist")

for f in ["main.py", "plugin.json", "package.json", "LICENSE", "install.sh"]:
    shutil.copy(PROJECT_DIR / f, DECKTUNE_DIR)

# Copy backend (exclude __pycache__)
for root, dirs, files in os.walk(PROJECT_DIR / "backend"):
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    rel_root = Path(root).relative_to(PROJECT_DIR / "backend")
    target_dir = DECKTUNE_DIR / "backend" / rel_root
    target_dir.mkdir(parents=True, exist_ok=True)
    for file in files:
        if not file.endswith(".pyc"):
            shutil.copy(Path(root) / file, target_dir / file)

# Copy bin
shutil.copytree(PROJECT_DIR / "bin", DECKTUNE_DIR / "bin", dirs_exist_ok=True)

# Create zip with Unix paths
print(f"Creating {ZIP_FILE.name}...")
with zipfile.ZipFile(ZIP_FILE, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(DECKTUNE_DIR):
        for file in files:
            file_path = Path(root) / file
            arcname = file_path.relative_to(TEMP_DIR).as_posix()  # Unix paths
            zf.write(file_path, arcname)
            print(f"  + {arcname}")

# Cleanup
shutil.rmtree(TEMP_DIR)

# Show result
size_mb = ZIP_FILE.stat().st_size / (1024 * 1024)
print(f"\n=== Build Complete ===")
print(f"Version: v{version}")
print(f"Output: {ZIP_FILE}")
print(f"Size: {size_mb:.2f} MB")
print(f"\nInstall: Decky Loader > Settings > Developer > Install from ZIP")
