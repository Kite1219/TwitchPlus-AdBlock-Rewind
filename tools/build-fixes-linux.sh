#!/usr/bin/env bash
set -euo pipefail
compiler_root="${1:?Usage: build-fixes-linux.sh RUST_COMPONENT ZIG_DIRECTORY}"
zig_root="${2:?Pass the Zig 0.14.1 directory}"
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"
mkdir -p build
export ZIG_GLOBAL_CACHE_DIR="$repo_root/build/zig-cache"
export ZIG_LOCAL_CACHE_DIR="$repo_root/build/zig-local-cache"
python3 tools/embed-playlist-engine.py
"$zig_root/zig" cc -target aarch64-ios -mios-version-min=16.4 -fobjc-arc -fblocks -ffreestanding -fvisibility=hidden -Os -Wall -Wextra -Werror -c src/TwitchPlusFixes.m -o build/TwitchPlusFixes.o
"$zig_root/zig" cc -target aarch64-ios -mios-version-min=16.4 -ffreestanding -fvisibility=hidden -Os -Wall -Wextra -Werror -c src/TwitchPlusCore.c -o build/TwitchPlusCore.o
"$compiler_root/lib/rustlib/x86_64-unknown-linux-gnu/bin/gcc-ld/ld64.lld" -dylib -arch arm64 -platform_version ios 16.4 16.4 -install_name @executable_path/Frameworks/TwitchAdBlock.dylib -undefined dynamic_lookup -no_adhoc_codesign -o build/TwitchAdBlock.dylib build/TwitchPlusFixes.o build/TwitchPlusCore.o
cc -shared -fPIC -O2 -Wall -Wextra -Werror src/TwitchPlusCore.c -o build/TwitchPlusCore-test.so
python3 tests/test_fixes_core.py
node tests/playlist-upstream.test.js
node tests/playlist-native.test.js
