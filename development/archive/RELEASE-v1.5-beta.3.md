This beta removes Beta 2's reserved-strip compatibility workaround, changes the feed player to fit the complete video inside the current sidebar pane, repairs missing/stacked trailing toolbar glyphs, and adds an independent native live ad recovery method.

### Display and controls

- Restores the edge-to-edge SDK 27.1 declaration and removes the earlier horizontal-bar overrides. Backgrounds can use the full Duo window again.
- Sizes the preview from its visible pane. Opening the sidebar shrinks the video to fit; closing it expands it again, preserving the whole frame and aspect ratio. Natural letterboxing may remain.
- Replaces malformed custom trailing icon content with a simple ellipsis while preserving its original tap action/gesture and accessibility label. Leaves legitimate single icons and text controls intact.

### Ad recovery and rewind settings

Tap the sliders icon at the left of the purple timeline to open **Rewind Settings**:

- **Live ad recovery (experimental): ON by default.** Detects ad markers in live playlists and tries alternate anonymous Twitch playback sources. It may briefly buffer or temporarily use a fixed quality. If none is clean, normal playback continues. This is an independent native implementation informed by static inspection of Pie's public browser package; no Pie code/assets are bundled.
- **Automatic rewind (experimental): OFF by default.** Your previous choice is preserved. It remains a separate recording-based workaround and requires an accessible ongoing recording.

The bundled original ad blocker is preserved. Its proxy health remains unverified because automatic approval review blocked a health request involving the proxy's embedded credential. The new recovery path uses anonymous Twitch requests instead. See AD-RECOVERY-RESEARCH.md for findings and limits.

### Validation

92 host tests and 5 packaging tests passed; ARM64 compilation/linking and complete archive integrity/hash checks passed. A public anonymous Caedrel token/master/media request succeeded, but no actual ad break was observed during that probe.

**Unsigned experimental IPA: sign all executable components before installing.** Full Duo rendering, folding, playback continuity and ad-break effectiveness still require device testing. This is not a promise that every native Twitch layout problem or ad is fixed.

Download the `.ipa` asset. Updated source, SHA256SUMS and archive validation are attached.
