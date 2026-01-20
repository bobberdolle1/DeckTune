#!/usr/bin/env python3
"""Build proper Decky Loader zip with Unix paths"""

import os
import zipfile
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
RELEASE_DIR = PROJECT_DIR / "release"
TEMP_DIR = RELEASE_DIR / "temp"

print("=== DeckTune Decky Zip Builder ===")

# Clean
if TEMP_DIR.exists():
    shutil.rmtree(TEMP_DIR)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Copy files
print("Copying files...")
files_to_copy = [
    "plugin.json", "main.py", "LICENSE", "package.json",
    "README.md", "CHANGELOG.md", "install.sh", "setup-sudo.sh"
]

for file in files_to_copy:
    src = PROJECT_DIR / file
    if src.exists():
        shutil.copy2(src, TEMP_DIR / file)

# Copy directories
for dir_name in ["dist", "backend", "bin"]:
    src_dir = PROJECT_DIR / dir_name
    dst_dir = TEMP_DIR / dir_name
    if src_dir.exists():
        shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

# Get version
import json
with open(TEMP_DIR / "plugin.json") as f:
    version = json.load(f)["version"]

# Create zip with DeckTune/ folder and Unix paths
zip_path = RELEASE_DIR / f"DeckTune-v{version}.zip"
print(f"Creating {zip_path.name}...")

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(TEMP_DIR):
        # Remove __pycache__ from dirs to prevent traversal
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.pyc'):
                continue
                
            file_path = Path(root) / file
            # Create Unix-style relative path with DeckTune/ prefix
            rel_path = file_path.relative_to(TEMP_DIR)
            arcname = f"DeckTune/{str(rel_path).replace(chr(92), '/')}"
            zf.write(file_path, arcname)
            print(f"  + {arcname}")

# Cleanup
shutil.rmtree(TEMP_DIR)

# Copy to root
root_zip = PROJECT_DIR / f"DeckTune-v{version}.zip"
shutil.copy2(zip_path, root_zip)

size_mb = zip_path.stat().st_size / (1024 * 1024)
print(f"\n=== Build Complete ===")
print(f"Version: v{version}")
print(f"Output: {zip_path}")
print(f"Size: {size_mb:.2f} MB")
print(f"\nInstall: Decky Loader > Settings > Developer > Install from ZIP")
