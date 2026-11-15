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
type Appear=unsafe extern "C" fn(Id,Sel,bool);
type Json=unsafe extern "C" fn(Id,Sel,Id,usize,Id)->Id;

#[repr(C)]struct Insets{top:f64,left:f64,bottom:f64,right:f64}
unsafe extern "C"{
 fn objc_getClass(n:*const u8)->Id;fn object_getClass(o:Id)->Id;fn sel_registerName(n:*const u8)->Sel;
 fn objc_allocateClassPair(base:Id,name:*const u8,extra:usize)->Id;fn objc_registerClassPair(c:Id);
 fn class_getInstanceMethod(c:Id,s:Sel)->Id;fn method_getImplementation(m:Id)->Id;fn method_getTypeEncoding(m:Id)->*const u8;
 fn class_addMethod(c:Id,s:Sel,imp:Id,encoding:*const u8)->bool;fn method_setImplementation(m:Id,imp:Id)->Id;
 fn class_getInstanceVariable(c:Id,n:*const u8)->Id;fn ivar_getOffset(i:Id)->usize;
 fn objc_getAssociatedObject(o:Id,k:Id)->Id;fn objc_setAssociatedObject(o:Id,k:Id,v:Id,p:usize);
 fn dlsym(h:Id,n:*const u8)->Id;fn dispatch_async_f(q:Id,c:Id,f:unsafe extern "C" fn(Id));fn dispatch_get_global_queue(q:usize,flags:usize)->Id;
 fn CFAbsoluteTimeGetCurrent()->f64;
 #[link_name="objc_msgSend"]fn m0(o:Id,s:Sel)->Id;
 #[link_name="objc_msgSend"]fn m1(o:Id,s:Sel,a:Id)->Id;
 #[link_name="objc_msgSend"]fn m2(o:Id,s:Sel,a:Id,b:Id)->Id;
 #[link_name="objc_msgSend"]fn m3(o:Id,s:Sel,a:Id,b:Id,c:Id)->Id;
 #[link_name="objc_msgSend"]fn mu(o:Id,s:Sel,a:usize)->Id;
 #[link_name="objc_msgSend"]fn count(o:Id,s:Sel)->usize;
 #[link_name="objc_msgSend"]fn b0(o:Id,s:Sel)->bool;
 #[link_name="objc_msgSend"]fn b1(o:Id,s:Sel,a:Id)->bool;
 #[link_name="objc_msgSend"]fn mb(o:Id,s:Sel,v:bool)->Id;
 #[link_name="objc_msgSend"]fn md(o:Id,s:Sel,v:f64)->Id;
 #[link_name="objc_msgSend"]fn title(o:Id,s:Sel,v:Id,state:usize)->Id;
 #[link_name="objc_msgSend"]fn action(o:Id,s:Sel,t:Id,a:Sel,event:usize)->Id;
 #[link_name="objc_msgSend"]fn inset(o:Id,s:Sel,v:Insets)->Id;
 #[link_name="objc_msgSend"]fn timer(o:Id,s:Sel,seconds:f64,t:Id,a:Sel,info:Id,repeats:bool)->Id;
 #[link_name="objc_msgSend"]fn observe(o:Id,s:Sel,t:Id,a:Sel,name:Id,filter:Id)->Id;
}
static mut LOCK:Id=0 as Id;static mut MAIN:Id=0 as Id;static mut TARGET:Id=0 as Id;
static mut SAVED:Id=0 as Id;static mut LIVE:Id=0 as Id;static mut BUTTONS:Id=0 as Id;static mut SCREENS:Id=0 as Id;
static mut QUERY:Id=0 as Id;static mut OLD_JSON:Id=0 as Id;static mut SIDEBARS:Id=0 as Id;static mut OLD_SIDEBAR_APPEAR:Id=0 as Id;static mut OLD_BASE_APPEAR:Id=0 as Id;
static mut BUSY:bool=false;static mut ACTIVE:bool=true;static mut GENERATION:usize=0;static mut UPDATED:f64=0.0;

static mut OLD_PROFILE_MOVE:Id=0 as Id;static mut OLD_PROFILE_LAYOUT:Id=0 as Id;static mut OLD_FOLLOWING_APPEAR:Id=0 as Id;
static BUTTON_KEY:u8=0;static CHANNEL_KEY:u8=0;
unsafe fn s(v:*const u8)->Sel{unsafe{sel_registerName(v)}}
unsafe fn cls(v:*const u8)->Id{unsafe{objc_getClass(v)}}
unsafe fn str(v:*const u8)->Id{unsafe{m1(cls(b"NSString\0" as *const u8),s(b"stringWithUTF8String:\0" as *const u8),v as Id)}}
unsafe fn retain(o:Id)->Id{unsafe{m0(o,s(b"retain\0" as *const u8))}}
unsafe fn release(o:Id){unsafe{m0(o,s(b"release\0" as *const u8));}}
unsafe fn lock(){unsafe{m0(LOCK,s(b"lock\0" as *const u8));}}
unsafe fn unlock(){unsafe{m0(LOCK,s(b"unlock\0" as *const u8));}}
unsafe fn assoc(o:Id,k:*const u8)->Id{unsafe{objc_getAssociatedObject(o,k as Id)}}
unsafe fn put(o:Id,k:*const u8,v:Id){unsafe{objc_setAssociatedObject(o,k as Id,v,1);}}
unsafe fn get(o:Id,k:*const u8)->Id{unsafe{if is_dict(o){m1(o,s(b"objectForKey:\0" as *const u8),str(k))}else{0 as Id}}}
unsafe fn set(o:Id,k:*const u8,v:Id){unsafe{m2(o,s(b"setObject:forKey:\0" as *const u8),v,str(k));}}
unsafe fn array()->Id{unsafe{m0(cls(b"NSMutableArray\0" as *const u8),s(b"array\0" as *const u8))}}
unsafe fn dict()->Id{unsafe{m0(cls(b"NSMutableDictionary\0" as *const u8),s(b"dictionary\0" as *const u8))}}
unsafe fn number(v:usize)->Id{unsafe{mu(cls(b"NSNumber\0" as *const u8),s(b"numberWithUnsignedInteger:\0" as *const u8),v)}}
unsafe fn add(a:Id,o:Id){unsafe{m1(a,s(b"addObject:\0" as *const u8),o);}}
unsafe fn eq(a:Id,b:Id)->bool{unsafe{is_string(a)&&is_string(b)&&b1(a,s(b"isEqualToString:\0" as *const u8),b)}}
unsafe fn is_dict(o:Id)->bool{unsafe{o!=0 as Id&&b1(o,s(b"isKindOfClass:\0" as *const u8),cls(b"NSDictionary\0" as *const u8))}}
unsafe fn is_array(o:Id)->bool{unsafe{o!=0 as Id&&b1(o,s(b"isKindOfClass:\0" as *const u8),cls(b"NSArray\0" as *const u8))}}
unsafe fn is_string(o:Id)->bool{unsafe{o!=0 as Id&&b1(o,s(b"isKindOfClass:\0" as *const u8),cls(b"NSString\0" as *const u8))}}
unsafe fn null()->Id{unsafe{m0(cls(b"NSNull\0" as *const u8),s(b"null\0" as *const u8))}}
unsafe fn mutable(o:Id)->Id{unsafe{m0(m0(o,s(b"mutableCopy\0" as *const u8)),s(b"autorelease\0" as *const u8))}}
unsafe fn field(o:Id,n:*const u8)->Id{unsafe{if o==0 as Id{return 0 as Id;}let iv=class_getInstanceVariable(object_getClass(o),n);if iv==0 as Id{return 0 as Id;}*((o as usize+ivar_getOffset(iv)) as *const Id)}}
unsafe fn hook(c:Id,sel:Sel,imp:Id)->Id{unsafe{let m=class_getInstanceMethod(c,sel);if m==0 as Id{return 0 as Id;}let old=method_getImplementation(m);if !class_addMethod(c,sel,imp,method_getTypeEncoding(m)){method_setImplementation(m,imp);}old}}
unsafe fn json(data:Id)->Id{unsafe{transmute::<Id,Json>(OLD_JSON)(cls(b"NSJSONSerialization\0" as *const u8),s(b"JSONObjectWithData:options:error:\0" as *const u8),data,0,0 as Id)}}
unsafe fn encode(o:Id)->Id{unsafe{m3(cls(b"NSJSONSerialization\0" as *const u8),s(b"dataWithJSONObject:options:error:\0" as *const u8),o,0 as Id,0 as Id)}}
unsafe fn chosen(id:Id)->bool{unsafe{m1(SAVED,s(b"objectForKey:\0" as *const u8),id)!=0 as Id}}
unsafe fn user_id(node:Id)->Id{unsafe{get(get(get(node,b"stream\0" as *const u8),b"broadcaster\0" as *const u8),b"userID\0" as *const u8)}}

// iPad's persistent Following drawer uses PersonalSectionChannel cards rather
// than the phone tab's FollowedLiveUserEdge. Both use the same exact fragments.
unsafe fn sidebar_user_id(item:Id)->Id{unsafe{let direct=get(get(item,b"user\0" as *const u8),b"userID\0" as *const u8);if is_string(direct){direct}else{get(get(get(item,b"content\0" as *const u8),b"broadcaster\0" as *const u8),b"userID\0" as *const u8)}}}
unsafe fn followed_section(value:Id)->bool{unsafe{
 eq(value,str(b"FOLLOWED_SECTION\0" as *const u8))||eq(value,str(b"ALPHABETICAL_FOLLOWED_SECTION\0" as *const u8))||eq(value,str(b"RECS_FOLLOWED_SECTION\0" as *const u8))
}}
unsafe fn sidebar_items(old:Id,rows:Id,selected:Id)->Id{unsafe{
 if old!=0 as Id&&old!=null()&&!is_array(old){return old;}
 let ids=m0(cls(b"NSMutableSet\0" as *const u8),s(b"set\0" as *const u8));
 if is_array(old){let en=m0(old,s(b"objectEnumerator\0" as *const u8));let mut item=m0(en,s(b"nextObject\0" as *const u8));while item!=0 as Id{let id=sidebar_user_id(item);if is_string(id){m1(ids,s(b"addObject:\0" as *const u8),id);}item=m0(en,s(b"nextObject\0" as *const u8));}}
 let result=array();let keys=m0(selected,s(b"allKeys\0" as *const u8));let en=m0(keys,s(b"objectEnumerator\0" as *const u8));let mut id=m0(en,s(b"nextObject\0" as *const u8));
 while id!=0 as Id{
  let stream=get(m1(rows,s(b"objectForKey:\0" as *const u8),id),b"stream\0" as *const u8);let user=get(stream,b"broadcaster\0" as *const u8);
  if is_dict(user)&&eq(get(stream,b"__typename\0" as *const u8),str(b"Stream\0" as *const u8))&&!b1(ids,s(b"containsObject:\0" as *const u8),id){
   let item=dict();set(item,b"__typename\0" as *const u8,str(b"PersonalSectionChannel\0" as *const u8));set(item,b"user\0" as *const u8,user);set(item,b"content\0" as *const u8,stream);add(result,item);m1(ids,s(b"addObject:\0" as *const u8),id);
  }id=m0(en,s(b"nextObject\0" as *const u8));
 }
 if count(result,s(b"count\0" as *const u8))==0{return old;}if is_array(old){m1(result,s(b"addObjectsFromArray:\0" as *const u8),old);}result
}}
unsafe fn merge_sidebar(root:Id,rows:Id,selected:Id)->Id{unsafe{
 let data=get(root,b"data\0" as *const u8);let sections=get(data,b"personalSections\0" as *const u8);if !is_array(sections){return root;}
 let out=array();let en=m0(sections,s(b"objectEnumerator\0" as *const u8));let mut section=m0(en,s(b"nextObject\0" as *const u8));let mut changed=false;
 while section!=0 as Id{
  let mut value=section;
  if followed_section(get(section,b"type\0" as *const u8)){
   let before=get(section,b"items\0" as *const u8);let after=sidebar_items(before,rows,selected);
   if before!=after{value=mutable(section);set(value,b"items\0" as *const u8,after);changed=true;}
  }add(out,value);section=m0(en,s(b"nextObject\0" as *const u8));
 }
 if !changed{return root;}let d=mutable(data);set(d,b"personalSections\0" as *const u8,out);let result=mutable(root);set(result,b"data\0" as *const u8,d);result
}}
unsafe fn merge_one(root:Id,rows:Id,selected:Id)->Id{unsafe{
 if !is_dict(root){return root;}
 let operation=get(get(root,b"extensions\0" as *const u8),b"operationName\0" as *const u8);
 if eq(operation,str(b"personalSectionsSidebar\0" as *const u8)){return merge_sidebar(root,rows,selected);}if !eq(operation,str(b"FireflyFollowedLiveStreams\0" as *const u8)){return root;}
 let data=get(root,b"data\0" as *const u8);let user=get(data,b"currentUser\0" as *const u8);let conn=get(user,b"followedLiveUsers\0" as *const u8);
 if !eq(get(conn,b"__typename\0" as *const u8),str(b"FollowedLiveUserConnection\0" as *const u8)){return root;}
 let old_edges=get(conn,b"edges\0" as *const u8);if !is_array(old_edges){return root;}
 let ids=m0(cls(b"NSMutableSet\0" as *const u8),s(b"set\0" as *const u8));let n=count(old_edges,s(b"count\0" as *const u8));let mut i=0usize;
 while i<n{let id=user_id(get(mu(old_edges,s(b"objectAtIndex:\0" as *const u8),i),b"node\0" as *const u8));if is_string(id){m1(ids,s(b"addObject:\0" as *const u8),id);}i=i+1;}
 let edges=array();let keys=m0(selected,s(b"allKeys\0" as *const u8));let total=count(keys,s(b"count\0" as *const u8));i=0;
 while i<total{let id=mu(keys,s(b"objectAtIndex:\0" as *const u8),i);let node=m1(rows,s(b"objectForKey:\0" as *const u8),id);
  if is_dict(node)&&!b1(ids,s(b"containsObject:\0" as *const u8),id){
   let edge=dict();set(edge,b"__typename\0" as *const u8,str(b"FollowedLiveUserEdge\0" as *const u8));set(edge,b"cursor\0" as *const u8,str(b"\0" as *const u8));set(edge,b"trackingID\0" as *const u8,null());set(edge,b"node\0" as *const u8,node);add(edges,edge);m1(ids,s(b"addObject:\0" as *const u8),id);
  }i=i+1;
 }
 if count(edges,s(b"count\0" as *const u8))==0{return root;}
 // Prepend additions; the real final server edge/cursor remains final.
 let added=count(edges,s(b"count\0" as *const u8));m1(edges,s(b"addObjectsFromArray:\0" as *const u8),old_edges);
 let c=mutable(conn);set(c,b"edges\0" as *const u8,edges);let u=mutable(user);set(u,b"followedLiveUsers\0" as *const u8,c);
 let follows=get(u,b"follows\0" as *const u8);if is_dict(follows){let value=get(follows,b"totalCount\0" as *const u8);if value!=0 as Id&&b1(value,s(b"isKindOfClass:\0" as *const u8),cls(b"NSNumber\0" as *const u8)){let f=mutable(follows);set(f,b"totalCount\0" as *const u8,number(count(value,s(b"unsignedIntegerValue\0" as *const u8))+added));set(u,b"follows\0" as *const u8,f);}}
 let d=mutable(data);set(d,b"currentUser\0" as *const u8,u);let result=mutable(root);set(result,b"data\0" as *const u8,d);result
}}
// The native app uses FireflyFollowedLiveStreams ONLY for cursor:nil and the
// distinct FollowedLiveStreams operation for pagination (verified disassembly).
// Apollo dynamically calls this exact Foundation class method before decoding.
unsafe fn merge_root(root:Id)->Id{unsafe{
 lock();let rows=retain(LIVE);let selected=m0(SAVED,s(b"copy\0" as *const u8));let fresh=UPDATED!=0.0&&CFAbsoluteTimeGetCurrent()<UPDATED+90.0;unlock();
 if !fresh{release(rows);release(selected);return root;}
 let mut result=root;
 if is_array(root){let n=count(root,s(b"count\0" as *const u8));let out=array();let mut i=0usize;let mut changed=false;while i<n{let before=mu(root,s(b"objectAtIndex:\0" as *const u8),i);let after=merge_one(before,rows,selected);if before!=after{changed=true;}add(out,after);i=i+1;}if changed{result=out;}
 }else{result=merge_one(root,rows,selected);}
 release(rows);release(selected);result
}}
unsafe extern "C" fn parse_response(o:Id,sel:Sel,data:Id,options:usize,error:Id)->Id{unsafe{
 let parsed=transmute::<Id,Json>(OLD_JSON)(o,sel,data,options,error);if parsed==0 as Id{return parsed;}
 merge_root(parsed)
}}

unsafe extern "C" fn publish(_:Id){unsafe{
 let pool=m0(cls(b"NSAutoreleasePool\0" as *const u8),s(b"new\0" as *const u8));
 let screens=m0(SCREENS,s(b"allObjects\0" as *const u8));let mut e=m0(screens,s(b"objectEnumerator\0" as *const u8));let mut screen=m0(e,s(b"nextObject\0" as *const u8));
 while screen!=0 as Id{m0(screen,s(b"setNeedsRefreshAllContents\0" as *const u8));screen=m0(e,s(b"nextObject\0" as *const u8));}
 let sidebars=m0(SIDEBARS,s(b"allObjects\0" as *const u8));e=m0(sidebars,s(b"objectEnumerator\0" as *const u8));let mut sidebar=m0(e,s(b"nextObject\0" as *const u8));
 while sidebar!=0 as Id{let view=m0(sidebar,s(b"viewIfLoaded\0" as *const u8));if m0(view,s(b"window\0" as *const u8))!=0 as Id{m0(sidebar,s(b"triggerRefresh\0" as *const u8));}sidebar=m0(e,s(b"nextObject\0" as *const u8));}
 let buttons=m0(BUTTONS,s(b"allObjects\0" as *const u8));e=m0(buttons,s(b"objectEnumerator\0" as *const u8));let mut button=m0(e,s(b"nextObject\0" as *const u8));
 while button!=0 as Id{update_button(button);button=m0(e,s(b"nextObject\0" as *const u8));}
 m0(pool,s(b"drain\0" as *const u8));
}}
unsafe extern "C" fn fetch_metadata(_:Id){unsafe{
 let pool=m0(cls(b"NSAutoreleasePool\0" as *const u8),s(b"new\0" as *const u8));
 lock();let ids=retain(m0(SAVED,s(b"allKeys\0" as *const u8)));let generation=GENERATION;unlock();
 let live=dict();let n=count(ids,s(b"count\0" as *const u8));let mut i=0usize;
 while i<n{
  let batch=array();let mut j=0usize;while i<n&&j<20{add(batch,mu(ids,s(b"objectAtIndex:\0" as *const u8),i));i=i+1;j=j+1;}
  let variables=dict();set(variables,b"userIDs\0" as *const u8,batch);set(variables,b"includeHasBrandedContent\0" as *const u8,mb(cls(b"NSNumber\0" as *const u8),s(b"numberWithBool:\0" as *const u8),false));set(variables,b"includeIsParticipatingDJ\0" as *const u8,mb(cls(b"NSNumber\0" as *const u8),s(b"numberWithBool:\0" as *const u8),true));set(variables,b"includeCollaborationCount\0" as *const u8,mb(cls(b"NSNumber\0" as *const u8),s(b"numberWithBool:\0" as *const u8),true));
  let payload=dict();set(payload,b"operationName\0" as *const u8,str(b"LiveStreamsForUsers\0" as *const u8));set(payload,b"variables\0" as *const u8,variables);set(payload,b"query\0" as *const u8,QUERY);
  let url=m1(cls(b"NSURL\0" as *const u8),s(b"URLWithString:\0" as *const u8),str(b"https://gql.twitch.tv/gql\0" as *const u8));let request=m1(cls(b"NSMutableURLRequest\0" as *const u8),s(b"requestWithURL:\0" as *const u8),url);
  m1(request,s(b"setHTTPMethod:\0" as *const u8),str(b"POST\0" as *const u8));md(request,s(b"setTimeoutInterval:\0" as *const u8),12.0);
  m2(request,s(b"setValue:forHTTPHeaderField:\0" as *const u8),str(b"application/json\0" as *const u8),str(b"Content-Type\0" as *const u8));
  // Public client ID already present in this supplied app, verified by a real
  // unauthenticated native-query probe. No account/OAuth header is accessed.
  m2(request,s(b"setValue:forHTTPHeaderField:\0" as *const u8),str(b"kimne78kx3ncx6brgo4mv6wki5h1ko\0" as *const u8),str(b"Client-ID\0" as *const u8));m1(request,s(b"setHTTPBody:\0" as *const u8),encode(payload));
  let mut response=0 as Id;let mut error=0 as Id;
  let bytes=m3(cls(b"NSURLConnection\0" as *const u8),s(b"sendSynchronousRequest:returningResponse:error:\0" as *const u8),request,&raw mut response as Id,&raw mut error as Id);
  let status=count(response,s(b"statusCode\0" as *const u8));
  if bytes!=0 as Id&&error==0 as Id&&status>=200&&status<300{
   let users=get(get(json(bytes),b"data\0" as *const u8),b"users\0" as *const u8);
   if is_array(users){let mut en=m0(users,s(b"objectEnumerator\0" as *const u8));let mut user=m0(en,s(b"nextObject\0" as *const u8));while user!=0 as Id{
    let id=user_id(user);let stream=get(user,b"stream\0" as *const u8);
    if is_string(id)&&eq(get(stream,b"__typename\0" as *const u8),str(b"Stream\0" as *const u8))&&is_string(get(stream,b"id\0" as *const u8)){m2(live,s(b"setObject:forKey:\0" as *const u8),user,id);}
    user=m0(en,s(b"nextObject\0" as *const u8));
   }}
  }
 }
 lock();let old=LIVE;LIVE=retain(live);UPDATED=CFAbsoluteTimeGetCurrent();BUSY=false;let again=generation!=GENERATION;unlock();release(old);release(ids);
 dispatch_async_f(MAIN,0 as Id,publish);if again{start_fetch();}
 m0(pool,s(b"drain\0" as *const u8));
}}
unsafe fn start_fetch(){unsafe{
 lock();let run=!BUSY&&ACTIVE&&QUERY!=0 as Id&&count(SAVED,s(b"count\0" as *const u8))!=0;
 if run{BUSY=true;dispatch_async_f(dispatch_get_global_queue(0,0),0 as Id,fetch_metadata);}unlock();
}}
unsafe extern "C" fn tick(_:Id,_:Sel,_:Id){unsafe{
 let screens=m0(SCREENS,s(b"allObjects\0" as *const u8));let en=m0(screens,s(b"objectEnumerator\0" as *const u8));let mut screen=m0(en,s(b"nextObject\0" as *const u8));let mut visible=false;
 while screen!=0 as Id{let view=m0(screen,s(b"viewIfLoaded\0" as *const u8));if m0(view,s(b"window\0" as *const u8))!=0 as Id{visible=true;}screen=m0(en,s(b"nextObject\0" as *const u8));}
 let sidebars=m0(SIDEBARS,s(b"allObjects\0" as *const u8));let se=m0(sidebars,s(b"objectEnumerator\0" as *const u8));let mut sidebar=m0(se,s(b"nextObject\0" as *const u8));
 while sidebar!=0 as Id{let view=m0(sidebar,s(b"viewIfLoaded\0" as *const u8));if m0(view,s(b"window\0" as *const u8))!=0 as Id{visible=true;}sidebar=m0(se,s(b"nextObject\0" as *const u8));}
 if visible{start_fetch();}
}}
unsafe extern "C" fn suspend(_:Id,_:Sel,_:Id){unsafe{lock();ACTIVE=false;unlock();}}
unsafe extern "C" fn resume(_:Id,_:Sel,_:Id){unsafe{lock();ACTIVE=true;unlock();start_fetch();}}

unsafe fn update_button(button:Id){unsafe{let id=assoc(button,&raw const CHANNEL_KEY);lock();let on=id!=0 as Id&&chosen(id);unlock();mb(button,s(b"setSelected:\0" as *const u8),on);m1(button,s(b"setAccessibilityValue:\0" as *const u8),if on{str(b"On, saved only on this device\0" as *const u8)}else{str(b"Off\0" as *const u8)});}}
unsafe extern "C" fn toggle(_:Id,_:Sel,button:Id){unsafe{
 let id=assoc(button,&raw const CHANNEL_KEY);if !is_string(id){return;}
 lock();if chosen(id){m1(SAVED,s(b"removeObjectForKey:\0" as *const u8),id);}else{m2(SAVED,s(b"setObject:forKey:\0" as *const u8),number(1),id);}GENERATION=GENERATION+1;
 let defaults=m0(cls(b"NSUserDefaults\0" as *const u8),s(b"standardUserDefaults\0" as *const u8));m2(defaults,s(b"setObject:forKey:\0" as *const u8),SAVED,str(b"TwitchForcedFollow.LocalChannels.v1\0" as *const u8));unlock();
 update_button(button);publish(0 as Id);start_fetch();
}}
unsafe fn attach_button(header:Id){unsafe{
 let iv=class_getInstanceVariable(object_getClass(header),b"viewModel\0" as *const u8);if iv==0 as Id{return;}
 let storage=header as usize+ivar_getOffset(iv);let tag=*((storage+8)as *const u8);
 let stack=field(header,b"$__lazy_storage_$_infoStackView\0" as *const u8);if stack==0 as Id{return;}
 let mut button=assoc(header,&raw const BUTTON_KEY);
 if tag!=0{if button!=0 as Id{put(button,&raw const CHANNEL_KEY,0 as Id);mb(button,s(b"setHidden:\0" as *const u8),true);}return;}
 let id=*((storage+4)as *const u32);if id==0{if button!=0 as Id{put(button,&raw const CHANNEL_KEY,0 as Id);mb(button,s(b"setHidden:\0" as *const u8),true);}return;}
 if button==0 as Id{
  button=mu(cls(b"UIButton\0" as *const u8),s(b"buttonWithType:\0" as *const u8),1);
  title(button,s(b"setTitle:forState:\0" as *const u8),str(b"Forced Follow\0" as *const u8),0);title(button,s(b"setTitle:forState:\0" as *const u8),str(b"Forced Following\0" as *const u8),4);
  action(button,s(b"addTarget:action:forControlEvents:\0" as *const u8),TARGET,s(b"toggle:\0" as *const u8),64);
  let label=m0(button,s(b"titleLabel\0" as *const u8));let font=m1(cls(b"UIFont\0" as *const u8),s(b"preferredFontForTextStyle:\0" as *const u8),str(b"UICTFontTextStyleSubhead\0" as *const u8));m1(label,s(b"setFont:\0" as *const u8),font);mb(label,s(b"setAdjustsFontForContentSizeCategory:\0" as *const u8),true);
  m1(button,s(b"setBackgroundColor:\0" as *const u8),m0(cls(b"UIColor\0" as *const u8),s(b"secondarySystemFillColor\0" as *const u8)));md(m0(button,s(b"layer\0" as *const u8)),s(b"setCornerRadius:\0" as *const u8),6.0);
  inset(button,s(b"setContentEdgeInsets:\0" as *const u8),Insets{top:10.0,left:12.0,bottom:10.0,right:12.0});
  m1(button,s(b"setAccessibilityIdentifier:\0" as *const u8),str(b"TwitchForcedFollowToggle\0" as *const u8));m1(button,s(b"setAccessibilityLabel:\0" as *const u8),str(b"Forced Follow\0" as *const u8));m1(button,s(b"setAccessibilityHint:\0" as *const u8),str(b"Includes this channel in Following on this device\0" as *const u8));
  put(header,&raw const BUTTON_KEY,button);m1(BUTTONS,s(b"addObject:\0" as *const u8),button);m1(stack,s(b"addArrangedSubview:\0" as *const u8),button);
  m0(header,s(b"setNeedsLayout\0" as *const u8));m0(m0(header,s(b"superview\0" as *const u8)),s(b"setNeedsLayout\0" as *const u8));
 }
 let channel=m0(number(id as usize),s(b"stringValue\0" as *const u8));put(button,&raw const CHANNEL_KEY,channel);mb(button,s(b"setHidden:\0" as *const u8),false);update_button(button);
}}
unsafe extern "C" fn profile_moved(o:Id,sel:Sel){unsafe{transmute::<Id,Zero>(OLD_PROFILE_MOVE)(o,sel);if m0(o,s(b"window\0" as *const u8))!=0 as Id{attach_button(o);}}}
unsafe extern "C" fn profile_layout(o:Id,sel:Sel){unsafe{transmute::<Id,Zero>(OLD_PROFILE_LAYOUT)(o,sel);attach_button(o);}}
unsafe extern "C" fn following_appeared(o:Id,sel:Sel,animated:bool){unsafe{transmute::<Id,Appear>(OLD_FOLLOWING_APPEAR)(o,sel,animated);m1(SCREENS,s(b"addObject:\0" as *const u8),o);start_fetch();}}

// This sidebar uses lazy Swift/ObjC metadata. Direct registration works once
// realized; the filtered superclass hook also catches its first appearance.
unsafe fn register_sidebar(o:Id){unsafe{m1(SIDEBARS,s(b"addObject:\0" as *const u8),o);start_fetch();}}
unsafe extern "C" fn sidebar_appeared(o:Id,sel:Sel,animated:bool){unsafe{transmute::<Id,Appear>(OLD_SIDEBAR_APPEAR)(o,sel,animated);register_sidebar(o);}}
unsafe extern "C" fn base_appeared(o:Id,sel:Sel,animated:bool){unsafe{
 transmute::<Id,Appear>(OLD_BASE_APPEAR)(o,sel,animated);
 let sidebar=cls(b"_TtC6Twitch27ViewerSidebarViewController\0" as *const u8);
 if sidebar!=0 as Id&&b1(o,s(b"isKindOfClass:\0" as *const u8),sidebar){register_sidebar(o);}
}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn forced_follow_initialize(){unsafe{
 LOCK=m0(cls(b"NSRecursiveLock\0" as *const u8),s(b"new\0" as *const u8));MAIN=dlsym(18446744073709551614usize as Id,b"_dispatch_main_q\0" as *const u8);
 let profile=cls(b"_TtC6Twitch15ProfileInfoView\0" as *const u8);let following=cls(b"_TtC6Twitch23FollowingViewController\0" as *const u8);let serialization=object_getClass(cls(b"NSJSONSerialization\0" as *const u8));
 if LOCK==0 as Id||MAIN==0 as Id||profile==0 as Id||following==0 as Id||serialization==0 as Id{return;}
 let defaults=m0(cls(b"NSUserDefaults\0" as *const u8),s(b"standardUserDefaults\0" as *const u8));let saved=m1(defaults,s(b"dictionaryForKey:\0" as *const u8),str(b"TwitchForcedFollow.LocalChannels.v1\0" as *const u8));SAVED=if is_dict(saved){m0(saved,s(b"mutableCopy\0" as *const u8))}else{m0(cls(b"NSMutableDictionary\0" as *const u8),s(b"new\0" as *const u8))};
 LIVE=m0(cls(b"NSDictionary\0" as *const u8),s(b"new\0" as *const u8));BUTTONS=retain(m0(cls(b"NSHashTable\0" as *const u8),s(b"weakObjectsHashTable\0" as *const u8)));SCREENS=retain(m0(cls(b"NSHashTable\0" as *const u8),s(b"weakObjectsHashTable\0" as *const u8)));
 SIDEBARS=retain(m0(cls(b"NSHashTable\0" as *const u8),s(b"weakObjectsHashTable\0" as *const u8)));
 let path=m2(m0(cls(b"NSBundle\0" as *const u8),s(b"mainBundle\0" as *const u8)),s(b"pathForResource:ofType:\0" as *const u8),str(b"ForcedFollowLive\0" as *const u8),str(b"graphql\0" as *const u8));QUERY=retain(m3(cls(b"NSString\0" as *const u8),s(b"stringWithContentsOfFile:encoding:error:\0" as *const u8),path,4 as Id,0 as Id));if QUERY==0 as Id{return;}
 let target_class=objc_allocateClassPair(cls(b"NSObject\0" as *const u8),b"TwitchForcedFollowActions\0" as *const u8,0);if target_class==0 as Id{return;}
 class_addMethod(target_class,s(b"toggle:\0" as *const u8),toggle as Id,b"v24@0:8@16\0" as *const u8);class_addMethod(target_class,s(b"tick:\0" as *const u8),tick as Id,b"v24@0:8@16\0" as *const u8);class_addMethod(target_class,s(b"suspend:\0" as *const u8),suspend as Id,b"v24@0:8@16\0" as *const u8);class_addMethod(target_class,s(b"resume:\0" as *const u8),resume as Id,b"v24@0:8@16\0" as *const u8);objc_registerClassPair(target_class);TARGET=m0(target_class,s(b"new\0" as *const u8));
 OLD_JSON=hook(serialization,s(b"JSONObjectWithData:options:error:\0" as *const u8),parse_response as Id);
 OLD_PROFILE_MOVE=hook(profile,s(b"didMoveToWindow\0" as *const u8),profile_moved as Id);OLD_PROFILE_LAYOUT=hook(profile,s(b"layoutSubviews\0" as *const u8),profile_layout as Id);OLD_FOLLOWING_APPEAR=hook(following,s(b"viewDidAppear:\0" as *const u8),following_appeared as Id);
 let sidebar=cls(b"_TtC6Twitch27ViewerSidebarViewController\0" as *const u8);
 if sidebar!=0 as Id{OLD_SIDEBAR_APPEAR=hook(sidebar,s(b"viewDidAppear:\0" as *const u8),sidebar_appeared as Id);}
 OLD_BASE_APPEAR=hook(cls(b"UIViewController\0" as *const u8),s(b"viewDidAppear:\0" as *const u8),base_appeared as Id);
 timer(cls(b"NSTimer\0" as *const u8),s(b"scheduledTimerWithTimeInterval:target:selector:userInfo:repeats:\0" as *const u8),30.0,TARGET,s(b"tick:\0" as *const u8),0 as Id,true);
 let center=m0(cls(b"NSNotificationCenter\0" as *const u8),s(b"defaultCenter\0" as *const u8));observe(center,s(b"addObserver:selector:name:object:\0" as *const u8),TARGET,s(b"suspend:\0" as *const u8),str(b"UIApplicationDidEnterBackgroundNotification\0" as *const u8),0 as Id);observe(center,s(b"addObserver:selector:name:object:\0" as *const u8),TARGET,s(b"resume:\0" as *const u8),str(b"UIApplicationWillEnterForegroundNotification\0" as *const u8),0 as Id);
}}
#[used]#[unsafe(link_section="__DATA,__mod_init_func")]static INITIALIZE:unsafe extern "C" fn()=forced_follow_initialize;
