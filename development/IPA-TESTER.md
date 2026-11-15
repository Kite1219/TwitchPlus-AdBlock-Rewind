# Package testing

The offline inspector checks IPA structure, hashes and native-library packaging. It does not emulate iOS or certify ad blocking.

## GitHub Actions

Open [Test Twitch IPA](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/actions/workflows/test-ipa.yml). Defaults target **v1.5 / TwitchPlus-v1.5.ipa**, using the `twitchplus` profile.

Leave the legacy baseline comparison off for v1.5: that comparison allows only NativeRewind to change, but v1.5 also replaces TwitchAdBlock. The release packaging validation records preservation of all other members.

## Local use

Python 3.9+ is sufficient for package checks. Run from `development/` on the current main branch:

```sh
python3 tools/test-twitch-ipa.py TwitchPlus-v1.5.ipa --profile twitchplus --expect-sha256 4696b3c3b7026cc52332a51f56900d699fed3ce2b133a7ada4d78ee819eeb07a --output-dir results
```

Open `results/report.html`; a JSON report is saved alongside it. No files are uploaded and account credentials are not read.

Use `--profile generic` for general IPA structure. The legacy `beta3` profile checks historical markers and should not be used for the current release.

## Source and device checks

`--source-tests` requires matching release sources and the pinned Rust compiler. See the [build guide](BUILD.md). Package tests do not prove signing entitlements, private API compatibility or live playback.

On a device, verify launch, chat on/off, both rotation directions, rewind/LIVE, settings persistence and an observed ad break. “No ad observed” is not proof of blocking.

[Back to TwitchPlus](../README.md)
