#!/usr/bin/env python3
"""Build proper zip archive for Decky Loader with Unix-style paths."""

import zipfile
import os
from pathlib import Path

def create_release_zip():
    project_dir = Path(__file__).parent.parent
    release_dir = project_dir / "release"
    source_dir = release_dir / "DeckTune"
    output_zip = release_dir / "DeckTune.zip"
    
    if not source_dir.exists():
        print(f"Error: {source_dir} does not exist")
        return False
    
    # Remove old zip if exists
    if output_zip.exists():
        output_zip.unlink()
    
    print(f"Creating {output_zip}...")
    
    # Required files per Decky documentation
    required_files = ['plugin.json', 'main.py', 'LICENSE', 'package.json', 'dist/index.js']
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                # Skip .pyc files
                if file.endswith('.pyc'):
                    continue
                
                file_path = Path(root) / file
                # Create archive path relative to release_dir with forward slashes
                arcname = file_path.relative_to(release_dir).as_posix()
                
                # Fix line endings for shell scripts BEFORE adding to zip
                if file.endswith('.sh'):
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    if b'\r\n' in content:
                        print(f"  Fixing line endings: {arcname}")
                        content = content.replace(b'\r\n', b'\n')
                        # Write to temp location with fixed line endings
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False) as tmp:
                            tmp.write(content)
                            tmp_path = tmp.name
                        
                        print(f"  Adding: {arcname}")
                        zf.write(tmp_path, arcname)
                        os.unlink(tmp_path)
                        
                        # Set executable permissions
                        info = zf.getinfo(arcname)
                        info.external_attr = 0o755 << 16
                        continue
                
                print(f"  Adding: {arcname}")
                zf.write(file_path, arcname)
                
                # Set executable permissions for specific files
                if file in ['stress-ng', 'memtester', 'gymdeck3', 'ryzenadj']:
                    info = zf.getinfo(arcname)
                    info.external_attr = 0o755 << 16  # Unix executable permissions
    
    size_mb = output_zip.stat().st_size / (1024 * 1024)
    print(f"\nCreated: {output_zip} ({size_mb:.2f} MB)")
    return True

if __name__ == "__main__":
    success = create_release_zip()
    exit(0 if success else 1)
