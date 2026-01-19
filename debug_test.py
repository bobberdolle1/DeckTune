#!/usr/bin/env python3
import sys
import os
import subprocess

print("=" * 60)
print("DEBUG TEST")
print("=" * 60)
print()

# Check if we're root
uid = os.geteuid()
print(f"Current UID: {uid}")
print(f"Are we root? {uid == 0}")
print()

# Test direct execution
print("Test 1: Direct execution")
binary = "/home/deck/homebrew/plugins/DeckTune/bin/ryzenadj"
try:
    result = subprocess.run([binary, "--info"], capture_output=True, text=True, timeout=5)
    print(f"Return code: {result.returncode}")
    if result.returncode == 0:
        print("✓ SUCCESS")
        print(f"Output: {result.stdout[:100]}...")
    else:
        print("✗ FAILED")
        print(f"Stderr: {result.stderr}")
except Exception as e:
    print(f"✗ Exception: {e}")

print()
print("Test 2: With sudo")
try:
    result = subprocess.run(["sudo", binary, "--info"], capture_output=True, text=True, timeout=5)
    print(f"Return code: {result.returncode}")
    if result.returncode == 0:
        print("✓ SUCCESS")
        print(f"Output: {result.stdout[:100]}...")
    else:
        print("✗ FAILED")
        print(f"Stderr: {result.stderr}")
except Exception as e:
    print(f"✗ Exception: {e}")

print()
print("Test 3: With sudo -n")
try:
    result = subprocess.run(["sudo", "-n", binary, "--info"], capture_output=True, text=True, timeout=5)
    print(f"Return code: {result.returncode}")
    if result.returncode == 0:
        print("✓ SUCCESS")
        print(f"Output: {result.stdout[:100]}...")
    else:
        print("✗ FAILED")
        print(f"Stderr: {result.stderr}")
except Exception as e:
    print(f"✗ Exception: {e}")
