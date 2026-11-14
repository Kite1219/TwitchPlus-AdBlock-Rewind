import ctypes as C
import math
from pathlib import Path
import unittest

class Point(C.Structure): _fields_=[('x',C.c_double),('y',C.c_double)]
class Size(C.Structure): _fields_=[('width',C.c_double),('height',C.c_double)]
class Rect(C.Structure): _fields_=[('origin',Point),('size',Size)]
def rect(x,y,w,h): return Rect(Point(x,y),Size(w,h))
lib=C.CDLL(str(Path(__file__).parents[1]/'build/TwitchPlusCore-test.so'))
lib.tp_aspect_fit.argtypes=[Size,Rect];lib.tp_aspect_fit.restype=Rect
lib.tp_intersect_horizontal.argtypes=[Rect,Rect];lib.tp_intersect_horizontal.restype=Rect
lib.tp_rect_valid.argtypes=[Rect];lib.tp_rect_valid.restype=C.c_int
lib.tp_buffer_fits.argtypes=[C.c_size_t,C.c_size_t,C.c_size_t];lib.tp_buffer_fits.restype=C.c_int
lib.tp_hls_valid.argtypes=[C.c_char_p,C.c_size_t];lib.tp_hls_valid.restype=C.c_int

class CoreTests(unittest.TestCase):
    def test_sidebar_clipping_far_above_card_reduces_viewport(self):
        area=rect(0,0,1280,700)
        for ancestor in (rect(0,0,1280,900),rect(448,0,832,900),rect(0,0,1280,900)):
            area=lib.tp_intersect_horizontal(area,ancestor)
        result=lib.tp_aspect_fit(Size(1920,1080),area)
        self.assertEqual(result.origin.x,448)
        self.assertEqual(result.size.width,832)
        self.assertEqual(result.size.height,468)

    def test_sidebar_close_restores_full_source_without_reusing_narrow_size(self):
        wide=rect(0,0,1280,900)
        narrow=lib.tp_intersect_horizontal(wide,rect(448,0,832,900))
        self.assertEqual(lib.tp_aspect_fit(Size(2560,1080),narrow).size.width,832)
        self.assertEqual(lib.tp_aspect_fit(Size(2560,1080),wide).size.width,1280)

    def test_vertical_scrolling_does_not_resize_video(self):
        area=lib.tp_intersect_horizontal(rect(0,0,832,700),rect(0,-400,832,900))
        self.assertEqual(area.size.height,700)
        self.assertEqual(area.origin.y,0)

    def test_full_frame_always_fits_for_ultrawide_portrait_and_standard_sources(self):
        for vw,vh in ((2560,1080),(1920,1080),(1080,1920),(1080,1080)):
            for w,h in ((1280,900),(832,700),(390,844),(844,390),(320,240)):
                with self.subTest(video=(vw,vh),pane=(w,h)):
                    r=lib.tp_aspect_fit(Size(vw,vh),rect(0,0,w,h))
                    self.assertGreaterEqual(r.origin.x,0);self.assertGreaterEqual(r.origin.y,0)
                    self.assertLessEqual(r.origin.x+r.size.width,w+1e-6)
                    self.assertLessEqual(r.origin.y+r.size.height,h+1e-6)
                    self.assertAlmostEqual(r.size.width/r.size.height,vw/vh)

    def test_invalid_source_size_does_not_create_layout_constraints(self):
        for size in (Size(0,0),Size(math.nan,1080),Size(1920,math.inf),Size(-1,3)):
            self.assertFalse(lib.tp_rect_valid(lib.tp_aspect_fit(size,rect(0,0,1280,900))))

    def test_nonintersecting_sidebar_geometry_is_rejected(self):
        r=lib.tp_intersect_horizontal(rect(0,0,100,100),rect(200,0,100,100))
        self.assertFalse(lib.tp_rect_valid(r))

    def test_chunk_buffer_limit_has_no_integer_overflow(self):
        self.assertTrue(lib.tp_buffer_fits(1024,1024,1048576))
        self.assertTrue(lib.tp_buffer_fits(1048576,0,1048576))
        self.assertFalse(lib.tp_buffer_fits(1048576,1,1048576))
        self.assertFalse(lib.tp_buffer_fits(C.c_size_t(-1).value,2,1048576))
        self.assertFalse(lib.tp_buffer_fits(3,C.c_size_t(-1).value,1048576))

    def test_playlist_validation_rejects_html_empty_and_oversized_bodies(self):
        for data in (b'',b'<html>bad gateway</html>',b'#EXTM3U\n'+b'x'*1048576):
            self.assertFalse(lib.tp_hls_valid(data,len(data)))
        self.assertTrue(lib.tp_hls_valid(b'#EXTM3U\n',8))

if __name__=='__main__': unittest.main(verbosity=2)
