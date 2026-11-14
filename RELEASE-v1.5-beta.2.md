Automatic rewind is now optional and OFF by default. Tap the small sliders/gear button at the left of the purple timeline to open **Rewind Settings**, then enable **Automatic rewind (experimental)**. Your choice is saved on this device and applies when you next open a stream. Turning it off cancels a waiting automatic switch; tap LIVE to leave an existing replay. Manual rewind remains available.

This may avoid some live ads but is not guaranteed. It needs an accessible ongoing recording, and playback may lag farther behind the broadcast than one second.

### Duo compatibility changes

- Use the iOS 27.0 compatibility SDK declaration instead of 27.1 to avoid forcing this older Twitch binary into edge-to-edge vertical system bars. This can leave a reserved strip for system status controls; it is a compatibility workaround, not a true rebuild of Twitch for a newer SDK.
- Request native tab-bar mode rather than automatic sidebar navigation to reduce the crowded navigation seen in the supplied screenshots.
- Reserve enough height for the settings button and improve the drag-only thumb behavior. Retain the existing native-control collision and player-binding fixes.

**Unsigned beta: sign all executable components before installing.** The remaining closed-source native profile/feed layouts, folding, launch and ad behavior still require device testing. These changes target the screenshots; they have not been visually verified on a Duo.

Validation: 69 host tests and 5 packaging tests pass. ARM64 compilation and linking pass. Archive CRCs and all member hashes are verified. Only NativeRewind.dylib, the main executable's SDK field, and Info.plist's SDK metadata change relative to v1.4. The third-party ad blocker, chat and ForcedFollow libraries are preserved.

Download the `.ipa` asset; updated source, validation JSON and SHA256SUMS are attached. See BETA2.md for implementation details.
