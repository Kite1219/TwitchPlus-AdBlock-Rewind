# v1.5 Beta 2

Supersedes Beta 1's always-on automatic rewind and SDK 27.1 layout declaration.

## Settings

A 44-point settings button at the start of the purple player timeline opens a scrollable native settings sheet. Its switch uses NSUserDefaults key `TwitchPlusAutomaticRewindEnabled` (absent = false). No migration enables existing Beta 1 installs implicitly. Both IVS live-load entry points read this preference, and playback processing checks it again before making an automatic transition. Disabling cancels queued auto flags without interrupting manually selected or existing replay. Enabling applies to a new live-channel load. Presentation is resolved through the button's own responder chain, avoiding a global/incorrect window. Existing modals are not stacked. The sheet has a Done button and supports narrow/resized content through Auto Layout.

## Layout workaround

The supplied screenshots show vertical system status controls still present despite the Beta 1 container overrides, a crowded automatic sidebar, clipping, and misplaced native controls. This beta changes the main executable's advertised SDK from 27.1 to 27.0 and matches DTSDKName/DTPlatformVersion in Info.plist. It does not alter code instructions, minimum OS, UIDeviceFamily, orientation declarations, window/scene settings, or UIKit globally. Only the four-byte SDK field is permitted to differ in the main executable. It is not a recompilation or a guarantee that UIKit compatibility behavior will fix every native Twitch layout.

The main Twitch tab controller additionally requests UITabBarControllerModeTabBar (raw value 1) after its original viewDidLoad, guarded by selector availability and current mode. No repeated setter runs on every layout. This requests a less crowded navigation mode; device testing is needed to establish what Twitch's closed-source UI does with it.

The player timeline is now 44 points high to accommodate its settings button. Collision checks and clearance calculations match this height. Thumb images are refreshed when drag tracking changes, including selected/highlighted combinations, so a stale highlight does not leave the white dot visible.

## Build

Use tools/build-rewind-linux.sh with the Rust 1.99 component. It runs production host tests plus tests/test_package_update.py. Package the pinned public v1.4 base with:

```
python tools/package-rewind-update.py --base base.ipa --library build/NativeRewind.dylib --duo-compatibility --output TwitchPlus-v1.5-beta.2.ipa
```

The optional packaging flag is required for the compatibility change. It rejects encrypted/mismatched binaries. All other archive members are hash-preserved. Re-sign before installing. No physical Duo or iOS simulator is available here.

Primary references: https://developer.apple.com/iphone-duo/prepare/ (27.0 vs 27.1 layouts); https://developer.apple.com/documentation/uikit/uitabbarcontroller/mode-swift.enum (mode); https://learn.microsoft.com/dotnet/api/uikit.uitabbarcontrollermode (native enum values).
