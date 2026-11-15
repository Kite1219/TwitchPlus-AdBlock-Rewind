# TwitchPlus v1.5 Beta 5 — Player Layout & Rotation

Layout repair for the reported chat overlap, short controls/timeline and lost player taps after rotating.

- Visible side chat reserves video space. Closing chat expands it again, with aspect-fit playback.
- Native controls and the purple timeline follow the video's final Auto Layout bounds, including portrait height changes.
- Video stays inside its native touch owner's bounds. Native constraints are released/restored before size changes, and native tap recognizers are refreshed after rotation without replacing their targets or delegates.
- Beta 4's accepted compact Duo navigation and saved settings are preserved. **The ad-filter/network implementation and playlist engine are unchanged.** Layout and the filter share `TwitchAdBlock.dylib`, so that library is rebuilt for this layout update.

Open **sliders on the purple timeline → Rewind Settings - Beta 5**. Runtime diagnostics include the rotation hook flag and viewport/chat geometry.

Built against Apple's SDK on GitHub Actions. Validation includes a real UIKit simulator fixture for layout, constraint restoration and hit testing, plus host checks and archive preservation. **The fixture does not run Twitch or verify live playback on a physical Duo.** Please verify chat on/off and both rotation directions on your device; this release makes no new ad-blocking claim.

Unsigned IPA; use your normal signing/LiveContainer workflow. Main executable, Info.plist and every archive member except the two replacement libraries remain byte-identical to the v1.4 base.
