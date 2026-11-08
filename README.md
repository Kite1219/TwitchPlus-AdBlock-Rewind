# TwitchPlus — Twitch Ad Block + Live Rewind for iPhone & iPad

![TwitchPlus — Ad Block and Live Rewind](assets/hero.svg)

**Twitch ad blocking + native live rewind, with Anti-Ban chat and local Forced Follow.**

Go back to a moment you missed, skip in ten-second steps, and return to LIVE—all in the existing player. The included TwitchAdBlock base handles ad blocking.

![Version](https://img.shields.io/badge/version-1.2.2--beta.6-9146FF) ![Platform](https://img.shields.io/badge/platform-iPhone%20%7C%20iPad-555) ![Status](https://img.shields.io/badge/status-beta-orange)

[![Download IPA](https://img.shields.io/badge/Download_IPA-9146FF?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/releases/latest)
[![Releases](https://img.shields.io/github/v/release/Kite1219/TwitchPlus-AdBlock-Rewind?style=for-the-badge&label=Updates)](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/releases)
[![GitHub stars](https://img.shields.io/github/stars/Kite1219/TwitchPlus-AdBlock-Rewind?style=for-the-badge)](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind)

**Find it useful? Give the repo a star to help other people discover it.**

## Download

### [Download the latest IPA](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/releases/download/v1.2.2-beta.6/TwitchPlus-1.2.2-Beta6-unsigned.ipa)

[Release notes and downloads](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/releases) · [Report a problem](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/issues/new)

The home-screen app name stays **Twitch**. This is an **unsigned beta**; sign it using your normal sideloading or LiveContainer workflow.

## Ad Block + Live Rewind, plus more

| Feature | What it does |
| --- | --- |
| **Ad Block** | Includes the existing TwitchAdBlock component from the supplied base IPA. Ad-blocking behavior depends on that component and Twitch changes. |
| **Native live rewind** | Scrub through an available ongoing recording in the existing video player. No separate browser or popup. |
| **Purple timeline** | Full-width Twitch-colored progress bar above the normal bottom controls. |
| **Precise timestamps** | HH:MM:SS shows your selected position while dragging and during replay. Hidden at live. |
| **Minimal thumb** | A small white dot appears only while dragging. |
| **10-second skips** | Circular back/forward controls grouped around the middle of the player. |
| **LIVE shortcut** | Red LIVE badge at live; a dark return-to-live badge when behind. Positioned above the right edge of the timeline. |
| **Background preparation** | Recording access and manifests prepare while you watch live. |
| **Anti-Ban: read chat** | Anonymous, read-only chat in the native chat area when a channel ban blocks your signed-in chat view and public chat remains accessible. |
| **Anti-Ban: Forced Follow** | Keep a banned channel in your local live Following list for quick access, even when Twitch will not let your account follow it. Includes the iPad sidebar. |
| **Existing ad blocking** | Preserves the TwitchAdBlock component supplied in the base IPA. This project did not author that component. |
| **iPhone and iPad layouts** | Uses native controls and preserves the existing iPad Following fix. Device coverage is still incomplete. |

## Anti-Ban: read chat + Forced Follow

A channel ban can leave you unable to read that channel's chat in the app or follow the channel for quick access. **Anti-Ban combines two local workarounds:**

- **Read chat while banned:** the native chat area can use an anonymous, read-only connection when public chat is available. No extra chat window or manual streamer-name entry.
- **Forced Follow:** add the channel to your device's Following list without performing a real Twitch follow. When the channel is live, it can appear alongside your normally followed live channels, including in the iPad sidebar.

### Why Forced Follow?

If you cannot follow a banned channel, it disappears from your usual quick-access list. Forced Follow lets you keep it within reach and see it when live instead of searching for it every time.

1. Open the channel page and tap **Forced Follow**.
2. The button changes to **Forced Following**. The channel is saved on this device.
3. Look in your live Following list when the channel is broadcasting. Tap the button again to remove the local entry.

These features bypass the **app-side viewing and local-list limitations** for accessible public content. They **do not remove the channel ban**, restore permission to send chat messages, or create a real server-side follow. Saved channels are local to the app's data; they do not sync as actual Twitch follows.

## Updates and version downloads

**[Open all releases](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/releases)** to download an IPA and read its update notes. Open a version and expand **Assets** if needed; choose the **`.ipa` file**, not GitHub's automatically generated source-code ZIP.

Each newly published version gets its own release, IPA, update notes, checksum, and validation summary. Older published releases remain on GitHub when local build copies are cleaned up. Builds made before this repository existed are described in the changelog but do not have historical IPA assets here.

## Install

1. Download the IPA from the link above.
2. Sign all executable components with your preferred sideloading setup, or use your existing LiveContainer workflow.
3. Open a live channel and tap the video to show its controls. Drag the timeline, use the ten-second skips, or tap LIVE.

Keep the same app identity when updating if you want to retain local saved channels. Rewind is unavailable when Twitch does not expose an accessible ongoing recording.

## Latest performance changes

- One startup seek instead of two potentially competing seeks.
- Rapid skip taps combine into one final requested position over a short 120ms window.
- Ready preparation stays available until its replacement is actually ready.
- Stale or insufficient prepared history is rejected.
- Preparation begins when the stream loads; temporary API failures retry sooner.

## Beta status: please read

The custom components are pinned to the supplied **Twitch 30.7** binary layout. Do not assume they support arbitrary Twitch versions.

Previous builds were tested by the maintainer on a phone. This release passes **35 host tests** and IPA integrity/preservation checks, but the performance changes have **not** been benchmarked on an iPhone or iPad. LiveContainer, normal sideloading, rotation, playback lifecycle, and different device sizes still need wider testing. Some buffering is controlled by Twitch, the video decoder, and your connection; instant or flawless playback is not promised.

When reporting a problem, include your device, iOS/iPadOS version, installation method, channel, and whether the delay happened entering rewind or while already rewound. Never post account tokens or signing credentials.

## Source and rebuilding

`src/` contains the custom NativeRewind, NativeChat, ForcedFollow, and public metadata-query sources. `tools/` contains the native build and bring-your-own-base packaging helpers. The original Twitch application and third-party ad blocker are not source code owned by this project; no license for those components is granted here.

See [BUILD.md](BUILD.md). The packaged release retains the existing base app and ad-blocking component; custom source is published so the changes can be inspected.

Unofficial project. Not affiliated with or endorsed by Twitch, Amazon, YouTube, Apple, or the base IPA's original maintainers.
