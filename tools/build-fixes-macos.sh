#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"
mkdir -p build
python3 tools/embed-playlist-engine.py
sdk_path="$(xcrun --sdk iphoneos --show-sdk-path)"
# Compile the shipping module against Apple's real Foundation/UIKit headers.
# Availability is guarded with respondsToSelector for older deployment targets.
xcrun --sdk iphoneos clang -arch arm64 -mios-version-min=16.4 -isysroot "$sdk_path" \
  -DTP_USE_APPLE_SDK -fobjc-arc -fblocks -fvisibility=hidden -Os -Wall -Wextra -Werror \
  -Wno-unguarded-availability-new -Wno-deprecated-declarations \
  -dynamiclib -Wl,-no_adhoc_codesign \
  -install_name @executable_path/Frameworks/TwitchAdBlock.dylib \
  -framework Foundation -framework UIKit -framework JavaScriptCore \
  src/TwitchPlusFixes.m src/TwitchPlusCore.c -o build/TwitchAdBlock.dylib
xcrun --sdk iphoneos --show-sdk-version > build/apple-sdk-version.txt
xcodebuild -version > build/xcode-version.txt
