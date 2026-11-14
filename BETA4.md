# v1.5 Beta 4 — native playlist filtering and wide-phone layout

Beta 3 did not fix the device failures reported by the maintainer. Its host tests did not establish that ads were blocked or that Duo rendered correctly. Beta 4 replaces that implementation rather than treating those tests as proof of a fix.

## Investigation

- Downloaded official [Rizin 0.9.1](https://github.com/rizinorg/rizin/releases/tag/v0.9.1) and disassembled the bundled Amazon IVS player. `IVSPlayerURLSessionDelegate` exposes data/completion callbacks with the expected five-object-call ABI. Data reaches the native consumer before completion removes the request.
- Downloaded the current official Pie CRX: **1.33.9**, SHA-256 `7ba1ab6266b643c8200945d4d6933f3637500c79e0903beb41c10fa3a4255e50`. Its Twitch script is unchanged from the earlier inspection. It intercepts worker responses and includes an Android autoplay fallback; polling separate manifests after playback starts does not reproduce that behavior.
- Inspected [Twitch AdBlock HQ](https://github.com/Nello1717/TwitchAdBlock) at `9ab8e5c827c5ab5a09ee3d605989cc0b0787650b`. Its MIT-licensed playlist parser/timeline is adapted for the native response engine, with attribution and the full license embedded in the binary. No Pie code or extension assets are distributed.
- Whole-playlist swaps can change session-relative sequence numbers. Ad markers can also remain while the actual newest segments are live. The replacement distinguishes those cases and preserves a continuous timeline.
- [Apple documents](https://developer.apple.com/documentation/uikit/uibarbuttonitem/hidessharedbackground) that shared-background settings are ignored for multi-item bar-button groups. The old icon-count/cover heuristic did not identify those groups.

The original blocker's proxy health and actual device-side settings were not established. Beta 4 replaces `TwitchAdBlock.dylib`, removing its proxy/token-rewrite hooks. The earlier rejected proxy credential probe was not retried. The replacement uses anonymous requests to Twitch with no third-party proxy.

## Native response filtering

`TwitchPlusFixes.m` recognizes both usher API paths, maps video renditions to streams, buffers split playlist bodies within 1 MiB, and transforms complete responses before IVS receives them. Unrelated requests and media segments pass through. Slow backup requests run off IVS's delegate queue; delivery returns to that queue afterward.

The embedded JavaScriptCore engine parses actual segments, removes ad announcements without dropping live content, aligns channel-wide sequence numbers, avoids duplicates, and emits discontinuities when renditions change. The native adaptation preserves fMP4 maps, encryption keys / implicit AES IVs, and byte ranges. Rewritten responses omit prefetch/partial-segment hints that might leak ad media.

On an actual ad at the live edge, anonymous popout, mobile_web and Android autoplay sessions are tried in parallel. Compatible codecs are required. Exact or lower compatible renditions, including 360p, may be used. Original live content returns when usable. The filter never calls play, seeks or reloads the player.

If no clean source exists, available live history can hold the last frames while later polls retry. At startup with neither history nor a usable backup, the original response is preserved; ads can still appear in that case. Separate client-side/display ads, unsupported formats, changed private APIs and regions without usable sources remain limitations. This prerelease cannot guarantee ad-free playback.

**Live ad recovery** defaults on and is independent of optional automatic rewind. Its setting is latched when a stream opens: reopen the stream after changing it. Automatic rewind preserves its existing choice and defaults off.

## Duo layout

Wide phones use the window's regular-width trait, not guessed screen dimensions, to select native compact navigation by default. The override is removed on folding/narrowing. iPad navigation is retained. **Compact layout on wide phones** in Rewind Settings can be disabled for sidebar testing.

Feed fitting checks all clipping ancestors, the window, and identifiable visible sidebar overlays. Source dimensions can come from the player before the feed caches them. Internal rendering constraints remain owned by Twitch. Theater video backgrounds extend horizontally into the reserved status area; controls retain native constraints. Natural aspect-ratio letterboxing may remain.

Toolbar groups are split before applying Apple's background options. Original items, targets and menus remain intact. The old image-count replacement/cover heuristic is removed.

Only NativeRewind and TwitchAdBlock libraries are replaced. The main executable and Info.plist stay byte-identical to v1.4. The shipping filter is compiled on a Mac against Apple's actual Foundation, UIKit and JavaScriptCore SDK headers. SDK/Xcode versions accompany the release.

## Evidence and limits

Rewind Settings shows **Beta 4** and **Copy runtime diagnostics**. It copies installed-hook flags, real manifest/ad/substitution counters, window traits and the latest feed/theater geometry. No account tokens or signed URLs are included; nothing is sent anywhere.

Local checks cover 66 rewind/preferences host tests, 8 compiled C geometry/buffer tests, 15 upstream playlist tests, 15 native-engine tests and 7 packaging tests. These exercise policy/parser code and packaging, not Twitch on iOS.

Anonymous live probes succeeded for ohnepixel, caedrel and jynxzi247: 1080p popout/mobile_web and 360p Android autoplay sources were usable. Those samples contained live content, so this verifies request compatibility rather than an observed ad break.

Actual hook execution, Duo rendering, decoding through a real ad break, casting and installation require device testing. No device success is claimed by build/package checks.
