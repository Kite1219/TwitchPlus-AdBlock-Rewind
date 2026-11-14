"""Replace only NativeRewind in an existing TwitchPlus IPA and verify preservation."""
import argparse, copy, hashlib, json, zipfile
from pathlib import Path

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base', type=Path, required=True)
    p.add_argument('--library', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.base.resolve() == args.output.resolve():
        raise ValueError('Input must not be overwritten')
    name = 'Payload/Twitch.app/Frameworks/NativeRewind.dylib'
    data = args.library.read_bytes()
    if data[:8] != bytes.fromhex('cffaedfe0c000001'):
        raise ValueError('Expected ARM64 Mach-O library')
    before = sha(args.base.read_bytes())
    hashes = {}
    with zipfile.ZipFile(args.base) as src:
        if len(src.namelist()) != len(set(src.namelist())) or name not in src.namelist():
            raise ValueError('Expected TwitchPlus archive without duplicate members')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as dst:
            for entry in src.infolist():
                original = src.read(entry)
                hashes[entry.filename] = sha(original)
                dst.writestr(copy.copy(entry), data if entry.filename == name else original)
    with zipfile.ZipFile(args.output) as dst:
        assert dst.testzip() is None
        assert len(dst.namelist()) == len(hashes) and set(dst.namelist()) == set(hashes)
        for member, digest in hashes.items():
            assert sha(dst.read(member)) == (sha(data) if member == name else digest), member
    assert sha(args.base.read_bytes()) == before
    report = {'baseSha256': before, 'outputSha256': sha(args.output.read_bytes()),
              'bytes': args.output.stat().st_size, 'changedMembers': [name],
              'allOtherMembersByteIdentical': True, 'zipCRC': 'passed', 'deviceTested': False}
    args.output.with_suffix('.validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
