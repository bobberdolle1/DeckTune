#!/usr/bin/env python3
"""
Test script to verify binning functionality works.
This simulates what the plugin does when binning starts.
"""

import asyncio
import os
import sys

# Add plugin directory to path
PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, PLUGIN_DIR)

from backend.core.ryzenadj import RyzenadjWrapper
from backend.platform.detect import detect_platform

async def test_binning_prerequisites():
    """Test that binning prerequisites are met."""
    print("=" * 60)
    print("Testing Binning Prerequisites")
    print("=" * 60)
    print()
    
    # 1. Detect platform
    print("1. Detecting platform...")
    try:
        platform = detect_platform()
        print(f"   ✓ Platform: {platform.model} ({platform.variant})")
        print(f"   ✓ Safe limit: {platform.safe_limit}mV")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # 2. Initialize ryzenadj
    print()
    print("2. Initializing ryzenadj...")
    ryzenadj_path = os.path.join(PLUGIN_DIR, "bin", "ryzenadj")
    try:
        wrapper = RyzenadjWrapper(ryzenadj_path, PLUGIN_DIR, None)
        print(f"   ✓ RyzenadjWrapper created")
        print(f"   ✓ Binary path: {ryzenadj_path}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # 3. Run diagnostics (this is what binning does)
    print()
    print("3. Running ryzenadj diagnostics...")
    print("   (This is what binning does before starting)")
    try:
        result = await wrapper.diagnose()
        
        print(f"   Binary exists: {result['binary_exists']}")
        print(f"   Binary executable: {result['binary_executable']}")
        print(f"   Sudo available: {result['sudo_available']}")
        
        if result['test_command_result']:
            print(f"   ✓ Test command: SUCCESS")
            print(f"   Output preview: {result['test_command_result'][:100]}...")
        else:
            print(f"   ✗ Test command: FAILED")
            if result['error']:
                print(f"   Error: {result['error']}")
        
        if result['error']:
            print()
            print(f"   ⚠ Warning: {result['error']}")
            return False
        else:
            print()
            print("   ✓ All diagnostics passed!")
            return True
            
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_apply_values():
    """Test applying undervolt values."""
    print()
    print("=" * 60)
    print("Testing Undervolt Application")
    print("=" * 60)
    print()
    
    ryzenadj_path = os.path.join(PLUGIN_DIR, "bin", "ryzenadj")
    wrapper = RyzenadjWrapper(ryzenadj_path, PLUGIN_DIR, None)
    
    # Test with safe values
    test_values = [-10, -10, -10, -10]
    print(f"Applying test values: {test_values}")
    print("(These are very safe values)")
    print()
    
    try:
        success, error = await wrapper.apply_values_async(test_values)
        
        if success:
            print("✓ Values applied successfully!")
            print()
            print("Commands executed:")
            for cmd in wrapper.get_last_commands():
                print(f"  {cmd}")
            
            # Reset to 0
            print()
            print("Resetting to 0...")
            success_reset, error_reset = await wrapper.disable_async()
            if success_reset:
                print("✓ Values reset to 0")
            else:
                print(f"✗ Reset failed: {error_reset}")
            
            return True
        else:
            print(f"✗ Failed to apply values: {error}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print()
    print("=" * 60)
    print("DeckTune Binning API Test")
    print("=" * 60)
    print()
    print("This test verifies that binning can work properly.")
    print("It checks the same things that binning checks before starting.")
    print()
    
    # Test prerequisites
    prereq_ok = await test_binning_prerequisites()
    
    if not prereq_ok:
        print()
        print("=" * 60)
        print("RESULT: PREREQUISITES FAILED")
        print("=" * 60)
        print()
        print("Binning will NOT work because ryzenadj diagnostics failed.")
        print("This is the same error you would see in the UI.")
        print()
        return 1
    
    # Test applying values
    apply_ok = await test_apply_values()
    
    print()
    print("=" * 60)
    if prereq_ok and apply_ok:
        print("RESULT: ALL TESTS PASSED ✓")
        print("=" * 60)
        print()
        print("Binning should work correctly!")
        print("The plugin can:")
        print("  ✓ Detect platform")
        print("  ✓ Initialize ryzenadj")
        print("  ✓ Run diagnostics (--info)")
        print("  ✓ Apply undervolt values")
        print("  ✓ Reset values")
        print()
        print("You can now use Silicon Binning in the UI.")
        return 0
    else:
        print("RESULT: SOME TESTS FAILED ✗")
        print("=" * 60)
        print()
        print("There are still issues that need to be fixed.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
