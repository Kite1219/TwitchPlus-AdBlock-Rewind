# Beta 5: chat-aware player sizing and rotation

The user's Beta 4 compact navigation feedback is accepted. The compact trait policy, toolbar handling and feed fitting remain the baseline. Ad blocking is still being tested; its implementation is not changed here.

## Cause and repair

Beta 4's theater hook unconditionally replaced the video stack's horizontal constraints with the full window width. That ignored visible side chat and could draw outside `TheaterView`, which owns the native tap recognizers. It left `controlsContainerView` and `controlsView` on their narrower native constraints. UIKit drawing outside an ancestor does not extend that ancestor's hit area. The screenshots are consistent with these mismatches; they do not establish every cause of the rotation failure.

Beta 5 computes the horizontal viewport inside the intersection of the theater's bounds and its window. It excludes an actually visible edge-docked `accessoryContainerView`; an offscreen/hidden pane and portrait chat below the video do not reserve width. Native vertical and aspect-ratio constraints stay in charge of the video stack. Both control containers are pinned by relative edges to the final video stack instead of copying a pre-solve width or height. Playback remains aspect-fit. Content is no longer extended outside its native gesture owner merely to fill a reserved system strip.

The supplied Twitch 30.7 Objective-C metadata identifies `TheaterView`'s `setFrame:`, `setBounds:`, `tapGestureRecognized`, `gestureRecognizer:shouldReceiveTouch:` and `TheaterViewController`'s `viewWillTransitionToSize:withTransitionCoordinator:`. Named ivars include the video stack, video view, controls container, controls view, accessory container and native tap/double-tap recognizers. Static inspection of the native constraint construction shows portrait stack height is tied to width at 9/16; controls must follow the final solve rather than a cached height.

Placement saves weak references to suppressed native constraints, which Twitch retains in its current constraint sets. This allows obsolete chat/orientation sets to expire. Before a frame/bounds size change or controller rotation, patch constraints are removed and still-current native constraints restored. Layout then uses the new geometry. The transition completion cancels/re-enables only already-enabled native tap/double-tap recognizers, retaining their native targets, delegates and attachment; disabled gestures remain disabled. No global hit-test override, synthetic play/seek, replacement tap recognizer or player reload is added.

## Preservation and evidence

`test_layout_preservation.py` pins hashes of the entire pre-layout native network implementation, `PlaylistEngine.js` and the compact navigation policy to Beta 4. The shared `TwitchAdBlock.dylib` is rebuilt because it also contains layout code; the binary is not byte-identical. `NativeRewind.rs` changes only the settings heading to Beta 5. MIT attribution remains embedded.

`tests/LayoutFixture.m` includes the shipping layout code and runs in an iPhone simulator with real UIKit, Auto Layout and hit testing. It deliberately constructs stale/narrow controls, toggles chat 30 times, cycles portrait/landscape dimensions 12 times, checks the right video edge remains hittable, protects chat touches, preserves disabled recognizers, and verifies native-constraint restoration/obsolete-constraint expiry. This is a controlled fixture, not Twitch execution, an actual IVS stream, a hardware fold or physical-device rotation test.

The release workflow also checks compiled viewport/aspect geometry, the existing rewind/preferences and packaging tests, and unchanged playlist tests. Packaging verifies all archive members other than NativeRewind/TwitchAdBlock are byte-identical to v1.4. The main executable remains Twitch 30.7 and retains its existing SDK declaration; the shipping replacement is compiled against the actual Apple SDK recorded in the release assets.

Device acceptance remains: open a live stream, toggle side chat repeatedly, show controls and scrub near both edges, rotate both ways, and repeat while paused. Confirm video is fully visible beside chat, controls span that same video area, taps keep showing controls, and paused playback stays paused. No physical-device or ad-break success is claimed.
