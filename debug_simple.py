#!/usr/bin/env python3
import telegram
import telegram.ext

print(f"telegram version: {telegram.__version__}")
print(f"telegram.ext path: {telegram.ext.__file__}")

# Test simplest possible
from telegram.ext import Updater

print("\nTrying Updater with just token...")
try:
    updater = Updater("dummy_token")
    print("✅ Updater() works with just token")
except Exception as e:
    print(f"❌ Failed: {e}")

print("\nTrying Updater with use_context...")
try:
    updater = Updater("dummy_token", use_context=True)
    print("✅ Updater() works with use_context=True")
except Exception as e:
    print(f"❌ Failed: {e}")
