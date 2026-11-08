# Rebuilding

The current custom sources were compiled with **rustc 1.99.0 (2026-09-28)** using the experimental `no_core` ABI bridge and LLVM `ld64.lld`. Compiler internal language items can change; another Rust version may require source adjustments. This build uses the existing local toolchain; the scripts do not download dependencies.

On Windows with PowerShell, Python 3, and that Rust/LLVM toolchain available:

```powershell
./tools/build-native.ps1 -CompilerRoot C:/path/to/rust/compiler
python ./tools/package.py --base C:/path/to/tv.twitch-30.7-TwitchAdBlock-0.1.13.ipa --libs ./build --output ./build/TwitchPlus-unsigned.ipa
```

Supply your own decrypted, thin ARM64 Twitch 30.7 base with its existing TwitchAdBlock component. The packager refuses encrypted executables, different app versions, insufficient header padding, duplicate archive members, and output paths that overwrite the input. It preserves the original files except the main executable's load-command padding and adds the three custom libraries plus the ForcedFollow query. Sign every executable component before installing.

This repository does not bundle a signing identity, an Apple account, the Rust toolchain, or an iOS SDK. The experimental dylib bridge resolves Apple and app symbols at runtime; compilation and archive checks do not replace real-device testing.
