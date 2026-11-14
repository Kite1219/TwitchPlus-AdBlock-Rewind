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

// Theater uses both axes (feed scrolling intentionally clips horizontally only).
// Start from the native player's vertical region so portrait metadata/chat below
// it cannot move into the video. Expand horizontally only inside the hit area.
CGRect tp_theater_viewport(CGRect bounds,CGRect window,CGRect nativePlayer,CGRect chat,int expand) {
    CGRect area=tp_intersect_horizontal(bounds,window);
    if(!tp_rect_valid(area) || !tp_rect_valid(nativePlayer)) return (CGRect){0};
    if(!expand) area=tp_intersect_horizontal(area,nativePlayer);
    double top=bounds.origin.y>nativePlayer.origin.y?bounds.origin.y:nativePlayer.origin.y;
    if(window.origin.y>top) top=window.origin.y;
    double bottom=bounds.origin.y+bounds.size.height;
    if(nativePlayer.origin.y+nativePlayer.size.height<bottom) bottom=nativePlayer.origin.y+nativePlayer.size.height;
    if(window.origin.y+window.size.height<bottom) bottom=window.origin.y+window.size.height;
    area.origin.y=top; area.size.height=bottom>top?bottom-top:0;
    if(!tp_rect_valid(area) || !tp_rect_valid(chat)) return area;
    double overlapTop=chat.origin.y>top?chat.origin.y:top;
    double overlapBottom=chat.origin.y+chat.size.height<bottom?chat.origin.y+chat.size.height:bottom;
    // Only an edge-docked side pane. A portrait transcript below the player,
    // hidden chat, an unrelated floating sheet, and a fully offscreen pane do
    // not reserve width. Coordinates are physical, so left-side chat works too.
    if(overlapBottom-overlapTop<area.size.height*.6 || chat.size.width>area.size.width*.65) return area;
    double left=area.origin.x,right=left+area.size.width,chatRight=chat.origin.x+chat.size.width;
    if(chat.origin.x>left+2 && chat.origin.x<right && chatRight>=right-2) area.size.width=chat.origin.x-left;
    else if(chat.origin.x<=left+2 && chatRight>left && chatRight<right-2) {
        area.origin.x=chatRight; area.size.width=right-chatRight;
    }
    return area;
}
