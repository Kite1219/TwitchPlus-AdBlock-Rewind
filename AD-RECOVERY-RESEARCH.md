# Native ad recovery investigation

## Existing blocker

The v1.4 IPA includes TwitchAdBlock 0.1.18 built for Twitch 31.9 inside a Twitch 30.7 host. Inspection of its published source shows three relevant dependencies: Foundation/AVURLAsset request hooks, playback-token parameter rewriting to random UUID values, and an upstream proxy. Failure or mismatch in any one of those paths can leave native playback with ads. The user's actual runtime hook coverage, settings, region and proxy health cannot be established from screenshots. This investigation does not prove a single root cause.

Automatic approval review rejected a proposed proxy health check because it would decode and send the bundled embedded proxy credential to an external service. That check was not executed or retried through another route. Proxy health remains unverified; no proxy credential is included in this report or new native recovery implementation.

## Pie inspection

The publicly downloadable Pie Chrome extension package inspected was version 1.33.9. Static inspection (without installing or executing it) found `assets/scripts/twitch-vaft-userscript-v2.js`, reporting TwitchAdSolutions version 58. Its browser-side approach includes detecting Twitch ad playlist markers and requesting alternate playback types. It also contains browser-worker/fetch interception and segment-handling logic that does not directly run inside an IVS iOS player.

No Pie script or proprietary extension asset is copied into this repository or IPA. The new native implementation is independently written around public HLS markers and Twitch's existing playback interfaces. It implements only the alternate-source recovery concept, not the entire Pie/VAFT engine.

## Native implementation

- Watch recognized live IVS loads, outside manual recording replay, while buffering or playing. Check at most one job per player at a time, normally every five seconds. Do not restart paused or ended players.
- Fetch only HTTPS playlist URLs on ttvnw.net or its subdomains. Accept successful UTF-8 HLS responses under 1 MiB. Resolve relative video variant URIs, skip audio-only entries, and inspect a video media playlist rather than mistaking the master for ad-free content.
- Detect explicit EXT-X-CUE-OUT and Twitch ad DATERANGE classes. Ordinary URLs containing words such as ad or processing are not sufficient evidence.
- On an ad marker, attempt anonymous playback tokens for site, popout and mobile_web, subject to a bounded attempt/deadline policy and a 45-second cooldown. The literal web platform and variable named kind avoid the old blocker's known random-platform variable rewrite. No account OAuth header or account cookie is added by this code, and it contacts Twitch directly rather than a new third-party proxy.
- Only switch to a candidate after fetching a valid media playlist with no recognized ad markers. Keep the original live URL/source. If no candidate is clean, continue normal playback rather than deleting segments or freezing the player.
- Generation/login checks discard stale requests. Settings, manual replay, external playback, paused state and ended state are checked before applying. A decode/load error on a selected candidate restores the original URL, invalidates in-flight work and backs off. LIVE can also restore the original source.
- Failed probes back off for 15 seconds; failed replacements for 60 seconds. A switch may briefly buffer or temporarily use a fixed quality. Startup ads may begin before the first check. Twitch may return ads for every alternative. This is experimental recovery, not guaranteed ad removal.

## Evidence and limits

A public anonymous protocol probe succeeded for Caedrel: token present, master HLS valid, five video variants, chosen media HLS valid with no recognized ad marker at that moment. xQc's master returned HTTP 404 (offline). Responses and signed token values are not published. This proves the request path can produce valid public HLS, not that the algorithm succeeds during an actual ad break on iOS.

Native policy tests cover marker parsing, audio-only skipping, relative URI resolution, hostname/scheme validation, stale responses, setting races, polling backoff, failure recovery, and pause/ended/manual replay safety. Device-level ad-break testing and behavior across regions remain outstanding.

Sources:
- Pie store package: https://chromewebstore.google.com/detail/jpkfgepcmmchgfbjblnodjhldacghenp
- Pie's supported browser scope: https://help.pie.org/en/articles/8783041
- Existing blocker's source: https://github.com/gunnerkidBT/TwitchAdBlock/tree/v31.9-0.1.18
- IVS state enumeration: https://aws.github.io/amazon-ivs-player-docs/1.56.0/ios/Enums/IVSPlayerState.html
