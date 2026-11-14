import importlib.util
import struct
import unittest
import json
import plistlib
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
spec = importlib.util.spec_from_file_location('packager', Path(__file__).parents[1]/'tools/package-rewind-update.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def binary(sdk=0x1b0100, platform=2, encrypted=False):
    commands = struct.pack('<6I', 0x32, 24, platform, 0x100400, sdk, 0)
    if encrypted:
        commands += struct.pack('<6I', 0x2c, 24, 0, 0, 1, 0)
    return struct.pack('<8I', 0xfeedfacf, 0x100000c, 0, 2, 2 if encrypted else 1, len(commands), 0, 0)+commands+b'PAYLOAD-CODE-UNCHANGED'

class PackagingTests(unittest.TestCase):
    def test_sdk_patch_preserves_all_other_bytes(self):
        original = binary()
        result = m.compat_sdk(original)
        self.assertEqual(result[:48], original[:48])
        self.assertEqual(result[52:], original[52:])
        self.assertEqual(struct.unpack_from('<I',result,48)[0],0x1b0000)
        self.assertEqual(len(result),len(original))
    def test_rejects_unexpected_sdk(self):
        with self.assertRaises(ValueError):m.compat_sdk(binary(sdk=0x1f0000))
    def test_rejects_non_ios_platform(self):
        with self.assertRaises(ValueError):m.compat_sdk(binary(platform=1))
    def test_rejects_encrypted_binary(self):
        with self.assertRaises(ValueError):m.compat_sdk(binary(encrypted=True))
    def test_rejects_bad_load_command(self):
        original=bytearray(binary());struct.pack_into('<I',original,36,4)
        with self.assertRaises(ValueError):m.compat_sdk(original)

    def test_two_library_update_preserves_app_and_resources(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);base=root/'base.ipa';rewind=root/'rewind.dylib';ad=root/'ad.dylib';output=root/'new.ipa'
            before={'Payload/Twitch.app/Info.plist':plistlib.dumps({'DTSDKName':'iphoneos27.1'}),
                    'Payload/Twitch.app/Twitch':binary(),
                    'Payload/Twitch.app/Frameworks/NativeRewind.dylib':binary()+b'OLD-REWIND',
                    'Payload/Twitch.app/Frameworks/TwitchAdBlock.dylib':binary()+b'OLD-ADBLOCK',
                    'Payload/Twitch.app/Assets.car':b'KEEP-ASSETS'}
            with zipfile.ZipFile(base,'w') as archive:
                for name,data in before.items():archive.writestr(name,data)
            rewind.write_bytes(binary()+b'NEW-REWIND');ad.write_bytes(binary()+b'NEW-FILTER')
            result=subprocess.run([sys.executable,str(Path(m.__file__)), '--base',str(base),'--library',str(rewind),
                                   '--ad-library',str(ad),'--output',str(output)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            report=json.loads(output.with_suffix('.validation.json').read_text())
            self.assertEqual(report['adBlockImplementation'],'native-response-filter')
            self.assertEqual(len(report['changedMembers']),2)
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(archive.testzip(),None)
                for name in ('Payload/Twitch.app/Twitch','Payload/Twitch.app/Info.plist','Payload/Twitch.app/Assets.car'):
                    self.assertEqual(archive.read(name),before[name])
                self.assertEqual(archive.read('Payload/Twitch.app/Frameworks/TwitchAdBlock.dylib'),ad.read_bytes())

    def test_missing_legacy_ad_library_cannot_silently_drop_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);base=root/'base.ipa';library=root/'lib.dylib'
            library.write_bytes(binary())
            with zipfile.ZipFile(base,'w') as archive:
                archive.writestr('Payload/Twitch.app/Frameworks/NativeRewind.dylib',binary())
                archive.writestr('Payload/Twitch.app/Info.plist',plistlib.dumps({}))
            result=subprocess.run([sys.executable,str(Path(m.__file__)), '--base',str(base),'--library',str(library),
                                   '--ad-library',str(library),'--output',str(root/'new.ipa')],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertFalse((root/'new.ipa').exists())

if __name__=='__main__':unittest.main(verbosity=2)
