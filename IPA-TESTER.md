# Twitch IPA Tester

An offline package inspector and device test report for TwitchPlus. It does not run an IPA in a browser or emulate iOS. Package checks work on Windows, macOS and Linux with Python 3.9+; no Python packages or accounts are required.

## Easiest: run on GitHub

Open **[Actions → Test Twitch IPA](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/actions/workflows/test-ipa.yml)**, select **Run workflow**, and leave the Beta 3 defaults. It downloads that release from this repository, checks the GitHub asset digest, compares it with the pinned v1.4 base, and runs the source regressions. Download the `twitch-ipa-test-report` artifact and open `report.html`.

The workflow accepts a release tag and exact `.ipa` asset name from this repository. Source tests check out the selected release tag and require the rebuilt native library to match the IPA exactly. The compiler is downloaded only for source tests. Reports are retained for three days; the published tester release also includes the initial Beta 3 report.

## Run on your laptop

Download and unzip **[Twitch IPA Tester v1.0.0](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/releases/tag/ipa-tester-v1.0.0)**. With Python installed, run:

```sh
python3 tools/test-twitch-ipa.py --gui
```

Choose the IPA. The report opens in your browser, and a results folder is created beside the IPA. On Windows, use `py` in place of `python3`. The file picker needs Python's optional Tk support; the command below works without it.

```sh
python3 tools/test-twitch-ipa.py "/path/to/TwitchPlus.ipa" --output-dir results
```

Open `results/report.html`. No files are uploaded, no credentials are read, and no iOS binaries are executed. The inspector streams the archive without extracting it. JSON results are in `results/report.json`; the command exits with `1` for failed checks and `0` for a package with no failed checks. Warnings and pending device tests remain visible even when the command succeeds.

For Beta 3's full verification:

```sh
python3 tools/test-twitch-ipa.py TwitchPlus-v1.5-beta.3-Duo-fit-native-ad-recovery-unsigned.ipa \
  --baseline TwitchPlus-base-v1.4.ipa \
  --expect-sha256 2e2e748a3caa120f5a1852fd6d1fe10fc0f3ae36ca10b1ce8df9f76b9c8ad6f9 \
  --output-dir results
```

## What it checks

- SHA-256 and, when supplied, the expected release digest.
- ZIP CRCs, duplicates, ambiguous paths, escaping symlinks and bounded archive sizes.
- Main application metadata and executable presence.
- Thin and universal Mach-O slice bounds, load commands, segments and sections.
- Physical iOS ARM64 support, declared FairPlay encryption, minimum OS and SDK consistency.
- Required bundled library paths, including inherited executable runpaths.
- Twitch 30.7 compatibility declaration, loaded custom libraries and a native initializer.
- Beta 3's settings / recovery / feed-hook compiled markers and Duo opt-in metadata.
- Optional byte-for-byte preservation against a reference IPA. Only `NativeRewind.dylib` may change; this comparison is intended for the unsigned release archives before re-signing.
- Optional source regressions and an exact match between the tested library and the packaged tweak.

The default `beta3` profile expects Beta 3 features. Use `--profile twitchplus` for older custom releases, or `--profile generic` for general iOS package structure without TwitchPlus-specific requirements. Code-signature presence is informational; this tool does not cryptographically verify signing identities, provisioning, entitlements, symbol resolution or private runtime ABI compatibility.

## Native source regression tests

On Linux, with this project's pinned Rust 1.99.0 compiler component installed:

```sh
python3 tools/test-twitch-ipa.py TwitchPlus.ipa \
  --source-tests --compiler-root /path/to/rustc-component \
  --source-repo /path/to/checkout-of-the-ipa-release \
  --output-dir results
```

This runs the release checkout's build and host tests, captures `source-tests.log`, and checks that its `build/NativeRewind.dylib` is byte-identical to the IPA's library. A different binary is a failed provenance check, even if the tests themselves pass. Host tests use mocks for UIKit and player behavior; they do not test Apple's runtime or Twitch's servers.

To test the inspector itself:

```sh
python3 tests/test_ipa_tester.py
```

## Test on the actual device

The HTML report includes a checklist for launch, full-width Duo backgrounds, sidebar preview fit, toolbar icon / taps, settings persistence, both rewind modes, observed ad breaks, failed recovery and playback lifecycle. Fill it out while using the signed IPA. An ad test with no observed ad break must be recorded as **Not observed**, not a pass.

**Download session report** saves a local JSON file with your observations. Automatic checks and manual observations remain separate, and `deviceTested` is never changed to true by the automatic checks. Save the session before closing the page; form entries are not stored or uploaded. Record ordinary device details and symptoms, not tokens or signing credentials.

Actual UI geometry, native runtime crashes and ad-block effectiveness still require a real iPhone/iPad test. The published Beta 3 report has no device observations.
