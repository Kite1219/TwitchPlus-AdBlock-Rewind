# TwitchPlus

**Rewind live streams. Jump back to LIVE. Keep your favorite channels close.**

![Version](https://img.shields.io/badge/version-1.2.2--beta.6-9146FF) ![Platform](https://img.shields.io/badge/platform-iPhone%20%7C%20iPad-555) ![Status](https://img.shields.io/badge/status-beta-orange)

## Download

### [Download the latest IPA](https://github.com/Kite1219/TwitchPlus/releases/download/v1.2.2-beta.6/TwitchPlus-1.2.2-Beta6-unsigned.ipa)

[Release notes and downloads](https://github.com/Kite1219/TwitchPlus/releases) · [Report a problem](https://github.com/Kite1219/TwitchPlus/issues/new)

The home-screen app name stays **Twitch**. This is an **unsigned beta**; sign it using your normal sideloading or LiveContainer workflow.

## What you get

| Feature | What it does |
| --- | --- |
| **Native live rewind** | Scrub through an available ongoing recording in the existing video player. No separate browser or popup. |
| **Purple timeline** | Full-width Twitch-colored progress bar above the normal bottom controls. |
| **Precise timestamps** | HH:MM:SS shows your selected position while dragging and during replay. Hidden at live. |
| **Minimal thumb** | A small white dot appears only while dragging. |
| **10-second skips** | Circular back/forward controls grouped around the middle of the player. |
| **LIVE shortcut** | Red LIVE badge at live; a dark return-to-live badge when behind. Positioned above the right edge of the timeline. |
| **Background preparation** | Recording access and manifests prepare while you watch live. |
| **Local Forced Follow** | Save a channel locally and include it in native live Following lists, including the iPad sidebar. This does not follow the channel on Twitch's servers. |
| **Native read-only chat fallback** | Anonymous read-only chat can appear in the existing chat area when the signed-in chat is unavailable. It does not grant permission to send messages. |
| **Existing ad blocking** | Preserves the TwitchAdBlock component supplied in the base IPA. This project did not author that component. |
| **iPhone and iPad layouts** | Uses native controls and preserves the existing iPad Following fix. Device coverage is still incomplete. |

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
