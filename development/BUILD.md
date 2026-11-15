# Building TwitchPlus

The compiled-source commit is recorded in `development/release.json`. Promotion to v1.5 did not rebuild the IPA.

## GitHub Actions

[Build TwitchPlus Release](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/actions/workflows/release.yml) runs manually. Enter a plain version such as **v1.6**. It builds with Apple's SDK, runs UIKit fixtures and host tests, rebuilds rewind, packages against the pinned v1.4 base, then publishes a regular release titled **TwitchPlus v1.6**. It does not create prereleases.

Editing documentation does not trigger an IPA release. The workflow downloads the pinned compiler and base inside GitHub's runners, not onto your PC.

## Local components

On the current main branch, run commands from `development/`. The historical v1.5 source tag uses the original root-level layout; run there without this extra `cd`.

- `tools/build-fixes-macos.sh`: layout and playlist filter using an installed Apple SDK.
- `tools/build-rewind-linux.sh /path/to/rustc-component`: rewind and host tests using Rust 1.99.0.
- `tools/package-rewind-update.py`: replace both libraries in an existing unsigned TwitchPlus base.
- `tools/package.py` and `tools/build-native.ps1`: original custom-library/base packaging helpers.

After building both replacement libraries:

```sh
python3 tools/package-rewind-update.py --base base-v1.4.ipa --library build/NativeRewind.dylib --ad-library build/TwitchAdBlock.dylib --output output/TwitchPlus.ipa
```

Pinned v1.4 base SHA-256: `6d573ecfc6686bed9a15fc061b315cc19ead5f93faab7fc5594d23aa4f104665`. The integrations target Twitch 30.7. The original Twitch app, signing identity, compiler and Apple SDK are not supplied as repository source assets.

Re-sign every executable component. Automated checks do not establish real-device compatibility or ad-block success. See the [package tester](IPA-TESTER.md) and [historical notes](archive/README.md).
