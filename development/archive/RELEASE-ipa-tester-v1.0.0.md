# Twitch IPA Tester v1.0.0

Reusable offline checks for TwitchPlus IPA releases, with JSON and browser-readable reports and a device test checklist.

Download **Twitch-IPA-Tester-v1.0.0.zip**, unzip, and run `python3 tools/test-twitch-ipa.py --gui` (Windows: `py`). Choose an IPA to inspect. No Python packages or network access are required for package inspection.

The tester checks package integrity, physical iOS architecture, encryption, library dependencies, tweak loading and initialization, feature markers, SDK declarations and optional preservation against the original IPA. Linux source testing also checks that the regression-tested library matches the IPA exactly.

The included **Beta3-test-report.html** and **Beta3-test-report.json** describe the published Beta 3 IPA. The report's device session lets you record and export sidebar, toolbar, rewind and ad-break observations locally. No IPA is bundled with this tester release.

Automatic package checks do not execute Twitch or certify its UI, signing, private runtime hooks or ad blocking. The existing unsigned IPA still needs your normal signing method. Beta 3 also carries a pre-existing Share Extension minimum of iOS 17.4 despite the main app's iOS 16.4 declaration; this appears as a report warning.

See [the tester guide](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/blob/main/IPA-TESTER.md) or [run the tester on GitHub](https://github.com/Kite1219/TwitchPlus-AdBlock-Rewind/actions/workflows/test-ipa.yml).
