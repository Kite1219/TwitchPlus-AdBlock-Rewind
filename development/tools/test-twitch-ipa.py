#!/usr/bin/env python3
"""Offline TwitchPlus IPA checks. Python 3.9+, standard library only.

This inspects packages; it does not execute iOS code or certify ad blocking.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import plistlib
import posixpath
import re
import stat
import struct
import subprocess
import sys
import webbrowser
import zipfile

VERSION = "1.0.0"
MAX_MEMBERS = 50000
MAX_MEMBER = 512 * 1024 * 1024
MAX_TOTAL = 4 * 1024 * 1024 * 1024
THIN = {b"\xcf\xfa\xed\xfe": ("<", True), b"\xfe\xed\xfa\xcf": (">", True),
        b"\xce\xfa\xed\xfe": ("<", False), b"\xfe\xed\xfa\xce": (">", False)}
FAT = {b"\xca\xfe\xba\xbe": (">", False), b"\xbe\xba\xfe\xca": ("<", False),
       b"\xca\xfe\xba\xbf": (">", True), b"\xbf\xba\xfe\xca": ("<", True)}
MAGICS = set(THIN) | set(FAT)
ARCHES = {0x100000C: "arm64", 0x1000007: "x86_64", 12: "arm", 7: "i386"}
PLATFORMS = {1: "macOS", 2: "iOS", 6: "Mac Catalyst", 7: "iOS Simulator"}
CUSTOM_LIBRARIES = ("NativeRewind.dylib", "NativeChat.dylib", "ForcedFollow.dylib", "TwitchAdBlock.dylib")
FEATURE_MARKERS = {
    "Rewind settings": b"TwitchPlusRewindSettings\0",
    "Optional automatic rewind": b"TwitchPlusAutomaticRewindEnabled\0",
    "Optional native ad recovery": b"TwitchPlusNativeAdRecoveryEnabled\0",
    "Feed sizing hook": b"_TtC6Twitch14FeedPlayerView\0",
}
CHECKLIST = [
    {"id": "launch", "title": "Launch and playback", "steps": "Install with your usual signing method. Launch, open a live stream, play audio, then switch channels."},
    {"id": "full_width", "title": "Duo full-width layout", "steps": "Rotate both ways and resize the app. Check that app backgrounds reach the available display edges and controls remain reachable. Aspect-ratio letterboxing may remain."},
    {"id": "sidebar", "title": "Sidebar preview fit", "steps": "Open and close the sidebar while a feed preview plays. Check both edges of the source video remain visible, then rotate and repeat."},
    {"id": "toolbar", "title": "Toolbar icon and tap", "steps": "Open Following / Live. Check the top-right control has one readable icon and opens its original menu when tapped."},
    {"id": "settings", "title": "Settings and persistence", "steps": "Open the sliders button on the purple timeline. Change each switch independently, close and reopen the app, and check both choices persist."},
    {"id": "rewind_off", "title": "Automatic rewind off", "steps": "Turn automatic rewind off, open a new live stream and check it stays live. Check manual rewind and Return to live still work."},
    {"id": "rewind_on", "title": "Automatic rewind on", "steps": "Turn automatic rewind on and reopen a channel with a public ongoing recording. Check the recording starts near its available end and LIVE restores live playback."},
    {"id": "ads", "title": "Observed live ad break", "steps": "Turn automatic rewind off and live ad recovery on. Observe an actual ad break and record channel, time, playback and buffering. If no ad break occurs, choose Not observed."},
    {"id": "recovery_off", "title": "Ad recovery off / failure", "steps": "Turn recovery off. Check normal playback and LIVE. With recovery on, briefly interrupt network connectivity and check the player can recover without repeatedly switching sources."},
    {"id": "lifecycle", "title": "Pause, background and casting", "steps": "Pause, resume, background, foreground, rotate and switch streams. If available, test AirPlay or casting. Check recovery does not resume a paused stream."},
]


class InvalidPackage(ValueError):
    pass


def digest_file(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def packed_version(value):
    return f"{value >> 16}.{(value >> 8) & 255}.{value & 255}"


def version_tuple(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d+(?:\.\d+){0,2}", value):
        raise InvalidPackage("Invalid OS version")
    parts = [int(part) for part in value.split(".")]
    return tuple(parts + [0] * (3 - len(parts)))


def parse_macho(data):
    """Validate slice / command bounds and return only public binary metadata."""
    magic = bytes(data[:4])
    if magic in FAT:
        endian, wide = FAT[magic]
        if len(data) < 8:
            raise InvalidPackage("Truncated universal header")
        count = struct.unpack_from(endian + "I", data, 4)[0]
        width = 32 if wide else 20
        if not 1 <= count <= 32 or 8 + count * width > len(data):
            raise InvalidPackage("Invalid universal slice table")
        ranges, images = [], []
        for index in range(count):
            fmt = "IIQQII" if wide else "IIIII"
            fields = struct.unpack_from(endian + fmt, data, 8 + index * width)
            cpu, subtype, offset, size, alignment = fields[:5]
            if alignment > 31 or offset % (1 << alignment) or size < 28 or offset < 8 + count * width or offset + size > len(data):
                raise InvalidPackage("Invalid universal slice bounds or alignment")
            if any(offset < end and start < offset + size for start, end in ranges):
                raise InvalidPackage("Overlapping universal slices")
            ranges.append((offset, offset + size))
            image = parse_thin(data[offset:offset + size])
            if image["cpu"] != cpu or image["subtype"] != subtype:
                raise InvalidPackage("Universal slice architecture disagrees with its header")
            images.append(image)
        return images
    return [parse_thin(data)]


def parse_thin(data):
    magic = bytes(data[:4])
    if magic not in THIN:
        raise InvalidPackage("Not a Mach-O binary")
    endian, wide = THIN[magic]
    header = 32 if wide else 28
    if len(data) < header:
        raise InvalidPackage("Truncated Mach-O header")
    _, cpu, subtype, filetype, count, size, _ = struct.unpack_from(endian + "7I", data)
    if count > 65535 or header + size > len(data) or count * 8 > size:
        raise InvalidPackage("Invalid Mach-O command table")
    result = {"cpu": cpu, "subtype": subtype, "architecture": ARCHES.get(cpu, hex(cpu)),
              "fileType": filetype, "platform": None, "minimumOS": None, "sdk": None,
              "encrypted": False, "hasCodeSignature": False, "initializerSections": 0,
              "dependencies": [], "rpaths": [], "installName": None}
    cursor = header
    for _ in range(count):
        if cursor + 8 > header + size:
            raise InvalidPackage("Truncated Mach-O load command")
        command, length = struct.unpack_from(endian + "II", data, cursor)
        kind = command & 0x7fffffff
        if length < 8 or length % 4 or cursor + length > header + size:
            raise InvalidPackage("Invalid Mach-O load command bounds")

        def need(minimum):
            if length < minimum:
                raise InvalidPackage("Truncated Mach-O command payload")

        if kind in (0xC, 0xD, 0x18, 0x1F, 0x20, 0x23, 0x1C):
            minimum = 12 if kind == 0x1C else 24
            need(minimum)
            offset = struct.unpack_from(endian + "I", data, cursor + 8)[0]
            if not minimum <= offset < length:
                raise InvalidPackage("Invalid Mach-O string offset")
            raw = data[cursor + offset:cursor + length]
            if b"\0" not in raw:
                raise InvalidPackage("Unterminated Mach-O string")
            name = raw.split(b"\0", 1)[0].decode("utf-8", "strict")
            if not name:
                raise InvalidPackage("Empty Mach-O library path")
            if kind == 0x1C:
                result["rpaths"].append(name)
            elif kind == 0xD:
                result["installName"] = name
            else:
                result["dependencies"].append({"path": name, "weak": kind in (0x18, 0x20)})
        elif kind == 0x32:
            need(24)
            platform, minimum, sdk, tools = struct.unpack_from(endian + "4I", data, cursor + 8)
            if 24 + 8 * tools > length:
                raise InvalidPackage("Truncated build-version tools")
            result.update(platform=platform, minimumOS=packed_version(minimum), sdk=packed_version(sdk))
        elif kind in (0x24, 0x25, 0x2F, 0x30):
            need(16)
            minimum, sdk = struct.unpack_from(endian + "II", data, cursor + 8)
            result.update(platform=2 if kind == 0x25 else -1, minimumOS=packed_version(minimum), sdk=packed_version(sdk))
        elif kind in (0x21, 0x2C):
            need(24 if kind == 0x2C else 20)
            start, extent, crypt = struct.unpack_from(endian + "III", data, cursor + 8)
            if start + extent > len(data):
                raise InvalidPackage("Encryption range exceeds binary")
            result["encrypted"] |= crypt != 0
        elif kind == 0x1D:
            need(16)
            start, extent = struct.unpack_from(endian + "II", data, cursor + 8)
            if start + extent > len(data):
                raise InvalidPackage("Signature range exceeds binary")
            result["hasCodeSignature"] = extent > 0
        elif kind == 0x19:
            need(72)
            file_offset, file_size = struct.unpack_from(endian + "QQ", data, cursor + 40)
            sections = struct.unpack_from(endian + "I", data, cursor + 64)[0]
            if file_offset + file_size > len(data) or 72 + 80 * sections > length:
                raise InvalidPackage("Invalid Mach-O segment bounds")
            for index in range(sections):
                at = cursor + 72 + index * 80
                extent = struct.unpack_from(endian + "Q", data, at + 40)[0]
                start = struct.unpack_from(endian + "I", data, at + 48)[0]
                flags = struct.unpack_from(endian + "I", data, at + 64)[0] & 255
                if flags not in (1, 0xC, 0x12) and extent and start + extent > len(data):
                    raise InvalidPackage("Invalid Mach-O section bounds")
                # dyld supports both pointer initializers and modern 32-bit
                # __init_offsets (S_INIT_FUNC_OFFSETS), emitted by ld64.lld.
                if flags in (9, 0x16) and extent:
                    result["initializerSections"] += 1
        cursor += length
    if cursor != header + size:
        raise InvalidPackage("Mach-O command size disagrees with command count")
    return result


def archive_inventory(archive):
    entries = archive.infolist()
    if not entries or len(entries) > MAX_MEMBERS:
        raise InvalidPackage("Empty archive or too many members")
    names = [entry.filename for entry in entries]
    if len(names) != len(set(names)):
        raise InvalidPackage("Duplicate ZIP members")
    total = 0
    for entry in entries:
        name = entry.filename
        if (not name or entry.orig_filename != name or "\\" in name or "\0" in name or ":" in name or name.startswith("/")
                or any(part in (".", "..", "") for part in name.rstrip("/").split("/"))):
            raise InvalidPackage("Unsafe or ambiguous archive member path")
        if entry.flag_bits & 1:
            raise InvalidPackage("Password-encrypted ZIP member")
        if entry.file_size > MAX_MEMBER:
            raise InvalidPackage("Archive member exceeds 512 MiB inspection limit")
        total += entry.file_size
    if total > MAX_TOTAL:
        raise InvalidPackage("Archive exceeds 4 GiB inspection limit")
    hashes, machos = {}, []
    for entry in entries:
        result = hashlib.sha256()
        first, consumed = b"", 0
        with archive.open(entry) as stream:
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                if not first:
                    first = chunk[:4]
                consumed += len(chunk)
                if consumed > MAX_MEMBER or consumed > entry.file_size:
                    raise InvalidPackage("ZIP member expands beyond its declared size")
                result.update(chunk)
        if consumed != entry.file_size:
            raise InvalidPackage("ZIP member size mismatch")
        hashes[entry.filename] = result.hexdigest()
        if first in MAGICS:
            machos.append(entry.filename)
        if stat.S_ISLNK(entry.external_attr >> 16):
            target = archive.read(entry).decode("utf-8", "strict")
            normalized = posixpath.normpath(posixpath.join(posixpath.dirname(entry.filename), target))
            if target.startswith("/") or "\\" in target or ":" in target or normalized == ".." or normalized.startswith("../"):
                raise InvalidPackage("Archive symlink escapes its root")
    return hashes, machos, total


def check(report, key, title, status, detail):
    report["checks"].append({"id": key, "title": title, "status": status, "detail": str(detail)})


def finish(report):
    counts = Counter(item["status"] for item in report["checks"])
    report["summary"] = {key: counts[key] for key in ("pass", "fail", "warn", "skip")}
    report["result"] = "failed" if counts["fail"] else "passed_with_warnings" if counts["warn"] else "passed"
    return report


def host_executable(member, root, executable):
    parts = PurePosixPath(member).parts
    for index, part in enumerate(parts):
        if part.endswith(".appex"):
            # Plug-in executables are normally the extension stem; their Info.plist
            # is consulted by the caller when the actual name differs.
            return "/".join(parts[:index + 1]) + "/" + part[:-6]
    return root + "/" + executable


def resolve_dependency(dependency, loader, executable, runpaths, names):
    def expand(value):
        for token, base in (("@loader_path", posixpath.dirname(loader)), ("@executable_path", posixpath.dirname(executable))):
            if value == token or value.startswith(token + "/"):
                return posixpath.normpath(base + value[len(token):])
        return value

    if dependency.startswith(("/usr/lib/", "/System/Library/")):
        return "system"
    candidates = [expand(dependency)]
    if dependency.startswith("@rpath/"):
        candidates = [posixpath.normpath(expand(path) + "/" + dependency[7:]) for path in runpaths]
    for candidate in candidates:
        if candidate in names:
            return candidate
    # A /usr/lib/swift runpath must not make every missing app framework look
    # available in the shared cache. Only Swift runtime dylibs get that fallback.
    if dependency.startswith("@rpath/") and re.fullmatch(r"libswift[^/]+\.dylib", dependency[7:]):
        if any(candidate.startswith("/usr/lib/swift/") for candidate in candidates):
            return "system"
    return None


def inspect_ipa(path, baseline=None, expected_sha=None, profile="beta3", library=None):
    path = Path(path)
    report = {"tool": "Twitch IPA Tester", "toolVersion": VERSION,
              "generatedAt": datetime.now(timezone.utc).isoformat(), "file": path.name,
              "profile": profile, "scope": "static-package", "deviceTested": False,
              "checks": [], "images": [], "manualChecklist": CHECKLIST,
              "limitations": ["No iOS code was executed by the package checks.",
                              "Feature strings and dependencies do not prove runtime hook compatibility.",
                              "Code-signature presence is not cryptographic signature or provisioning validation.",
                              "Screen layout, playback and real ad breaks require device testing."]}
    try:
        report["bytes"] = path.stat().st_size
        report["sha256"] = digest_file(path)
        if expected_sha:
            check(report, "checksum", "Expected SHA-256", "pass" if report["sha256"] == expected_sha.lower() else "fail", report["sha256"])
        else:
            check(report, "checksum", "SHA-256 calculated", "pass", report["sha256"] + " (no expected digest supplied)")
        with zipfile.ZipFile(path) as archive:
            hashes, image_names, total = archive_inventory(archive)
            check(report, "zip", "ZIP integrity and paths", "pass", f"CRC and SHA-256 read for all {len(hashes)} members; {total:,} uncompressed bytes. Nothing extracted.")
            roots = [name[:-11] for name in hashes if re.fullmatch(r"Payload/[^/]+\.app/Info\.plist", name)]
            if len(roots) != 1:
                raise InvalidPackage("Expected exactly one Payload/*.app/Info.plist")
            root = roots[0]
            info = plistlib.loads(archive.read(root + "/Info.plist"))
            if not isinstance(info, dict):
                raise InvalidPackage("Info.plist must be a dictionary")
            executable = info.get("CFBundleExecutable")
            bundle = info.get("CFBundleIdentifier")
            if not isinstance(executable, str) or not executable or "/" in executable or "\\" in executable or executable in (".", ".."):
                raise InvalidPackage("Invalid CFBundleExecutable")
            if not isinstance(bundle, str) or not re.fullmatch(r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", bundle):
                raise InvalidPackage("Invalid CFBundleIdentifier")
            minimum_os = version_tuple(info.get("MinimumOSVersion"))
            main = root + "/" + executable
            if main not in image_names:
                raise InvalidPackage("Main executable is missing or is not Mach-O")
            report["app"] = {key: info.get(key) for key in ("CFBundleIdentifier", "CFBundleShortVersionString", "CFBundleVersion", "CFBundleExecutable", "MinimumOSVersion", "DTSDKName", "UIDeviceFamily", "UIDesignRequiresCompatibility")}
            check(report, "metadata", "Application metadata", "pass", f"{bundle}; version {info.get('CFBundleShortVersionString')}; iOS {info['MinimumOSVersion']}+")
            images, invalid = {}, []
            for name in image_names:
                try:
                    images[name] = parse_macho(archive.read(name))
                    report["images"].append({"member": name, "slices": images[name]})
                except (InvalidPackage, UnicodeError, struct.error) as exc:
                    invalid.append(f"{name}: {exc}")
            check(report, "macho", "Mach-O structure", "fail" if invalid else "pass", "\n".join(invalid) if invalid else f"{len(images)} binaries have valid slice, load-command, segment and section bounds.")
            incompatible, encrypted, higher_os = [], [], []
            for name, slices in images.items():
                ios = [image for image in slices if image["cpu"] == 0x100000C and image["platform"] == 2]
                if not ios:
                    incompatible.append(name)
                for image in ios:
                    if image["encrypted"]:
                        encrypted.append(name)
                    if image["minimumOS"] and version_tuple(image["minimumOS"]) > minimum_os:
                        higher_os.append(f"{name}: {image['minimumOS']}")
            check(report, "architecture", "Physical iOS ARM64 support", "fail" if incompatible else "pass", "\n".join(incompatible) if incompatible else "Every inspected binary includes an ARM64 physical-iOS slice.")
            check(report, "encryption", "Executable encryption", "fail" if encrypted else "pass", "\n".join(encrypted) if encrypted else "No inspected ARM64 iOS slice declares FairPlay encryption.")
            check(report, "minimum_os", "Minimum OS consistency", "warn" if higher_os else "pass", "\n".join(higher_os) if higher_os else "Bundled binaries do not require a newer OS than the app declares.")
            main_slices = images.get(main, [])
            if any(image["fileType"] != 2 for image in main_slices):
                check(report, "executable_type", "Main binary type", "fail", "Main binary must have MH_EXECUTE file type.")
            main_ios = next((image for image in main_slices if image["cpu"] == 0x100000C and image["platform"] == 2), None)
            if main_ios:
                declared_sdk = info.get("DTSDKName")
                same_sdk = declared_sdk == "iphoneos" + ".".join(main_ios["sdk"].split(".")[:2])
                check(report, "sdk", "SDK metadata consistency", "pass" if same_sdk else "warn", f"Executable SDK {main_ios['sdk']}; Info.plist {declared_sdk}.")
            missing, weak_missing = [], []
            for name, slices in images.items():
                image = next((item for item in slices if item["cpu"] == 0x100000C and item["platform"] == 2), None)
                if image is None:
                    continue
                host = host_executable(name, root, executable)
                host_root = posixpath.dirname(host)
                host_plist = host_root + "/Info.plist"
                if host_root != root and host_plist in hashes:
                    extension = plistlib.loads(archive.read(host_plist))
                    extension_exec = extension.get("CFBundleExecutable") if isinstance(extension, dict) else None
                    if isinstance(extension_exec, str) and "/" not in extension_exec and "\\" not in extension_exec:
                        host = host_root + "/" + extension_exec
                host_image = next((item for item in images.get(host, []) if item["cpu"] == 0x100000C and item["platform"] == 2), {})
                # Inherited host runpaths have the host as their loader, so expand
                # that token before resolving the dependent library's own paths.
                inherited = [value.replace("@loader_path", posixpath.dirname(host), 1) if value.startswith("@loader_path") else value for value in host_image.get("rpaths", [])]
                runpaths = image["rpaths"] + inherited
                for dependency in image["dependencies"]:
                    resolved = resolve_dependency(dependency["path"], name, host, runpaths, images)
                    if resolved is None:
                        (weak_missing if dependency["weak"] else missing).append(f"{name} -> {dependency['path']}")
            check(report, "dependencies", "Required library paths", "fail" if missing else "pass", "\n".join(missing) if missing else "Required bundled library paths resolve; Apple system libraries are assumed available on the device.")
            if weak_missing:
                check(report, "weak_dependencies", "Optional library paths", "warn", "\n".join(weak_missing))
            unsigned = [name for name, slices in images.items() if any(not item["hasCodeSignature"] for item in slices if item["cpu"] == 0x100000C and item["platform"] == 2)]
            check(report, "signing", "Signing readiness", "warn", f"{len(unsigned)} binaries have no embedded signature. Sign the modified app and all components before ordinary installation. Existing signatures were not cryptographically verified.")
            if profile != "generic":
                check(report, "twitch_version", "Pinned Twitch version", "pass" if info.get("CFBundleShortVersionString") == "30.7" else "fail", "Custom hooks are pinned to Twitch 30.7; other versions need a separate ABI audit.")
                family = info.get("UIDeviceFamily", [])
                check(report, "devices", "Phone and tablet support declared", "pass" if isinstance(family, list) and 1 in family and 2 in family else "fail", str(family))
                loaded = {item["path"] for image in main_slices for item in image["dependencies"]}
                for library_name in CUSTOM_LIBRARIES:
                    member = root + "/Frameworks/" + library_name
                    installed = member in images and any(resolve_dependency(dep, main, main, main_ios.get("rpaths", []) if main_ios else [], images) == member for dep in loaded)
                    check(report, "library_" + library_name, library_name + " installed and loaded", "pass" if installed else "fail", "Bundled Mach-O and main executable load command found." if installed else "Missing binary or main executable dependency.")
                native = root + "/Frameworks/NativeRewind.dylib"
                if native in hashes:
                    native_data = archive.read(native)
                    initialized = any(item["initializerSections"] for item in images.get(native, []))
                    check(report, "initializer", "Native tweak initializer", "pass" if initialized else "fail", "A nonempty module-initializer section is present." if initialized else "No module-initializer section found.")
                    if profile == "beta3":
                        for label, marker in FEATURE_MARKERS.items():
                            check(report, "marker_" + label.lower().replace(" ", "_"), label + " compiled marker", "pass" if marker in native_data else "fail", "String present; runtime behavior is checked separately on a device." if marker in native_data else "Expected Beta 3 feature marker is absent.")
                        full_width = main_ios is not None and version_tuple(main_ios["sdk"]) >= (27, 1, 0) and info.get("UIDesignRequiresCompatibility") is False
                        check(report, "duo_declaration", "Duo full-width opt-in metadata", "pass" if full_width else "fail", "Checks SDK 27.1+ and explicit UIDesignRequiresCompatibility=false; does not prove rendered geometry.")
                    if library:
                        same = hashlib.sha256(native_data).hexdigest() == digest_file(library)
                        check(report, "source_match", "Tested source matches packaged tweak", "pass" if same else "fail", "NativeRewind.dylib is byte-identical to the library built for source regression tests." if same else "Source test library differs from the packaged tweak. Source tests cannot be attributed to this IPA.")
            if baseline:
                with zipfile.ZipFile(baseline) as original:
                    previous, _, _ = archive_inventory(original)
                changed = sorted(name for name in set(hashes) | set(previous) if hashes.get(name) != previous.get(name))
                allowed = {root + "/Frameworks/NativeRewind.dylib"}
                unexpected = [name for name in changed if name not in allowed]
                report["baseline"] = {"file": Path(baseline).name, "sha256": digest_file(baseline), "changedMembers": changed}
                check(report, "preservation", "Baseline preservation", "fail" if unexpected else "pass", ("Unexpected changes outside NativeRewind:\n" + "\n".join(unexpected)) if unexpected else f"{len(changed)} changed member(s), all within the allowed NativeRewind replacement. All other members are byte-identical.")
            else:
                check(report, "preservation", "Baseline preservation", "skip", "Supply --baseline to verify only NativeRewind changed. Use an unsigned, unmodified reference archive.")
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError, NotImplementedError, struct.error, EOFError) as exc:
        check(report, "inspection", "Complete package inspection", "fail", str(exc))
    check(report, "device", "Device behavior", "skip", "Not run. Complete the report's device checklist to record UI and live ad results.")
    return finish(report)


def run_source_tests(repo, compiler_root):
    repo = Path(repo).resolve()
    result = subprocess.run(["bash", str(repo / "tools/build-rewind-linux.sh"), str(Path(compiler_root).resolve())],
                            cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=600)
    return result.returncode, result.stdout


def render_html(report):
    esc = lambda value: html.escape(str(value), quote=True)
    rows = "".join(f'<tr><td><span class="badge {item["status"]}">{esc(item["status"].upper())}</span></td><td><strong>{esc(item["title"])}</strong><pre>{esc(item["detail"])}</pre></td></tr>' for item in report["checks"])
    facts = "".join(f"<dt>{esc(key)}</dt><dd>{esc(value)}</dd>" for key, value in report.get("app", {}).items())
    manual = "".join(f'<article><h3>{esc(item["title"])}</h3><p>{esc(item["steps"])}</p><label>Result <select data-case="{esc(item["id"])}"><option value="not_run">Not run</option><option value="pass">Pass — observed on device</option><option value="fail">Fail</option><option value="not_observed">Not observed / unavailable</option></select></label><label>Notes <textarea data-notes="{esc(item["id"])}" rows="2" placeholder="What happened? Do not include account tokens."></textarea></label></article>' for item in CHECKLIST)
    payload = json.dumps(report, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    label = "Package checks failed" if report["summary"]["fail"] else "Package checks passed — device testing pending"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark light"><title>Twitch IPA Tester report</title>
<style>
:root{{font-family:system-ui,sans-serif;color:#f2eef9;background:#111016;line-height:1.5}}body{{max-width:980px;margin:auto;padding:24px}}h1{{font-size:clamp(26px,5vw,42px);margin-bottom:8px}}h2{{margin-top:38px}}.sub{{color:#bfb7ce}}.result{{background:#252032;border-left:5px solid #a970ff;padding:18px;border-radius:8px;margin:24px 0}}.badge{{font-size:12px;font-weight:700;padding:4px 7px;border-radius:5px}}.pass{{background:#153a2a;color:#98f3bf}}.fail{{background:#52212d;color:#ffc2cc}}.warn{{background:#423415;color:#ffdc91}}.skip{{background:#302d3a;color:#d4cce5}}table{{border-collapse:collapse;width:100%}}td{{vertical-align:top;border-bottom:1px solid #37313f;padding:14px 8px}}pre{{font:13px ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere;margin:8px 0}}dl{{display:grid;grid-template-columns:minmax(100px,1fr) minmax(0,2fr);gap:8px}}dd{{margin:0;overflow-wrap:anywhere}}dt{{color:#bfb7ce;overflow-wrap:anywhere}}article{{background:#1e1a25;padding:18px;border-radius:12px;margin:16px 0}}h3{{margin-top:0}}label{{display:block;margin:12px 0}}input,select,textarea{{font:inherit;color:inherit;background:#121016;border:1px solid #72677f;border-radius:6px;padding:8px;box-sizing:border-box;max-width:100%}}input,textarea{{display:block;width:100%;margin-top:6px}}button{{background:#a970ff;color:#160b26;border:0;border-radius:8px;padding:12px 20px;font:700 16px system-ui;cursor:pointer;margin:12px 8px 12px 0}}button.secondary{{background:#393041;color:#f2eef9}}:focus-visible{{outline:3px solid #caa2ff;outline-offset:3px}}@media print{{:root{{color:black;background:white}}article,.result{{background:#f3f0f7}}button{{display:none}}pre{{font-size:10px}}.sub,dt{{color:#333}}}}
</style></head><body><p class="sub">TwitchPlus · IPA Tester {esc(VERSION)}</p><h1>Your Twitch IPA test report</h1>
<p class="sub">{esc(report['file'])} · {esc(report['generatedAt'])}</p>
<div class="result"><strong>{esc(label)}</strong><p>{report['summary']['pass']} passed · {report['summary']['fail']} failed · {report['summary']['warn']} warnings · {report['summary']['skip']} not run</p><p>This report inspects the package. It does not run Twitch or verify that live ads are blocked.</p></div>
<h2>Build details</h2><dl>{facts}</dl><p>SHA-256</p><pre>{esc(report.get('sha256', 'Unavailable'))}</pre>
<h2>Automatic checks</h2><table><caption class="sub">Static package and optional source checks</caption><tbody>{rows}</tbody></table>
<h2>Device test session</h2><p>Record results while using the signed IPA on your iPhone or iPad. These are manual observations, separate from the automatic checks. No data is sent anywhere; export your results before closing the page.</p>
<label>Device and iOS version<input id="device" placeholder="Device model, OS version, installation method"></label>
{manual}
<button id="export">Download session report</button><button class="secondary" id="print">Print / save PDF</button><p id="export-status" role="status"></p>
<h2>Scope</h2><ul>{''.join('<li>'+esc(value)+'</li>' for value in report['limitations'])}</ul>
<script type="application/json" id="report-data">{payload}</script>
<script>
document.getElementById('print').addEventListener('click',()=>window.print());
document.getElementById('export').addEventListener('click',()=>{{
 const report=JSON.parse(document.getElementById('report-data').textContent);
 const observations=Array.from(document.querySelectorAll('[data-case]')).map(el=>({{id:el.dataset.case,status:el.value,notes:document.querySelector('[data-notes="'+el.dataset.case+'"]').value}}));
 report.manualSession={{recordedAt:new Date().toISOString(),device:document.getElementById('device').value,userEntered:true,observations}};
 const blob=new Blob([JSON.stringify(report,null,2)+'\\n'],{{type:'application/json'}});
 const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download='twitch-ipa-session.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 document.getElementById('export-status').textContent='Session exported. Automatic checks and your observations are labeled separately.';
}});
</script></body></html>'''


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ipa", type=Path, nargs="?")
    parser.add_argument("--gui", action="store_true", help="Choose an IPA using a local file picker and open its report")
    parser.add_argument("--baseline", type=Path, help="Unsigned reference: only NativeRewind may differ")
    parser.add_argument("--expect-sha256", help="Trusted release digest, 64 hexadecimal characters")
    parser.add_argument("--profile", choices=("beta3", "twitchplus", "generic"), default="beta3", help="beta3 checks known features; twitchplus supports older custom releases; generic checks any iOS package")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--source-tests", action="store_true", help="Build and run this checkout's native regressions, then match its dylib to the IPA (Linux only)")
    parser.add_argument("--compiler-root", type=Path, help="Rust 1.99.0 rustc component directory")
    parser.add_argument("--source-repo", type=Path, help="Checkout to build for --source-tests (defaults to this tool's repository)")
    args = parser.parse_args(argv)
    if args.ipa is None and args.gui:
        try:
            from tkinter import Tk, filedialog
            window = Tk()
            window.withdraw()
            selected = filedialog.askopenfilename(title="Choose a Twitch IPA", filetypes=[("iOS app", "*.ipa"), ("All files", "*")])
            window.destroy()
            if not selected:
                return 0
            args.ipa = Path(selected)
        except (ImportError, RuntimeError) as exc:
            parser.error(f"File picker unavailable: {exc}. Pass the IPA path without --gui.")
        except Exception as exc:
            # TclError is unavailable on Python builds without tkinter.
            parser.error(f"File picker unavailable: {exc}. Pass the IPA path without --gui.")
    if args.ipa is None:
        parser.error("Provide an IPA path, or use --gui for the file picker")
    if args.output_dir is None:
        args.output_dir = args.ipa.parent / (args.ipa.stem + "-test-results") if args.gui else Path("ipa-test-results")
    if args.expect_sha256 and not re.fullmatch(r"[a-fA-F0-9]{64}", args.expect_sha256):
        parser.error("--expect-sha256 must be exactly 64 hexadecimal characters")
    if args.source_tests and (not args.compiler_root or not sys.platform.startswith("linux")):
        parser.error("--source-tests requires Linux and --compiler-root; package checks also run on macOS/Windows")
    if args.source_tests and args.profile == "generic":
        parser.error("--source-tests requires the beta3 or twitchplus profile")
    if args.source_repo and not args.source_tests:
        parser.error("--source-repo requires --source-tests")
    inputs = {value.resolve() for value in (args.ipa, args.baseline) if value}
    for output in ("report.json", "report.html", "source-tests.log"):
        if (args.output_dir / output).resolve() in inputs:
            parser.error("Output files must not overwrite an input archive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    repo = (args.source_repo or Path(__file__).resolve().parents[1]).resolve()
    library = None
    source_status = None
    if args.source_tests:
        try:
            code, output = run_source_tests(repo, args.compiler_root)
            source_status = code == 0
            (args.output_dir / "source-tests.log").write_text(output, encoding="utf-8")
            if source_status:
                library = repo / "build/NativeRewind.dylib"
        except (OSError, subprocess.TimeoutExpired) as exc:
            source_status = False
            (args.output_dir / "source-tests.log").write_text(str(exc), encoding="utf-8")
    report = inspect_ipa(args.ipa, args.baseline, args.expect_sha256, args.profile, library)
    if source_status is not None:
        check(report, "source_regressions", "Native source regression suite", "pass" if source_status else "fail", "See source-tests.log. These are host mocks, not an iOS runtime test; the separate source-match check ties the compiled tweak to this IPA.")
        try:
            commit = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
            if commit.returncode == 0:
                report["sourceCommit"] = commit.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            pass
    else:
        check(report, "source_regressions", "Native source regression suite", "skip", "Use --source-tests --compiler-root on Linux to rebuild, test, and check binary provenance.")
    finish(report)
    report_path = args.output_dir / "report.json"
    html_path = args.output_dir / "report.html"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_html(report), encoding="utf-8")
    for item in report["checks"]:
        print(f"{item['status'].upper():4}  {item['title']}")
        if item["status"] == "fail":
            print("      " + item["detail"].replace("\n", "\n      "))
    print(f"\n{report['result']}: {report['summary']}\nReport: {html_path}\nDevice behavior: not run")
    if args.gui:
        webbrowser.open(html_path.resolve().as_uri())
    return 1 if report["summary"]["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
