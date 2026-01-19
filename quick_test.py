#!/usr/bin/env python3
import sys
import os
import asyncio

sys.path.insert(0, "/home/deck/homebrew/plugins/DeckTune")

from backend.core.ryzenadj import RyzenadjWrapper

async def test():
    w = RyzenadjWrapper("/home/deck/homebrew/plugins/DeckTune/bin/ryzenadj", "/home/deck/homebrew/plugins/DeckTune", None)
    result = await w.diagnose()
    print("=" * 60)
    print("DIAGNOSE RESULT:")
    print("=" * 60)
    for key, value in result.items():
        if key == "test_command_result" and value:
            print(f"{key}: {value[:100]}...")
        else:
            print(f"{key}: {value}")
    print("=" * 60)
    if result["error"]:
        print("FAILED!")
        return 1
    else:
        print("SUCCESS!")
        return 0

exit_code = asyncio.run(test())
sys.exit(exit_code)
