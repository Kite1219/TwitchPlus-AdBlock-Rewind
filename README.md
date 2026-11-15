# TwitchPlus

Ad blocking, live rewind, read-only chat and local Forced Follow for iPhone and iPad, with iPhone Duo layout adaptations.

## Download

### [Download TwitchPlus v1.5](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/releases/download/v1.5/TwitchPlus-v1.5.ipa)

[Latest release](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/releases/latest) · [Version history](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/releases) · [Report a problem](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/issues/new)

The home-screen name remains **Twitch**.

## Features

- **Ad blocking:** native live-playlist filtering and alternate-source recovery, without a third-party proxy.
- **Live rewind:** purple timeline, HH:MM:SS position, 10-second skips and LIVE. Automatic rewind is optional and off by default.
- **Read-only chat:** anonymous public-chat fallback in the native chat area when the signed-in view is blocked.
- **Forced Follow:** save channels in the local Following list for quick access, including the iPad sidebar.
- **Duo layouts:** compact navigation on wide phones, chat-aware video sizing, aligned controls and rotation handling. Video keeps its aspect ratio.

Read-only chat and Forced Follow do not remove bans, enable posting while banned, or create real Twitch follows.

## Install

1. Download the **.ipa** asset, not the source-code ZIP.
2. Sign all executable components with your usual sideloading setup, or use your existing LiveContainer workflow.
3. Open a stream. Use the sliders button on the purple timeline to open **Rewind Settings**.

Keep the same app identity when updating to retain local settings and saved channels.

## Compatibility

Based on **Twitch 30.7**, minimum iOS **16.4**. Rewind requires an accessible ongoing recording. Ad blocking depends on available clean playback sources and may not suppress every ad.

v1.5 is the former Beta 5 build, promoted unchanged to a regular release. Automated package, host and UIKit-fixture checks passed; the fixtures do not run Twitch or establish physical-device playback or ad-block effectiveness. The installed settings heading may still say “Beta 5.”

## Development

[Build guide](development/BUILD.md) · [Package tester](development/IPA-TESTER.md) · [Release notes](development/releases/v1.5.md) · [Changelog](CHANGELOG.md)

All development material is kept in `development/`: source, tests, build tools, release records and archived notes. Historical investigation notes are in [development/archive](development/archive/README.md).

Unofficial community project. Not affiliated with Twitch, Amazon or Apple. Upstream attribution is retained in [third_party](development/third_party/).
