"""Replace only NativeRewind in an existing TwitchPlus IPA and verify preservation."""
import argparse, copy, hashlib, json, zipfile, struct, plistlib
from pathlib import Path

def sha(data):
    return hashlib.sha256(data).hexdigest()

def compat_sdk(data):
    # Only the advertised SDK field changes. No code, offsets or min OS change.
    if data[:8] != bytes.fromhex('cffaedfe0c000001'):
        raise ValueError('Expected thin ARM64 executable')
    result = bytearray(data)
    cursor = 32
    changed = []
    for _ in range(struct.unpack_from('<I', data, 16)[0]):
        cmd, size = struct.unpack_from('<II', data, cursor)
        if size < 8 or cursor + size > 32 + struct.unpack_from('<I', data, 20)[0]:
            raise ValueError('Invalid Mach-O commands')
        if cmd == 0x2c and struct.unpack_from('<I', data, cursor+16)[0] != 0:
            raise ValueError('Encrypted executable')
        if cmd == 0x32:
            platform, minimum, sdk = struct.unpack_from('<III', data, cursor+8)
            if platform != 2 or sdk != 0x1b0100:
                raise ValueError('Expected v1.4 iOS 27.1 SDK field')
            struct.pack_into('<I', result, cursor+16, 0x1b0000)
            changed.append(cursor+16)
        cursor += size
    if len(changed) != 1:
        raise ValueError('Expected one LC_BUILD_VERSION')
    offset = changed[0]
    assert result[:offset] == data[:offset] and result[offset+4:] == data[offset+4:]
    return bytes(result)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base', type=Path, required=True)
    p.add_argument('--library', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--duo-compatibility', action='store_true')
    args = p.parse_args()
    if args.base.resolve() == args.output.resolve():
        raise ValueError('Input must not be overwritten')
    name = 'Payload/Twitch.app/Frameworks/NativeRewind.dylib'
    data = args.library.read_bytes()
    if data[:8] != bytes.fromhex('cffaedfe0c000001'):
        raise ValueError('Expected ARM64 Mach-O library')
    before = sha(args.base.read_bytes())
    hashes = {}
    replacements = {name: data}
    with zipfile.ZipFile(args.base) as src:
        if len(src.namelist()) != len(set(src.namelist())) or name not in src.namelist():
            raise ValueError('Expected TwitchPlus archive without duplicate members')
        if args.duo_compatibility:
            binary_name = 'Payload/Twitch.app/Twitch'
            plist_name = 'Payload/Twitch.app/Info.plist'
            replacements[binary_name] = compat_sdk(src.read(binary_name))
            info = plistlib.loads(src.read(plist_name))
            if info.get('DTSDKName') != 'iphoneos27.1':
                raise ValueError('Expected v1.4 SDK metadata')
            info['DTSDKName'] = 'iphoneos27.0'
            info['DTPlatformVersion'] = '27.0'
            replacements[plist_name] = plistlib.dumps(info, fmt=plistlib.FMT_BINARY)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as dst:
            for entry in src.infolist():
                original = src.read(entry)
                hashes[entry.filename] = sha(original)
                dst.writestr(copy.copy(entry), replacements.get(entry.filename, original))
    with zipfile.ZipFile(args.output) as dst:
        assert dst.testzip() is None
        assert len(dst.namelist()) == len(hashes) and set(dst.namelist()) == set(hashes)
        for member, digest in hashes.items():
            assert sha(dst.read(member)) == (sha(replacements[member]) if member in replacements else digest), member
    assert sha(args.base.read_bytes()) == before
    report = {'baseSha256': before, 'outputSha256': sha(args.output.read_bytes()),
              'bytes': args.output.stat().st_size, 'changedMembers': list(replacements), 'duoCompatibilitySDK': '27.0' if args.duo_compatibility else None,
              'allOtherMembersByteIdentical': True, 'zipCRC': 'passed', 'deviceTested': False}
    args.output.with_suffix('.validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
