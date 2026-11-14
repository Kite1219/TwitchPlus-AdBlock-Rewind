**Current version:** Beta 2 makes automatic rewind optional and OFF by default. Open Rewind Settings using the sliders button at the left of the purple timeline. See [BETA2.md](BETA2.md). The earlier always-on behavior below describes Beta 1.

# Experimental automatic rewind

Based on the public v1.4 IPA and its attached `v1.4-update-sources.zip`, whose NativeRewind source includes newer responsive layout fixes than the repository main branch.

On each recognized live-channel load, automatically enter the accessible ongoing recording and seek to one second before its available end. This uses the same replay path as the rewind button. It runs even before playback controls appear. Manual rewind takes over; LIVE or a failed replay cancels the automatic switch until the next channel load. There is no repeated seek on every timer tick.

This is one second before the recording end, not necessarily one second behind the actual broadcast: recording availability and metadata can lag. The live source starts normally while recording access is fetched, so this cannot guarantee suppression of startup ads. Channels without accessible ongoing recordings stay live. The bundled TwitchAdBlock library is preserved byte for byte. Ad effectiveness has not been tested on a device.

## Build and validate on Linux

Use the Rust 1.99.0 rustc component including its bundled LLVM linker:

```sh
bash tools/build-rewind-linux.sh /path/to/rustc-component
python tools/package-rewind-update.py --base /path/to/v1.4.ipa --library build/NativeRewind.dylib --output build/TwitchPlus-auto-rewind-unsigned.ipa
```

46 host tests pass, including one automatic switch without visible controls, waiting for recording access, LIVE cancellation, existing replay/fallback behavior, and responsive geometry tests. These mock Apple APIs and do not establish runtime behavior on iOS. Packaging verifies archive CRCs and every member hash: only NativeRewind.dylib changes. Re-sign all executable components before installing.

## Duo layout test update

Skip controls now also require clearance from the full-width timeline and the timestamp, preventing overlap in short resized player panes. Controls restore when space permits. Detaching the player keeps the timestamp hidden during timer refreshes. 49 host tests pass, including geometry sweeps and detachment; device testing remains required. This update addresses the custom player overlay, not all native Twitch navigation layouts.
