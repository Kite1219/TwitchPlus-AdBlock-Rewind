#!/usr/bin/env bash
set -euo pipefail
# Pass the rustc component directory from Rust 1.99.0 as the first argument.
compiler_root="${1:?Usage: build-rewind-linux.sh /path/to/rustc-component}"
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"
mkdir -p build
export RUSTC_BOOTSTRAP=1
"$compiler_root/bin/rustc" --edition 2024 --target aarch64-apple-ios --crate-type lib --emit=obj -C panic=abort -C opt-level=s -C overflow-checks=no src/NativeRewind.rs -o build/NativeRewind.o
"$compiler_root/lib/rustlib/x86_64-unknown-linux-gnu/bin/gcc-ld/ld64.lld" -dylib -arch arm64 -platform_version ios 16.4 16.4 -install_name @executable_path/Frameworks/NativeRewind.dylib -undefined dynamic_lookup -no_adhoc_codesign -o build/NativeRewind.dylib build/NativeRewind.o
python tests/build-host.py
"$compiler_root/bin/rustc" --edition 2024 --crate-type cdylib --emit=obj -C panic=abort -C opt-level=s -C overflow-checks=no -A warnings tests/NativeRewind-host.rs -o build/host.o
"$compiler_root/lib/rustlib/x86_64-unknown-linux-gnu/bin/gcc-ld/ld.lld" -shared -o tests/NativeRewind-test.dll build/host.o
python tests/test_native.py
