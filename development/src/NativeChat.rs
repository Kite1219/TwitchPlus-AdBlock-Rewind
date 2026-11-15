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
type Send=unsafe extern "C" fn(Id,Sel,Id)->Id;
type Connect=unsafe extern "C" fn(Id,Sel)->Id;
type Ban=unsafe extern "C" fn(Id,Sel,Id,bool,u32);
type Active=unsafe extern "C" fn(Id,Sel,u32);
type Join=unsafe extern "C" fn(Id,Sel,u32,u32);
type Unban=unsafe extern "C" fn(Id,Sel,Id,Id,Id,u32);
type Reset=unsafe extern "C" fn(Id,Sel);
type Completion=unsafe extern "C" fn(Id,Id,Id);
type Api=unsafe extern "C" fn(Id,Sel,Id,Id,Id,Id,Id);

unsafe extern "C" {
 fn objc_getClass(name:*const u8)->Id;
 fn sel_registerName(name:*const u8)->Sel;
 fn class_getInstanceMethod(class:Id,selector:Sel)->Id;
 fn class_addMethod(class:Id,selector:Sel,imp:Id,types:*const u8)->bool;
 fn method_getImplementation(method:Id)->Id;
 fn method_getTypeEncoding(method:Id)->*const u8;
 fn method_setImplementation(method:Id,imp:Id)->Id;
 fn class_getInstanceVariable(class:Id,name:*const u8)->Id;
 fn ivar_getOffset(ivar:Id)->usize;
 fn object_getClass(object:Id)->Id;
 fn objc_getAssociatedObject(object:Id,key:Id)->Id;
 fn objc_setAssociatedObject(object:Id,key:Id,value:Id,policy:usize);
 fn arc4random_uniform(upper:u32)->u32;
 fn dlsym(handle:Id,name:*const u8)->Id;
 fn dispatch_async_f(queue:Id,context:Id,callback:unsafe extern "C" fn(Id));
 #[link_name="objc_msgSend"] fn m0(object:Id,selector:Sel)->Id;
 #[link_name="objc_msgSend"] fn m1(object:Id,selector:Sel,a:Id)->Id;
 #[link_name="objc_msgSend"] fn m2(object:Id,selector:Sel,a:Id,b:Id)->Id;
 #[link_name="objc_msgSend"] fn mu(object:Id,selector:Sel,a:usize)->Id;
 #[link_name="objc_msgSend"] fn bool0(object:Id,selector:Sel)->bool;
 #[link_name="objc_msgSend"] fn bool1(object:Id,selector:Sel,a:Id)->bool;
 #[link_name="objc_msgSend"] fn mb(object:Id,selector:Sel,a:bool)->Id;
 #[link_name="objc_msgSend"] fn uint0(object:Id,selector:Sel)->usize;
 #[link_name="objc_msgSend"] fn insert(object:Id,selector:Sel,a:Id,index:usize)->Id;
}

static mut LOCK:Id=0 as Id;
static mut MAIN_QUEUE:Id=0 as Id;
static mut BANNED:Id=0 as Id;
static mut ACTIVE_ID:u32=0;
static mut WANT_GUEST:bool=false;
static mut LAST_SOCKET:Id=0 as Id;
static mut OLD_SEND:Id=0 as Id;
static mut OLD_BAN:Id=0 as Id;
static mut OLD_ACTIVE:Id=0 as Id;
static mut OLD_RESET:Id=0 as Id;
static mut OLD_CONNECT:Id=0 as Id;
static mut OLD_JOIN:Id=0 as Id;
static mut OLD_UNBAN:Id=0 as Id;
static mut OLD_API:Id=0 as Id;
static mut OLD_BAN_MOVED:Id=0 as Id;
static mut OLD_LAYOUT:Id=0 as Id;
static SESSION_GUEST:u8=0;
static SESSION_TASK:u8=0;
static ROTATE_QUEUED:u8=0;
static GUEST_NICK:u8=0;
static mut ACCOUNT_ID:u32=0;
static mut ACCOUNT_SEEN:bool=false;
static mut ACCOUNT_LOGIN:Id=0 as Id;

unsafe fn s(p:*const u8)->Sel{unsafe{sel_registerName(p)}}
unsafe fn c(p:*const u8)->Id{unsafe{objc_getClass(p)}}
unsafe fn text(p:*const u8)->Id{unsafe{m1(c(b"NSString\0" as *const u8),s(b"stringWithUTF8String:\0" as *const u8),p as Id)}}
unsafe fn retain(x:Id)->Id{unsafe{m0(x,s(b"retain\0" as *const u8))}}
unsafe fn release(x:Id){unsafe{m0(x,s(b"release\0" as *const u8));}}
unsafe fn lock(){unsafe{m0(LOCK,s(b"lock\0" as *const u8));}}
unsafe fn unlock(){unsafe{m0(LOCK,s(b"unlock\0" as *const u8));}}
unsafe fn key(id:u32)->Id{unsafe{mu(c(b"NSNumber\0" as *const u8),s(b"numberWithUnsignedInteger:\0" as *const u8),id as usize)}}
unsafe fn known(id:u32)->bool{unsafe{m1(BANNED,s(b"objectForKey:\0" as *const u8),key(id))!=0 as Id}}
unsafe fn append(a:Id,b:Id)->Id{unsafe{m1(a,s(b"stringByAppendingString:\0" as *const u8),b)}}
unsafe fn assoc(o:Id,k:*const u8)->Id{unsafe{objc_getAssociatedObject(o,k as Id)}}
unsafe fn put(o:Id,k:*const u8,v:Id){unsafe{objc_setAssociatedObject(o,k as Id,v,1);}}
unsafe fn field(o:Id,name:*const u8)->Id{
 unsafe{if o==0 as Id{return 0 as Id;}let v=class_getInstanceVariable(object_getClass(o),name);if v==0 as Id{return 0 as Id;}*((o as usize+ivar_getOffset(v)) as *const Id)}
}
unsafe fn room_id(o:Id)->u32{
 unsafe{if o==0 as Id{return 0;}let v=class_getInstanceVariable(object_getClass(o),b"channelID\0" as *const u8);if v==0 as Id{return 0;}*((o as usize+ivar_getOffset(v)) as *const u32)}
}
unsafe fn hook(class:Id,selector:Sel,imp:Id)->Id{
 unsafe{if class==0 as Id{return 0 as Id;}let m=class_getInstanceMethod(class,selector);if m==0 as Id{return 0 as Id;}let old=method_getImplementation(m);if !class_addMethod(class,selector,imp,method_getTypeEncoding(m)){method_setImplementation(m,imp);}old}
}

// Account credentials and identity remain in Twitch's account model. Only the
// active banned room's reading transport gets a guest handshake.
unsafe extern "C" fn rotate_socket(socket:Id){
 unsafe{
  lock();
  put(socket,&raw const ROTATE_QUEUED,0 as Id);
  let mode=assoc(socket,&raw const SESSION_GUEST);
  let task=field(socket,b"task\0" as *const u8);
  let current=bool0(mode,s(b"boolValue\0" as *const u8));
  let rotate=socket==LAST_SOCKET && mode!=0 as Id && task==assoc(socket,&raw const SESSION_TASK) && current!=WANT_GUEST;
  unlock();
  // This publishes socket-disconnected; KMP's existing retry rejoins its rooms.
  // Calling the channel controller's disconnect would instead PART the room.
  if rotate{m0(socket,s(b"disconnect\0" as *const u8));}
  release(socket);
 }
}
unsafe fn queue_rotation(socket:Id){
 unsafe{
  if socket!=0 as Id && !bool0(assoc(socket,&raw const ROTATE_QUEUED),s(b"boolValue\0" as *const u8)){
   put(socket,&raw const ROTATE_QUEUED,key(1));
   dispatch_async_f(MAIN_QUEUE,retain(socket),rotate_socket);
  }
 }
}
unsafe fn update_mode(){
 unsafe{
  let desired=ACTIVE_ID!=0 && known(ACTIVE_ID);
  if desired!=WANT_GUEST{
   WANT_GUEST=desired;
   queue_rotation(LAST_SOCKET);
  }
 }
}
unsafe fn mark_banned(id:u32){unsafe{if id!=0{m2(BANNED,s(b"setObject:forKey:\0" as *const u8),key(1),key(id));if ACTIVE_ID==0{ACTIVE_ID=id;}update_mode();}}}

unsafe extern "C" fn ban_changed(o:Id,sel:Sel,manager:Id,banned:bool,id:u32){
 unsafe{
  lock();
  if banned{mark_banned(id);}else if !WANT_GUEST{m1(BANNED,s(b"removeObjectForKey:\0" as *const u8),key(id));update_mode();}
  unlock();
  // Keep the native transcript subscribed. The actual ban is retained above,
  // and the existing API receives its real typed banned-result for posting.
  transmute::<Id,Ban>(OLD_BAN)(o,sel,manager,false,id);
 }
}
unsafe extern "C" fn active_changed(o:Id,sel:Sel,id:u32){unsafe{lock();ACTIVE_ID=id;update_mode();unlock();transmute::<Id,Active>(OLD_ACTIVE)(o,sel,id);}}
unsafe extern "C" fn active_reset(o:Id,sel:Sel){unsafe{lock();ACTIVE_ID=0;update_mode();unlock();transmute::<Id,Reset>(OLD_RESET)(o,sel);}}
unsafe extern "C" fn join_channel(o:Id,sel:Sel,channel:u32,user:u32){
 unsafe{
  lock();
  if ACCOUNT_SEEN && ACCOUNT_ID!=user{
   m0(BANNED,s(b"removeAllObjects\0" as *const u8));release(ACCOUNT_LOGIN);ACCOUNT_LOGIN=0 as Id;update_mode();
  }
  ACCOUNT_ID=user;ACCOUNT_SEEN=true;
  unlock();transmute::<Id,Join>(OLD_JOIN)(o,sel,channel,user);
 }
}
unsafe extern "C" fn user_unbanned(o:Id,sel:Sel,manager:Id,target:Id,moderator:Id,channel:u32){
 unsafe{
  lock();
  let lhs=m0(target,s(b"lowercaseString\0" as *const u8));let rhs=m0(ACCOUNT_LOGIN,s(b"lowercaseString\0" as *const u8));
  if ACCOUNT_LOGIN!=0 as Id && bool1(lhs,s(b"isEqualToString:\0" as *const u8),rhs){
   m1(BANNED,s(b"removeObjectForKey:\0" as *const u8),key(channel));update_mode();
  }
  unlock();transmute::<Id,Unban>(OLD_UNBAN)(o,sel,manager,target,moderator,channel);
 }
}

unsafe extern "C" fn connect_socket(o:Id,sel:Sel)->Id{
 unsafe{
  lock();
  if LAST_SOCKET!=o{let previous=LAST_SOCKET;LAST_SOCKET=retain(o);release(previous);}
  unlock();
  let result=transmute::<Id,Connect>(OLD_CONNECT)(o,sel);
  lock();
  let mode=assoc(o,&raw const SESSION_GUEST);
  if mode!=0 as Id && field(o,b"task\0" as *const u8)==assoc(o,&raw const SESSION_TASK) && bool0(mode,s(b"boolValue\0" as *const u8))!=WANT_GUEST{queue_rotation(o);}
  unlock();result
 }
}

unsafe extern "C" fn send_text(o:Id,sel:Sel,message:Id)->Id{
 unsafe{
  lock();
  let task=field(o,b"task\0" as *const u8);
  if task!=assoc(o,&raw const SESSION_TASK){
   put(o,&raw const SESSION_TASK,task);put(o,&raw const SESSION_GUEST,0 as Id);put(o,&raw const GUEST_NICK,0 as Id);
  }
  let lines=m1(message,s(b"componentsSeparatedByString:\0" as *const u8),text(b"\r\n\0" as *const u8));
  let result=m0(c(b"NSMutableArray\0" as *const u8),s(b"array\0" as *const u8));
  let enumerator=m0(lines,s(b"objectEnumerator\0" as *const u8));
  let mut line=m0(enumerator,s(b"nextObject\0" as *const u8));
  while line!=0 as Id{
   let mut replacement=line;
   let password=bool1(line,s(b"hasPrefix:\0" as *const u8),text(b"PASS \0" as *const u8));
   let nickname=bool1(line,s(b"hasPrefix:\0" as *const u8),text(b"NICK \0" as *const u8));
   if (password || nickname) && assoc(o,&raw const SESSION_GUEST)==0 as Id{
    // Bind the mode to the actual task on its first auth command. Repeated
    // connect() calls that reuse a running task cannot relabel that task.
    put(o,&raw const SESSION_GUEST,mb(c(b"NSNumber\0" as *const u8),s(b"numberWithBool:\0" as *const u8),WANT_GUEST));
   }
   if password{
    if bool0(assoc(o,&raw const SESSION_GUEST),s(b"boolValue\0" as *const u8)){replacement=text(b"PASS pass\0" as *const u8);}
   }else if nickname{
    let login=mu(line,s(b"substringFromIndex:\0" as *const u8),5);
    if o==LAST_SOCKET{retain(login);release(ACCOUNT_LOGIN);ACCOUNT_LOGIN=login;}
    if bool0(assoc(o,&raw const SESSION_GUEST),s(b"boolValue\0" as *const u8)){
     let mut guest=assoc(o,&raw const GUEST_NICK);
     if guest==0 as Id{
      let number=mu(c(b"NSNumber\0" as *const u8),s(b"numberWithUnsignedInteger:\0" as *const u8),arc4random_uniform(900000000) as usize+100000000);
      guest=append(text(b"justinfan\0" as *const u8),m0(number,s(b"stringValue\0" as *const u8)));
      put(o,&raw const GUEST_NICK,guest);
     }
     replacement=append(text(b"NICK \0" as *const u8),guest);
    }
   }
   m1(result,s(b"addObject:\0" as *const u8),replacement);
   line=m0(enumerator,s(b"nextObject\0" as *const u8));
  }
  let outbound=retain(m1(result,s(b"componentsJoinedByString:\0" as *const u8),text(b"\r\n\0" as *const u8)));
  unlock();
  let response=transmute::<Id,Send>(OLD_SEND)(o,sel,outbound);
  release(outbound);
  lock();let mode=assoc(o,&raw const SESSION_GUEST);if o==LAST_SOCKET && mode!=0 as Id && bool0(mode,s(b"boolValue\0" as *const u8))!=WANT_GUEST{queue_rotation(o);}unlock();response
 }
}

unsafe extern "C" fn send_api(o:Id,sel:Sel,channel:Id,message:Id,reply:Id,nonce:Id,completion:Id){
 unsafe{
  let number=uint0(channel,s(b"longLongValue\0" as *const u8)) as u32;
  lock();let banned=known(number);unlock();
  if banned && completion!=0 as Id{
   let reason=m0(c(b"KMPMCChatMessageDropReason\0" as *const u8),s(b"userBanned\0" as *const u8));
   let result=m1(m0(c(b"KMPMCSendChatMessageApiSendChatMessageResultDropped\0" as *const u8),s(b"alloc\0" as *const u8)),s(b"initWithDropReason:\0" as *const u8),reason);
   if result!=0 as Id{
    let callback=*((completion as usize+16) as *const Id);
    transmute::<Id,Completion>(callback)(completion,result,0 as Id);release(result);return;
   }
  }
  transmute::<Id,Api>(OLD_API)(o,sel,channel,message,reply,nonce,completion);
 }
}

// Only existing Twitch views are touched. There is no added renderer, entry
// button, sheet, header, streamer field, WebView, or custom chat surface.
unsafe fn restore_transcript(view:Id){
 unsafe{
  let full=field(view,b"fullInfoView\0" as *const u8);
  if full==0 as Id{return;}
  let matches=bool1(full,s(b"isKindOfClass:\0" as *const u8),c(b"_TtC6Twitch18ChatBannedInfoView\0" as *const u8));
  if !matches{return;}
  let stack=field(view,b"stackView\0" as *const u8);let transcript=field(view,b"transcriptView\0" as *const u8);
  if stack==0 as Id || transcript==0 as Id{return;}
  mb(full,s(b"setHidden:\0" as *const u8),true);
  let arranged=m0(stack,s(b"arrangedSubviews\0" as *const u8));
  if !bool1(arranged,s(b"containsObject:\0" as *const u8),transcript){insert(stack,s(b"insertArrangedSubview:atIndex:\0" as *const u8),transcript,0);}
  mb(transcript,s(b"setHidden:\0" as *const u8),false);
  mb(transcript,s(b"setAccessibilityElementsHidden:\0" as *const u8),false);
 }
}
unsafe extern "C" fn chat_layout(o:Id,sel:Sel){unsafe{transmute::<Id,Reset>(OLD_LAYOUT)(o,sel);restore_transcript(o);}}
unsafe extern "C" fn ban_view_moved(o:Id,sel:Sel){
 unsafe{
  transmute::<Id,Reset>(OLD_BAN_MOVED)(o,sel);
  if m0(o,s(b"window\0" as *const u8))==0 as Id{return;}
  // The native view stores its own UInt32 room ID. Never infer a stale view's
  // room from the new active channel during navigation.
  let id=room_id(o);lock();if id!=0 && id==ACTIVE_ID{mark_banned(id);}unlock();
  mb(o,s(b"setHidden:\0" as *const u8),true);
  let mut parent=m0(o,s(b"superview\0" as *const u8));
  let chat_class=c(b"_TtC6Twitch8ChatView\0" as *const u8);
  while parent!=0 as Id{
   if bool1(parent,s(b"isKindOfClass:\0" as *const u8),chat_class){restore_transcript(parent);break;}
   parent=m0(parent,s(b"superview\0" as *const u8));
  }
 }
}

#[unsafe(no_mangle)] pub unsafe extern "C" fn native_chat_initialize(){
 unsafe{
  LOCK=m0(c(b"NSRecursiveLock\0" as *const u8),s(b"new\0" as *const u8));
  BANNED=m0(c(b"NSMutableDictionary\0" as *const u8),s(b"new\0" as *const u8));
  MAIN_QUEUE=dlsym(18446744073709551614usize as Id,b"_dispatch_main_q\0" as *const u8);
  if LOCK==0 as Id || MAIN_QUEUE==0 as Id{return;}
  let socket=c(b"_TtC6TwitchP33_0E46226D557B6F3C153807A0C430F2E513ChatWebSocket\0" as *const u8);
  let controller=c(b"_TtC6Twitch20TwitchChatController\0" as *const u8);
  let manager=c(b"_TtC6Twitch17TwitchChatManager\0" as *const u8);
  let api=c(b"_TtC6Twitch18SendChatMessageApi\0" as *const u8);
  // Fail closed on another app version instead of partially installing hooks.
  if socket==0 as Id || controller==0 as Id || manager==0 as Id || api==0 as Id{return;}
  OLD_API=hook(api,s(b"sendGqlChatMessageChannelId:text:replyParentMessageId:nonce:completionHandler:\0" as *const u8),send_api as Id);
  OLD_CONNECT=hook(socket,s(b"connect\0" as *const u8),connect_socket as Id);
  OLD_SEND=hook(socket,s(b"sendMessage:\0" as *const u8),send_text as Id);
  OLD_BAN=hook(controller,s(b"chatManager:userBanStatusChangedTo:in:\0" as *const u8),ban_changed as Id);
  OLD_UNBAN=hook(controller,s(b"chatManager:targetUserWithName:unbannedByModeraterWithName:in:\0" as *const u8),user_unbanned as Id);
  OLD_ACTIVE=hook(manager,s(b"setActiveChannelID:\0" as *const u8),active_changed as Id);
  OLD_RESET=hook(manager,s(b"resetActiveChannelID\0" as *const u8),active_reset as Id);
  OLD_JOIN=hook(manager,s(b"joinChannel:as:\0" as *const u8),join_channel as Id);
  OLD_LAYOUT=hook(c(b"_TtC6Twitch8ChatView\0" as *const u8),s(b"layoutSubviews\0" as *const u8),chat_layout as Id);
  OLD_BAN_MOVED=hook(c(b"_TtC6Twitch18ChatBannedInfoView\0" as *const u8),s(b"didMoveToWindow\0" as *const u8),ban_view_moved as Id);
 }
}
#[used] #[unsafe(link_section="__DATA,__mod_init_func")]
static INITIALIZE:unsafe extern "C" fn()=native_chat_initialize;
