import importlib.util
import struct
import unittest
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

if __name__=='__main__':unittest.main(verbosity=2)
