"""Meaningful failure cases for the offline inspector; no iOS runtime implied."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import plistlib
import stat
import struct
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile

spec = importlib.util.spec_from_file_location("ipa_tester", Path(__file__).parents[1] / "tools/test-twitch-ipa.py")
tester = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tester)
ROOT = "Payload/Twitch.app/"


def dylib_command(name, kind=0xC):
    raw = name.encode() + b"\0"
    size = (24 + len(raw) + 7) // 8 * 8
    return struct.pack("<6I", kind, size, 24, 0, 0, 0) + raw + b"\0" * (size - 24 - len(raw))


def macho(dependencies=(), platform=2, cpu=0x100000C, encrypted=False, filetype=2,
          initializer=False, markers=b"", sdk=0x1B0100, minimum=0x100400, rpaths=()):
    commands = [struct.pack("<6I", 0x32, 24, platform, minimum, sdk, 0)]
    for dependency in dependencies:
        commands.append(dylib_command(dependency) if isinstance(dependency, str) else dylib_command(*dependency))
    for path in rpaths:
        text = path.encode() + b"\0"
        size = (12 + len(text) + 7) // 8 * 8
        commands.append(struct.pack("<III", 0x8000001C, size, 12) + text + b"\0" * (size - 12 - len(text)))
    if encrypted:
        commands.append(struct.pack("<6I", 0x2C, 24, 0, 0, 1, 0))
    if initializer:
        segment = struct.pack("<II16s4Q4I", 0x19, 152, b"__DATA", 0, 8, 0, 8, 3, 3, 1, 0)
        section = struct.pack("<16s16s2Q8I", b"__mod_init_func", b"__DATA", 0, 8, 0, 3, 0, 0, 9, 0, 0, 0)
        commands.append(segment + section)
    raw = b"".join(commands)
    return struct.pack("<8I", 0xFEEDFACF, cpu, 0, filetype, len(commands), len(raw), 0, 0) + raw + b"FIXTURE-PAYLOAD" + markers


def members():
    info = {"CFBundleIdentifier": "tv.twitch", "CFBundleExecutable": "Twitch", "CFBundleVersion": "123",
            "CFBundleShortVersionString": "30.7", "MinimumOSVersion": "16.4", "DTSDKName": "iphoneos27.1",
            "UIDeviceFamily": [1, 2], "UIDesignRequiresCompatibility": False}
    result = {ROOT + "Info.plist": plistlib.dumps(info), ROOT + "Twitch": macho(
        ["@executable_path/Frameworks/" + name for name in tester.CUSTOM_LIBRARIES])}
    for name in tester.CUSTOM_LIBRARIES:
        result[ROOT + "Frameworks/" + name] = macho(filetype=6, initializer=True,
            markers=b"".join(tester.FEATURE_MARKERS.values()) if name == "NativeRewind.dylib" else b"")
    result[ROOT + "Assets.car"] = b"UNRELATED-ORIGINAL-ASSET"
    return result


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)

    def ipa(self, data=None, name="sample.ipa"):
        path = self.folder / name
        with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as archive:
            for member, content in (members() if data is None else data).items():
                archive.writestr(member, content)
        return path

    def checks(self, report):
        return {item["id"]: item for item in report["checks"]}

    def test_valid_package_still_marks_device_tests_pending(self):
        report = tester.inspect_ipa(self.ipa())
        self.assertEqual(report["summary"]["fail"], 0)
        self.assertFalse(report["deviceTested"])
        self.assertEqual(self.checks(report)["device"]["status"], "skip")
        self.assertEqual(self.checks(report)["signing"]["status"], "warn")

    def test_fairplay_encryption_is_rejected(self):
        data = members(); data[ROOT + "Twitch"] = macho(encrypted=True)
        self.assertEqual(self.checks(tester.inspect_ipa(self.ipa(data)))["encryption"]["status"], "fail")

    def test_simulator_build_is_not_reported_as_device_compatible(self):
        data = members(); data[ROOT + "Twitch"] = macho(platform=7, cpu=0x1000007)
        report = tester.inspect_ipa(self.ipa(data), profile="generic")
        self.assertEqual(self.checks(report)["architecture"]["status"], "fail")

    def test_missing_required_framework_is_rejected(self):
        data = members(); del data[ROOT + "Frameworks/NativeChat.dylib"]
        report = tester.inspect_ipa(self.ipa(data))
        self.assertEqual(self.checks(report)["dependencies"]["status"], "fail")
        self.assertEqual(self.checks(report)["library_NativeChat.dylib"]["status"], "fail")

    def test_unloaded_tweak_is_rejected_even_when_file_exists(self):
        data = members(); data[ROOT + "Twitch"] = macho()
        report = tester.inspect_ipa(self.ipa(data))
        self.assertEqual(self.checks(report)["library_NativeRewind.dylib"]["status"], "fail")

    def test_missing_initializer_is_rejected(self):
        data = members(); data[ROOT + "Frameworks/NativeRewind.dylib"] = macho(filetype=6)
        report = tester.inspect_ipa(self.ipa(data))
        self.assertEqual(self.checks(report)["initializer"]["status"], "fail")

    def test_missing_beta_feature_is_reported(self):
        data = members()
        member = ROOT + "Frameworks/NativeRewind.dylib"
        data[member] = data[member].replace(b"TwitchPlusNativeAdRecoveryEnabled", b"TwitchPlusMissingFeatureDisabled")
        report = tester.inspect_ipa(self.ipa(data))
        self.assertEqual(self.checks(report)["marker_optional_native_ad_recovery"]["status"], "fail")

    def test_old_release_profile_does_not_require_new_features(self):
        data = members(); data[ROOT + "Frameworks/NativeRewind.dylib"] = macho(filetype=6, initializer=True)
        report = tester.inspect_ipa(self.ipa(data), profile="twitchplus")
        self.assertEqual(report["summary"]["fail"], 0)

    def test_unsupported_twitch_version_is_rejected(self):
        data = members(); info = plistlib.loads(data[ROOT + "Info.plist"])
        info["CFBundleShortVersionString"] = "31.9"
        data[ROOT + "Info.plist"] = plistlib.dumps(info)
        self.assertEqual(self.checks(tester.inspect_ipa(self.ipa(data)))["twitch_version"]["status"], "fail")

    def test_sdk_compatibility_workaround_is_detected(self):
        data = members(); data[ROOT + "Twitch"] = macho(sdk=0x1B0000)
        report = tester.inspect_ipa(self.ipa(data))
        self.assertEqual(self.checks(report)["duo_declaration"]["status"], "fail")
        self.assertEqual(self.checks(report)["sdk"]["status"], "warn")

    def test_checksum_mismatch_fails(self):
        self.assertEqual(self.checks(tester.inspect_ipa(self.ipa(), expected_sha="0" * 64))["checksum"]["status"], "fail")

    def test_baseline_allows_only_native_rewind_replacement(self):
        base = self.ipa(name="base.ipa")
        data = members(); data[ROOT + "Frameworks/NativeRewind.dylib"] += b"NEW-TWEAK"
        updated = self.ipa(data, "updated.ipa")
        report = tester.inspect_ipa(updated, baseline=base)
        self.assertEqual(self.checks(report)["preservation"]["status"], "pass")
        self.assertEqual(report["baseline"]["changedMembers"], [ROOT + "Frameworks/NativeRewind.dylib"])

    def test_baseline_detects_tampered_asset(self):
        base = self.ipa(name="base.ipa")
        data = members(); data[ROOT + "Assets.car"] = b"MODIFIED-ASSET"
        report = tester.inspect_ipa(self.ipa(data, "updated.ipa"), baseline=base)
        self.assertEqual(self.checks(report)["preservation"]["status"], "fail")

    def test_source_provenance_mismatch_fails(self):
        library = self.folder / "built.dylib"; library.write_bytes(b"DIFFERENT-LIBRARY")
        report = tester.inspect_ipa(self.ipa(), library=library)
        self.assertEqual(self.checks(report)["source_match"]["status"], "fail")

    def test_duplicate_members_fail(self):
        path = self.ipa()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with zipfile.ZipFile(path, "a") as archive:
                archive.writestr(ROOT + "Info.plist", b"DUPLICATE")
        report = tester.inspect_ipa(path)
        self.assertIn("Duplicate", self.checks(report)["inspection"]["detail"])

    def test_unsafe_archive_paths_fail(self):
        for name in ("../escape", "/absolute", "C:/drive", "Payload/./Twitch", "Payload//Twitch", "Payload\\Twitch"):
            with self.subTest(name=name):
                report = tester.inspect_ipa(self.ipa({name: b"X"}))
                self.assertGreater(report["summary"]["fail"], 0)

    def test_symlink_escape_fails(self):
        path = self.ipa()
        with zipfile.ZipFile(path, "a") as archive:
            entry = zipfile.ZipInfo(ROOT + "escape")
            entry.create_system = 3; entry.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(entry, "../../../outside")
        self.assertIn("symlink", self.checks(tester.inspect_ipa(path))["inspection"]["detail"])

    def test_corrupt_zip_crc_fails(self):
        path = self.ipa()
        data = path.read_bytes().replace(b"UNRELATED-ORIGINAL-ASSET", b"UNRELATED-CORRUPTED-ASST", 1)
        path.write_bytes(data)
        report = tester.inspect_ipa(path)
        self.assertGreater(report["summary"]["fail"], 0)

    def test_archive_size_limit_applies_before_decompression(self):
        with patch.object(tester, "MAX_TOTAL", 100):
            report = tester.inspect_ipa(self.ipa())
        self.assertIn("inspection limit", self.checks(report)["inspection"]["detail"])

    def test_invalid_plist_is_reported_without_traceback(self):
        data = members(); data[ROOT + "Info.plist"] = b"NOT-A-PLIST"
        self.assertGreater(tester.inspect_ipa(self.ipa(data))["summary"]["fail"], 0)

    def test_missing_input_produces_failure_report(self):
        report = tester.inspect_ipa(self.folder / "missing.ipa")
        self.assertGreater(report["summary"]["fail"], 0)
        self.assertFalse(report["deviceTested"])

    def test_cli_writes_json_and_html_for_a_broken_package(self):
        path = self.folder / "bad.ipa"; path.write_bytes(b"NOT-A-ZIP")
        output = self.folder / "report"
        with contextlib.redirect_stdout(io.StringIO()):
            code = tester.main([str(path), "--output-dir", str(output)])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads((output / "report.json").read_text())["result"], "failed")
        self.assertIn("Package checks failed", (output / "report.html").read_text())

    def test_cli_does_not_overwrite_input(self):
        path = self.ipa(name="report.json")
        original = path.read_bytes()
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            tester.main([str(path), "--output-dir", str(self.folder)])
        self.assertEqual(path.read_bytes(), original)

    def test_html_escapes_untrusted_text_and_script_payload(self):
        report = tester.inspect_ipa(self.ipa())
        report["file"] = "</script><script>alert('unsafe')</script>"
        report["checks"][0]["detail"] = "<img src=x onerror=alert(1)>"
        page = tester.render_html(report)
        self.assertNotIn("<script>alert('unsafe')", page)
        self.assertNotIn("<img src=x", page)
        self.assertIn("\\u003c/script\\u003e", page)


class MachOTests(unittest.TestCase):
    def test_modern_initializer_offsets_are_recognized(self):
        image = bytearray(macho(initializer=True))
        struct.pack_into("<I", image, 32 + 24 + 72 + 64, 0x16)
        self.assertEqual(tester.parse_macho(image)[0]["initializerSections"], 1)

    def test_command_outside_table_is_rejected(self):
        data = bytearray(macho()); struct.pack_into("<I", data, 36, 4096)
        with self.assertRaises(tester.InvalidPackage): tester.parse_macho(data)

    def test_truncated_header_is_rejected(self):
        with self.assertRaises(tester.InvalidPackage): tester.parse_macho(bytes.fromhex("cffaedfe"))

    def test_unterminated_library_path_is_rejected(self):
        data = bytearray(macho(["@rpath/missing.dylib"]))
        command_start = 32 + 24
        data[command_start + 24:] = b"X" * (len(data) - command_start - 24)
        with self.assertRaises(tester.InvalidPackage): tester.parse_macho(data)

    def test_valid_universal_ios_and_simulator_slices(self):
        one = macho(); two = macho(platform=7, cpu=0x1000007)
        first, second = 4096, 8192
        header = struct.pack(">II", 0xCAFEBABE, 2) + struct.pack(">5I", 0x100000C, 0, first, len(one), 12) + struct.pack(">5I", 0x1000007, 0, second, len(two), 12)
        data = header + b"\0" * (first - len(header)) + one
        data += b"\0" * (second - len(data)) + two
        self.assertEqual([image["architecture"] for image in tester.parse_macho(data)], ["arm64", "x86_64"])

    def test_overlapping_universal_slices_are_rejected(self):
        image = macho()
        header = struct.pack(">II", 0xCAFEBABE, 2) + struct.pack(">5I", 0x100000C, 0, 64, len(image), 0) * 2
        with self.assertRaises(tester.InvalidPackage): tester.parse_macho(header + b"\0" * (64 - len(header)) + image)

    def test_universal_architecture_mismatch_is_rejected(self):
        image = macho()
        header = struct.pack(">II", 0xCAFEBABE, 1) + struct.pack(">5I", 0x1000007, 0, 32, len(image), 0)
        with self.assertRaises(tester.InvalidPackage): tester.parse_macho(header + b"\0" * 4 + image)

    def test_rpath_and_loader_path_resolution(self):
        main = "Payload/Twitch.app/Twitch"
        dependency = "Payload/Twitch.app/Frameworks/Test.framework/Test"
        resolved = tester.resolve_dependency("@rpath/Test.framework/Test", main, main, ["@executable_path/Frameworks"], {dependency})
        self.assertEqual(resolved, dependency)

    def test_unresolved_dependency_is_not_assumed_to_be_system(self):
        self.assertIsNone(tester.resolve_dependency("@rpath/Absent.dylib", "app/a", "app/a", ["@loader_path/Frameworks"], set()))

    def test_system_swift_runpath_does_not_hide_a_missing_framework(self):
        self.assertIsNone(tester.resolve_dependency("@rpath/Absent.framework/Absent", "app/a", "app/a", ["/usr/lib/swift", "@loader_path/Frameworks"], set()))

    def test_swift_runtime_can_resolve_to_system_runpath(self):
        self.assertEqual(tester.resolve_dependency("@rpath/libswiftCore.dylib", "app/a", "app/a", ["/usr/lib/swift"], set()), "system")


if __name__ == "__main__":
    unittest.main(verbosity=2)
