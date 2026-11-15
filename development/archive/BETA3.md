# v1.5 Beta 3

## Edge-to-edge and preview sizing

This beta packages the public v1.4 base without Beta 2's `--duo-compatibility` switch. The main executable and Info.plist keep their original SDK 27.1 declarations byte for byte. The iOS 27.0 workaround that reserved a right-side strip is removed. The horizontal vertical-bar-preference overrides are also removed; UIKit can supply its normal edge-to-edge window geometry and system reserved regions again. This is still the old Twitch 30.7 application, not a source rebuild of Twitch.

The native FeedPlayerView's videoSize is a CGSize, playerContainerView is a UIView, and playerView is a VideoPlayerView, as confirmed in the supplied binary's Swift field descriptors. A targeted layout hook uses the current container and immediate visible pane, not UIScreen or a phone model. It deactivates native placement/aspect constraints that make this video oversized, preserves internal scroll/rendering constraints, and owns four persistent center/size constraints for an aspect-fit rectangle. Width changes update these existing constraints. They are reactivated after reattachment, without creating duplicates. Portrait and landscape media both preserve all content and the original aspect ratio. Normal letterboxing may therefore remain; video is never stretched to remove mathematically necessary space.

A VideoPlayerView hook only operates inside FeedPlayerView. It disables fill mode, resets stale zoom on bounds changes, and applies AVLayerVideoGravityResizeAspect when available. Fullscreen/theater zoom behavior is left to Twitch. All runtime field offsets are looked up by name; these integrations remain pinned to Twitch 30.7.

## Trailing toolbar glyph

Discovery feed navigation items and their owning container items are inspected. Supported bar items opt out of shared glass backgrounds. A custom trailing control without text and with missing/stacked image content gets a single ellipsis glyph. UIControl-based controls forward to the original control's actions and retain its enabled state and accessibility label. Gesture-based controls keep the original view and recognizers, with a noninteractive icon cover. Titled controls, single valid icons, and unrelated screens are preserved. This is a bounded repair for legacy glyph rendering, not a confirmed identification of every layer visible in the screenshot.

## Native live ad recovery

The independent recovery implementation is documented in AD-RECOVERY-RESEARCH.md. It is ON by default and can be disabled in Rewind Settings. Automatic recording rewind remains a separate saved option, OFF by default; existing Beta 2 preferences persist. Open the sliders button at the left of the purple timeline to find both switches.

## Validation

92 production host tests plus 5 packaging tests pass. Layout tests exercise a stale 1172-point container clipped to a 760-point sidebar pane, restore expansion, portrait videos, aspect-ratio invariants, invalid sizes, reattachment, and preservation of internal constraints. Toolbar tests check text/icon preservation, action forwarding, disabled state and gesture target retention. Ad tests check markers, URI validation, variant selection, cooldown/deduplication, stale channels, disabled settings, pause/ended/rewind states, and fallback invalidation. The tests mock Apple APIs and raw ivar access; they do not render UIKit on a device.

A live anonymous token + HLS probe returned a valid Caedrel master with five video variants and a valid clean source playlist. xQc was offline (playlist HTTP 404). No real ad break was observed. Native rendering, playback continuity, effective ad suppression, AirPlay/Cast and folding still require an iPhone Duo test. See the release notes for the unsigned IPA.
