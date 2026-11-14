# Duo v2 compatibility test build

This build includes the automatic recording rewind and addresses native navigation as well as the custom player overlay. It is based on the public TwitchPlus v1.4 IPA, SHA-256 `6d573ecfc6686bed9a15fc061b315cc19ead5f93faab7fc5594d23aa4f104665`, and the NativeRewind source attached to that release.

## Binary inspection

The app is Twitch 30.7. Its main executable declares iOS SDK 27.1 in LC_BUILD_VERSION; Info.plist also declares iphoneos27.1. Merely changing these declarations does not modernize the app's native layout implementations.

Decoded Objective-C metadata confirms these classes exist in the actual base binary:

- `_TtC6Twitch16TabBarController`
- `_TtC6Twitch21TheaterViewController`
- `_TtC6Twitch30TheaterContainerViewController`
- `_TtC6Twitch25TheaterPlayerControlsView`

The tab controller's `tw_floatingViewLayoutInsets` implementation at 0x101f51f98 calls its Swift body at 0x101f51ff0. It reads tabBar.bounds, converts to its view coordinates, then computes a bottom inset from vertical coordinates. The selector stubs resolve to `tabBar` at 0x104bc1f60, `view` at 0x104bc4ce0, `bounds` at 0x104b9f960 and `convertRect:fromCoordinateSpace:` at 0x104ba2ba0. This is evidence of a horizontal bottom-bar layout assumption, not proof of the precise glitch on the user's device.

Player controls expose Objective-C getters for allButtons, bottomRightStackView, topLeftStackView and topRightStackView. These supply actual native geometry, without hardcoded ivar offsets.

## Changes

1. On systems that expose both APIs, add `preferredVerticalBarBehavior = disabled` and `childViewControllerForPreferredVerticalBarBehavior = nil` overrides to the three Twitch container classes above. This is a stable container preference, not an orientation-dependent toggle. It retains Duo resizing metadata while requesting horizontal navigation. Inherited UIKit methods are never modified, existing class implementations are not overwritten, and older systems skip installation.
2. Read native buttons' converted bounds and ancestor visibility on each layout. Move the custom timeline above a tall bottom action stack. Hide custom controls where they would cover native buttons or header stacks; restore them when space returns.
3. Include safe-area origins and RTL mirroring in the collision geometry. Keep the LIVE button's whole 44-point touch target above the slider rather than overlapping it by 8 points. Give skip buttons exact 44-point dimensions and the timestamp an explicit height so layout and collision calculations agree.
4. Reject an ambiguous player subtree instead of binding controls to the first of two live streams. A unique player in a nearer subtree remains eligible.
5. Preserve automatic rewind, queued seeking, stale-request checks, LIVE cancellation, and detached-player visibility fixes from the earlier build.

## Validation and limits

62 host tests pass against the compiled production Rust functions with mocked Apple APIs. These include the existing geometry sweep, actual native-control collision fixtures, hidden ancestors, RTL/asymmetric origins, player ambiguity, API availability gating, ABI encodings and subclass-only method installation. Native ARM64 compilation/linking passes. Archive verification checks every member hash and ZIP CRC. Only NativeRewind.dylib changes; the main executable, Info.plist, ad blocker, chat and ForcedFollow remain byte-identical.

No iOS simulator or physical Duo is available in this Linux workspace. Tests do not establish real UIKit rendering, launch compatibility, folding animations, performance, ad suppression or complete native app layout correctness. Any remaining orientation/idiom assumptions inside Twitch's closed source may need further targeted work after device testing. This is an unsigned experimental build: re-sign every executable component before installing.

Build with `bash tools/build-rewind-linux.sh /path/to/rustc-component` using Rust 1.99.0, then use `tools/package-rewind-update.py` with the public v1.4 IPA as the base. See AUTO-REWIND.md for recording availability and live-lag limitations.

## API references

- https://developer.apple.com/iphone-duo/prepare/ — SDK opt-in, safe areas and dynamic sizing.
- https://developer.apple.com/documentation/uikit/uiviewcontroller/preferredverticalbarbehavior — stable horizontal-bar opt-out.
- https://developer.apple.com/documentation/uikit/uiviewcontroller/childforpreferredverticalbarbehavior — container preference propagation.
- https://github.com/dotnet/macios/wiki/UIKit-tvOS-xcode27.2-b3 — Apple header diff confirms Disabled = 1, signed NSInteger return, and the Objective-C childViewControllerForPreferredVerticalBarBehavior selector.
