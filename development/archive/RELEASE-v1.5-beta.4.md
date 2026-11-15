# TwitchPlus v1.5 Beta 4

Replaces Beta 3's delayed checker with filtering in the native player's actual playlist-response path. Compatible alternate sessions include a 360p fallback, with continuous segment numbering. The legacy proxy/token-rewrite blocker is replaced.

Wide phones now use native compact navigation by default. Preview fitting checks the full clipping hierarchy and sidebar overlays; theater video backgrounds extend into the reserved side area. Toolbar groups replace the old icon-cover heuristic.

Open the **sliders button on the purple timeline → Rewind Settings - Beta 4**. Automatic rewind remains optional. Live ad recovery defaults on; reopen the stream after changing it. **Compact layout on wide phones** can be disabled for sidebar testing. **Copy runtime diagnostics** reports installed hooks and real response counters.

The shipping module is built on a Mac with Apple's SDK. Source, SDK/Xcode information, checksums and package validation accompany the IPA.

**Unsigned prerelease.** Use your normal signing/LiveContainer method. Quality may drop or frames may hold briefly. If no usable source exists at startup, ads can still appear. Duo rendering and an on-device ad break have not been verified; host checks are not device proof.

[Investigation and limitations](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/blob/release/v1.5-beta.4/BETA4.md).
