#include "TwitchPlusCore.h"

static size_t strsize(const char *s) { size_t n=0; while(s[n]) n++; return n; }
static int starts(const char *text,size_t length,const char *prefix) {
    size_t n=strsize(prefix); if(n>length) return 0;
    for(size_t i=0;i<n;i++) if(text[i]!=prefix[i]) return 0;
    return 1;
}
int tp_hls_valid(const char *text,size_t length) {
    return text && length<=1048576 && starts(text,length,"#EXTM3U");
}
int tp_buffer_fits(size_t current,size_t incoming,size_t limit) {
    return current<=limit && incoming<=limit-current;
}
int tp_rect_valid(CGRect r) {
    return r.origin.x>-100000 && r.origin.x<100000 && r.origin.y>-100000 && r.origin.y<100000 &&
           r.size.width>0 && r.size.width<100000 && r.size.height>0 && r.size.height<100000;
}
CGRect tp_intersect_horizontal(CGRect current,CGRect clip) {
    double left=current.origin.x>clip.origin.x?current.origin.x:clip.origin.x;
    double right=current.origin.x+current.size.width<clip.origin.x+clip.size.width?
                 current.origin.x+current.size.width:clip.origin.x+clip.size.width;
    current.origin.x=left; current.size.width=right>left?right-left:0;
    return current;
}
CGRect tp_aspect_fit(CGSize video,CGRect available) {
    if(!(video.width>0 && video.width<100000 && video.height>0 && video.height<100000) || !tp_rect_valid(available)) {
        available.size=(CGSize){0,0}; return available;
    }
    double scale=available.size.width/video.width;
    double other=available.size.height/video.height;
    if(other<scale) scale=other;
    double width=video.width*scale,height=video.height*scale;
    available.origin.x+=(available.size.width-width)*0.5;
    available.origin.y+=(available.size.height-height)*0.5;
    available.size=(CGSize){width,height}; return available;
}
