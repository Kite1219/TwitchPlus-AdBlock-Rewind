#ifndef TWITCHPLUS_CORE_H
#define TWITCHPLUS_CORE_H
#include <stddef.h>
#ifdef TP_USE_APPLE_SDK
#include <CoreGraphics/CoreGraphics.h>
#else
typedef struct CGPoint { double x, y; } CGPoint;
typedef struct CGSize { double width, height; } CGSize;
typedef struct CGRect { CGPoint origin; CGSize size; } CGRect;
typedef struct UIEdgeInsets { double top, left, bottom, right; } UIEdgeInsets;
#endif
int tp_hls_valid(const char *text, size_t length);
int tp_buffer_fits(size_t current, size_t incoming, size_t limit);
CGRect tp_intersect_horizontal(CGRect current, CGRect clip);
CGRect tp_aspect_fit(CGSize video, CGRect available);
int tp_rect_valid(CGRect rect);
#endif
