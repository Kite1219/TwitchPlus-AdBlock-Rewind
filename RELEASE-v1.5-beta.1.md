TwitchPlus v1.5 Beta 1 adds automatic recording rewind and further iPhone Duo layout fixes, based on v1.4.

- Automatically switches to an accessible ongoing recording and seeks to one second before its available end. The recording may lag farther behind the actual live broadcast. LIVE cancels the automatic switch.
- Requests horizontal navigation for Twitch's main and theater containers on supported systems to address older layout assumptions.
- Moves or hides custom controls when they overlap native buttons, accounts for asymmetric safe areas and RTL layouts, and avoids binding controls to an ambiguous player.

**Unsigned experimental IPA: sign all executable components before installing.** Device testing is still required. Ad prevention, launch and folding behavior have not been verified on an iPhone Duo; startup ads may still appear and channels without accessible recordings remain live.

Validation: 62 host tests passed; ARM64 compilation and linking passed; ZIP CRC and every archive member hash verified. Only NativeRewind.dylib changes from the v1.4 IPA. The included third-party ad blocker is unchanged.

Download the `.ipa` asset to install. Updated source, SHA256SUMS.txt and the archive validation report are attached. See DUO-V2.md in the source for inspection evidence and build instructions.
