#![feature(no_core, lang_items, auto_traits, intrinsics)]
#![no_core]
#![allow(internal_features, improper_ctypes, clashing_extern_declarations, ambiguous_wide_pointer_comparisons)]

#[lang="pointee_sized"] pub trait PointeeSized {}
#[lang="meta_sized"] pub trait MetaSized: PointeeSized {}
#[lang="sized"] pub trait Sized: MetaSized {}
#[lang="sync"] pub unsafe auto trait Sync {}
#[lang="copy"] pub trait Copy {}
impl<T:PointeeSized> Copy for *const T {}
impl<T:PointeeSized> Copy for *mut T {}
impl Copy for u8 {} impl Copy for u32 {} impl Copy for usize {} impl Copy for bool {}
#[lang="drop_glue"] pub unsafe fn drop_glue<T:PointeeSized>(_:*mut T) {}
#[lang="legacy_receiver"] pub trait LegacyReceiver:PointeeSized {}
impl<T:PointeeSized> LegacyReceiver for &T {}
impl<T:PointeeSized> LegacyReceiver for &mut T {}
#[lang="eq"] pub trait PartialEq<Rhs:PointeeSized=Self> {fn eq(&self,rhs:&Rhs)->bool;fn ne(&self,rhs:&Rhs)->bool;}
impl<T:PointeeSized> PartialEq for *mut T {fn eq(&self,rhs:&Self)->bool{*self==*rhs}fn ne(&self,rhs:&Self)->bool{*self!=*rhs}}
impl<T:PointeeSized> PartialEq for *const T {fn eq(&self,rhs:&Self)->bool{*self==*rhs}fn ne(&self,rhs:&Self)->bool{*self!=*rhs}}
impl PartialEq for usize {fn eq(&self,rhs:&Self)->bool{*self==*rhs}fn ne(&self,rhs:&Self)->bool{*self!=*rhs}}
impl PartialEq for bool {fn eq(&self,rhs:&Self)->bool{*self==*rhs}fn ne(&self,rhs:&Self)->bool{*self!=*rhs}}
impl PartialEq for u32 {fn eq(&self,rhs:&Self)->bool{*self==*rhs}fn ne(&self,rhs:&Self)->bool{*self!=*rhs}}
#[lang="add"] pub trait Add<Rhs=Self>{type Output;fn add(self,rhs:Rhs)->Self::Output;}
impl Add for usize{type Output=Self;fn add(self,rhs:Self)->Self{self+rhs}}
#[lang="not"] pub trait Not{type Output;fn not(self)->Self::Output;}
impl Not for bool{type Output=Self;fn not(self)->Self{if self{false}else{true}}}
#[lang="partial_ord"] pub trait PartialOrd<Rhs:PointeeSized=Self>:PartialEq<Rhs>{fn lt(&self,rhs:&Rhs)->bool;fn le(&self,rhs:&Rhs)->bool;fn gt(&self,rhs:&Rhs)->bool;fn ge(&self,rhs:&Rhs)->bool;}
impl PartialOrd for usize{fn lt(&self,rhs:&Self)->bool{*self<*rhs}fn le(&self,rhs:&Self)->bool{*self<=*rhs}fn gt(&self,rhs:&Self)->bool{*self>*rhs}fn ge(&self,rhs:&Self)->bool{*self>=*rhs}}
#[rustc_intrinsic] pub unsafe fn transmute<Src,Dst>(source:Src)->Dst;

type Id=*mut u8; type Sel=*mut u8;
impl PartialEq for u8{fn eq(&self,rhs:&Self)->bool{*self==*rhs}fn ne(&self,rhs:&Self)->bool{*self!=*rhs}}
impl Copy for f64 {}
impl Add for f64{type Output=Self;fn add(self,rhs:Self)->Self{self+rhs}}
impl PartialEq for f64{fn eq(&self,rhs:&Self)->bool{*self==*rhs}fn ne(&self,rhs:&Self)->bool{*self!=*rhs}}
impl PartialOrd for f64{fn lt(&self,rhs:&Self)->bool{*self<*rhs}fn le(&self,rhs:&Self)->bool{*self<=*rhs}fn gt(&self,rhs:&Self)->bool{*self>*rhs}fn ge(&self,rhs:&Self)->bool{*self>=*rhs}}


type Zero=unsafe extern "C" fn(Id,Sel);
type Load=unsafe extern "C" fn(Id,Sel,Id,Id);
#[repr(C)]struct CMTime{value:i64,scale:i32,flags:u32,epoch:i64}
impl Copy for i64{} impl Copy for i32{} impl Copy for CMTime{}
#[lang="sub"]pub trait Sub<Rhs=Self>{type Output;fn sub(self,rhs:Rhs)->Self::Output;}
impl Sub for f64{type Output=Self;fn sub(self,rhs:Self)->Self{self-rhs}}
impl Copy for f32{}
#[lang="mul"]pub trait Mul<Rhs=Self>{type Output;fn mul(self,rhs:Rhs)->Self::Output;}impl Mul for f64{type Output=Self;fn mul(self,rhs:Self)->Self{self*rhs}}
#[lang="div"]pub trait Div<Rhs=Self>{type Output;fn div(self,rhs:Rhs)->Self::Output;}impl Div for f64{type Output=Self;fn div(self,rhs:Self)->Self{self/rhs}}
#[repr(C)]struct Point{x:f64,y:f64}
#[repr(C)]struct Size{width:f64,height:f64}
#[repr(C)]struct Rect{origin:Point,size:Size}
impl Copy for Point{} impl Copy for Size{} impl Copy for Rect{}
struct Responsive{padding:f64,bottom:f64,skip:f64,visible:bool,sides:bool}
// Width and height are the current player safe-area rectangle, never a model ID.
fn responsive(width:f64,height:f64)->Responsive{
 let visible=width>=240.0&&width<10000.0&&height>=128.0&&height<10000.0;
 let raw=if width>=0.0&&width<10000.0{width*0.18}else{64.0};let skip=if raw<64.0{64.0}else{if raw>88.0{88.0}else{raw}};
 let padding=if width<360.0{12.0}else{16.0};
 let bottom=if height<180.0{24.0}else{if height<210.0{36.0}else{48.0}};
 // Keep the 44-point skip target clear of the LIVE badge during narrow/short resize states.
 let clear_horizontal=width*0.5+skip+22.0+8.0<=width-padding-68.0;
 let clear_vertical=height*0.5+22.0+8.0<=height-bottom-92.0;
 // The timeline spans the whole width, so horizontal badge clearance alone
 // cannot make center skip buttons safe in a short landscape/split pane.
 let clear_timeline=height*0.5+22.0+8.0<=height-bottom-44.0;
 // The timestamp occupies the left 72 points above the timeline.
 let clear_label_horizontal=width*0.5-skip-22.0>=padding+72.0+8.0;
 let clear_label_vertical=height*0.5+22.0+8.0<=height-bottom-44.0-2.0-20.0;
 Responsive{padding:padding,bottom:bottom,skip:skip,visible:visible,sides:visible&&width>=280.0&&height>=180.0&&clear_timeline&&(clear_horizontal||clear_vertical)&&(clear_label_horizontal||clear_label_vertical)}
}
unsafe extern "C"{
 #[link_name="objc_msgSend"]fn convert_rect(o:Id,s:Sel,r:Rect,to:Id)->Rect;
 #[link_name="objc_msgSend"]fn rect(o:Id,s:Sel)->Rect;
 #[link_name="objc_msgSend"]fn rgba(o:Id,s:Sel,r:f64,g:f64,b:f64,a:f64)->Id;
 #[link_name="objc_msgSend"]fn font2(o:Id,s:Sel,size:f64,weight:f64)->Id;
 fn CFAbsoluteTimeGetCurrent()->f64;
 #[link_name="objc_msgSend"]fn mf(o:Id,s:Sel,v:f32)->Id;
 #[link_name="objc_msgSend"]fn float(o:Id,s:Sel)->f32;
 #[link_name="objc_msgSend"]fn b0(o:Id,s:Sel)->bool;
 #[link_name="objc_msgSend"]fn anchor(o:Id,s:Sel,a:Id,c:f64)->Id;
 fn objc_getClass(n:*const u8)->Id;fn object_getClass(o:Id)->Id;fn sel_registerName(n:*const u8)->Sel;
 fn objc_allocateClassPair(base:Id,name:*const u8,extra:usize)->Id;fn objc_registerClassPair(c:Id);
 fn class_getInstanceMethod(c:Id,s:Sel)->Id;fn method_getImplementation(m:Id)->Id;fn method_getTypeEncoding(m:Id)->*const u8;
 fn class_addMethod(c:Id,s:Sel,imp:Id,encoding:*const u8)->bool;fn method_setImplementation(m:Id,imp:Id)->Id;
 fn class_getInstanceVariable(c:Id,n:*const u8)->Id;fn ivar_getOffset(i:Id)->usize;
 fn objc_getAssociatedObject(o:Id,k:Id)->Id;fn objc_setAssociatedObject(o:Id,k:Id,v:Id,p:usize);
 fn dlsym(h:Id,n:*const u8)->Id;fn dispatch_async_f(q:Id,c:Id,f:unsafe extern "C" fn(Id));fn dispatch_get_global_queue(q:usize,flags:usize)->Id;
 fn CMTimeMakeWithSeconds(seconds:f64,scale:i32)->CMTime;fn CMTimeGetSeconds(t:CMTime)->f64;
 #[link_name="objc_msgSend"]fn set_bool(o:Id,s:Sel,v:bool,key:Id);
 #[link_name="objc_msgSend"]fn present(o:Id,s:Sel,vc:Id,animated:bool,completion:Id);
 #[link_name="objc_msgSend"]fn dismiss(o:Id,s:Sel,animated:bool,completion:Id);
 #[link_name="objc_msgSend"]fn m0(o:Id,s:Sel)->Id;
 #[link_name="objc_msgSend"]fn m1(o:Id,s:Sel,a:Id)->Id;
 #[link_name="objc_msgSend"]fn m2(o:Id,s:Sel,a:Id,b:Id)->Id;
 #[link_name="objc_msgSend"]fn m3(o:Id,s:Sel,a:Id,b:Id,c:Id)->Id;
 #[link_name="objc_msgSend"]fn mu(o:Id,s:Sel,a:usize)->Id;
 #[link_name="objc_msgSend"]fn count(o:Id,s:Sel)->usize;
 #[link_name="objc_msgSend"]fn b1(o:Id,s:Sel,a:Id)->bool;
 #[link_name="objc_msgSend"]fn mb(o:Id,s:Sel,v:bool)->Id;
 #[link_name="objc_msgSend"]fn md(o:Id,s:Sel,v:f64)->Id;
 #[link_name="objc_msgSend"]fn double(o:Id,s:Sel)->f64;
 #[link_name="objc_msgSend"]fn time(o:Id,s:Sel)->CMTime;
 #[link_name="objc_msgSend"]fn seek(o:Id,s:Sel,t:CMTime);
 #[link_name="objc_msgSend"]fn title(o:Id,s:Sel,v:Id,state:usize)->Id;
 #[link_name="objc_msgSend"]fn action(o:Id,s:Sel,t:Id,a:Sel,event:usize)->Id;
 #[link_name="objc_msgSend"]fn timer(o:Id,s:Sel,seconds:f64,t:Id,a:Sel,info:Id,repeats:bool)->Id;
}
static mut MAIN:Id=0 as Id;static mut TARGET:Id=0 as Id;static mut ROWS:Id=0 as Id;static mut PLAYERS:Id=0 as Id;
static mut OLD_TAB_LOAD:Id=0 as Id;
static mut OLD_LOAD:Id=0 as Id;static mut OLD_SOURCE:Id=0 as Id;static mut OLD_LAYOUT:Id=0 as Id;
static DOT_KEY:u8=0;static CLEAR_KEY:u8=0;static TRACKING_KEY:u8=0;static OPTIONS_KEY:u8=0;static STATE_KEY:u8=0;static INTERNAL_KEY:u8=0;static ROW_KEY:u8=0;static PLAYER_KEY:u8=0;static PAD_LEFT_KEY:u8=0;static PAD_RIGHT_KEY:u8=0;static BOTTOM_KEY:u8=0;static SKIP_LEFT_KEY:u8=0;static SKIP_RIGHT_KEY:u8=0;static GEOMETRY_VISIBLE_KEY:u8=0;static BADGE_KEY:u8=0;static BACK_KEY:u8=0;static FORWARD_KEY:u8=0;static SLIDER_KEY:u8=0;static LABEL_KEY:u8=0;static LIVE_KEY:u8=0;
// SDK metadata enables vertical bars, but this Twitch version predates them.
// UIVerticalBarBehaviorDisabled = 1 (UIKit public header).
unsafe extern "C" fn horizontal_bars(_:Id,_:Sel)->i64{1}
unsafe extern "C" fn bar_preference_owner(_:Id,_:Sel)->Id{0 as Id}
unsafe fn install_horizontal_bars(c:Id){unsafe{
 if c==0 as Id{return;}
 let base=cls(b"UIViewController\0" as *const u8);
 let preferred=s(b"preferredVerticalBarBehavior\0" as *const u8);
 let child=s(b"childViewControllerForPreferredVerticalBarBehavior\0" as *const u8);
 let pm=class_getInstanceMethod(base,preferred);let cm=class_getInstanceMethod(base,child);
 if pm==0 as Id||cm==0 as Id{return;}
 // addMethod leaves any existing class implementation intact.
 class_addMethod(c,preferred,horizontal_bars as Id,method_getTypeEncoding(pm));
 class_addMethod(c,child,bar_preference_owner as Id,method_getTypeEncoding(cm));
}}
unsafe fn initialize_duo_bars(){unsafe{
 install_horizontal_bars(cls(b"_TtC6Twitch16TabBarController\0" as *const u8));
 install_horizontal_bars(cls(b"_TtC6Twitch21TheaterViewController\0" as *const u8));
 install_horizontal_bars(cls(b"_TtC6Twitch30TheaterContainerViewController\0" as *const u8));
}}
unsafe fn auto_enabled()->bool{unsafe{
 let defaults=m0(cls(b"NSUserDefaults\0" as *const u8),s(b"standardUserDefaults\0" as *const u8));
 b1(defaults,s(b"boolForKey:\0" as *const u8),str(b"TwitchPlusAutomaticRewindEnabled\0" as *const u8))
}}
unsafe fn save_auto(enabled:bool){unsafe{
 let defaults=m0(cls(b"NSUserDefaults\0" as *const u8),s(b"standardUserDefaults\0" as *const u8));
 set_bool(defaults,s(b"setBool:forKey:\0" as *const u8),enabled,str(b"TwitchPlusAutomaticRewindEnabled\0" as *const u8));
 // Changes apply to the next channel load; disabling also cancels waiting work.
 if !enabled{let players=m0(PLAYERS,s(b"allObjects\0" as *const u8));let n=count(players,s(b"count\0" as *const u8));let mut i=0;while i<n{set(assoc(mu(players,s(b"objectAtIndex:\0" as *const u8),i),&raw const STATE_KEY),b"autoRewind\0" as *const u8,number(0));i=i+1;}}
}}
unsafe extern "C" fn toggle_auto(_:Id,_:Sel,sender:Id){unsafe{save_auto(b0(sender,s(b"isOn\0" as *const u8)));}}
unsafe fn settings_label(text:*const u8)->Id{unsafe{
 let label=m0(cls(b"UILabel\0" as *const u8),s(b"new\0" as *const u8));m1(label,s(b"setText:\0" as *const u8),str(text));mu(label,s(b"setNumberOfLines:\0" as *const u8),0);m1(label,s(b"setTextColor:\0" as *const u8),m0(cls(b"UIColor\0" as *const u8),s(b"labelColor\0" as *const u8)));return label;
}}
unsafe extern "C" fn settings_done(o:Id,_:Sel,_:Id){unsafe{dismiss(o,s(b"dismissViewControllerAnimated:completion:\0" as *const u8),true,0 as Id);}}
unsafe extern "C" fn settings_load(o:Id,_:Sel){unsafe{
 let scroll=m0(cls(b"UIScrollView\0" as *const u8),s(b"new\0" as *const u8));m1(o,s(b"setView:\0" as *const u8),scroll);m1(scroll,s(b"setBackgroundColor:\0" as *const u8),m0(cls(b"UIColor\0" as *const u8),s(b"systemBackgroundColor\0" as *const u8)));
 let stack=m0(cls(b"UIStackView\0" as *const u8),s(b"new\0" as *const u8));mu(stack,s(b"setAxis:\0" as *const u8),1);md(stack,s(b"setSpacing:\0" as *const u8),20.0);mb(stack,s(b"setTranslatesAutoresizingMaskIntoConstraints:\0" as *const u8),false);m1(scroll,s(b"addSubview:\0" as *const u8),stack);
 let content=m0(scroll,s(b"contentLayoutGuide\0" as *const u8));let frame=m0(scroll,s(b"safeAreaLayoutGuide\0" as *const u8));pin(stack,b"leadingAnchor\0" as *const u8,content,b"leadingAnchor\0" as *const u8,20.0);pin(stack,b"trailingAnchor\0" as *const u8,content,b"trailingAnchor\0" as *const u8,0.0-20.0);pin(stack,b"widthAnchor\0" as *const u8,frame,b"widthAnchor\0" as *const u8,0.0-40.0);pin(stack,b"topAnchor\0" as *const u8,content,b"topAnchor\0" as *const u8,32.0);pin(stack,b"bottomAnchor\0" as *const u8,content,b"bottomAnchor\0" as *const u8,0.0-24.0);
 let heading=settings_label(b"Rewind Settings\0" as *const u8);m1(stack,s(b"addArrangedSubview:\0" as *const u8),heading);release(heading);
 let row=m0(cls(b"UIStackView\0" as *const u8),s(b"new\0" as *const u8));mu(row,s(b"setAxis:\0" as *const u8),0);mu(row,s(b"setAlignment:\0" as *const u8),3);md(row,s(b"setSpacing:\0" as *const u8),12.0);let label=settings_label(b"Automatic rewind (experimental)\0" as *const u8);m1(row,s(b"addArrangedSubview:\0" as *const u8),label);release(label);
 let toggle=m0(cls(b"UISwitch\0" as *const u8),s(b"new\0" as *const u8));mb(toggle,s(b"setOn:\0" as *const u8),auto_enabled());m1(toggle,s(b"setAccessibilityLabel:\0" as *const u8),str(b"Automatic rewind\0" as *const u8));action(toggle,s(b"addTarget:action:forControlEvents:\0" as *const u8),TARGET,s(b"toggleAuto:\0" as *const u8),4096);m1(row,s(b"addArrangedSubview:\0" as *const u8),toggle);m1(stack,s(b"addArrangedSubview:\0" as *const u8),row);release(toggle);release(row);
 let explanation=settings_label(b"Start one second before the available recording ends. This may avoid some live ads, but is not guaranteed and may add more delay. An accessible ongoing recording is required.\n\nOff by default. Changes apply when you next open a stream. Turning this off cancels any waiting automatic switch. Tap LIVE to leave an existing replay. Manual rewind always remains available.\0" as *const u8);m1(stack,s(b"addArrangedSubview:\0" as *const u8),explanation);release(explanation);
 let done=mu(cls(b"UIButton\0" as *const u8),s(b"buttonWithType:\0" as *const u8),1);title(done,s(b"setTitle:forState:\0" as *const u8),str(b"Done\0" as *const u8),0);action(done,s(b"addTarget:action:forControlEvents:\0" as *const u8),o,s(b"done:\0" as *const u8),64);mb(md(m0(done,s(b"heightAnchor\0" as *const u8)),s(b"constraintEqualToConstant:\0" as *const u8),44.0),s(b"setActive:\0" as *const u8),true);m1(stack,s(b"addArrangedSubview:\0" as *const u8),done);release(stack);release(scroll);
}}
unsafe extern "C" fn open_settings(_:Id,_:Sel,sender:Id){unsafe{
 let mut responder=sender;let mut depth=0;while responder!=0 as Id&&depth<32{if kind(responder,b"UIViewController\0" as *const u8){break;}responder=m0(responder,s(b"nextResponder\0" as *const u8));depth=depth+1;}
 if responder==0 as Id||!kind(responder,b"UIViewController\0" as *const u8){return;}
 // Never stack a second modal on top of an existing sheet.
 if m0(responder,s(b"presentedViewController\0" as *const u8))!=0 as Id{return;}
 let vc=m0(cls(b"TwitchPlusRewindSettings\0" as *const u8),s(b"new\0" as *const u8));if vc==0 as Id{return;}present(responder,s(b"presentViewController:animated:completion:\0" as *const u8),vc,true,0 as Id);release(vc);
}}
unsafe fn configure_tabs(o:Id){unsafe{
 if responds(o,s(b"setMode:\0" as *const u8))&&responds(o,s(b"mode\0" as *const u8))&&count(o,s(b"mode\0" as *const u8))!=1{mu(o,s(b"setMode:\0" as *const u8),1);}
}}
unsafe extern "C" fn tabs_loaded(o:Id,sel:Sel){unsafe{transmute::<Id,Zero>(OLD_TAB_LOAD)(o,sel);configure_tabs(o);}}
unsafe fn s(v:*const u8)->Sel{unsafe{sel_registerName(v)}}
unsafe fn cls(v:*const u8)->Id{unsafe{objc_getClass(v)}}
unsafe fn str(v:*const u8)->Id{unsafe{m1(cls(b"NSString\0" as *const u8),s(b"stringWithUTF8String:\0" as *const u8),v as Id)}}
unsafe fn retain(o:Id)->Id{unsafe{m0(o,s(b"retain\0" as *const u8))}}
unsafe fn release(o:Id){unsafe{m0(o,s(b"release\0" as *const u8));}}
unsafe fn assoc(o:Id,k:*const u8)->Id{unsafe{objc_getAssociatedObject(o,k as Id)}}
unsafe fn put(o:Id,k:*const u8,v:Id){unsafe{objc_setAssociatedObject(o,k as Id,v,1);}}
unsafe fn kind(o:Id,n:*const u8)->bool{unsafe{o!=0 as Id&&b1(o,s(b"isKindOfClass:\0" as *const u8),cls(n))}}
unsafe fn get(o:Id,k:*const u8)->Id{unsafe{if kind(o,b"NSDictionary\0" as *const u8){m1(o,s(b"objectForKey:\0" as *const u8),str(k))}else{0 as Id}}}
unsafe fn set(o:Id,k:*const u8,v:Id){unsafe{if v!=0 as Id{m2(o,s(b"setObject:forKey:\0" as *const u8),v,str(k));}else{m1(o,s(b"removeObjectForKey:\0" as *const u8),str(k));}}}
unsafe fn dict()->Id{unsafe{m0(cls(b"NSMutableDictionary\0" as *const u8),s(b"dictionary\0" as *const u8))}}
unsafe fn number(v:usize)->Id{unsafe{mu(cls(b"NSNumber\0" as *const u8),s(b"numberWithUnsignedInteger:\0" as *const u8),v)}}
unsafe fn real(v:f64)->Id{unsafe{md(cls(b"NSNumber\0" as *const u8),s(b"numberWithDouble:\0" as *const u8),v)}}
unsafe fn value(o:Id,k:*const u8)->usize{unsafe{count(get(o,k),s(b"unsignedIntegerValue\0" as *const u8))}}
unsafe fn eq(a:Id,b:Id)->bool{unsafe{kind(a,b"NSString\0" as *const u8)&&kind(b,b"NSString\0" as *const u8)&&b1(a,s(b"isEqualToString:\0" as *const u8),b)}}
unsafe fn hook(c:Id,sel:Sel,imp:Id)->Id{unsafe{let m=class_getInstanceMethod(c,sel);if m==0 as Id{return 0 as Id;}let old=method_getImplementation(m);if !class_addMethod(c,sel,imp,method_getTypeEncoding(m)){method_setImplementation(m,imp);}old}}
unsafe fn field(o:Id,n:*const u8)->Id{unsafe{if o==0 as Id{return 0 as Id;}let iv=class_getInstanceVariable(object_getClass(o),n);if iv==0 as Id{return 0 as Id;}*((o as usize+ivar_getOffset(iv)) as *const Id)}}
unsafe fn weak(o:Id)->Id{unsafe{let t=m0(cls(b"NSHashTable\0" as *const u8),s(b"weakObjectsHashTable\0" as *const u8));m1(t,s(b"addObject:\0" as *const u8),o);t}}
unsafe fn weak_get(t:Id)->Id{unsafe{m0(t,s(b"anyObject\0" as *const u8))}}
unsafe fn url(text:Id)->Id{unsafe{m1(cls(b"NSURL\0" as *const u8),s(b"URLWithString:\0" as *const u8),text)}}
unsafe fn text_valid(o:Id)->bool{unsafe{kind(o,b"NSString\0" as *const u8)&&count(o,s(b"length\0" as *const u8))!=0}}
// Only exact usher live-channel URLs identify a channel. VODs and arbitrary URLs
// never gain rewind controls. No account follow or playback entitlement is changed.
unsafe fn login_from_url(u:Id)->Id{unsafe{
 if !kind(u,b"NSURL\0" as *const u8){return 0 as Id;}
 if !eq(m0(u,s(b"host\0" as *const u8)),str(b"usher.ttvnw.net\0" as *const u8)){return 0 as Id;}
 let path=m0(u,s(b"path\0" as *const u8));if !b1(path,s(b"hasPrefix:\0" as *const u8),str(b"/api/channel/hls/\0" as *const u8))||!eq(m0(path,s(b"pathExtension\0" as *const u8)),str(b"m3u8\0" as *const u8)){return 0 as Id;}
 let login=m0(m0(path,s(b"lastPathComponent\0" as *const u8)),s(b"stringByDeletingPathExtension\0" as *const u8));let len=count(login,s(b"length\0" as *const u8));if len==0||len>25{return 0 as Id;}
 let chars=m1(cls(b"NSCharacterSet\0" as *const u8),s(b"characterSetWithCharactersInString:\0" as *const u8),str(b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_\0" as *const u8));let clean=count(m1(login,s(b"stringByTrimmingCharactersInSet:\0" as *const u8),chars),s(b"length\0" as *const u8));if clean!=0{return 0 as Id;}login
}}
unsafe extern "C" fn load(o:Id,sel:Sel,u:Id,configuration:Id){unsafe{
 if assoc(o,&raw const INTERNAL_KEY)==0 as Id{
  let login=login_from_url(u);let state=dict();let old=assoc(o,&raw const STATE_KEY);let generation=value(old,b"generation\0" as *const u8)+1;
  set(state,b"generation\0" as *const u8,number(generation));set(state,b"login\0" as *const u8,login);set(state,b"liveURL\0" as *const u8,u);set(state,b"configuration\0" as *const u8,configuration);put(o,&raw const STATE_KEY,state);if text_valid(login){set(state,b"autoRewind\0" as *const u8,number(if auto_enabled(){1}else{0}));m1(PLAYERS,s(b"addObject:\0" as *const u8),o);}schedule_prepare(o);
 }
 transmute::<Id,Load>(OLD_LOAD)(o,sel,u,configuration);
}}
unsafe extern "C" fn load_source(o:Id,sel:Sel,source:Id,configuration:Id){unsafe{
 if assoc(o,&raw const INTERNAL_KEY)==0 as Id{
  let mut u=m0(source,s(b"path\0" as *const u8));if kind(u,b"NSString\0" as *const u8){u=url(u);}
  let login=login_from_url(u);let state=dict();let old=assoc(o,&raw const STATE_KEY);
  set(state,b"generation\0" as *const u8,number(value(old,b"generation\0" as *const u8)+1));set(state,b"login\0" as *const u8,login);set(state,b"liveURL\0" as *const u8,u);set(state,b"liveSource\0" as *const u8,source);set(state,b"configuration\0" as *const u8,configuration);put(o,&raw const STATE_KEY,state);if text_valid(login){set(state,b"autoRewind\0" as *const u8,number(if auto_enabled(){1}else{0}));m1(PLAYERS,s(b"addObject:\0" as *const u8),o);}schedule_prepare(o);
 }
 transmute::<Id,Load>(OLD_SOURCE)(o,sel,source,configuration);
}}
unsafe fn switch_url(player:Id,u:Id,state:Id){unsafe{
 put(player,&raw const INTERNAL_KEY,number(1));transmute::<Id,Load>(OLD_LOAD)(player,s(b"load:configuration:\0" as *const u8),u,get(state,b"configuration\0" as *const u8));put(player,&raw const INTERNAL_KEY,0 as Id);if value(state,b"mode\0" as *const u8)!=2{m0(player,s(b"play\0" as *const u8));}
}}
unsafe fn go_live(player:Id){unsafe{
 let state=assoc(player,&raw const STATE_KEY);let u=get(state,b"liveURL\0" as *const u8);if u==0 as Id{return;}
 // Explicit LIVE and replay failure cancel the automatic switch for this load.
 set(state,b"autoRewind\0" as *const u8,number(0));
 set(state,b"generation\0" as *const u8,number(value(state,b"generation\0" as *const u8)+1));set(state,b"mode\0" as *const u8,number(0));set(state,b"pending\0" as *const u8,0 as Id);set(state,b"notice\0" as *const u8,0 as Id);set(state,b"cacheBusy\0" as *const u8,number(0));let source=get(state,b"liveSource\0" as *const u8);if source!=0 as Id{put(player,&raw const INTERNAL_KEY,number(1));transmute::<Id,Load>(OLD_SOURCE)(player,s(b"loadSource:configuration:\0" as *const u8),source,get(state,b"configuration\0" as *const u8));put(player,&raw const INTERNAL_KEY,0 as Id);m0(player,s(b"play\0" as *const u8));}else{switch_url(player,u,state);}
}}
unsafe fn request(query:*const u8,variables:Id)->Id{unsafe{
 let payload=dict();set(payload,b"query\0" as *const u8,str(query));set(payload,b"variables\0" as *const u8,variables);
 let req=m1(cls(b"NSMutableURLRequest\0" as *const u8),s(b"requestWithURL:\0" as *const u8),url(str(b"https://gql.twitch.tv/gql\0" as *const u8)));
 m1(req,s(b"setHTTPMethod:\0" as *const u8),str(b"POST\0" as *const u8));md(req,s(b"setTimeoutInterval:\0" as *const u8),6.0);mb(req,s(b"setHTTPShouldHandleCookies:\0" as *const u8),false);
 m2(req,s(b"setValue:forHTTPHeaderField:\0" as *const u8),str(b"application/json\0" as *const u8),str(b"Content-Type\0" as *const u8));m2(req,s(b"setValue:forHTTPHeaderField:\0" as *const u8),str(b"kimne78kx3ncx6brgo4mv6wki5h1ko\0" as *const u8),str(b"Client-ID\0" as *const u8));
 let data=m3(cls(b"NSJSONSerialization\0" as *const u8),s(b"dataWithJSONObject:options:error:\0" as *const u8),payload,0 as Id,0 as Id);m1(req,s(b"setHTTPBody:\0" as *const u8),data);
 let mut response=0 as Id;let mut error=0 as Id;let bytes=m3(cls(b"NSURLConnection\0" as *const u8),s(b"sendSynchronousRequest:returningResponse:error:\0" as *const u8),req,&raw mut response as Id,&raw mut error as Id);
 let code=count(response,s(b"statusCode\0" as *const u8));if bytes==0 as Id||error!=0 as Id||code<200||code>=300{return 0 as Id;}
 let parsed=m3(cls(b"NSJSONSerialization\0" as *const u8),s(b"JSONObjectWithData:options:error:\0" as *const u8),bytes,0 as Id,0 as Id);get(parsed,b"data\0" as *const u8)
}}
unsafe fn query_item(items:Id,name:*const u8,v:Id){unsafe{let item=m2(cls(b"NSURLQueryItem\0" as *const u8),s(b"queryItemWithName:value:\0" as *const u8),str(name),v);m1(items,s(b"addObject:\0" as *const u8),item);}}
unsafe extern "C" fn fetch_recording(job:Id){unsafe{
 let pool=m0(cls(b"NSAutoreleasePool\0" as *const u8),s(b"new\0" as *const u8));
 let vars=dict();set(vars,b"login\0" as *const u8,get(job,b"login\0" as *const u8));
 let data=request(b"query RewindArchive($login:String!){user(login:$login){login stream{id} videos(first:1,sort:TIME,type:ARCHIVE){edges{node{id status lengthSeconds}}}}}\0" as *const u8,vars);
 if data==0 as Id{set(job,b"networkFailed\0" as *const u8,number(1));}
 let user=get(data,b"user\0" as *const u8);let edges=get(get(user,b"videos\0" as *const u8),b"edges\0" as *const u8);let mut node=0 as Id;
 if kind(edges,b"NSArray\0" as *const u8)&&count(edges,s(b"count\0" as *const u8))!=0{node=get(mu(edges,s(b"objectAtIndex:\0" as *const u8),0),b"node\0" as *const u8);}
 let id=get(node,b"id\0" as *const u8);let duration=get(node,b"lengthSeconds\0" as *const u8);
 if text_valid(id)&&eq(get(node,b"status\0" as *const u8),str(b"RECORDING\0" as *const u8))&&kind(get(user,b"stream\0" as *const u8),b"NSDictionary\0" as *const u8)&&kind(duration,b"NSNumber\0" as *const u8)&&double(duration,s(b"doubleValue\0" as *const u8))>2.0{
  let vars=dict();set(vars,b"id\0" as *const u8,id);let data=request(b"query RewindToken($id:ID!){videoPlaybackAccessToken(id:$id,params:{platform:\"ios\",playerBackend:\"mediaplayer\",playerType:\"site\"}){signature value}}\0" as *const u8,vars);if data==0 as Id{set(job,b"networkFailed\0" as *const u8,number(1));}let token=get(data,b"videoPlaybackAccessToken\0" as *const u8);let signature=get(token,b"signature\0" as *const u8);let access=get(token,b"value\0" as *const u8);
  if text_valid(signature)&&text_valid(access){
   let c=m0(cls(b"NSURLComponents\0" as *const u8),s(b"new\0" as *const u8));m1(c,s(b"setScheme:\0" as *const u8),str(b"https\0" as *const u8));m1(c,s(b"setHost:\0" as *const u8),str(b"usher.ttvnw.net\0" as *const u8));let path=m1(m1(str(b"/vod/\0" as *const u8),s(b"stringByAppendingString:\0" as *const u8),id),s(b"stringByAppendingString:\0" as *const u8),str(b".m3u8\0" as *const u8));m1(c,s(b"setPath:\0" as *const u8),path);
   let items=m0(cls(b"NSMutableArray\0" as *const u8),s(b"array\0" as *const u8));query_item(items,b"nauth\0" as *const u8,access);query_item(items,b"nauthsig\0" as *const u8,signature);query_item(items,b"allow_source\0" as *const u8,str(b"true\0" as *const u8));query_item(items,b"allow_audio_only\0" as *const u8,str(b"true\0" as *const u8));m1(c,s(b"setQueryItems:\0" as *const u8),items);set(job,b"resultURL\0" as *const u8,m0(c,s(b"URL\0" as *const u8)));set(job,b"duration\0" as *const u8,duration);release(c);
  }
 }
 dispatch_async_f(MAIN,job,apply_recording);m0(pool,s(b"drain\0" as *const u8));
}}
unsafe extern "C" fn prepare_on_main(weak_player:Id){unsafe{let player=weak_get(weak_player);if player!=0 as Id{prefetch(player);}release(weak_player);}}
unsafe fn schedule_prepare(player:Id){unsafe{if MAIN!=0 as Id{dispatch_async_f(MAIN,retain(weak(player)),prepare_on_main);}}}
// Keep the previous ready source until its replacement really is ready.
unsafe fn promote_prepared(state:Id){unsafe{
 let warming=get(state,b"warmingPlayer\0" as *const u8);if warming==0 as Id{return;}
 if count(warming,s(b"state\0" as *const u8))>=1&&m0(warming,s(b"error\0" as *const u8))==0 as Id&&m0(warming,s(b"source\0" as *const u8))!=0 as Id{
  set(state,b"preparedPlayer\0" as *const u8,warming);set(state,b"preparedAt\0" as *const u8,get(state,b"warmingAt\0" as *const u8));set(state,b"preparedDuration\0" as *const u8,get(state,b"warmingDuration\0" as *const u8));set(state,b"warmingPlayer\0" as *const u8,0 as Id);
 }
}}
unsafe fn prepared_source(state:Id,target:f64)->Id{unsafe{
 promote_prepared(state);let ready=get(state,b"preparedPlayer\0" as *const u8);let prepared_at=get(state,b"preparedAt\0" as *const u8);let duration=double(get(state,b"preparedDuration\0" as *const u8),s(b"doubleValue\0" as *const u8));
 if ready==0 as Id||prepared_at==0 as Id||CFAbsoluteTimeGetCurrent()>double(prepared_at,s(b"doubleValue\0" as *const u8))+90.0||target>duration-2.0||count(ready,s(b"state\0" as *const u8))<1||m0(ready,s(b"error\0" as *const u8))!=0 as Id{return 0 as Id;}
 m0(ready,s(b"source\0" as *const u8))
}}
unsafe fn queue_seek(player:Id,target:f64,delay:f64){unsafe{
 let state=assoc(player,&raw const STATE_KEY);set(state,b"pending\0" as *const u8,real(if target>0.0{target}else{0.0}));set(state,b"seekDueAt\0" as *const u8,real(CFAbsoluteTimeGetCurrent()+delay));set(state,b"attempts\0" as *const u8,number(0));
}}
// Prepare recording access and master playlists while the live player keeps playing.
unsafe fn prefetch(player:Id){unsafe{
 let state=assoc(player,&raw const STATE_KEY);if !text_valid(get(state,b"login\0" as *const u8))||value(state,b"cacheBusy\0" as *const u8)!=0{return;}
 let interval=if get(state,b"cachedURL\0" as *const u8)==0 as Id&&value(state,b"prepareFailed\0" as *const u8)!=0{5.0}else{30.0};let last=get(state,b"cacheRequestAt\0" as *const u8);if last!=0 as Id&&CFAbsoluteTimeGetCurrent()<double(last,s(b"doubleValue\0" as *const u8))+interval{return;}
 set(state,b"cacheBusy\0" as *const u8,number(1));set(state,b"cacheRequestAt\0" as *const u8,real(CFAbsoluteTimeGetCurrent()));
 let job=dict();set(job,b"login\0" as *const u8,get(state,b"login\0" as *const u8));set(job,b"player\0" as *const u8,weak(player));set(job,b"generation\0" as *const u8,get(state,b"generation\0" as *const u8));dispatch_async_f(dispatch_get_global_queue(0,0),retain(job),fetch_recording);
}}
unsafe extern "C" fn apply_recording(job:Id){unsafe{
 let player=weak_get(get(job,b"player\0" as *const u8));let state=assoc(player,&raw const STATE_KEY);
 if player!=0 as Id&&value(state,b"generation\0" as *const u8)==value(job,b"generation\0" as *const u8)&&eq(get(state,b"login\0" as *const u8),get(job,b"login\0" as *const u8)){
  set(state,b"cacheBusy\0" as *const u8,number(0));set(state,b"prepareFailed\0" as *const u8,get(job,b"networkFailed\0" as *const u8));if value(state,b"prepareFailed\0" as *const u8)!=0{set(state,b"cacheRequestAt\0" as *const u8,real(CFAbsoluteTimeGetCurrent()));}let u=get(job,b"resultURL\0" as *const u8);
  if u!=0 as Id{
   set(state,b"cachedURL\0" as *const u8,u);set(state,b"cachedDuration\0" as *const u8,get(job,b"duration\0" as *const u8));set(state,b"cacheAt\0" as *const u8,real(CFAbsoluteTimeGetCurrent()));set(state,b"notice\0" as *const u8,0 as Id);
   // A paused, unattached IVS player resolves manifests without playing video.
   let prepared=m0(cls(b"IVSPlayer\0" as *const u8),s(b"new\0" as *const u8));if prepared!=0 as Id{put(prepared,&raw const INTERNAL_KEY,number(1));transmute::<Id,Load>(OLD_LOAD)(prepared,s(b"load:configuration:\0" as *const u8),u,get(state,b"configuration\0" as *const u8));put(prepared,&raw const INTERNAL_KEY,0 as Id);set(state,b"warmingPlayer\0" as *const u8,prepared);set(state,b"warmingAt\0" as *const u8,real(CFAbsoluteTimeGetCurrent()));set(state,b"warmingDuration\0" as *const u8,get(job,b"duration\0" as *const u8));release(prepared);}
  }else{if get(state,b"cachedURL\0" as *const u8)==0 as Id{set(state,b"notice\0" as *const u8,str(b"N/A\0" as *const u8));}}
 }
 release(job);
}}
unsafe fn sender_player(sender:Id)->Id{unsafe{{let direct=weak_get(assoc(sender,&raw const PLAYER_KEY));if direct!=0 as Id{direct}else{weak_get(assoc(m0(sender,s(b"superview\0" as *const u8)),&raw const PLAYER_KEY))}}}}
unsafe fn seek_position(player:Id,target:f64){unsafe{let duration=CMTimeGetSeconds(time(player,s(b"duration\0" as *const u8)));if duration>2.0&&duration<604800.0{let t=if target<0.0{0.0}else{if target>duration-1.0{duration-1.0}else{target}};seek(player,s(b"seekTo:\0" as *const u8),CMTimeMakeWithSeconds(t,600));}}}
unsafe fn start_replay(player:Id,target:f64){unsafe{
 let state=assoc(player,&raw const STATE_KEY);let u=get(state,b"cachedURL\0" as *const u8);if u==0 as Id{prefetch(player);return;}
 set(state,b"autoRewind\0" as *const u8,number(0));set(state,b"mode\0" as *const u8,number(2));queue_seek(player,target,0.0);set(state,b"switchStartedAt\0" as *const u8,real(CFAbsoluteTimeGetCurrent()));set(state,b"notice\0" as *const u8,0 as Id);
 m0(player,s(b"pause\0" as *const u8));let source=prepared_source(state,target);
 if source!=0 as Id{put(player,&raw const INTERNAL_KEY,number(1));transmute::<Id,Load>(OLD_SOURCE)(player,s(b"loadSource:configuration:\0" as *const u8),source,get(state,b"configuration\0" as *const u8));put(player,&raw const INTERNAL_KEY,0 as Id);}else{switch_url(player,u,state);}
 // A single Ready-state seek starts replay. Do not seek here as well:
 // that second request can cancel the first seek and restart buffering.

}}
unsafe fn timeline_end(player:Id)->f64{unsafe{let state=assoc(player,&raw const STATE_KEY);if value(state,b"mode\0" as *const u8)==2{let d=CMTimeGetSeconds(time(player,s(b"duration\0" as *const u8)));if d>2.0&&d<604800.0{return d;}}double(get(state,b"cachedDuration\0" as *const u8),s(b"doubleValue\0" as *const u8))}}
unsafe extern "C" fn scrub(_:Id,_:Sel,sender:Id){unsafe{
 let player=sender_player(sender);let state=assoc(player,&raw const STATE_KEY);let fraction=float(sender,s(b"value\0" as *const u8)) as f64;let end=timeline_end(player);if !(fraction>=0.0&&fraction<=1.0&&end>2.0){return;}
 let target=fraction*end;if target>=end-2.0{if value(state,b"mode\0" as *const u8)!=0{go_live(player);}return;}
 if value(state,b"mode\0" as *const u8)==2{if get(state,b"pending\0" as *const u8)!=0 as Id{queue_seek(player,target,0.0);}else{queue_seek(player,target,0.0);}}else{start_replay(player,target);}
}}
unsafe extern "C" fn rewind(_:Id,_:Sel,sender:Id){unsafe{let player=sender_player(sender);let state=assoc(player,&raw const STATE_KEY);if value(state,b"mode\0" as *const u8)==2{let pending=get(state,b"pending\0" as *const u8);if pending!=0 as Id{let t=double(pending,s(b"doubleValue\0" as *const u8))-10.0;queue_seek(player,if t>0.0{t}else{0.0},0.12);}else{queue_seek(player,CMTimeGetSeconds(time(player,s(b"position\0" as *const u8)))-10.0,0.12);}}else{let end=timeline_end(player);if end>2.0{start_replay(player,if end>10.0{end-10.0}else{0.0});}else{prefetch(player);}}}}
unsafe extern "C" fn forward(_:Id,_:Sel,sender:Id){unsafe{let player=sender_player(sender);let state=assoc(player,&raw const STATE_KEY);if value(state,b"mode\0" as *const u8)!=2{return;}let pending=get(state,b"pending\0" as *const u8);let target=if pending!=0 as Id{double(pending,s(b"doubleValue\0" as *const u8))+10.0}else{CMTimeGetSeconds(time(player,s(b"position\0" as *const u8)))+10.0};if target>=timeline_end(player)-2.0{go_live(player);}else{if pending!=0 as Id{queue_seek(player,target,0.12);}else{queue_seek(player,target,0.12);}}}}
unsafe extern "C" fn live(_:Id,_:Sel,sender:Id){unsafe{let player=sender_player(sender);if value(assoc(player,&raw const STATE_KEY),b"mode\0" as *const u8)!=0{go_live(player);}}}
unsafe fn find_player(view:Id,depth:usize)->Id{unsafe{
 if view==0 as Id||depth>10{return 0 as Id;}if kind(view,b"IVSPlayerView\0" as *const u8){let player=m0(view,s(b"player\0" as *const u8));if text_valid(get(assoc(player,&raw const STATE_KEY),b"login\0" as *const u8)){return player;}}
 let children=m0(view,s(b"subviews\0" as *const u8));let n=count(children,s(b"count\0" as *const u8));let mut i=0;let mut found=0 as Id;
 while i<n{let p=find_player(mu(children,s(b"objectAtIndex:\0" as *const u8),i),depth+1);if p==1 as Id{return p;}if p!=0 as Id{if found!=0 as Id&&found!=p{return 1 as Id;}found=p;}i=i+1;}found
}}
unsafe fn button(label:*const u8,selector:*const u8)->Id{unsafe{
 let b=mu(cls(b"UIButton\0" as *const u8),s(b"buttonWithType:\0" as *const u8),1);title(b,s(b"setTitle:forState:\0" as *const u8),str(label),0);title(b,s(b"setTitleColor:forState:\0" as *const u8),m0(cls(b"UIColor\0" as *const u8),s(b"whiteColor\0" as *const u8)),0);action(b,s(b"addTarget:action:forControlEvents:\0" as *const u8),TARGET,s(selector),64);m1(b,s(b"setAccessibilityLabel:\0" as *const u8),str(label));let height=md(m0(b,s(b"heightAnchor\0" as *const u8)),s(b"constraintEqualToConstant:\0" as *const u8),44.0);mb(height,s(b"setActive:\0" as *const u8),true);let width=md(m0(b,s(b"widthAnchor\0" as *const u8)),s(b"constraintEqualToConstant:\0" as *const u8),44.0);mb(width,s(b"setActive:\0" as *const u8),true);return b;
}}
unsafe fn pin(row:Id,from:*const u8,view:Id,to:*const u8,offset:f64)->Id{unsafe{let constraint=anchor(m0(row,s(from)),s(b"constraintEqualToAnchor:constant:\0" as *const u8),m0(view,s(to)),offset);mb(constraint,s(b"setActive:\0" as *const u8),true);constraint}}
unsafe fn tracked_pin(owner:Id,key:*const u8,view:Id,from:*const u8,other:Id,to:*const u8,offset:f64){unsafe{let constraint=pin(view,from,other,to,offset);put(owner,key,weak(constraint));}}
unsafe fn update_pin(owner:Id,key:*const u8,offset:f64){unsafe{let constraint=weak_get(assoc(owner,key));if constraint!=0 as Id&&double(constraint,s(b"constant\0" as *const u8))!=offset{md(constraint,s(b"setConstant:\0" as *const u8),offset);}}}
unsafe fn layout_visible(row:Id)->bool{unsafe{let stored=assoc(row,&raw const GEOMETRY_VISIBLE_KEY);stored==0 as Id||count(stored,s(b"unsignedIntegerValue\0" as *const u8))!=0}}
fn valid_rect(r:Rect)->bool{
 r.origin.x>0.0-10000.0&&r.origin.x<10000.0&&r.origin.y>0.0-10000.0&&r.origin.y<10000.0&&r.size.width>0.0&&r.size.width<10000.0&&r.size.height>0.0&&r.size.height<10000.0
}
fn overlaps(a:Rect,b:Rect)->bool{
 valid_rect(a)&&valid_rect(b)&&a.origin.x<b.origin.x+b.size.width+8.0&&b.origin.x<a.origin.x+a.size.width+8.0&&a.origin.y<b.origin.y+b.size.height+8.0&&b.origin.y<a.origin.y+a.size.height+8.0
}
unsafe fn responds(o:Id,selector:Sel)->bool{unsafe{o!=0 as Id&&b1(o,s(b"respondsToSelector:\0" as *const u8),selector)}}
unsafe fn native_view(controls:Id,name:*const u8)->Id{unsafe{let sel=s(name);if responds(controls,sel){m0(controls,sel)}else{0 as Id}}}
unsafe fn view_visible(view:Id,controls:Id)->bool{unsafe{
 let mut v=view;let mut depth=0;while v!=0 as Id&&v!=controls&&depth<20{
  if b0(v,s(b"isHidden\0" as *const u8))||double(v,s(b"alpha\0" as *const u8))<0.01{return false;}
  v=m0(v,s(b"superview\0" as *const u8));depth=depth+1;
 }v==controls
}}
unsafe fn view_frame(view:Id,controls:Id)->Rect{unsafe{convert_rect(view,s(b"convertRect:toView:\0" as *const u8),rect(view,s(b"bounds\0" as *const u8)),controls)}}
unsafe fn collides_native(controls:Id,target:Rect)->bool{unsafe{
 let left=native_view(controls,b"topLeftStackView\0" as *const u8);let right=native_view(controls,b"topRightStackView\0" as *const u8);
 if left!=0 as Id&&view_visible(left,controls)&&overlaps(target,view_frame(left,controls)){return true;}
 if right!=0 as Id&&view_visible(right,controls)&&overlaps(target,view_frame(right,controls)){return true;}
 let buttons=native_view(controls,b"allButtons\0" as *const u8);if !kind(buttons,b"NSArray\0" as *const u8){return false;}let n=count(buttons,s(b"count\0" as *const u8));let mut i=0;
 while i<n{let button=mu(buttons,s(b"objectAtIndex:\0" as *const u8),i);if view_visible(button,controls)&&overlaps(target,view_frame(button,controls)){return true;}i=i+1;}false
}}
unsafe fn adapt(controls:Id,row:Id){unsafe{
 let guide=m0(controls,s(b"safeAreaLayoutGuide\0" as *const u8));let frame=rect(guide,s(b"layoutFrame\0" as *const u8));let spec=responsive(frame.size.width,frame.size.height);
 let mut bottom=spec.bottom;
 // Native mute/fullscreen/chat actions may occupy more than the old fixed 48pt.
 let native=native_view(controls,b"bottomRightStackView\0" as *const u8);
 if native!=0 as Id&&view_visible(native,controls){let r=view_frame(native,controls);if valid_rect(r)&&r.origin.y>=frame.origin.y+frame.size.height*0.5&&r.origin.y<frame.origin.y+frame.size.height{let required=frame.origin.y+frame.size.height-r.origin.y+8.0;if required>bottom{bottom=required;}}}
 let timeline=Rect{origin:Point{x:frame.origin.x+spec.padding,y:frame.origin.y+frame.size.height-bottom-44.0},size:Size{width:frame.size.width-spec.padding*2.0,height:44.0}};
 let rtl=responds(controls,s(b"effectiveUserInterfaceLayoutDirection\0" as *const u8))&&count(controls,s(b"effectiveUserInterfaceLayoutDirection\0" as *const u8))==1;
 let live=Rect{origin:Point{x:if rtl{timeline.origin.x}else{frame.origin.x+frame.size.width-spec.padding-68.0},y:timeline.origin.y-48.0},size:Size{width:68.0,height:44.0}};
 let label=Rect{origin:Point{x:if rtl{timeline.origin.x+timeline.size.width-72.0}else{timeline.origin.x},y:timeline.origin.y-22.0},size:Size{width:72.0,height:20.0}};
 let back=Rect{origin:Point{x:frame.origin.x+frame.size.width*0.5-spec.skip-22.0,y:frame.origin.y+frame.size.height*0.5-22.0},size:Size{width:44.0,height:44.0}};
 let forward=Rect{origin:Point{x:frame.origin.x+frame.size.width*0.5+spec.skip-22.0,y:back.origin.y},size:Size{width:44.0,height:44.0}};
 let visible=valid_rect(frame)&&spec.visible&&live.origin.y>=frame.origin.y+8.0&&!collides_native(controls,timeline)&&!collides_native(controls,live)&&!collides_native(controls,label);
 let sides=visible&&spec.sides&&!overlaps(back,timeline)&&!overlaps(forward,timeline)&&!overlaps(back,label)&&!overlaps(forward,label)&&!overlaps(back,live)&&!overlaps(forward,live)&&!collides_native(controls,back)&&!collides_native(controls,forward);
 update_pin(row,&raw const PAD_LEFT_KEY,spec.padding);update_pin(row,&raw const PAD_RIGHT_KEY,0.0-spec.padding);update_pin(row,&raw const BOTTOM_KEY,0.0-bottom);update_pin(row,&raw const SKIP_LEFT_KEY,0.0-spec.skip);update_pin(row,&raw const SKIP_RIGHT_KEY,spec.skip);
 put(row,&raw const GEOMETRY_VISIBLE_KEY,number(if visible{1}else{0}));mb(row,s(b"setHidden:\0" as *const u8),!visible);mb(assoc(row,&raw const LIVE_KEY),s(b"setHidden:\0" as *const u8),!visible);mb(assoc(row,&raw const BACK_KEY),s(b"setHidden:\0" as *const u8),!sides);mb(assoc(row,&raw const FORWARD_KEY),s(b"setHidden:\0" as *const u8),!sides);if !visible{mb(assoc(row,&raw const LABEL_KEY),s(b"setHidden:\0" as *const u8),true);}
}}
unsafe fn append(a:Id,b:Id)->Id{unsafe{m1(a,s(b"stringByAppendingString:\0" as *const u8),b)}}
unsafe fn digits(v:usize)->Id{unsafe{let n=m0(number(v),s(b"stringValue\0" as *const u8));if v<10{append(str(b"0\0" as *const u8),n)}else{n}}}
// Position since the beginning of the stream, never a negative live offset.
unsafe fn clock(position:f64)->Id{unsafe{let sec=if position>=0.0&&position<604800.0{position}else{0.0};let h=(sec/3600.0) as usize;let m=((sec-(h as f64)*3600.0)/60.0) as usize;let ss=(sec-(h as f64)*3600.0-(m as f64)*60.0) as usize;append(append(append(append(digits(h),str(b":\0" as *const u8)),digits(m)),str(b":\0" as *const u8)),digits(ss))}}
unsafe extern "C" fn preview(_:Id,_:Sel,sender:Id){unsafe{let row=m0(sender,s(b"superview\0" as *const u8));if !layout_visible(row){return;}let end=timeline_end(sender_player(sender));let fraction=float(sender,s(b"value\0" as *const u8)) as f64;if fraction>=0.0&&fraction<=1.0&&end>2.0{let text=clock(fraction*end);mb(assoc(row,&raw const LABEL_KEY),s(b"setHidden:\0" as *const u8),false);m1(assoc(row,&raw const LABEL_KEY),s(b"setText:\0" as *const u8),text);m1(sender,s(b"setAccessibilityValue:\0" as *const u8),text);}}}
unsafe fn icon_button(b:Id,name:*const u8){unsafe{let image=m1(cls(b"UIImage\0" as *const u8),s(b"systemImageNamed:\0" as *const u8),str(name));let conf=md(cls(b"UIImageSymbolConfiguration\0" as *const u8),s(b"configurationWithPointSize:\0" as *const u8),22.0);let image=m1(image,s(b"imageWithConfiguration:\0" as *const u8),conf);title(b,s(b"setImage:forState:\0" as *const u8),image,0);title(b,s(b"setTitle:forState:\0" as *const u8),str(b"\0" as *const u8),0);m1(b,s(b"setTintColor:\0" as *const u8),m0(cls(b"UIColor\0" as *const u8),s(b"whiteColor\0" as *const u8)));}}
unsafe fn attach(controls:Id){unsafe{
 let mut root=m0(controls,s(b"superview\0" as *const u8));let mut player=0 as Id;let mut i=0;
 while root!=0 as Id&&i<4&&player==0 as Id{player=find_player(root,0);root=m0(root,s(b"superview\0" as *const u8));i=i+1;}
 if player==1 as Id{player=0 as Id;}
 let mut row=assoc(controls,&raw const ROW_KEY);if player==0 as Id{if row!=0 as Id{put(row,&raw const GEOMETRY_VISIBLE_KEY,number(0));mb(row,s(b"setHidden:\0" as *const u8),true);mb(assoc(row,&raw const LABEL_KEY),s(b"setHidden:\0" as *const u8),true);mb(assoc(row,&raw const BACK_KEY),s(b"setHidden:\0" as *const u8),true);mb(assoc(row,&raw const FORWARD_KEY),s(b"setHidden:\0" as *const u8),true);mb(assoc(row,&raw const LIVE_KEY),s(b"setHidden:\0" as *const u8),true);put(row,&raw const PLAYER_KEY,0 as Id);}return;}
 if row==0 as Id{
  row=m0(cls(b"UIStackView\0" as *const u8),s(b"new\0" as *const u8));mu(row,s(b"setAxis:\0" as *const u8),0);md(row,s(b"setSpacing:\0" as *const u8),6.0);mu(row,s(b"setAlignment:\0" as *const u8),3);mb(row,s(b"setTranslatesAutoresizingMaskIntoConstraints:\0" as *const u8),false);
  let label=m0(cls(b"UILabel\0" as *const u8),s(b"new\0" as *const u8));m1(label,s(b"setText:\0" as *const u8),str(b"--:--:--\0" as *const u8));m1(label,s(b"setTextColor:\0" as *const u8),m0(cls(b"UIColor\0" as *const u8),s(b"whiteColor\0" as *const u8)));mb(md(m0(label,s(b"heightAnchor\0" as *const u8)),s(b"constraintEqualToConstant:\0" as *const u8),20.0),s(b"setActive:\0" as *const u8),true);let label_width=md(m0(label,s(b"widthAnchor\0" as *const u8)),s(b"constraintEqualToConstant:\0" as *const u8),72.0);mb(label_width,s(b"setActive:\0" as *const u8),true);m1(label,s(b"setFont:\0" as *const u8),font2(cls(b"UIFont\0" as *const u8),s(b"monospacedDigitSystemFontOfSize:weight:\0" as *const u8),12.0,0.0));
  let slider=m0(cls(b"UISlider\0" as *const u8),s(b"new\0" as *const u8));mb(slider,s(b"setContinuous:\0" as *const u8),true);mf(slider,s(b"setMinimumValue:\0" as *const u8),0.0);mf(slider,s(b"setMaximumValue:\0" as *const u8),1.0);mf(slider,s(b"setValue:\0" as *const u8),1.0);mb(slider,s(b"setEnabled:\0" as *const u8),false);action(slider,s(b"addTarget:action:forControlEvents:\0" as *const u8),TARGET,s(b"preview:\0" as *const u8),4096);action(slider,s(b"addTarget:action:forControlEvents:\0" as *const u8),TARGET,s(b"scrub:\0" as *const u8),192);m1(slider,s(b"setAccessibilityLabel:\0" as *const u8),str(b"Rewind timeline\0" as *const u8));
  let purple=rgba(cls(b"UIColor\0" as *const u8),s(b"colorWithRed:green:blue:alpha:\0" as *const u8),0.56862745098,0.27450980392,1.0,1.0);m1(slider,s(b"setMinimumTrackTintColor:\0" as *const u8),purple);m1(slider,s(b"setThumbTintColor:\0" as *const u8),m0(cls(b"UIColor\0" as *const u8),s(b"whiteColor\0" as *const u8)));let track=rgba(cls(b"UIColor\0" as *const u8),s(b"colorWithRed:green:blue:alpha:\0" as *const u8),1.0,1.0,1.0,0.30);m1(slider,s(b"setMaximumTrackTintColor:\0" as *const u8),track);
  let mut dot=m1(cls(b"UIImage\0" as *const u8),s(b"systemImageNamed:\0" as *const u8),str(b"circle.fill\0" as *const u8));let conf=md(cls(b"UIImageSymbolConfiguration\0" as *const u8),s(b"configurationWithPointSize:\0" as *const u8),9.0);dot=m1(dot,s(b"imageWithConfiguration:\0" as *const u8),conf);let hidden=m1(dot,s(b"imageWithTintColor:\0" as *const u8),m0(cls(b"UIColor\0" as *const u8),s(b"clearColor\0" as *const u8)));dot=m1(dot,s(b"imageWithTintColor:\0" as *const u8),m0(cls(b"UIColor\0" as *const u8),s(b"whiteColor\0" as *const u8)));put(row,&raw const DOT_KEY,dot);put(row,&raw const CLEAR_KEY,hidden);title(slider,s(b"setThumbImage:forState:\0" as *const u8),hidden,0);title(slider,s(b"setThumbImage:forState:\0" as *const u8),dot,1);title(slider,s(b"setThumbImage:forState:\0" as *const u8),hidden,2);title(slider,s(b"setThumbImage:forState:\0" as *const u8),hidden,4);title(slider,s(b"setThumbImage:forState:\0" as *const u8),hidden,8);
  let live_button=mu(cls(b"UIButton\0" as *const u8),s(b"buttonWithType:\0" as *const u8),1);action(live_button,s(b"addTarget:action:forControlEvents:\0" as *const u8),TARGET,s(b"live:\0" as *const u8),64);m1(live_button,s(b"setAccessibilityLabel:\0" as *const u8),str(b"Return to live\0" as *const u8));let badge=m0(cls(b"UILabel\0" as *const u8),s(b"new\0" as *const u8));m1(badge,s(b"setText:\0" as *const u8),str(b"LIVE\0" as *const u8));m1(badge,s(b"setTextColor:\0" as *const u8),m0(cls(b"UIColor\0" as *const u8),s(b"whiteColor\0" as *const u8)));m1(badge,s(b"setFont:\0" as *const u8),md(cls(b"UIFont\0" as *const u8),s(b"boldSystemFontOfSize:\0" as *const u8),12.0));mu(badge,s(b"setTextAlignment:\0" as *const u8),1);md(m0(badge,s(b"layer\0" as *const u8)),s(b"setCornerRadius:\0" as *const u8),3.0);mb(badge,s(b"setClipsToBounds:\0" as *const u8),true);mb(badge,s(b"setTranslatesAutoresizingMaskIntoConstraints:\0" as *const u8),false);m1(live_button,s(b"addSubview:\0" as *const u8),badge);pin(badge,b"centerXAnchor\0" as *const u8,live_button,b"centerXAnchor\0" as *const u8,0.0);pin(badge,b"centerYAnchor\0" as *const u8,live_button,b"centerYAnchor\0" as *const u8,0.0);mb(md(m0(badge,s(b"widthAnchor\0" as *const u8)),s(b"constraintEqualToConstant:\0" as *const u8),60.0),s(b"setActive:\0" as *const u8),true);mb(md(m0(badge,s(b"heightAnchor\0" as *const u8)),s(b"constraintEqualToConstant:\0" as *const u8),24.0),s(b"setActive:\0" as *const u8),true);put(row,&raw const BADGE_KEY,badge);release(badge);let back=button(b"-10s\0" as *const u8,b"rewind:\0" as *const u8);let forward_button=button(b"+10s\0" as *const u8,b"forward:\0" as *const u8);icon_button(back,b"gobackward.10\0" as *const u8);icon_button(forward_button,b"goforward.10\0" as *const u8);m1(m0(live_button,s(b"titleLabel\0" as *const u8)),s(b"setFont:\0" as *const u8),md(cls(b"UIFont\0" as *const u8),s(b"boldSystemFontOfSize:\0" as *const u8),12.0));mb(label,s(b"setTranslatesAutoresizingMaskIntoConstraints:\0" as *const u8),false);m1(controls,s(b"addSubview:\0" as *const u8),label);mb(label,s(b"setHidden:\0" as *const u8),true);let options=button(b"Rewind Settings\0" as *const u8,b"openSettings:\0" as *const u8);icon_button(options,b"slider.horizontal.3\0" as *const u8);put(row,&raw const OPTIONS_KEY,options);m1(row,s(b"addArrangedSubview:\0" as *const u8),options);m1(row,s(b"addArrangedSubview:\0" as *const u8),slider);
  put(row,&raw const SLIDER_KEY,slider);put(row,&raw const LABEL_KEY,label);put(row,&raw const LIVE_KEY,live_button);put(row,&raw const BACK_KEY,back);put(row,&raw const FORWARD_KEY,forward_button);release(label);release(slider);
  m1(controls,s(b"addSubview:\0" as *const u8),row);let guide=m0(controls,s(b"safeAreaLayoutGuide\0" as *const u8));tracked_pin(row,&raw const PAD_LEFT_KEY,row,b"leadingAnchor\0" as *const u8,guide,b"leadingAnchor\0" as *const u8,12.0);tracked_pin(row,&raw const PAD_RIGHT_KEY,row,b"trailingAnchor\0" as *const u8,guide,b"trailingAnchor\0" as *const u8,0.0-12.0);tracked_pin(row,&raw const BOTTOM_KEY,row,b"bottomAnchor\0" as *const u8,guide,b"bottomAnchor\0" as *const u8,0.0-48.0);let h=md(m0(row,s(b"heightAnchor\0" as *const u8)),s(b"constraintEqualToConstant:\0" as *const u8),44.0);mb(h,s(b"setActive:\0" as *const u8),true);
  mb(back,s(b"setTranslatesAutoresizingMaskIntoConstraints:\0" as *const u8),false);mb(forward_button,s(b"setTranslatesAutoresizingMaskIntoConstraints:\0" as *const u8),false);m1(controls,s(b"addSubview:\0" as *const u8),back);m1(controls,s(b"addSubview:\0" as *const u8),forward_button);tracked_pin(row,&raw const SKIP_LEFT_KEY,back,b"centerXAnchor\0" as *const u8,guide,b"centerXAnchor\0" as *const u8,0.0-72.0);pin(back,b"centerYAnchor\0" as *const u8,guide,b"centerYAnchor\0" as *const u8,0.0);tracked_pin(row,&raw const SKIP_RIGHT_KEY,forward_button,b"centerXAnchor\0" as *const u8,guide,b"centerXAnchor\0" as *const u8,72.0);pin(forward_button,b"centerYAnchor\0" as *const u8,guide,b"centerYAnchor\0" as *const u8,0.0);
  mb(live_button,s(b"setTranslatesAutoresizingMaskIntoConstraints:\0" as *const u8),false);m1(controls,s(b"addSubview:\0" as *const u8),live_button);pin(live_button,b"trailingAnchor\0" as *const u8,row,b"trailingAnchor\0" as *const u8,0.0);pin(live_button,b"bottomAnchor\0" as *const u8,row,b"topAnchor\0" as *const u8,0.0-4.0);mb(md(m0(live_button,s(b"widthAnchor\0" as *const u8)),s(b"constraintEqualToConstant:\0" as *const u8),68.0),s(b"setActive:\0" as *const u8),true);mb(md(m0(live_button,s(b"heightAnchor\0" as *const u8)),s(b"constraintEqualToConstant:\0" as *const u8),44.0),s(b"setActive:\0" as *const u8),true);
  pin(label,b"leadingAnchor\0" as *const u8,row,b"leadingAnchor\0" as *const u8,0.0);pin(label,b"bottomAnchor\0" as *const u8,row,b"topAnchor\0" as *const u8,0.0-2.0);
  put(controls,&raw const ROW_KEY,row);m1(ROWS,s(b"addObject:\0" as *const u8),row);release(row);
 }
 put(assoc(row,&raw const BACK_KEY),&raw const PLAYER_KEY,weak(player));put(assoc(row,&raw const FORWARD_KEY),&raw const PLAYER_KEY,weak(player));put(assoc(row,&raw const LIVE_KEY),&raw const PLAYER_KEY,weak(player));mb(assoc(row,&raw const BACK_KEY),s(b"setHidden:\0" as *const u8),false);mb(assoc(row,&raw const FORWARD_KEY),s(b"setHidden:\0" as *const u8),false);mb(assoc(row,&raw const LIVE_KEY),s(b"setHidden:\0" as *const u8),false);put(row,&raw const PLAYER_KEY,weak(player));mb(row,s(b"setHidden:\0" as *const u8),false);m1(controls,s(b"bringSubviewToFront:\0" as *const u8),row);adapt(controls,row);prefetch(player);
}}
unsafe extern "C" fn layout(o:Id,sel:Sel){unsafe{transmute::<Id,Zero>(OLD_LAYOUT)(o,sel);attach(o);}}
// Process every loaded live player, even before controls have been displayed.
unsafe fn update_playback(player:Id){unsafe{
 let state=assoc(player,&raw const STATE_KEY);promote_prepared(state);
 if !auto_enabled(){set(state,b"autoRewind\0" as *const u8,number(0));}
 if value(state,b"autoRewind\0" as *const u8)==1&&value(state,b"mode\0" as *const u8)==0&&get(state,b"cachedURL\0" as *const u8)!=0 as Id{
  let end=double(get(state,b"cachedDuration\0" as *const u8),s(b"doubleValue\0" as *const u8));
  if end>2.0&&end<604800.0{start_replay(player,end-1.0);}
 }
 let mode=value(state,b"mode\0" as *const u8);
  if mode==2&&get(state,b"pending\0" as *const u8)!=0 as Id&&CFAbsoluteTimeGetCurrent()>=double(get(state,b"seekDueAt\0" as *const u8),s(b"doubleValue\0" as *const u8)){
   let attempts=value(state,b"attempts\0" as *const u8)+1;set(state,b"attempts\0" as *const u8,number(attempts));let duration=CMTimeGetSeconds(time(player,s(b"duration\0" as *const u8)));
   if duration>2.0&&duration<604800.0&&count(player,s(b"state\0" as *const u8))>=1{seek_position(player,double(get(state,b"pending\0" as *const u8),s(b"doubleValue\0" as *const u8)));set(state,b"pending\0" as *const u8,0 as Id);let began=get(state,b"switchStartedAt\0" as *const u8);if began!=0 as Id{set(state,b"lastSourceReadySeconds\0" as *const u8,real(CFAbsoluteTimeGetCurrent()-double(began,s(b"doubleValue\0" as *const u8))));set(state,b"switchStartedAt\0" as *const u8,0 as Id);}m0(player,s(b"play\0" as *const u8));}else{if attempts>100{go_live(player);set(state,b"notice\0" as *const u8,str(b"Replay unavailable\0" as *const u8));}}
  }

 if value(state,b"autoRewind\0" as *const u8)==1{prefetch(player);}
}}
unsafe extern "C" fn tick(_:Id,_:Sel,_:Id){unsafe{
 let players=m0(PLAYERS,s(b"allObjects\0" as *const u8));let total=count(players,s(b"count\0" as *const u8));let mut index=0;
 while index<total{update_playback(mu(players,s(b"objectAtIndex:\0" as *const u8),index));index=index+1;}
 let all=m0(ROWS,s(b"allObjects\0" as *const u8));let n=count(all,s(b"count\0" as *const u8));let mut i=0;while i<n{
  let row=mu(all,s(b"objectAtIndex:\0" as *const u8),i);let player=weak_get(assoc(row,&raw const PLAYER_KEY));let state=assoc(player,&raw const STATE_KEY);promote_prepared(state);
  let slider=assoc(row,&raw const SLIDER_KEY);let label=assoc(row,&raw const LABEL_KEY);let live_button=assoc(row,&raw const LIVE_KEY);let end=timeline_end(player);let mode=value(state,b"mode\0" as *const u8);
  if slider!=0 as Id{
   mb(slider,s(b"setEnabled:\0" as *const u8),end>2.0&&get(state,b"cachedURL\0" as *const u8)!=0 as Id);let pending=get(state,b"pending\0" as *const u8);let pos=if pending!=0 as Id{double(pending,s(b"doubleValue\0" as *const u8))}else{if mode==2{CMTimeGetSeconds(time(player,s(b"position\0" as *const u8)))}else{end}};
   if !b0(slider,s(b"isTracking\0" as *const u8)){mf(slider,s(b"setValue:\0" as *const u8),if end>0.0{(pos/end) as f32}else{1.0});}
   let tracking=b0(slider,s(b"isTracking\0" as *const u8));let previous=assoc(row,&raw const TRACKING_KEY);if previous==0 as Id||count(previous,s(b"unsignedIntegerValue\0" as *const u8))!=if tracking{1}else{0}{let dot=assoc(row,&raw const DOT_KEY);let clear=assoc(row,&raw const CLEAR_KEY);if dot!=0 as Id&&clear!=0 as Id{title(slider,s(b"setThumbImage:forState:\0" as *const u8),if tracking{dot}else{clear},1);title(slider,s(b"setThumbImage:forState:\0" as *const u8),if tracking{dot}else{clear},5);}put(row,&raw const TRACKING_KEY,number(if tracking{1}else{0}));}let fraction=float(slider,s(b"value\0" as *const u8)) as f64;let display_position=if tracking&&fraction>=0.0&&fraction<=1.0{fraction*end}else{pos};let notice=get(state,b"notice\0" as *const u8);mb(label,s(b"setHidden:\0" as *const u8),!layout_visible(row)||(mode==0&&!tracking));let text=if end>2.0{clock(display_position)}else{if notice!=0 as Id{notice}else{str(b"--:--:--\0" as *const u8)}};if !eq(m0(label,s(b"text\0" as *const u8)),text){m1(label,s(b"setText:\0" as *const u8),text);}let badge=assoc(row,&raw const BADGE_KEY);m1(badge,s(b"setText:\0" as *const u8),if mode==0{str(b"LIVE\0" as *const u8)}else{str(b"LIVE \xe2\x96\xb6\0" as *const u8)});m1(badge,s(b"setBackgroundColor:\0" as *const u8),rgba(cls(b"UIColor\0" as *const u8),s(b"colorWithRed:green:blue:alpha:\0" as *const u8),if mode==0{0.92}else{0.18},if mode==0{0.0}else{0.18},if mode==0{0.0}else{0.20},0.95));
  }
  if player!=0 as Id&&m0(row,s(b"window\0" as *const u8))!=0 as Id{prefetch(player);}i=i+1;
 }
}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn native_rewind_initialize(){unsafe{
 initialize_duo_bars();
 MAIN=dlsym(18446744073709551614usize as Id,b"_dispatch_main_q\0" as *const u8);let player=cls(b"IVSPlayer\0" as *const u8);let controls=cls(b"_TtC6Twitch25TheaterPlayerControlsView\0" as *const u8);
 if MAIN==0 as Id||player==0 as Id||controls==0 as Id||class_getInstanceMethod(player,s(b"load:configuration:\0" as *const u8))==0 as Id||class_getInstanceMethod(controls,s(b"layoutSubviews\0" as *const u8))==0 as Id{return;}
 let target=objc_allocateClassPair(cls(b"NSObject\0" as *const u8),b"TwitchNativeRewindActions\0" as *const u8,0);if target==0 as Id{return;}
 class_addMethod(target,s(b"preview:\0" as *const u8),preview as Id,b"v24@0:8@16\0" as *const u8);class_addMethod(target,s(b"scrub:\0" as *const u8),scrub as Id,b"v24@0:8@16\0" as *const u8);class_addMethod(target,s(b"rewind:\0" as *const u8),rewind as Id,b"v24@0:8@16\0" as *const u8);class_addMethod(target,s(b"forward:\0" as *const u8),forward as Id,b"v24@0:8@16\0" as *const u8);class_addMethod(target,s(b"live:\0" as *const u8),live as Id,b"v24@0:8@16\0" as *const u8);class_addMethod(target,s(b"tick:\0" as *const u8),tick as Id,b"v24@0:8@16\0" as *const u8);class_addMethod(target,s(b"openSettings:\0" as *const u8),open_settings as Id,b"v24@0:8@16\0" as *const u8);class_addMethod(target,s(b"toggleAuto:\0" as *const u8),toggle_auto as Id,b"v24@0:8@16\0" as *const u8);objc_registerClassPair(target);TARGET=m0(target,s(b"new\0" as *const u8));ROWS=retain(m0(cls(b"NSHashTable\0" as *const u8),s(b"weakObjectsHashTable\0" as *const u8)));
 let settings=objc_allocateClassPair(cls(b"UIViewController\0" as *const u8),b"TwitchPlusRewindSettings\0" as *const u8,0);if settings!=0 as Id{class_addMethod(settings,s(b"loadView\0" as *const u8),settings_load as Id,b"v16@0:8\0" as *const u8);class_addMethod(settings,s(b"done:\0" as *const u8),settings_done as Id,b"v24@0:8@16\0" as *const u8);objc_registerClassPair(settings);}
 let tabs=cls(b"_TtC6Twitch16TabBarController\0" as *const u8);if tabs!=0 as Id{OLD_TAB_LOAD=hook(tabs,s(b"viewDidLoad\0" as *const u8),tabs_loaded as Id);}
 PLAYERS=retain(m0(cls(b"NSHashTable\0" as *const u8),s(b"weakObjectsHashTable\0" as *const u8)));
 OLD_SOURCE=hook(player,s(b"loadSource:configuration:\0" as *const u8),load_source as Id);OLD_LOAD=hook(player,s(b"load:configuration:\0" as *const u8),load as Id);OLD_LAYOUT=hook(controls,s(b"layoutSubviews\0" as *const u8),layout as Id);
 timer(cls(b"NSTimer\0" as *const u8),s(b"scheduledTimerWithTimeInterval:target:selector:userInfo:repeats:\0" as *const u8),0.1,TARGET,s(b"tick:\0" as *const u8),0 as Id,true);
}}
#[used]#[unsafe(link_section="__DATA,__mod_init_func")]static INITIALIZE:unsafe extern "C" fn()=native_rewind_initialize;




