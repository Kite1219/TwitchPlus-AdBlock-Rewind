"""Guard the user's accepted Beta 4 behavior during this layout-only update."""
import hashlib
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class PreservationTests(unittest.TestCase):
    def test_beta4_native_network_filter_is_unchanged(self):
        source=(ROOT/'src/TwitchPlusFixes.m').read_bytes()
        network=source.split(b'// Layout implementation follows below;')[0]
        self.assertEqual(hashlib.sha256(network).hexdigest(),
                         '03610bf9b641d43806738d285db8e9f64576e0c005c603024912b2b507619fd1')

    def test_beta4_playlist_engine_is_unchanged(self):
        self.assertEqual(hashlib.sha256((ROOT/'src/PlaylistEngine.js').read_bytes()).hexdigest(),
                         'ad0e491cadecddd61e70ca9bd93f1bf05e0027f3570a76ecee3be41151d557c1')

    def test_beta4_compact_navigation_is_unchanged(self):
        source=(ROOT/'src/TwitchPlusFixes.m').read_bytes()
        compact=source.split(b'static BOOL TPWidePhone(')[1].split(b'static void TPRootLayout(')[0]
        self.assertEqual(hashlib.sha256(compact).hexdigest(),
                         'a3d2eca1d40b1aa3a9c829167dea1d9f1a61f372ab1031ba3a414177bbfcdc31')

if __name__=='__main__': unittest.main(verbosity=2)
